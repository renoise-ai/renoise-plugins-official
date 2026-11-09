#!/usr/bin/env python3
"""Measure a reference video for a remake: where the shots are and how each one should be made again.

    python analyze.py <video> -o <folder>

Writes into the folder:
  analysis.json   the source (size, fps, sound) and every shot: start, end, how it begins (cut, dissolve, fade,
                  flash, wipe), rn's measurements, and a route:
                    generate  footage, AI video, 3D, animation: made again by a video model
                    code      rendered graphics, cards, UI, screen recordings: built in code (or supplied), never
                              redrawn by a video model
                    still     a picture that holds: one image, moved locally when the source moves it
  storyboard.jpg  every shot's middle frame, numbered, with its time and route
  shots/          per shot: first and last frame, and a first / middle / last contact sheet
  review.json     what to fill after looking at the frames (route corrections, descriptions, prompts), read by plan_units.py
  overlays_draft.json  with --text (tesseract): the text on screen, read by rn text, as lines and as the places text keeps
                  appearing (a caption band: where, how big, what colours, when). OCR misreads styled type, so take the
                  style from it and the words from the frames

rn shots (renoise-kit 0.7 or newer) finds and measures the shots; this script routes them and writes their frames. The
route is a first guess from a few signals (see route()): check every route on the contact sheets.
"""
from __future__ import annotations

import argparse
import json
import math
import os
import subprocess
import sys
import tempfile
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

ANALYSIS_W = 480  # analysis.json keeps pans in pixels of a frame this wide (build_edit.py and check_units.py scale them)
RN_SHOTS = (0, 7, 0)


def usable_cpus() -> int:
    """CPUs this process may use: its affinity mask, capped by a cgroup v2 CPU limit (a container usually sees the
    host's count; a Modal sandbox's limit is its burst ceiling)."""
    try:
        n = len(os.sched_getaffinity(0))
    except AttributeError:
        n = os.cpu_count() or 1
    try:
        quota, period = Path("/sys/fs/cgroup/cpu.max").read_text().split()[:2]
        if quota != "max":
            n = min(n, max(1, int(int(quota) / int(period))))
    except (OSError, ValueError):
        pass
    return max(1, n)


# ---------------------------------------------------------------- media
ASPECTS = {"9:16": 9 / 16, "3:4": 3 / 4, "4:5": 4 / 5, "1:1": 1.0, "4:3": 4 / 3, "16:9": 16 / 9, "21:9": 21 / 9}


def _rate(text) -> float:
    try:
        num, _, den = str(text or "0").partition("/")
        return float(num) / float(den or 1)
    except (ValueError, ZeroDivisionError):
        return 0.0


def probe(path: Path) -> dict:
    """Size as shown (rotation applied), frame rate, length, the nearest named aspect ratio and whether there is sound."""
    info = json.loads(subprocess.run(["ffprobe", "-v", "error", "-of", "json", "-show_format", "-show_streams", str(path)],
                                     check=True, capture_output=True, text=True).stdout)
    streams = info.get("streams") or []
    video = [x for x in streams if x.get("codec_type") == "video" and not (x.get("disposition") or {}).get("attached_pic")]
    if not video:
        sys.exit(f"✗ no video stream in {path}")
    v = video[0]
    turn = next((abs(int(float(d["rotation"]))) % 360 for d in v.get("side_data_list") or [] if "rotation" in d), 0)
    w, h = int(v.get("width") or 0), int(v.get("height") or 0)
    shown = [h, w] if turn in (90, 270) else [w, h]
    shape = shown[0] / shown[1] if shown[1] else 0.0
    named = min(ASPECTS, key=lambda k: abs(shape - ASPECTS[k]) / ASPECTS[k]) if shape else None
    ratio = named if named and abs(shape - ASPECTS[named]) / ASPECTS[named] < 0.04 else f"{shown[0]}:{shown[1]}"
    length = v.get("duration") or (info.get("format") or {}).get("duration") or 0
    return {"path": str(path.resolve()), "width": w, "height": h, "display": shown, "rotation": turn,
            "fps": round(_rate(v.get("avg_frame_rate")) or _rate(v.get("r_frame_rate")) or 30.0, 3),
            "duration": round(float(length), 3), "aspect_ratio": ratio,
            "has_audio": any(x.get("codec_type") == "audio" for x in streams)}


def grab(path: Path, t: float, out: Path, width: int = 540) -> None:
    out.parent.mkdir(parents=True, exist_ok=True)
    r = subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", f"{max(t, 0):.3f}", "-i", str(path), "-frames:v", "1",
                        "-vf", f"scale={width}:-2", "-q:v", "3", str(out)], capture_output=True)
    if r.returncode != 0 or not out.exists():  # past the last frame: take the last one
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-sseof", "-1", "-i", str(path), "-update", "1", "-vf", f"scale={width}:-2",
                        "-q:v", "3", str(out)], check=True, capture_output=True)


# ---------------------------------------------------------------- pictures
def contact(paths: list[Path], out: Path, h: int = 320) -> None:
    from PIL import Image

    ims = [Image.open(p).convert("RGB") for p in paths if p.exists()]
    ims = [im.resize((max(1, round(im.width * h / im.height)), h)) for im in ims]
    sheet = Image.new("RGB", (sum(im.width for im in ims) + 4 * (len(ims) + 1), h + 8), (20, 20, 20))
    x = 4
    for im in ims:
        sheet.paste(im, (x, 4))
        x += im.width + 4
    sheet.save(out, quality=85)


def storyboard(root: Path, shots: list[dict], out: Path) -> None:
    from PIL import Image, ImageDraw

    cells = [(s, Image.open(root / s["assets"]["middle"]).convert("RGB")) for s in shots]
    h = 300
    cells = [(s, im.resize((max(1, round(im.width * h / im.height)), h))) for s, im in cells]
    cw = max(im.width for _, im in cells)
    cols = min(8, len(cells))
    rows = math.ceil(len(cells) / cols)
    sheet = Image.new("RGB", (cols * (cw + 6) + 6, rows * (h + 40) + 6), (20, 20, 20))
    d = ImageDraw.Draw(sheet)
    for k, (s, im) in enumerate(cells):
        x, y = 6 + (k % cols) * (cw + 6), 6 + (k // cols) * (h + 40)
        sheet.paste(im, (x, y))
        d.text((x, y + h + 4), f"#{s['index']} {s['start']:.1f}-{s['end']:.1f}s", fill=(240, 240, 240))
        d.text((x, y + h + 18), f"{s['route']} · {s['looks_like']}" + (" ?" if s["check"] else ""), fill=(170, 200, 255))
    sheet.save(out, quality=85)


# ---------------------------------------------------------------- route
def route(shot: dict, src: dict) -> tuple[str, str, float, list[str], str]:
    """A first guess at how to make the shot again, from rn's measurements -> (route, what it looks like, confidence,
    evidence, doubt: why to check it on the frames, or "").

    Drawn pictures (cards, titles, UI, flat motion graphics) are nearly free of fine texture, mostly flat, use few
    colours and leave most pixels untouched from frame to frame. Fine texture is the surest of these (a title measures
    about 0.005, filmed or generated footage 0.12 and up, even dark or smoky shots that are flat and few-coloured), so code
    needs it plus two more; the others alone leave the shot in doubt.
    A picture that holds is a still. Everything else is footage to generate, including a frame that moves as one plane:
    that is as often a camera move in generated footage as a pan over a photo, so the agent decides from the frames."""
    tex, held, mo, px = shot["texture"], shot["still"], shot["motion"], shot["pixels"]
    face = float((shot.get("faces") or {}).get("frames_with_face") or 0.0)
    signs = {"almost no fine texture": tex["fine_texture"] < 0.05, "mostly flat areas": tex["flat_blocks"] > 0.6,
             "few colours": tex["palette95"] <= 24, "most pixels never change": px["unchanged"] > 0.9}
    drawn = sum(signs.values()) - (1 if face >= 0.5 else 0)
    ev = [name for name, hit in signs.items() if hit]
    if face >= 0.5:
        ev.append(f"a face in {face:.0%} of the sampled frames")
    holds = held["identical_pairs"] >= 0.7 and held["first_last_diff"] < 5
    if holds:
        ev.append(f"{held['identical_pairs']:.0%} of frame pairs identical: the picture holds")
    if signs["almost no fine texture"] and drawn >= 3:
        what = "card" if holds else "screen / UI" if tex["saturation"] < 0.1 else "motion graphics"
        return "code", what, 0.9 if drawn == 4 else 0.7, ev, "" if drawn == 4 else "drawn look: code, or a flat render to generate?"
    if holds:
        return "still", "held picture", 0.85, ev, "" if drawn < 2 else "a held picture: a photo or AI still, or a card to build in code?"
    zoom, pan = float(mo["zoom_per_s"]), float(mo["pan_px_per_s"]) * pan_scale(src)
    if mo.get("rigid_fit", 0) >= 0.9 and float(mo.get("local_motion", 0)) <= 0.02 and (abs(zoom) > 0.004 or pan > 1.5):
        ev.append(f"the whole frame moves as one plane (zoom {zoom * 100:+.1f}%/s, pan {pan:.0f} px/s)")
        return "generate", "camera move", 0.55, ev, "a camera move in footage (generate), or a still image panned or zoomed (still)?"
    if drawn >= 2:
        return "generate", "rendered scene", 0.55, ev, "clean, flat look: a 3D or flat render (generate), or code graphics?"
    return "generate", "footage", 0.8, ev, ""


def pan_scale(src: dict) -> float:
    """rn measures pans in source pixels; analysis.json keeps them in pixels of an ANALYSIS_W-wide frame."""
    width = src["display"][0]
    return (min(ANALYSIS_W, width) // 2 * 2) / float(width) if width else 1.0


def camera(shot: dict, src: dict) -> str:
    mo = shot["motion"]
    moving = abs(float(mo["zoom_per_s"])) > 0.004 or float(mo["pan_px_per_s"]) * pan_scale(src) > 1.5
    if not moving:
        return "static" if float(mo.get("local_motion", 0)) <= 0.05 else "static_with_subject_motion"
    return "planar_zoom_pan" if float(mo.get("rigid_fit", 0)) > 0.5 else "moving"


def finish_shot(k: int, s: dict, m: dict, video: Path, src: dict, fps: float, root: Path, n: int) -> tuple[dict, str]:
    """Route an rn-measured shot and write its first / middle / last frames and contact sheet."""
    start, end = s["start_frame"] / fps, s["end_frame"] / fps
    if k == n and src["duration"]:
        end = max(end, src["duration"])
    rec = {"index": k, "id": f"shot_{k:03d}", "start": round(start, 3), "end": round(end, 3), "duration": round(end - start, 3),
           "transition_in": s["transition_in"]}
    r, what, conf, ev, doubt = route(m, src)
    mo = m["motion"]
    rec.update({"route": r, "looks_like": what, "confidence": round(conf, 3), "check": doubt, "evidence": ev,
                "motion": {"zoom_per_s": round(float(mo["zoom_per_s"]), 4), "pan_px_per_s": round(float(mo["pan_px_per_s"]) * pan_scale(src), 4),
                           "pan_dir_deg": round(float(mo["pan_dir_deg"]), 4)},
                "measured": {"kenburns_score": round(float(mo.get("rigid_fit", 0)), 4), "camera": camera(m, src),
                             **{key: m[key] for key in ("texture", "still", "cadence", "pixels", "faces") if m.get(key) is not None}}})
    for key, value in (("transition", s.get("transition")), ("beat", s.get("beat")), ("speed", m.get("speed")),
                       ("open_frame", s.get("open_frame"))):
        if value:
            rec[key] = value
    a = rec["assets"] = {x: f"shots/{rec['id']}_{x}.jpg" for x in ("first", "middle", "last")}
    grab(video, start + min(0.05, rec["duration"] / 4), root / a["first"])
    grab(video, (start + end) / 2, root / a["middle"])
    grab(video, max(start, end - min(0.08, rec["duration"] / 4)), root / a["last"])
    a["sheet"] = f"shots/{rec['id']}.jpg"
    contact([root / a[x] for x in ("first", "middle", "last")], root / a["sheet"])
    line = f"#{k} {start:.2f}-{end:.2f}s {s['transition_in'] or 'start'} → {r} ({what}, {conf:.0%})" + (f"  ? {doubt}" if doubt else "")
    return rec, line


# ---------------------------------------------------------------- rn shots
RN_SHOTS = (0, 7, 0)


def rn_version() -> tuple[int, ...] | None:
    try:
        out = subprocess.run(["rn", "--version"], capture_output=True, text=True, timeout=60).stdout.split()
        return tuple(int(part) for part in out[-1].split(".")[:3]) if out else None
    except (OSError, ValueError, subprocess.TimeoutExpired):
        return None


def rn_has(part: str) -> bool:
    """Whether `rn doctor` (rn 0.7+, about 0.1 s) finds one of rn's optional parts here, e.g. librosa for --beats."""
    with tempfile.TemporaryDirectory() as tmp:
        out = Path(tmp) / "doctor.json"
        subprocess.run(["rn", "doctor", "--json", str(out)], capture_output=True, text=True)
        if not out.exists():
            return False
        return any(c["name"] == part and c["status"] == "ok" for c in json.loads(out.read_text(encoding="utf-8"))["checks"])


def rn_shots(video: Path, min_shot: float, jobs: int | None, beats: bool, open_dir: Path | None = None) -> dict:
    """rn shots: boundaries and per-shot measurements, with faces when its face model is at hand and each cut against the
    beats of the source's own sound when it has any. --beats is asked only when rn has its beat tracker (it would fail
    after the whole scan); --faces fails at once without its model, and is then dropped. open_dir: each shot's first frame
    clear of its transitions (rn shots --keyframes --which first), the frame its keyframe opens on; an rn without
    --keyframes runs without it."""
    with tempfile.TemporaryDirectory() as tmp:
        out = Path(tmp) / "shots.json"
        cmd = ["rn", "shots", str(video), "--json", str(out), "--min-shot", str(min_shot)] + (["--jobs", str(jobs)] if jobs else [])
        if open_dir is not None:
            probe_help = subprocess.run(["rn", "shots", "--help"], capture_output=True, text=True).stdout
            if "--keyframes" in probe_help:
                cmd += ["--keyframes", str(open_dir), "--which", "first"]
        extras = ["--faces"] + (["--beats"] if beats and rn_has("librosa") else [])
        tries = [extras, [x for x in extras if x != "--faces"]] + ([[]] if len(extras) > 1 else [])
        for i, extra in enumerate(tries):
            r = subprocess.run(cmd + extra, capture_output=True, text=True)
            if r.returncode == 0:
                break
            if i + 1 < len(tries):  # no face model or no beat tracker here (outside the sandbox, offline)
                print(f"rn shots {' '.join(extra)}: " + (r.stderr or r.stdout).strip()[-300:] + f"; trying {' '.join(tries[i + 1]) or 'without them'}",
                      file=sys.stderr)
        if r.returncode != 0:
            sys.exit("✗ rn shots failed:\n" + (r.stderr or r.stdout)[-2000:])
        return json.loads(out.read_text(encoding="utf-8"))


def rn_overlays(video: Path) -> list[dict]:
    """The source's text on screen from rn text (rn 0.7+, tesseract): each line read, with its time, place, height and
    colours, in the cue format build_edit.py burns (review.json overlays). A draft: OCR misreads styled type (a caption on
    a busy picture comes back in pieces), and text that belongs to the scene (a label on a product) is not an overlay."""
    if not shutil.which("tesseract"):
        print("rn text needs tesseract: no overlay draft", file=sys.stderr)
        return []
    with tempfile.TemporaryDirectory() as tmp:
        out = Path(tmp) / "text.json"
        r = subprocess.run(["rn", "text", str(video), "--json", str(out)], capture_output=True, text=True)
        if r.returncode != 0 or not out.exists():
            print("rn text: " + (r.stderr or r.stdout).strip()[-300:] + "; no overlay draft", file=sys.stderr)
            return []
        found = json.loads(out.read_text(encoding="utf-8"))
    w, h = probe(video)["display"]
    cues = []
    for span in found.get("spans") or []:
        x, y, bw, bh = span["box"]
        style = span.get("style") or {}
        share = style.get("height_share") or bh / h
        if span.get("start") is None or share > 0.25:  # a box that tall is picture, not type
            continue
        # OCR noise: stray letters read once off texture. Keep 3+ letters or digits, or a short word read clearly twice
        letters = sum(ch.isalnum() for ch in span["text"])
        reads, conf = span.get("reads", 1), span.get("conf", 100.0)
        if (letters < 3 and not (reads >= 2 and conf >= 80)) or (reads == 1 and conf < 70):
            continue
        cue = {"t0": span["start"], "t1": span["end"], "text": span["text"], "x": round((x + bw / 2) / w, 4), "y": round((y + bh / 2) / h, 4),
               "size": round(share, 4), "_from": f"rn text ({reads} read(s), confidence {conf:.0f})"}
        if style.get("color"):
            cue["color"] = style["color"]
        if style.get("outline"):
            cue["outline"] = style["outline"]
        if style.get("background"):
            cue["_background"] = style["background"]  # behind the letters: a plate (then set "box") or the picture itself
        cues.append(cue)
    return cues


def _rgb(hexrgb: str | None) -> tuple[int, int, int] | None:
    return tuple(int(hexrgb[k:k + 2], 16) for k in (1, 3, 5)) if hexrgb else None


def text_places(cues: list[dict]) -> list[dict]:
    """Where text keeps appearing: lines read at about the same height (within 4% of the frame), the same size (within a
    third) and colour group into one place, such as a caption band or a corner tag, with when it shows and a few of its
    reads. The style of an overlay to rebuild comes from here even when the reads are garbled."""
    places: list[dict] = []
    for c in sorted(cues, key=lambda c: c["t0"]):
        rgb = _rgb(c.get("color"))
        for p in places:
            near_colour = rgb is None or p["_rgb"] is None or sum((a - b) ** 2 for a, b in zip(rgb, p["_rgb"])) <= 60 ** 2
            if abs(c["y"] - p["y"]) <= 0.04 and abs(c["size"] - p["size"]) <= p["size"] / 3 and near_colour:
                p["_lines"].append(c)
                break
        else:
            places.append({"y": c["y"], "size": c["size"], "_rgb": rgb, "_lines": [c]})
    out = []
    for p in places:
        lines = p["_lines"]
        if len(lines) < 2 and sum(ch.isalnum() for ch in lines[0]["text"]) < 4:
            continue
        mid = lambda key: sorted(x[key] for x in lines)[len(lines) // 2]  # noqa: E731
        common = lambda key: max({x.get(key) for x in lines}, key=lambda v: sum(x.get(key) == v for x in lines))  # noqa: E731
        reads = sorted({x["text"] for x in lines}, key=len, reverse=True)
        out.append({"x": mid("x"), "y": mid("y"), "size": mid("size"), "color": common("color"), "outline": common("outline"),
                    "background": common("_background"), "from": lines[0]["t0"], "to": max(x["t1"] for x in lines),
                    "shown_s": round(sum(x["t1"] - x["t0"] for x in lines), 2), "lines": len(lines), "reads": reads[:6]})
    return sorted(out, key=lambda p: -p["shown_s"])


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("video")
    ap.add_argument("-o", "--out", required=True, help="output folder")
    ap.add_argument("--min-shot", type=float, default=0.35, help="shortest shot in seconds (shorter ones merge into the previous)")
    ap.add_argument("--jobs", type=int, help="shots measured in parallel (default: every CPU this sandbox may use)")
    ap.add_argument("--text", action="store_true",
                    help="also read the text on screen (rn text, tesseract) into overlays_draft.json: for sources whose captions "
                         "or titles are rebuilt as overlays (about 2 s per second of video)")
    args = ap.parse_args()
    video, root = Path(args.video), Path(args.out)
    (root / "shots").mkdir(parents=True, exist_ok=True)
    src = probe(video)
    fps = src["fps"] if src["fps"] > 0 else 30.0
    version = rn_version()
    if not version or version < RN_SHOTS:
        sys.exit(f"✗ rn {'.'.join(map(str, version or ())) or 'not found'}: analyze.py needs renoise-kit 0.7 or newer (rn shots)")
    shots = []
    measured = rn_shots(video, args.min_shot, args.jobs, beats=bool(src.get("has_audio")), open_dir=root / "shots" / "open")
    raw = [{"start_frame": x["start_frame"], "end_frame": x["end_frame"], "transition_in": x["transition_in"],
            **{key: x[key] for key in ("transition", "beat") if x.get(key)},
            **({"open_frame": {"time": x["keyframe"]["time"], "index": x["keyframe"]["index"],
                               "path": os.path.relpath(x["keyframe"]["path"], root)}} if x.get("keyframe") else {})}
           for x in measured["shots"]]
    jobs = [(k, x, m, video, src, fps, root, len(raw)) for k, (x, m) in enumerate(zip(raw, measured["shots"]), 1)]
    print(f"{len(raw)} shots, measured by rn shots ({measured['workers']} worker(s)); writing their frames", flush=True)
    with ThreadPoolExecutor(max_workers=max(1, min(args.jobs or usable_cpus(), len(jobs)))) as pool:
        for rec, line in pool.map(lambda job: finish_shot(*job), jobs):
            shots.append(rec)
            print(line, flush=True)
    engine = f"rn shots {'.'.join(map(str, version))}"
    storyboard(root, shots, root / "storyboard.jpg")
    analysis = {"tool": "video-remake analyze.py", "measured_by": engine, "source": src, "shots": shots,
                "storyboard": "storyboard.jpg", **({"beats": measured["beats"]} if measured.get("beats") else {})}
    (root / "analysis.json").write_text(json.dumps(analysis, ensure_ascii=False, indent=2), encoding="utf-8")
    review = root / "review.json"
    if not review.exists():
        review.write_text(json.dumps({
            "_how": "Look at storyboard.jpg and each shots/<id>.jpg. Per shot (by number) set only what you change or add: "
                    "route (generate | code | still | keep), description (what is on screen), prompt (the English video prompt "
                    "for this shot alone: action, camera, end state), image_prompt (stills). Top level: cast and overlays.",
            "shots": {str(s["index"]): {} for s in shots},
            "cast": {"characters": [], "props": [], "style": ""},
            "overlays": []}, ensure_ascii=False, indent=2), encoding="utf-8")
    if args.text:
        lines = rn_overlays(video)
        places = text_places(lines)
        (root / "overlays_draft.json").write_text(json.dumps({
            "_how": "OCR drafts of the source's text. places: where text keeps appearing and its style (x, y: centre, "
                    "0-1 of the frame; size: text height, 0-1 of the frame height); lines: each read. For review.json "
                    "overlays, take the style from here and the words from the frames.",
            "places": places, "lines": lines}, ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"→ {root / 'overlays_draft.json'}  ({len(lines)} line(s) read, {len(places)} place(s) text keeps appearing)")
    print(f"→ {root / 'analysis.json'}  ({len(shots)} shots; {sum(bool(s['check']) for s in shots)} marked ? to check)")


if __name__ == "__main__":
    main()
