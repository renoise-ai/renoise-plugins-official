#!/usr/bin/env python3
"""Lay the remake out on the source's timeline as an rn edit (edit.json), then render and check it with rn.

    python build_edit.py <analysis folder> results.json [--audio units|source|none] [--music bed.m4a [--beat-sync auto|on|off]]
                         [--subs auto|none|file] [--width N] [--render]

results.json maps plan items (remake/plan.json) to files, paths relative to results.json or absolute:
    {"G1": "gen/G1.mp4", "G2": ["gen/G2_part1.mp4", "gen/G2_part2.mp4"], "C1": "code/C1.mp4", "P1": "kf/kf_9.png"}
  G (generated unit)  the unit's video, or its parts in order. Each shot is taken at the planned offset, snapped to the
                      cuts the model actually made (rn cuts, --snap seconds), and slowed to the shot's exact length
                      when the generation came out short.
  C (code part)       a video covering the part's whole span.
  P (still)           an image, moved with the zoom / pan measured on the source shot, or a video.
  K (kept)            always the source; leave it out. Anything else missing becomes an rn placeholder card.

Every shot is one main-track clip whose length is the source shot's, to the frame, so the cuts land where the source's
do. Where the source does not cut (rn shots measured the transition), the edit makes its transition again between the two
pieces: a dissolve or wipe as an overlap of its frames, a fade through black or white on each side's own frames. With
--music under a source that cut to the beat, the cuts that were on a beat move onto the music's beats. Overlay lines
from review.json are burned as subtitles; the mix goes to -14 LUFS / -1 dBTP.

Writes <folder>/remake/edit.json and overlays.ass. With --render it then runs
    rn assemble edit.json  ->  remake/out/remake.mp4   (--placeholders when pieces are missing)
    rn qa                  ->  remake/out/qa.json
    rn compare --cuts      ->  remake/out/compare.mp4 (source | remake), compare.jpg, compare.json
and writes remake/out/qc.json: delivery findings, cuts the remake has where the source has none (and the reverse),
pieces still missing, shots that play slower than generated, the transitions made again (and why any was not), and with
--music the cuts moved onto beats. With rn 0.7+, rn qa reads edit.json itself (placeholder
cards included), and rn compare --shots adds, for every shot, where the remake begins a shot differently from the source
(a dissolve where it cuts) and where its camera move clearly differs.
"""
from __future__ import annotations

import argparse
import json
import math
import os
import shutil
import subprocess
import sys
import tempfile
from fractions import Fraction
from pathlib import Path


def rn_json(*args: str) -> dict:
    with tempfile.TemporaryDirectory() as tmp:
        out = Path(tmp) / "r.json"
        r = subprocess.run(["rn", *args, "--json", str(out)], capture_output=True, text=True)
        if r.returncode not in (0, 1) or not out.exists():
            msg = (r.stderr or r.stdout).strip().splitlines()
            sys.exit(f"✗ rn {args[0]}: {msg[-1] if msg else 'failed'}")
        return json.loads(out.read_text(encoding="utf-8"))


RN_07 = (0, 7, 0)


def rn_version() -> tuple[int, ...] | None:
    try:
        out = subprocess.run(["rn", "--version"], capture_output=True, text=True, timeout=60).stdout.split()
        return tuple(int(part) for part in out[-1].split(".")[:3]) if out else None
    except (OSError, ValueError, subprocess.TimeoutExpired):
        return None


def shot_findings(shots: dict | None) -> dict:
    """From rn compare --shots (rn 0.7+), the whole film against its source: shots that begin differently (a dissolve where
    the source cuts, or the reverse), transitions of the same kind that differ in frames (by more than 3 and a quarter),
    a wipe's side or a fade's colour, and shots whose camera move differs clearly (check_units.py's rule, now for every
    shot: still and code shots and their replayed zoom / pan too). Source shots by rn shots' number and time."""
    if not shots:
        return {}
    from check_units import camera_check, camera_words  # same folder
    begin, length, camera = [], [], []
    for p in shots["pairs"]:
        a, b = p["a"], p["b"]
        where = f"source shot at {a['start']:.2f}-{a['end']:.2f} s"
        if not b:
            continue
        ta, tb = a.get("transition") or {}, b.get("transition") or {}
        if b["transition_in"] != a["transition_in"]:
            begin.append({"at": a["start"], "source": a["transition_in"], "remake": b["transition_in"]})
        elif ta and tb and (abs((ta.get("frames") or 0) - (tb.get("frames") or 0)) > max(3, 0.25 * (ta.get("frames") or 0))
                            or ta.get("edge") != tb.get("edge") or ta.get("through") != tb.get("through")):
            length.append({"at": a["start"], "type": a["transition_in"], "source": ta, "remake": tb})
        if p["covered"] < 0.7:  # the remake's shot there spans more than this one
            continue
        ma, mb = p["motion"]["a"], p["motion"]["b"]
        src = {"zoom": ma["zoom_per_s"], "pan": ma["pan_widths_per_s"], "dir": ma["pan_dir_deg"], "fit": ma["rigid_fit"],
               "still": abs(ma["zoom_per_s"]) < 0.004 and ma["pan_widths_per_s"] < 0.003}
        got = {"zoom": mb["zoom_per_s"], "pan": mb["pan_widths_per_s"], "dir": mb["pan_dir_deg"], "fit": mb["rigid_fit"]}
        found = camera_check(a["shot"] + 1, src, got)
        if found:
            camera.append({"at": a["start"], "where": where, "source": camera_words(src["zoom"], src["pan"], src["dir"]),
                           "remake": camera_words(got["zoom"], got["pan"], got["dir"])})
    return {"shots_begin_differently": begin, "transitions_differ": length, "camera_differs": camera}


def duration(path: Path) -> float:
    r = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(path)],
                       capture_output=True, text=True, check=True)
    return float(r.stdout.strip() or 0)


def video_size(path: Path) -> tuple[int, int] | None:
    r = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries", "stream=width,height", "-of", "json",
                        str(path)], capture_output=True, text=True)
    s = (json.loads(r.stdout or "{}").get("streams") or [{}])[0]
    return (s["width"], s["height"]) if s.get("width") and s.get("height") else None


def footage_size(files: list[Path], w: int, h: int) -> tuple[float, float]:
    """The frame at the generated footage's own resolution: the source's shape, scaled down to the smallest generated
    video of that shape (generations are usually 480p or 720p), never up. The lowest resolution unless the user asks
    for more (--width)."""
    scale = 1.0
    for f in files:
        size = video_size(f) if f.suffix.lower() in (".mp4", ".mov", ".webm", ".mkv") else None
        if size and abs(size[0] / size[1] / (w / h) - 1) < 0.1:
            scale = min(scale, size[0] / w, size[1] / h)
    return w * scale, h * scale


def source_fps(path: str) -> Fraction:
    r = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries", "stream=r_frame_rate,avg_frame_rate",
                        "-of", "json", path], capture_output=True, text=True, check=True)
    s = (json.loads(r.stdout).get("streams") or [{}])[0]
    for k in ("avg_frame_rate", "r_frame_rate"):
        try:
            f = Fraction(s.get(k) or "0")
            if 0 < f <= 60:
                return f
        except (ValueError, ZeroDivisionError):
            pass
    return Fraction(30)


# ---------------------------------------------------------------- overlay text
def _ass_colour(hexrgb: str | None, default: str) -> str:
    """#RRGGBB or #RRGGBBAA (AA = opacity) -> ASS &HAABBGGRR."""
    h = (hexrgb or default).lstrip("#")
    r, g, b = h[0:2], h[2:4], h[4:6]
    alpha = 255 - int(h[6:8], 16) if len(h) >= 8 else 0
    return f"&H{alpha:02X}{b}{g}{r}".upper()


def _ass_time(t: float) -> str:
    cs = int(round(max(t, 0) * 100))
    return f"{cs // 360000}:{cs // 6000 % 60:02d}:{cs // 100 % 60:02d}.{cs % 100:02d}"


def overlays_ass(cues: list[dict], size: tuple[int, int]) -> str:
    """Overlay text lines -> an ASS file at the film's size. A line: {"t0", "t1", "text", optional "x", "y" (centre,
    0-1 of the frame; default 0.5, 0.82), "size" (text height, 0-1 of the frame height; default 0.045), "color",
    "outline" (#RRGGBB), "outline_w" (0-1 of the height; default 0.004), "box" (#RRGGBBAA band behind the text),
    "bold" (default true), "font" (default "Sans"), "fade" (seconds in and out; default 0.12)}."""
    w, h = size
    head = ["[Script Info]", "ScriptType: v4.00+", f"PlayResX: {w}", f"PlayResY: {h}", "WrapStyle: 0", "",
            "[V4+ Styles]",
            "Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, "
            "StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding",
            "Style: Default,Sans,40,&H00FFFFFF,&H00FFFFFF,&H00000000,&H00000000,1,0,0,0,100,100,0,0,1,2,0,5,0,0,0,1", "",
            "[Events]", "Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text"]
    lines = []
    for c in cues:
        size_px = max(8, round(float(c.get("size", 0.045)) * h))
        x, y = round(float(c.get("x", 0.5)) * w), round(float(c.get("y", 0.82)) * h)
        fade = round(float(c.get("fade", 0.12)) * 1000)
        fill = _ass_colour(c.get("color"), "#FFFFFF")
        # BorderStyle 3 (style Box) draws an opaque box in the outline colour, the border width as its padding
        edge = _ass_colour(c.get("box"), "#00000099") if c.get("box") else _ass_colour(c.get("outline"), "#000000")
        border = size_px // 4 if c.get("box") else max(0, round(float(c.get("outline_w", 0.004)) * h))
        tags = (f"\\an5\\pos({x},{y})\\fn{c.get('font', 'Sans')}\\fs{size_px}\\b{1 if c.get('bold', True) else 0}"
                f"\\1c&H{fill[4:]}&\\1a&H{fill[2:4]}&\\3c&H{edge[4:]}&\\3a&H{edge[2:4]}&\\bord{border}\\fad({fade},{fade})")
        style = "Box" if c.get("box") else "Default"
        text = str(c.get("text", "")).replace("\n", "\\N").replace("{", "(").replace("}", ")")
        lines.append(f"Dialogue: 0,{_ass_time(float(c['t0']))},{_ass_time(float(c['t1']))},{style},,0,0,0,,{{{tags}}}{text}")
    if any(c.get("box") for c in cues):
        head.insert(head.index("[Events]") - 1,
                    "Style: Box,Sans,40,&H00FFFFFF,&H00FFFFFF,&H66000000,&H00000000,1,0,0,0,100,100,0,0,3,2,0,5,0,0,0,1")
    return "\n".join(head + lines) + "\n"


# ---------------------------------------------------------------- the edit
def snap(points: list[float], cuts: list[float], tol: float) -> list[float]:
    """Move each planned boundary to the nearest cut the model actually made within `tol` seconds."""
    out = []
    for p in points:
        near = min(cuts, key=lambda c: abs(c - p), default=None)
        out.append(near if near is not None and abs(near - p) <= tol else p)
    return out


def best_scale(L: float, D: float, planned: list[float], found: list[float], tol: float = 0.5) -> float:
    """How a generation shorter than planned (L < D seconds) maps onto the plan: squeezed evenly (L / D) or cut off at the
    end (1.0, the shots keep their lengths and the last one runs short). Whichever lines more planned cuts up with the
    cuts the model made; squeezed when neither does better."""
    if L >= D - 0.05:
        return 1.0

    def hits(scale: float) -> int:
        return sum(any(abs(f - t * scale) <= tol for f in found) for t in planned if t * scale < L)

    return 1.0 if planned and hits(1.0) > hits(L / D) else L / D


def still_keys(dur: float, size: tuple[int, int], motion: dict) -> dict:
    """Main-track keys that move a still the way the source shot moved: a steady zoom (zoom_per_s, a share of the frame
    each second) and a steady pan (pan_px_per_s in a 480-px-wide frame, towards pan_dir_deg), centred on the shot. The
    picture starts enlarged by just enough that no edge comes into view on the way."""
    w, h = size
    zoom = float(motion.get("zoom_per_s") or 0.0)
    speed = float(motion.get("pan_px_per_s") or 0.0) * w / 480.0
    if abs(zoom) < 0.002 and speed < 2:
        return {}
    heading = math.radians(float(motion.get("pan_dir_deg") or 0.0))
    travel_x, travel_y = speed * dur * math.cos(heading), speed * dur * math.sin(heading)
    end_factor = 1.0 + zoom * dur  # the scale at the end relative to the start
    margin = 1.02 + max(0.0, 1.0 - end_factor) + (abs(travel_x) / w + abs(travel_y) / h)
    keys = lambda a, b: [[0, round(a, 4)], [round(dur, 4), round(b, 4)]]  # noqa: E731
    return {"scale": keys(margin, margin * end_factor), "left": keys(-travel_x / 2, travel_x / 2), "top": keys(-travel_y / 2, travel_y / 2)}


# ---------------------------------------------------------------- transitions and beats
UNMEASURED_FADE_S = 0.25  # each side of a fade whose length was not measured (analyzed without rn 0.7)
BEAT_STRETCH = 0.06  # a shot may play this much slower so a cut lands on the beat when its piece has no frames to spare


def rebuild_transition(i: int, p: int, shots: dict, clip_of: dict, room_f: dict, head_f: dict, tail_f: dict, overlap_f: dict,
                       frames: dict, fps: Fraction) -> dict | None:
    """How shot i begins in the source (rn shots: type and frames), made again between the new pieces of shots p and i.
    A dissolve (xfade "fade", the smooth mix) or a wipe (xfade "wipe" + the side rn read) overlaps the two pieces for its
    measured length: half before the source's boundary, half after, as far as the pieces have frames to spare there
    (a generation has none before its first frame, so the overlap usually runs on after the boundary; plan_units.py asks
    for the frames after). A fade through black or white needs no overlap: each side fades on its own frames, out, held
    and in as measured. A kept shot's frames already hold its half. None for a cut; {"skip": ...} when not made."""
    kind = shots[i].get("transition_in")
    if kind not in ("dissolve", "wipe", "fade"):
        return None
    t = shots[i].get("transition") or {}
    where = {"shot": i, "type": kind}
    if shots[i]["item"] == shots[p]["item"]:
        return {"skip": {**where, "why": f"inside {shots[i]['item']}: that piece makes it"}}
    cards = [shots[x]["item"] for x in (p, i) if clip_of[x].get("_card")]
    if cards:
        return {"skip": {**where, "why": f"waiting for {', '.join(cards)}"}}
    kept = [x for x in (p, i) if clip_of[x].get("_kept")]
    if kind == "fade":
        through = t.get("through") or "black"
        out_n, hold_n, in_n = t.get("out_frames"), t.get("hold_frames") or 0, t.get("in_frames")
        if out_n is None or in_n is None:
            out_n = in_n = max(1, round(UNMEASURED_FADE_S * fps))
        out_n, hold_n = min(out_n, max(0, frames[p] - 1)), min(hold_n, max(0, frames[p] - 1 - out_n))
        in_n = min(in_n, max(0, frames[i] - 1))
        made: dict = {}
        if p not in kept and out_n:
            made["vf_out"] = {p: (out_n + hold_n, out_n, through)}
        if i not in kept and in_n:
            made["vf_in"] = {i: f"fade=t=in:st=0:d={float(Fraction(in_n) / fps):.4f}:color={through}"}
        if not made:
            return None  # two kept shots: the source's frames are the fade
        made["note"] = {**where, "made": f"fade through {through}", "out_frames": out_n, "hold_frames": hold_n, "in_frames": in_n,
                        **({"measured": False} if not t.get("out_frames") else {}),
                        **({"kept_side": f"#{kept[0]} (its own frames)"} if kept else {})}
        return made
    if kept:
        if len(kept) == 2:
            return None
        return {"skip": {**where, "why": f"#{kept[0]} is kept from the source, whose frames there already hold half of the source's {kind}"}}
    edge = t.get("edge")
    name = f"wipe{edge}" if kind == "wipe" and edge in ("left", "right", "up", "down") else "fade"
    want = int(t.get("frames") or max(2, round(0.5 * fps)))
    head_room, tail_room = room_f[i][0] - head_f[i], room_f[p][1] - tail_f[p]
    before = min(head_room, want // 2)
    after = min(tail_room, want - before)
    before = min(head_room, want - after)
    # rn: an overlap is shorter than both clips it joins and stays clear of the overlap into the clip before
    after = int(min(after, frames[i] - 1))
    before = int(min(before, frames[p] + head_f[p] - max(1, overlap_f.get(p, 0))))
    if after + before < max(2, want // 2):
        return {"skip": {**where, "why": f"no room: {shots[p]['item']} has {max(0, tail_room) / float(fps):.2f} s after #{p}, the "
                                         f"{kind} needs {want / float(fps):.2f} s; make that piece longer at the end"}}
    tail_f[p] += after
    head_f[i] += before
    overlap_f[i] = after + before
    note = {**where, "made": name, "frames": after + before, "source_frames": want}
    if not t.get("frames"):
        note["measured"] = False
    if after != before:
        note["late_by_s"] = round((after - before) / 2 / float(fps), 3)  # its middle against the source's boundary
    return {"xfade": {"type": name, "duration": round(float(Fraction(after + before) / fps), 6)}, "note": note}


def keep_on_beat(plan: dict, args, order: list[int], shots: dict, clip_of: dict, frames: dict, fps: Fraction, room_f: dict,
                 head_f: dict, tail_f: dict, overlap_f: dict, grow_f: dict) -> dict:
    """--music under a source that cut to the beat of its own sound (plan.json rhythm, from rn shots --beats): each cut
    that was on a beat moves onto the nearest beat of the new music (rn listen), keeping its offset from the beat, by at
    most --beat-max seconds. A move lengthens one neighbour (from its piece's spare frames, else played up to 6% slower;
    a kept shot is never lengthened) and shortens the other. Returns what moved, what could not, and the share of cuts
    within 2 frames of a beat: the source's, the remake's before the moves and after."""
    rh = plan.get("rhythm") or {}
    if args.beat_sync == "off":
        return {"beat_sync": "off"}
    if args.beat_sync == "auto" and not rh.get("cut_to_beat"):
        return {"beat_sync": "off: the source does not cut to the beat" if rh else "off: no beats measured (analyze with rn 0.7+)"}
    try:
        with tempfile.TemporaryDirectory() as tmp:  # its picture is not needed here
            beats = rn_json("listen", args.music, "-o", str(Path(tmp) / "listen.jpg")).get("beats") or {}
    except SystemExit as error:  # rn listen needs librosa: the sandbox has it
        return {"beat_sync": f"off: {error}"}
    times = beats.get("times") or []
    if len(times) < 2:
        return {"beat_sync": "off: no beat found in the music"}
    pos, acc = {}, 0
    for x in order:
        pos[x], acc = acc, acc + max(1, frames[x])

    def length(x: int) -> int:
        return max(1, frames[x]) + head_f[x] + tail_f[x] + grow_f[x]

    def spare(x: int) -> float:
        if clip_of[x].get("_kept"):
            return 0
        stretch = 0 if clip_of[x].get("_card") or "image" in clip_of[x] else math.floor(BEAT_STRETCH * frames[x])
        return room_f[x][1] - tail_f[x] - grow_f[x] + stretch

    def on_beat(at: dict) -> float | None:
        cuts = [at[x] for x in order[1:] if x not in overlap_f]
        near = [min(abs(float(Fraction(c) / fps) - b) for b in times) * float(fps) <= 2 + 1e-6 for c in cuts]
        return round(sum(near) / len(near), 3) if near else None

    on = set(rh.get("on_beat") or [])
    limit = round(args.beat_max * fps)
    moved, missed, at = [], [], dict(pos)
    for k, i in enumerate(order[1:], 1):
        if i not in on or i in overlap_f or shots[i].get("transition_in") not in ("cut", "flash", None):
            continue
        p = order[k - 1]
        off = float((shots[i].get("beat") or {}).get("offset_s") or 0.0)
        now = float(Fraction(pos[i]) / fps)
        beat = min(times, key=lambda b: abs(b + off - now))
        delta = round((beat + off) * fps) - pos[i]
        if delta == 0:
            continue
        grower, shrinker, n = (p, i, delta) if delta > 0 else (i, p, -delta)
        after_shrinker = order[order.index(shrinker) + 1] if shrinker != order[-1] else None
        # what the shorter shot must keep: half its frames, and room for the overlaps at both its ends
        floor = max(max(1, frames[shrinker]) // 2, overlap_f.get(shrinker, 0) + overlap_f.get(after_shrinker, 0) + 1)
        why = None
        if n > limit:
            why = f"the nearest beat is {n} frames away (--beat-max {args.beat_max} s)"
        elif spare(grower) < n:
            why = f"#{grower} ({shots[grower]['item']}) has no frames to spare at its end"
        elif length(shrinker) - n < floor:
            why = f"#{shrinker} is too short to give {n} frames"
        if why:
            missed.append({"shot": i, "frames": delta, "why": why})
            continue
        grow_f[grower] += n
        grow_f[shrinker] -= n
        at[i] = pos[i] + delta
        moved.append({"shot": i, "frames": delta})
    return {"beat_sync": "on", "music_bpm": beats.get("bpm"), "music_clear_pulse": beats.get("clear"), "moved": moved,
            "not_moved": missed, "cuts_within_2_frames_of_a_beat": {"source": rh.get("within_2_frames"),
                                                                    "remake_unmoved": on_beat(pos), "remake": on_beat(at)}}


def build(root: Path, results_path: Path, args) -> tuple[dict, dict]:
    plan = json.loads((root / "remake" / "plan.json").read_text(encoding="utf-8"))
    results = json.loads(results_path.read_text(encoding="utf-8"))
    edit_dir = root / "remake"

    def resolve(p: str) -> Path:
        q = Path(p) if Path(p).is_absolute() else results_path.parent / p
        if not q.exists():
            sys.exit(f"✗ {q} (from results.json) does not exist")
        return q

    def rel(p: Path | str) -> str:
        return os.path.relpath(Path(p).resolve(), edit_dir.resolve())

    src = plan["source"]
    fps = source_fps(src["path"])
    w, h = src["display"]
    if args.width:  # only when the user asks for a resolution; keeps the source's named ratio exactly
        rw, _, rh = str(src.get("aspect_ratio", "")).partition(":")
        shape = int(rh) / int(rw) if rw.isdigit() and rh.isdigit() else h / w
        w, h = args.width, round(args.width * shape)
    else:
        generated = [resolve(x) for it in plan["items"] if it["kind"] == "generate" and results.get(it["id"])
                     for x in (results[it["id"]] if isinstance(results[it["id"]], list) else [results[it["id"]]])]
        w, h = footage_size(generated, w, h)
    size = (int(w) // 2 * 2, int(h) // 2 * 2)
    sound = args.audio == "units"

    shots = {r["index"]: r for r in plan["shots"]}
    order = sorted(shots)
    # frame-exact lengths: each shot spans its source frames, so cuts land on the source's frames
    edge = {i: round(Fraction(str(shots[i]["start"])) * fps) for i in order}
    end_frame = round(Fraction(str(shots[order[-1]]["end"])) * fps)
    frames = {i: (edge[order[k + 1]] if k + 1 < len(order) else end_frame) - edge[i] for k, i in enumerate(order)}
    secs = {i: float(Fraction(max(1, frames[i])) / fps) for i in order}

    notes = {"placeholders": [], "retimed": [], "snapped": [], "transitions": [], "transitions_not_rebuilt": [],
             "expect": {"frames": sum(max(1, frames[i]) for i in order), "size": f"{size[0]}x{size[1]}", "fps": str(fps)}}
    # Each shot's piece, and how much more of it there is around the planned frames (file seconds before "in" and after
    # its planned end: "_room"), which transitions and beat moves draw on. An image or a placeholder card is any length;
    # a kept shot's neighbouring source frames belong to the source's own next shot, so it has none.
    INF = float("inf")
    clip_of: dict[int, dict] = {}
    for it in plan["items"]:
        got = results.get(it["id"])
        if it["kind"] == "keep":
            if got:
                sys.exit(f"✗ {it['id']} is a kept shot: it always comes from the source, leave it out of results.json")
            for i in it["shots"]:
                clip_of[i] = {"src": rel(src["path"]), "in": shots[i]["start"], "audio": args.audio == "units", "_room": (0.0, 0.0),
                              "_kept": True}
            continue
        if not got:
            notes["placeholders"].append(it["id"])
            label = f"{it['id']} not made yet"
            for i in it["shots"]:
                clip_of[i] = {"src": f"missing/{it['id']}.mp4", "meta": {"label": label, "prompt": (it.get("prompt_lines") or [""])[0][:200]},
                              "_room": (INF, INF), "_card": True}
            continue
        if it["kind"] == "generate":
            files = [resolve(x) for x in (got if isinstance(got, list) else [got])]
            if it["mode"] == "split":
                if len(files) != len(it["parts"]):
                    sys.exit(f"✗ {it['id']} has {len(it['parts'])} parts but results.json gives {len(files)} file(s)")
                parts = [(f, p["duration"], duration(f)) for f, p in zip(files, it["parts"])]
                clip_of[it["shots"][0]] = {"parts": parts, "_room": (0.0, max(0.0, parts[-1][2] - parts[-1][1]))}
                continue
            f = files[0]
            L, D = duration(f), it["duration"]
            made = [c["time"] for c in rn_json("cuts", str(f))["cuts"]] if len(it["offsets"]) > 1 else []
            scale = best_scale(L, D, [o["t1"] for o in it["offsets"][:-1]], made)
            bounds = [o["t0"] * scale for o in it["offsets"]] + [min(L, D * scale)]
            if len(it["offsets"]) > 1 and args.snap > 0:
                inner = snap(bounds[1:-1], made, args.snap)
                if inner != bounds[1:-1]:
                    notes["snapped"].append({"item": it["id"], "planned": [round(x, 3) for x in bounds[1:-1]], "used": inner})
                bounds = [bounds[0], *inner, bounds[-1]]
            for k, (o, a, z) in enumerate(zip(it["offsets"], bounds, bounds[1:])):
                last = k == len(it["offsets"]) - 1  # within the unit, the frames after a shot are the model's next shot
                clip_of[o["shot"]] = {"src": rel(f), "in": round(a, 4), "window": max(0.05, z - a), "audio": sound,
                                      "_room": (0.0, max(0.0, L - z) if last else 0.0)}
        elif it["kind"] == "code":
            f = resolve(got)
            L = duration(f)
            for i in it["shots"]:
                clip_of[i] = {"src": rel(f), "in": round(shots[i]["start"] - it["start"], 4), "audio": sound,
                              "_room": (0.0, max(0.0, L - it["duration"]) if i == it["shots"][-1] else 0.0)}
        elif it["kind"] == "still":
            f = resolve(got)
            i = it["shots"][0]
            if f.suffix.lower() in (".png", ".jpg", ".jpeg", ".webp"):
                clip_of[i] = {"image": rel(f), "_room": (INF, INF), "_motion": shots[i].get("motion") or {}}
            else:
                clip_of[i] = {"src": rel(f), "in": 0, "audio": sound, "_room": (0.0, max(0.0, duration(f) - secs[i]))}
    # the rate each piece plays at (file seconds per output second): a generation that came out short is slowed
    rate = {i: (clip_of[i]["window"] / secs[i] if "window" in clip_of[i] and abs(clip_of[i]["window"] / secs[i] - 1) > 0.02 else 1.0)
            for i in order}
    room_f = {i: tuple(x if x == INF else math.floor(x / rate[i] * fps + 1e-6) for x in clip_of[i]["_room"]) for i in order}

    head_f, tail_f = dict.fromkeys(order, 0), dict.fromkeys(order, 0)  # frames added before / after a shot's own
    xfade: dict[int, dict] = {}  # shot -> its main clip's transition
    overlap_f: dict[int, int] = {}  # shot -> frames it overlaps the clip before
    vf_in: dict[int, str] = {}
    vf_out: dict[int, tuple[int, int, str]] = {}  # shot -> (frames before its end where the fade starts, fade frames, colour)
    for k, i in enumerate(order[1:], 1):
        rebuilt = rebuild_transition(i, order[k - 1], shots, clip_of, room_f, head_f, tail_f, overlap_f, frames, fps)
        if not rebuilt:
            continue
        if "skip" in rebuilt:
            notes["transitions_not_rebuilt"].append(rebuilt["skip"])
            continue
        if "xfade" in rebuilt:
            xfade[i] = rebuilt["xfade"]
        vf_in.update(rebuilt.get("vf_in", {}))
        vf_out.update(rebuilt.get("vf_out", {}))
        notes["transitions"].append(rebuilt["note"])

    grow_f = dict.fromkeys(order, 0)  # frames a beat move adds to (or takes from) a shot
    if args.music:
        notes["rhythm"] = keep_on_beat(plan, args, order, shots, clip_of, frames, fps, room_f, head_f, tail_f, overlap_f, grow_f)

    main = []
    for i in order:
        c = {x: v for x, v in clip_of[i].items() if not x.startswith("_")}
        n_f = max(1, frames[i]) + head_f[i] + tail_f[i] + grow_f[i]
        d = float(Fraction(n_f) / fps)
        base = {"id": f"s{i}", "duration": round(d, 6), "meta": {"shot": i, "item": shots[i]["item"]}}
        fade_in = vf_in.get(i)
        fade_out = (lambda length: f"fade=t=out:st={float(Fraction(length - vf_out[i][0]) / fps):.4f}:d={float(Fraction(vf_out[i][1]) / fps):.4f}"
                    f":color={vf_out[i][2]}") if i in vf_out else None
        if "parts" in c:  # a split shot: its parts back to back, each its planned length (the last one takes what was added)
            parts = c["parts"]
            for k, (f, plen, L) in enumerate(parts, 1):
                if k == len(parts):
                    plen = max(0.05, d - sum(p[1] for p in parts[:-1]))
                part = {"id": f"s{i}.p{k}", "src": rel(f), "in": 0, "duration": round(plen, 6), "audio": sound,
                        "meta": {"shot": i, "item": shots[i]["item"], "part": k}}
                if L < plen - 0.05:
                    part["speed"] = round(L / plen, 4)
                    notes["retimed"].append({"shot": i, "part": k, "speed": part["speed"]})
                filters = [x for x in ((fade_in if k == 1 else None),
                                       (fade_out(round(plen * fps)) if fade_out and k == len(parts) else None)) if x]
                if filters:
                    part["vf"] = ",".join(filters)
                if k == 1 and i in xfade:
                    part["transition"] = xfade[i]
                main.append(part)
            continue
        if "src" in c and "in" in c and not clip_of[i].get("_card"):
            # the piece's frames from head_f before its own first frame, at its rate; slower when a beat move asks for more
            # than the piece has (within the few per cent keep_on_beat allows)
            r = rate[i]
            start = c["in"] - head_f[i] / float(fps) * r
            planned_end = c["in"] + c.pop("window", secs[i] * r)
            have = planned_end + clip_of[i]["_room"][1] - start
            if d * r > have + 1e-6:
                r = have / d
            c["in"] = round(max(0.0, start), 4)
            if abs(r - 1) > 0.02 or rate[i] != 1.0:
                c["speed"] = round(min(8.0, max(0.1, r)), 4)
                if r < 0.98:
                    notes["retimed"].append({"shot": i, "speed": c["speed"]})
        if "image" in c:
            keys = still_keys(d, size, clip_of[i]["_motion"])
            if keys:
                c["keys"] = keys
        filters = [x for x in (fade_in, fade_out(n_f) if fade_out else None) if x]
        if filters:
            c["vf"] = ",".join(filters)
        if i in xfade:
            c["transition"] = xfade[i]
        meta = {**base["meta"], **c.pop("meta", {})}
        main.append({**base, **c, "meta": meta})

    edit: dict = {"version": 2, "output": {"width": size[0], "height": size[1], "fps": str(fps)},
                  "tracks": [{"id": "main", "clips": main}], "audio": [],
                  # pieces from different generations meet at every cut: a short fade keeps their sound from clicking
                  "mix": {"lufs": -14, "true_peak": -1.0, "cut_fade": 0.03}}
    if args.audio == "source" and src.get("has_audio"):
        edit["audio"].append({"id": "source", "src": rel(src["path"]), "role": "music"})
    if args.music:
        edit["audio"].append({"id": "music", "src": rel(Path(args.music)), "role": "music", "gain_db": args.music_db, "fade_out": 1.0})
    if not edit["audio"]:
        del edit["audio"]
    ass = edit_dir / "overlays.ass"
    ass.unlink(missing_ok=True)
    if args.subs == "auto" and plan.get("overlays"):
        ass.write_text(overlays_ass(plan["overlays"], size), encoding="utf-8")
    elif args.subs.endswith(".json"):
        ass.write_text(overlays_ass(json.loads(Path(args.subs).read_text(encoding="utf-8")), size), encoding="utf-8")
    elif args.subs not in ("auto", "none"):
        shutil.copyfile(args.subs, ass)
    if ass.exists():
        edit["subtitles"] = {"file": "overlays.ass"}
    return edit, notes


def render(root: Path, edit_path: Path, notes: dict) -> dict:
    out = root / "remake" / "out"
    out.mkdir(parents=True, exist_ok=True)
    film = out / "remake.mp4"
    cmd = ["rn", "assemble", str(edit_path), "-o", str(film)] + (["--placeholders"] if notes["placeholders"] else [])
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        sys.exit("✗ rn assemble failed:\n" + (r.stderr or r.stdout)[-2000:])
    # rn 0.7+ reads the edit itself, placeholder cards included, and compares the film with its source shot by shot
    rn07 = (rn_version() or ()) >= RN_07
    if rn07:
        qa = rn_json("qa", str(film), "--edl", str(edit_path), *(["--placeholders"] if notes["placeholders"] else []))
    else:  # an older rn qa --edl rejects an edit that still has placeholder sources: expectations given directly
        e = notes["expect"]
        qa = rn_json("qa", str(film), "--expect-frames", str(e["frames"]), "--expect-size", e["size"], "--expect-fps", e["fps"])
    (out / "qa.json").write_text(json.dumps(qa, ensure_ascii=False, indent=2), encoding="utf-8")
    plan = json.loads((root / "remake" / "plan.json").read_text(encoding="utf-8"))
    cmp_ = rn_json("compare", plan["source"]["path"], str(film), "--cuts", *(["--shots"] if rn07 else []),
                   "--video", str(out / "compare.mp4"), "-o", str(out / "compare.jpg"))
    (out / "compare.json").write_text(json.dumps(cmp_, ensure_ascii=False, indent=2), encoding="utf-8")
    cuts = cmp_.get("cuts") or {}
    qc = {"remake": str(film), "compare_video": str(out / "compare.mp4"),
          "compare_sheets": [p["path"] for p in cmp_.get("pages", [])],
          "qa_status": qa.get("status"),
          "qa_findings": [c for c in qa.get("checks", []) if c.get("status") != "PASS"],
          "cuts_only_in_remake": cuts.get("only_b"),
          "cuts_missing_in_remake": [p["a"] for p in cuts.get("pairs", []) if p.get("b") is None],
          "cut_mean_abs_offset_s": cuts.get("mean_abs_offset"), **shot_findings(cmp_.get("shots")), **notes}
    (out / "qc.json").write_text(json.dumps(qc, ensure_ascii=False, indent=2), encoding="utf-8")
    return qc


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("dir", help="analyze.py output folder (has remake/plan.json)")
    ap.add_argument("results", help="results.json: plan item id -> file(s)")
    ap.add_argument("--audio", choices=("units", "source", "none"), default="units",
                    help="units: each generated or built piece keeps its own sound (default); source: the source's track; none")
    ap.add_argument("--music", help="a music bed under the whole film")
    ap.add_argument("--music-db", type=float, default=-8.0, help="music bed gain, dB")
    ap.add_argument("--beat-sync", choices=("auto", "on", "off"), default="auto",
                    help="with --music, move the cuts the source put on its beats onto the music's beats (auto: when the source "
                         "cuts to the beat, plan.json rhythm)")
    ap.add_argument("--beat-max", type=float, default=0.2, help="the furthest a cut moves to land on a beat, seconds")
    ap.add_argument("--subs", default="auto", help="auto: the overlay lines from review.json; none; a .json list of lines; or an .ass file")
    ap.add_argument("--snap", type=float, default=0.4, help="snap planned cuts inside a unit to the model's cuts within this many seconds")
    ap.add_argument("--width", type=int, help="output width, only when the user asks for a resolution (default: the generated "
                    "footage's own size in the source's shape, never larger than the source; never upscale unprompted)")
    ap.add_argument("--render", action="store_true", help="also run rn assemble, rn qa and rn compare, and write remake/out/qc.json")
    args = ap.parse_args()
    root = Path(args.dir)
    if not shutil.which("rn"):
        sys.exit("✗ rn not found: install renoise-kit (the Renoise sandbox has it)")
    edit, notes = build(root, Path(args.results), args)
    edit_path = root / "remake" / "edit.json"
    edit_path.write_text(json.dumps(edit, ensure_ascii=False, indent=1), encoding="utf-8")
    r = subprocess.run(["rn", "assemble", str(edit_path), "--dry-run"] + (["--placeholders"] if notes["placeholders"] else []),
                       capture_output=True, text=True)
    if r.returncode != 0:
        sys.exit(f"✗ rn rejected {edit_path}:\n" + (r.stderr or r.stdout)[-1500:])
    print(json.dumps({"edit": str(edit_path), **notes}, ensure_ascii=False, indent=2))
    if args.render:
        print(json.dumps(render(root, edit_path, notes), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
