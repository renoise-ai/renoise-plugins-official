#!/usr/bin/env python3
"""Plan a remake from analyze.py's output and the agent's review, for the model the user will generate with.

    python plan_units.py <analysis folder> --max 15 [--min 4] [--multi-shot] [--cut]

Reads analysis.json and review.json (route corrections, descriptions, prompts, cast, overlays). Every shot keeps one
route:
  generate  made again by a video model. Consecutive same-scene shots joined by hard cuts share one call (a
            generation unit, G1, G2...) when the model can cut inside one generation; a shot longer than one call is
            split into parts that continue each other.
  code      built in code, or supplied by the user (C1...): never redrawn by a video model.
  still     one image (the user's, or generated) moved with the measured zoom / pan (P1...).
  keep      shots the user owns and keeps as they are (K1...): cut from the source.
Code, still and kept shots sitting between generated shots do not break a unit: the generated shots are made back
to back and the inserts go back in the edit.

Every generated shot (each part of a split shot) and every still gets a keyframe: the source frame it opens on, which
an image model turns into the remake's opening frame with the slotted elements swapped in (skip a shot with
"keyframe": false in review.json when nothing in it changes).

Writes <folder>/remake/plan.json and plan.md; with --cut also each unit's source clip (remake/units/G1_ref.mp4: the
unit's source ranges joined, inserts removed, silent unless --ref-audio), which is the unit's reference video, and
the keyframes' source frames at full resolution (remake/keyframes/src_<shot>.jpg).

The model's limits (longest and shortest call, whether it cuts inside one call) come from the command line, that is from
live model data.
"""
from __future__ import annotations

import argparse
import json
import math
import subprocess
import sys
from pathlib import Path

ROUTES = ("generate", "code", "still", "keep")
JOIN_TRANSITIONS = ("cut", "flash")  # a dissolve, wipe or fade between two shots is made in the edit, not by the model
# Made in the edit by overlapping the two pieces (xfade): the piece before needs that many seconds more at its end. A fade
# through black or white needs no overlap (each side fades on its own frames).
OVERLAPPED = ("dissolve", "wipe")
UNMEASURED_OVERLAP_S = 0.5  # a dissolve or wipe whose length was not measured (analyzed without rn 0.7)
QUARTERS = ("first", "second", "third", "last")


def overlap_s(rec: dict | None) -> float:
    """Seconds the edit overlaps a shot with the piece before it to make its dissolve or wipe again (0: a cut or fade)."""
    if not rec or rec.get("transition_in") not in OVERLAPPED:
        return 0.0
    return float((rec.get("transition") or {}).get("seconds") or UNMEASURED_OVERLAP_S)


def transition_words(rec: dict) -> str:
    """How a shot begins, with its measured length: "dissolve 15 f (0.63 s)", "wipe, edge moving left, 13 f (0.54 s)",
    "fade through black: 3 f out, 4 f held, 8 f in"."""
    kind, t = rec.get("transition_in"), rec.get("transition") or {}
    if not t.get("frames"):
        return f"{kind} (length not measured)"
    if kind == "fade" and t.get("through"):
        return (f"fade through {t['through']}: {t.get('out_frames', 0)} f out, {t.get('hold_frames', 0)} f held, "
                f"{t.get('in_frames', 0)} f in ({t['seconds']:.2f} s)")
    edge = f", edge moving {t['edge']}," if t.get("edge") else ""  # rn names the way the wipe's edge runs, as xfade does
    return f"{kind}{edge} {t['frames']} f ({t['seconds']:.2f} s)"


def pace_words(speed: dict | None) -> str:
    """rn shots' speed (how much the picture changes in each quarter of the shot, the longest hold) in words for a prompt:
    a shot that settles, speeds up, or freezes. Empty when its pace is even."""
    if not speed:
        return ""
    q, words = speed.get("change_per_quarter") or [], []
    ramp, hold = float(speed.get("ramp") or 1.0), float(speed.get("longest_hold_s") or 0.0)
    if len(q) == 4 and ramp >= 3 and max(q) > 0:
        fast, slow = q.index(max(q)), q.index(min(q))
        if slow > fast:
            words.append(f"slows down: most motion in the {QUARTERS[fast]} quarter, {ramp:.0f}x less by the {QUARTERS[slow]}")
        else:
            words.append(f"speeds up: {ramp:.0f}x more motion in the {QUARTERS[fast]} quarter than in the {QUARTERS[slow]}")
    if hold >= 0.3:
        words.append(f"holds still for {hold:.1f} s")
    return "; ".join(words)


def rhythm(beats: dict | None, shots: list[dict]) -> dict | None:
    """Does the source cut to the beat of its own sound (rn shots --beats)? Clearly more cuts within a frame or two of a
    beat than chance gives. on_beat: the shots whose first frame is within 2 frames of a beat, which build_edit.py
    --music keeps on the new music's beats."""
    if not beats or not beats.get("boundaries"):
        return None
    w1, w2 = beats["within_1_frame"], beats["within_2_frames"]
    c1, c2 = beats["chance_within_1_frame"], beats["chance_within_2_frames"]
    return {"cut_to_beat": beats["boundaries"] >= 4 and (w1 >= 1.5 * c1 or w2 >= c2 + 0.1), "bpm": beats.get("bpm"),
            "clear_pulse": beats.get("clear"), "within_1_frame": w1, "within_2_frames": w2, "chance_within_1_frame": c1,
            "chance_within_2_frames": c2,
            "on_beat": [r["index"] for r in shots if r.get("beat") and abs(r["beat"]["offset_frames"]) <= 2]}


# ---------------------------------------------------------------- scene similarity
def histograms(root: Path, rec: dict) -> list:
    import cv2

    hs = []
    for k in ("first", "last"):
        p = (rec.get("assets") or {}).get(k)
        im = cv2.imread(str(root / p)) if p else None
        if im is None:
            continue
        h = cv2.calcHist([cv2.cvtColor(im, cv2.COLOR_BGR2HSV)], [0, 1, 2], None, [18, 4, 4], [0, 180, 0, 256, 0, 256])
        cv2.normalize(h, h)
        hs.append(h)
    return hs


def scene_distance(a: list, b: list) -> float:
    """Smallest colour-distribution distance between any key frames of two shots (0 = same, 1 = unrelated)."""
    import cv2

    d = [cv2.compareHist(x, y, cv2.HISTCMP_BHATTACHARYYA) for x in a for y in b]
    return float(min(d)) if d else 1.0


# ---------------------------------------------------------------- units
def runs(shots: list[dict], same_scene, inserts: set[int]) -> list[list[dict]]:
    """Generated shots that may share one call: consecutive, in the same scene, joined by a hard cut. Code, still and
    kept shots sitting between them (`inserts`) are stepped over: the generated shots are made back to back and the
    inserts go back in the edit."""
    groups: list[list[dict]] = []
    group: list[dict] | None = None
    stepped = False
    for shot in shots:
        if shot["route"] == "generate":
            if group and same_scene(group[-1], shot) and (stepped or shot.get("transition_in") in JOIN_TRANSITIONS):
                group.append(shot)
            else:
                group = [shot]
                groups.append(group)
            stepped = False
        elif shot["index"] in inserts and group:
            stepped = True
        else:
            group, stepped = None, False
    return groups


def split_run(run: list[dict], multi_shot: bool, cap: float, prefer: float, unit_min: float) -> list[list[dict]]:
    """Packs a run into calls, in order. A unit takes the next shot while it stays within the longest call (`cap`), and
    past the preferred stretch of hard cuts (`prefer`) only while it is still shorter than the shortest useful call
    (`unit_min`). A last unit that comes out short joins the one before when the two still fit one call. A shot longer
    than one call stays alone; make_unit splits it into parts."""
    if not multi_shot:
        return [[shot] for shot in run]
    length = lambda unit: sum(shot["duration"] for shot in unit)  # noqa: E731
    units: list[list[dict]] = []
    for shot in run:
        if units:
            grown = length(units[-1]) + shot["duration"]
            if grown <= cap and (grown <= prefer or length(units[-1]) < unit_min):
                units[-1].append(shot)
                continue
        units.append([shot])
    if len(units) > 1 and length(units[-1]) < unit_min and length(units[-2]) + length(units[-1]) <= cap:
        units[-2].extend(units.pop())
    return units


def merge_ranges(seg: list[dict]) -> list[list[float]]:
    ranges: list[list[float]] = []
    for r in seg:
        if ranges and abs(ranges[-1][1] - r["start"]) < 1e-3:
            ranges[-1][1] = r["end"]
        else:
            ranges.append([r["start"], r["end"]])
    return [[round(a, 3), round(z, 3)] for a, z in ranges]


def make_unit(seg: list[dict], args, prev: dict | None, same_prev: bool, after: dict | None) -> dict:
    """`after`: the shot that follows the unit's last shot. When it begins with a dissolve or wipe, the edit overlaps the
    two, so the unit is generated that much longer (its last shot runs on under the incoming picture)."""
    dur = round(sum(r["duration"] for r in seg), 3)
    tail = overlap_s(after)
    ranges = merge_ranges(seg)
    offsets, acc = [], 0.0
    for r in seg:
        offsets.append({"shot": r["index"], "t0": round(acc, 3), "t1": round(acc + r["duration"], 3)})
        acc += r["duration"]
    unit = {"kind": "generate", "shots": [r["index"] for r in seg], "start": seg[0]["start"], "end": seg[-1]["end"],
            "duration": dur, "ranges": ranges, "offsets": offsets, "first_frame": seg[0]["assets"].get("first"),
            "prompt_lines": [], "missing_prompts": []}
    for i, (r, o) in enumerate(zip(seg, offsets), 1):
        text = r.get("prompt") or r.get("description")
        if not text:
            unit["missing_prompts"].append(r["index"])
            text = "(write from the frames)"
        unit["prompt_lines"].append(f"Shot {i} ({o['t0']:.1f}-{o['t1']:.1f} s): {text}" if len(seg) > 1 else text)
    notes = []
    if len(seg) == 1 and dur > args.max:
        n = math.ceil(dur / args.max - 1e-6)
        step = dur / n
        a0 = seg[0]["start"]
        unit["parts"] = [{"range": [round(a0 + k * step, 3), round(a0 + (k + 1) * step, 3)], "duration": round(step, 3),
                          "request_s": max(math.ceil(step + (tail if k == n - 1 else 0.0) - 1e-6), math.ceil(args.min))}
                         for k in range(n)]
        unit["mode"], unit["calls"] = "split", n
        notes.append(f"one {dur:.1f} s shot is longer than one call ({args.max:g} s): {n} parts, each starting from the "
                     f"previous part's last frame (move a boundary to a pause in the action if the frames show one)")
    else:
        unit["mode"], unit["calls"] = ("multi_shot" if len(seg) > 1 else "single"), 1
        unit["request_s"] = math.ceil(max(dur + tail, args.min, args.unit_min if len(seg) == 1 else 0.0) - 1e-6)
        if unit["request_s"] > dur + tail + 0.5:
            notes.append(f"generate {unit['request_s']} s and keep the first {dur:.1f} s (very short generations are unstable)")
    if tail:
        unit["tail_s"] = round(tail, 3)
        notes.append(f"{tail:.2f} s more at the end: the {after['transition_in']} into #{after['index']} overlaps it, so describe "
                     f"the last shot running on a little")
    if len(ranges) > 1:
        notes.append("inserts sit between these shots in the edit: generate them back to back, the edit puts the inserts back")
    if notes:
        unit["note"] = "; ".join(notes)
    if prev and same_prev and abs(prev["end"] - seg[0]["start"]) < 1e-3 and seg[0].get("transition_in") in JOIN_TRANSITIONS:
        unit["continues"] = prev["id"]
    return unit


def cut_ref(src: str, ranges: list[list[float]], out: Path, audio: bool) -> None:
    """A unit's source clip: its ranges joined, re-encoded so every model accepts it."""
    out.parent.mkdir(parents=True, exist_ok=True)
    parts, labels = [], []
    for k, (a, z) in enumerate(ranges):
        parts.append(f"[0:v]trim=start={a}:end={z},setpts=PTS-STARTPTS[v{k}]")
        labels.append(f"[v{k}]")
        if audio:
            parts.append(f"[0:a]atrim=start={a}:end={z},asetpts=PTS-STARTPTS[a{k}]")
            labels.append(f"[a{k}]")
    graph = ";".join(parts) + ";" + "".join(labels) + f"concat=n={len(ranges)}:v=1:a={1 if audio else 0}[v]" + ("[a]" if audio else "")
    cmd = ["ffmpeg", "-v", "error", "-y", "-i", src, "-filter_complex", graph, "-map", "[v]"]
    cmd += ["-map", "[a]", "-c:a", "aac", "-b:a", "160k"] if audio else ["-an"]
    cmd += ["-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "18", "-movflags", "+faststart", str(out)]
    subprocess.run(cmd, check=True)


# ---------------------------------------------------------------- plan
def build(root: Path, args) -> dict:
    a = json.loads((root / "analysis.json").read_text(encoding="utf-8"))
    rp = root / "review.json"
    review = json.loads(rp.read_text(encoding="utf-8")) if rp.exists() else {}
    edits = review.get("shots") or {}
    keep = {int(x) for x in args.keep.split(",") if x.strip()} if args.keep else set()
    shots = []
    for rec in sorted(a["shots"], key=lambda r: r["index"]):
        e = edits.get(str(rec["index"])) or {}
        r = "keep" if rec["index"] in keep else e.get("route") or rec["route"]
        if r not in ROUTES:
            sys.exit(f"✗ review.json shot {rec['index']}: route {r!r} is not one of {', '.join(ROUTES)}")
        shots.append({
            "index": rec["index"], "start": rec["start"], "end": rec["end"], "duration": rec["duration"],
            "transition_in": rec.get("transition_in"), "route": r, "measured_route": rec["route"],
            "looks_like": rec.get("looks_like"), "confidence": rec.get("confidence"),
            "reviewed": bool(e), "assets": rec.get("assets") or {}, "motion": rec.get("motion") or {},
            "description": e.get("description", ""), "prompt": e.get("prompt", ""), "image_prompt": e.get("image_prompt", ""),
            "supply": e.get("supply", ""), "keyframe": e.get("keyframe", True) is not False,
            # rn 0.7+: the measured transition into the shot, its pace, its first frame against the beat, and its first
            # frame clear of the transition (the frame its keyframe opens on)
            **{key: rec[key] for key in ("transition", "speed", "beat", "open_frame") if rec.get(key)},
        })

    sig = {r["index"]: histograms(root, r) for r in shots}

    def same_scene(x: dict, y: dict) -> bool:
        return scene_distance(sig[x["index"]], sig[y["index"]]) <= args.scene_threshold

    inserts = {r["index"] for r in shots if r["route"] in ("code", "still", "keep")}
    by_index = {r["index"]: r for r in shots}
    units: list[dict] = []
    for run in runs(shots, same_scene, inserts):
        for seg in split_run(run, args.multi_shot, min(args.max, args.hardcut_max), args.hardcut_prefer, args.unit_min):
            prev = units[-1] if units else None
            u = make_unit(seg, args, prev, bool(prev) and same_scene(by_index[prev["shots"][-1]], seg[0]),
                          by_index.get(seg[-1]["index"] + 1))
            u["id"] = f"G{len(units) + 1}"
            units.append(u)

    items: list[dict] = list(units)
    cur: list[dict] = []
    n_code = 0
    for r in shots + [None]:
        if r is not None and r["route"] == "code":
            cur.append(r)
            continue
        if cur:
            n_code += 1
            items.append({"id": f"C{n_code}", "kind": "code", "shots": [x["index"] for x in cur], "start": cur[0]["start"],
                          "end": cur[-1]["end"], "duration": round(cur[-1]["end"] - cur[0]["start"], 3),
                          "describe": [f"#{x['index']}: {x['description'] or x['looks_like']}" for x in cur],
                          **({"tail_s": round(overlap_s(r), 3)} if overlap_s(r) else {})})
            cur = []
    for k, r in enumerate([r for r in shots if r["route"] == "still"], 1):
        items.append({"id": f"P{k}", "kind": "still", "shots": [r["index"]], "start": r["start"], "end": r["end"],
                      "duration": r["duration"], "motion": r["motion"], "first_frame": r["assets"].get("first"),
                      "image_prompt": r["image_prompt"]})
    for k, r in enumerate([r for r in shots if r["route"] == "keep"], 1):
        items.append({"id": f"K{k}", "kind": "keep", "shots": [r["index"]], "start": r["start"], "end": r["end"],
                      "duration": r["duration"]})
    items.sort(key=lambda it: it["start"])
    owner = {s: it["id"] for it in items for s in it["shots"]}
    for r in shots:
        r["item"] = owner[r["index"]]

    # keyframes: the source frame each generated shot (and each part of a split shot) and each still opens on; an image
    # model swaps the slotted elements into it, the user approves the set, then the video model starts from it
    keyframes = []
    for it in items:
        if it["kind"] == "generate":
            it["keyframes"] = []
            if it["mode"] == "split":
                starts = [(f"{it['shots'][0]}.{k}", by_index[it["shots"][0]].get("open_frame", {}).get("time", p["range"][0]) if k == 1
                           else p["range"][0]) for k, p in enumerate(it["parts"], 1)]
            else:
                # rn 0.7+: the shot's first frame clear of an incoming dissolve or fade, not a blended one
                starts = [(str(i), by_index[i].get("open_frame", {}).get("time", by_index[i]["start"])) for i in it["shots"]]
            for key, at in starts:
                if by_index[int(key.split(".")[0])]["keyframe"]:
                    keyframes.append({"key": key, "item": it["id"], "at": round(at, 3)})
                    it["keyframes"].append(key)
        elif it["kind"] == "still" and by_index[it["shots"][0]]["keyframe"]:
            keyframes.append({"key": str(it["shots"][0]), "item": it["id"], "at": round(it["start"], 3)})
    for k in keyframes:
        k["source_frame"] = f"remake/keyframes/src_{k['key'].replace('.', '_')}.jpg"

    src = a["source"]
    overlays = review.get("overlays") or []
    calls = sum(u["calls"] for u in units)
    plan = {
        "source": src,
        "model": {"max": args.max, "min": args.min, "multi_shot": args.multi_shot, "hardcut_prefer": args.hardcut_prefer,
                  "hardcut_max": args.hardcut_max, "unit_min": args.unit_min, "scene_threshold": args.scene_threshold},
        "summary": {"shots": len(shots), "units": len(units), "calls": calls,
                    "generate_s": sum(u.get("request_s") or sum(p["request_s"] for p in u.get("parts", [])) for u in units),
                    "code": n_code, "stills": sum(r["route"] == "still" for r in shots), "kept": sum(r["route"] == "keep" for r in shots),
                    "overlays": len(overlays), "keyframes": len(keyframes),
                    "single_generation": len(units) == 1 and calls == 1 and len(items) == 1 and not overlays},
        "items": items,
        "shots": shots,
        "overlays": overlays,
        "keyframes": keyframes,
        "cast": review.get("cast") or {},
        "supply": [{"shot": r["index"], "what": r["supply"]} for r in shots if r["supply"]],
        # how shots begin when not with a cut: build_edit.py makes these again between the new pieces
        "transitions": [{"shot": r["index"], "type": r["transition_in"], **(r.get("transition") or {})} for r in shots
                        if r.get("transition_in") not in (None, *JOIN_TRANSITIONS)],
        "rhythm": rhythm(a.get("beats"), shots),
        "unreviewed": [r["index"] for r in shots if not r["reviewed"]],
        "route_changed": [{"shot": r["index"], "measured": r["measured_route"], "now": r["route"]} for r in shots
                          if r["route"] != r["measured_route"]],
    }
    if args.cut:
        for u in units:
            u["ref_clip"] = f"remake/units/{u['id']}_ref.mp4"
            cut_ref(src["path"], u["ranges"], root / u["ref_clip"], args.ref_audio)
            for k, p in enumerate(u.get("parts", []), 1):
                p["ref_clip"] = f"remake/units/{u['id']}_part{k}_ref.mp4"
                cut_ref(src["path"], [p["range"]], root / p["ref_clip"], args.ref_audio)
        for k in keyframes:  # full resolution, a hair after the shot starts (clear of the cut)
            out = root / k["source_frame"]
            out.parent.mkdir(parents=True, exist_ok=True)
            open_frame = by_index[int(k["key"].split(".")[0])].get("open_frame")
            if open_frame and k["key"].split(".")[1:] in ([], ["1"]) and (root / open_frame["path"]).exists():
                # rn shots wrote this exact frame (decoded index, past any dissolve or fade into the shot)
                subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(root / open_frame["path"]), "-q:v", "2", str(out)], check=True)
                continue
            subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", f"{k['at'] + 0.04:.3f}", "-i", src["path"], "-frames:v", "1",
                            "-q:v", "2", str(out)], check=True)
    return plan


def markdown(plan: dict) -> str:
    s = plan["summary"]
    L = ["# Remake plan", "",
         f"{s['shots']} shots → {s['units']} generation unit(s), {s['calls']} call(s), about {s['generate_s']} s generated; "
         f"{s['code']} code part(s), {s['stills']} still(s), {s['kept']} kept shot(s), {s['overlays']} overlay text line(s); "
         f"{s['keyframes']} keyframe(s) to make.",
         "", "| Item | Shots | Source time | Length | How |", "|-|-|-|-|-|"]
    for it in plan["items"]:
        if it["kind"] == "generate":
            how = {"single": "one call", "multi_shot": "one call, cuts inside", "split": f"{it['calls']} parts"}[it["mode"]]
            how += f", request {it.get('request_s') or ' + '.join(str(p['request_s']) for p in it['parts'])} s"
            if it.get("continues"):
                how += f", continues {it['continues']}"
            if it["missing_prompts"]:
                how += f", prompt missing for #{', #'.join(map(str, it['missing_prompts']))}"
        else:
            how = {"code": "build in code", "still": "one image, moved locally", "keep": "kept from the source"}[it["kind"]]
        L.append(f"| {it['id']} | {', '.join(f'#{i}' for i in it['shots'])} | {it['start']:.1f}–{it['end']:.1f} s | "
                 f"{it['duration']:.1f} s | {how} |")
    if plan["supply"]:
        L += ["", "The user supplies:"] + [f"- #{m['shot']}: {m['what']}" for m in plan["supply"]]
    tails = [it for it in plan["items"] if it.get("tail_s") and it["kind"] != "generate"]  # units say it in their note
    if plan["transitions"]:
        shots = {r["index"]: r for r in plan["shots"]}
        L += ["", "Transitions (build_edit.py makes them again between the new pieces):"]
        L += [f"- #{t['shot']} begins with a {transition_words(shots[t['shot']])}" for t in plan["transitions"]]
        L += [f"- {it['id']}: make it {it['tail_s']:.2f} s longer at the end, under the next shot's {shots[it['shots'][-1] + 1]['transition_in']}"
              for it in tails]
    paced = [(r["index"], pace_words(r.get("speed"))) for r in plan["shots"] if r["route"] == "generate"]
    paced = [(i, w) for i, w in paced if w]
    if paced:
        L += ["", "Pace inside shots (measured; put it in the prompts):"] + [f"- #{i}: {w}" for i, w in paced]
    rh = plan.get("rhythm")
    if rh:
        verdict = "cuts to the beat" if rh["cut_to_beat"] else "does not cut to the beat"
        L += ["", f"Rhythm: the source {verdict} of its sound ({rh['bpm']} bpm{'' if rh['clear_pulse'] else ', no clear pulse'}): "
                  f"{rh['within_2_frames']:.0%} of its cuts are within 2 frames of a beat, {rh['chance_within_2_frames']:.0%} by chance."
              + (" With new music, build_edit.py --music moves those cuts onto its beats." if rh["cut_to_beat"] else "")]
    if plan["route_changed"]:
        L += ["", "Routes changed in review: " + ", ".join(f"#{c['shot']} {c['measured']}→{c['now']}" for c in plan["route_changed"])]
    if plan["unreviewed"]:
        L += ["", "Not reviewed yet: " + ", ".join(f"#{i}" for i in plan["unreviewed"])]
    return "\n".join(L) + "\n"


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("dir", help="analyze.py output folder (analysis.json, review.json)")
    ap.add_argument("--max", type=float, required=True, help="the chosen model's longest single generation, seconds (list_models)")
    ap.add_argument("--min", type=float, default=0.0, help="its shortest generation, seconds")
    ap.add_argument("--multi-shot", action="store_true", help="the model can make several shots with hard cuts in one generation")
    ap.add_argument("--hardcut-prefer", type=float, default=8.0, help="preferred longest run of hard cuts in one generation")
    ap.add_argument("--hardcut-max", type=float, default=10.0, help="longest run of hard cuts in one generation")
    ap.add_argument("--unit-min", type=float, default=4.0, help="a single shot shorter than this is generated this long and trimmed")
    ap.add_argument("--scene-threshold", type=float, default=0.5, help="colour distance under which two shots count as one scene")
    ap.add_argument("--keep", help="shot numbers the user owns and keeps as they are, e.g. 3,7 (same as route keep in review.json)")
    ap.add_argument("--cut", action="store_true", help="also cut each unit's source clip into remake/units/")
    ap.add_argument("--ref-audio", action="store_true", help="keep the source sound in the unit clips (default: silent)")
    args = ap.parse_args()
    root = Path(args.dir)
    if not (root / "analysis.json").exists():
        sys.exit(f"✗ {root}/analysis.json not found: run analyze.py first")
    plan = build(root, args)
    out = root / "remake"
    out.mkdir(parents=True, exist_ok=True)
    (out / "plan.json").write_text(json.dumps(plan, ensure_ascii=False, indent=2), encoding="utf-8")
    md = markdown(plan)
    (out / "plan.md").write_text(md, encoding="utf-8")
    print(md)
    print(f"→ {out / 'plan.json'}")


if __name__ == "__main__":
    main()
