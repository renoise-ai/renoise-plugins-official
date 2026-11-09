#!/usr/bin/env python3
"""Check each generated unit against its own source clip, before anything is assembled.

    python check_units.py <analysis folder> results.json [--only G1,G3] [--keyframes keyframes.json]

results.json is the same file build_edit.py reads ({"G1": "gen/G1.mp4", "G2": ["gen/G2_part1.mp4", ...], ...}); units
without a result are skipped. For each unit, measured with rn (shots or cuts, signal, text):

  length   generated vs needed seconds; a short result plays slower in the film
  cuts     the cuts the model made vs the cuts the plan asks for (shot boundaries inside the unit): a missing cut means
           two shots came out as one; an extra cut means the model cut where the source runs on. With rn 0.7+ (rn shots)
           dissolves and fades count too: one where the source cuts is reported, as the cut would show blended frames
  camera   with rn 0.7+: a shot whose source clearly pushes in, pulls out or pans (one rigid move of the whole frame) and
           whose result moves the other way or hardly at all, or a locked-off source shot whose result clearly moves
  motion   how the frame-to-frame change over time follows the source clip's (Pearson r of the smoothed curves): a low r
           with a moving source means the action or its timing drifted. A coarse cue, not a verdict: look at the sheet
  frozen   a still tail (generators often stop moving before the end) where the source still moves; black frames
  text     words OCR reads in the result but not in the source clip (the prompts ask for no added text); skipped
           when tesseract is missing

Writes remake/checks/<unit>.json and <unit>.jpg (per shot: source clip, keyframe if any, result, at the shot's middle)
and prints each unit's verdict ("pass" or "check") with the prompt changes that address what failed. Identity,
wardrobe and product details are for you to judge on the sheet.
"""
from __future__ import annotations

import argparse
import json
import math
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

import numpy as np

CUT_TOL = 0.5      # s: a planned cut and a detected one this close are the same cut
EDGE = 0.2         # s: cuts this close to a clip's ends are ignored
LOW_R = 0.2        # motion correlation below this, with a moving source, is reported
STILL_DIFF = 0.002  # mean frame difference (0..1) under which a frame counts as unchanged
FROZEN_S = 0.6
RN_SHOTS = (0, 7, 0)
# camera: a source shot counts as one clear move when one rigid zoom / pan explains it (rigid fit, 0..1) and it is at least
# this fast; the result must move the same way at a third of that speed or more. Conservative: generators drift a little
CAM_FIT = 0.5
CAM_ZOOM = 0.02    # zoom per second (2%/s)
CAM_PAN = 0.03     # frame widths per second
CAM_TURN = 60.0    # degrees between pan directions


def rn(*args: str) -> dict:
    """Run an rn command and return its --json result."""
    if not shutil.which("rn"):
        sys.exit("✗ rn not found: install renoise-kit (the Renoise sandbox has it)")
    with tempfile.TemporaryDirectory() as tmp:
        out = Path(tmp) / "r.json"
        r = subprocess.run(["rn", *args, "--json", str(out)], capture_output=True, text=True)
        if r.returncode != 0:
            raise RuntimeError((r.stderr or r.stdout).strip().splitlines()[-1] if (r.stderr or r.stdout).strip() else "rn failed")
        return json.loads(out.read_text(encoding="utf-8"))


def rn_version() -> tuple[int, ...] | None:
    try:
        out = subprocess.run(["rn", "--version"], capture_output=True, text=True, timeout=60).stdout.split()
        return tuple(int(part) for part in out[-1].split(".")[:3]) if out else None
    except (OSError, ValueError, subprocess.TimeoutExpired):
        return None


def camera_words(zoom: float, pan: float, pan_dir: float) -> str:
    """zoom per second, pan in frame widths per second, the picture's pan direction (image degrees, y down) as a camera move."""
    parts = []
    if abs(zoom) >= CAM_ZOOM / 2:
        parts.append(f"{'pushes in' if zoom > 0 else 'pulls out'} {abs(zoom):.0%}/s")
    if pan >= CAM_PAN / 2:  # the camera moves against the picture
        parts.append(["pans right", "tilts down", "pans left", "tilts up"][round(((pan_dir + 180) % 360) / 90) % 4]
                     + f" {pan:.0%} of the width/s")
    return " and ".join(parts) or "holds still"


def camera_check(shot: int, src: dict, gen: dict) -> tuple[str, str] | None:
    """src: the source shot's {zoom, pan, dir, fit, still}; gen: the result's. A flag and a prompt fix, or None."""
    turn = lambda a, b: abs((a - b + 180) % 360 - 180)  # noqa: E731
    said, got = camera_words(src["zoom"], src["pan"], src["dir"]), camera_words(gen["zoom"], gen["pan"], gen["dir"])
    if src["fit"] >= CAM_FIT and (abs(src["zoom"]) >= CAM_ZOOM or src["pan"] >= CAM_PAN):
        zoom_off = abs(src["zoom"]) >= CAM_ZOOM and (gen["zoom"] * src["zoom"] <= 0 or abs(gen["zoom"]) < abs(src["zoom"]) / 3)
        pan_off = src["pan"] >= CAM_PAN and (gen["pan"] < src["pan"] / 3 or turn(gen["dir"], src["dir"]) > CAM_TURN)
        if zoom_off or pan_off:
            return (f"shot #{shot}: the source camera {said}, the result {got}",
                    f"Shot #{shot}: describe the camera as one steady move that {said} over the whole shot.")
    elif src["still"] and gen["fit"] >= CAM_FIT and (abs(gen["zoom"]) >= 1.5 * CAM_ZOOM or gen["pan"] >= 1.5 * CAM_PAN):
        return (f"shot #{shot}: the source camera holds still, the result {got}",
                f"Shot #{shot}: ask for a locked-off, static camera.")
    return None


def best_scale(L: float, D: float, planned: list[float], found: list[float], tol: float = 0.5) -> float:
    """How a generation shorter than planned (L < D seconds) maps onto the plan: squeezed evenly (L / D) or cut off at the
    end (1.0, the shots keep their lengths and the last one runs short). Whichever lines more planned cuts up with the
    cuts the model made; squeezed when neither does better."""
    if L >= D - 0.05:
        return 1.0

    def hits(scale: float) -> int:
        return sum(any(abs(f - t * scale) <= tol for f in found) for t in planned if t * scale < L)

    return 1.0 if planned and hits(1.0) > hits(L / D) else L / D


def duration(path: Path) -> float:
    r = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(path)],
                       capture_output=True, text=True, check=True)
    return float(r.stdout.strip() or 0)


def smooth(x: np.ndarray, n: int) -> np.ndarray:
    if n <= 1 or len(x) < n:
        return x
    return np.convolve(x, np.ones(n) / n, mode="same")


def curve(sig: dict, span: float, points: int = 200) -> np.ndarray:
    """The frame-difference curve over [0, span] seconds, smoothed over half a second, on `points` samples."""
    fps = float(sig["fps"])
    d = smooth(np.asarray(sig["video"]["diff"], dtype=float), max(1, round(fps / 2)))
    t = np.arange(len(d)) / fps
    return np.interp(np.linspace(0, min(span, t[-1] if len(t) else 0), points), t, d) if len(d) else np.zeros(points)


def pearson(a: np.ndarray, b: np.ndarray) -> float | None:
    if a.std() < 1e-6 or b.std() < 1e-6:
        return None
    return float(np.corrcoef(a, b)[0, 1])


def still_tail(sig: dict, span: float) -> float | None:
    """Start (s) of an unchanged run reaching the end of [0, span], if longer than FROZEN_S."""
    fps = float(sig["fps"])
    d = np.asarray(sig["video"]["diff"], dtype=float)[: max(1, int(span * fps))]
    k = len(d)
    while k > 0 and d[k - 1] < STILL_DIFF:
        k -= 1
    return round(k / fps, 2) if (len(d) - k) / fps >= FROZEN_S else None


def black_runs(sig: dict, span: float) -> list[list[float]]:
    fps = float(sig["fps"])
    luma = np.asarray(sig["video"]["luma"], dtype=float)[: max(1, int(span * fps))]
    runs, start = [], None
    for i, v in enumerate(list(luma) + [1.0]):
        if v < 0.06 and start is None:
            start = i
        elif v >= 0.06 and start is not None:
            if (i - start) / fps >= 0.25:
                runs.append([round(start / fps, 2), round(i / fps, 2)])
            start = None
    return runs


def grab(path: Path, t: float, out: Path) -> Path | None:
    r = subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", f"{max(0.0, t):.3f}", "-i", str(path), "-frames:v", "1",
                        "-vf", "scale=-2:320", str(out)], capture_output=True)
    return out if r.returncode == 0 and out.exists() else None


def sheet(rows: list[tuple[str, list[Path | None]]], out: Path) -> None:
    """One column per shot: source clip / keyframe / result, top to bottom."""
    from PIL import Image, ImageDraw

    h = 320
    cols = []
    for label, paths in rows:
        ims = [Image.open(p).convert("RGB") if p else None for p in paths]
        w = max((im.width for im in ims if im), default=180)
        cols.append((label, ims, w))
    sheet_im = Image.new("RGB", (sum(w + 8 for _, _, w in cols) + 8, 3 * (h + 4) + 28), (24, 24, 24))
    d = ImageDraw.Draw(sheet_im)
    x = 8
    for label, ims, w in cols:
        d.text((x, 6), label, fill=(235, 235, 235))
        for row, im in enumerate(ims):
            y = 24 + row * (h + 4)
            if im:
                sheet_im.paste(im.resize((w, h)), (x, y))
            else:
                d.text((x + 6, y + h // 2), "—", fill=(150, 150, 150))
        x += w + 8
    sheet_im.save(out, quality=86)


def check_clip(f: Path, ref: Path, need: float, planned_cuts: list[float], shots: list[dict], text: bool,
               ref_text_cache: dict, cameras: dict | None = None) -> dict:
    """Measure one generated clip against its source clip. shots: [{"shot", "t0", "t1"}] on the source clip's clock.
    cameras: the source shots' camera moves by shot number, when rn shots (rn 0.7+) measures the result too; else None."""
    L = duration(f)
    measured = rn("shots", str(f)) if cameras is not None else None
    gen_shots = measured["shots"] if measured else None
    # rn shots: every boundary (cuts, dissolves, fades, flash cuts); rn cuts: hard cuts only
    kinds = {round(g["start"], 3): g["transition_in"] for g in gen_shots[1:]} if gen_shots else {}
    all_cuts = sorted(kinds) if gen_shots is not None else [c["time"] for c in rn("cuts", str(f))["cuts"]]
    scale = best_scale(L, need, planned_cuts, all_cuts)
    used = min(L, need * scale)
    res: dict = {"file": str(f), "generated_s": round(L, 2), "needed_s": round(need, 2), "speed": round(scale, 3)}
    flags, fixes = [], []
    if L < need - 0.05 and scale == 1.0:
        flags.append(f"generated {L:.1f} s for {need:.1f} s: it stops early, the last shot would run {need - L:.1f} s short")
        fixes.append(f"Request at least {math.ceil(need)} s.")
    elif scale < 0.85:
        flags.append(f"generated {L:.1f} s for {need:.1f} s: it would play at {scale:.0%} speed")
        fixes.append(f"Request at least {math.ceil(need)} s.")
    # cuts
    found = [t for t in all_cuts if EDGE < t < used - EDGE]
    want = [t * scale for t in planned_cuts if t * scale < used - EDGE]
    unused = list(found)
    missing = []
    soft = []
    for t in want:
        near = min(unused, key=lambda u: abs(u - t), default=None)
        if near is not None and abs(near - t) <= CUT_TOL:
            unused.remove(near)
            if kinds.get(near) in ("dissolve", "fade"):
                soft.append((near, kinds[near]))
        else:
            missing.append(round(t, 2))
    res["cuts"] = {"planned": [round(t, 2) for t in want], "found": found, "missing": missing, "extra": unused,
                   **({"kinds": {str(t): k for t, k in kinds.items()}} if kinds else {})}

    def shot_at(t: float) -> int:
        return next((s["shot"] for s in shots if s["t0"] * scale <= t < s["t1"] * scale), shots[-1]["shot"])

    for t in missing:
        a, b = shot_at(t - 0.05), shot_at(t + 0.05)
        flags.append(f"no cut near {t:.1f} s: shots #{a} and #{b} came out as one")
        fixes.append(f"Make the hard cut at {t / scale:.1f} s explicit: the shot before it ends on its end state, the next "
                     f"one opens on a new framing.")
    for t in unused:
        what = {"dissolve": "a dissolve", "fade": "a fade"}.get(kinds.get(t), "a cut")
        flags.append(f"{what} at {t:.1f} s inside shot #{shot_at(t)}, where the source runs on")
        fixes.append(f"Describe shot #{shot_at(t)} as one continuous shot with no cut.")
    for t, kind in soft:
        flags.append(f"{'a dissolve' if kind == 'dissolve' else 'a fade'} at {t:.1f} s where the source cuts from "
                     f"#{shot_at(t - 0.05)} to #{shot_at(t + 0.05)}: the cut would show blended frames")
        fixes.append(f"Make the change at {t / scale:.1f} s a hard cut, with no dissolve or fade.")
    # camera: each planned shot against the result's shot that covers its middle, when that shot is mostly this one
    if gen_shots and cameras:
        width = float(measured["size"][0])  # pans come in the result's own pixels
        res["camera"] = []
        for o in shots:
            src = cameras.get(o["shot"])
            if not src:
                continue
            t0, t1 = o["t0"] * scale, min(o["t1"] * scale, used)
            mid = (t0 + t1) / 2
            g = next((x for x in gen_shots if x["start"] <= mid < x["end"]), None)
            if g is None or (min(g["end"], t1) - max(g["start"], t0)) < 0.7 * (g["end"] - g["start"]):
                continue
            m = g["motion"]
            gen = {"zoom": float(m["zoom_per_s"]), "pan": float(m["pan_px_per_s"]) / width, "dir": float(m["pan_dir_deg"]),
                   "fit": float(m["rigid_fit"])}
            res["camera"].append({"shot": o["shot"], "source": camera_words(src["zoom"], src["pan"], src["dir"]),
                                  "result": camera_words(gen["zoom"], gen["pan"], gen["dir"])})
            found_off = camera_check(o["shot"], src, gen)
            if found_off:
                flags.append(found_off[0])
                fixes.append(found_off[1])
    # motion
    sig, rsig = rn("signal", str(f)), rn("signal", str(ref))
    a, b = curve(rsig, need), curve(sig, used)
    r = pearson(a, b)
    moving = float(np.asarray(rsig["video"]["diff"]).std()) > 0.004
    res["motion_r"] = None if r is None else round(r, 2)
    if r is not None and r < LOW_R and moving:
        flags.append(f"motion follows the source loosely (r = {r:.2f})")
        fixes.append("Name the source's beats in each shot prompt (what moves, when, how fast) and its end state.")
    # colour (rn 0.7+ rn look): units from separate calls drift apart in grade; fix it in the edit, not by regenerating
    try:
        vs = rn("look", str(f), "--ref", str(ref))["inputs"][0]["vs_ref"]
        res["look"] = {"match": vs["match"], "distance": vs["distance"], "de76": vs["de76"]}
        if vs["match"] == "far":
            flags.append(f"tone and colour far from the source clip (rn look distance {vs['distance']:.0f})")
            fixes.append(f"Grade it in the edit rather than regenerating: rn grade {f.name} --ref <source clip> -o {f.stem}.cube, "
                         f"then \"vf\": \"lut3d=file={f.stem}.cube\" on its clips.")
    except RuntimeError as exc:  # rn before 0.7.0 has no rn look
        res["look"] = f"skipped: {exc}"
    tail, rtail = still_tail(sig, used), still_tail(rsig, need)
    if tail is not None and (rtail is None or tail / scale < rtail - 0.5):
        flags.append(f"the picture freezes from {tail:.1f} s")
        fixes.append("Keep the action going to the last second; describe the end state as still in motion.")
    blacks = black_runs(sig, used)
    if blacks and not black_runs(rsig, need):
        flags.append(f"black frames at {blacks}")
    res.update(frozen_from=tail, black=blacks)
    # text the source clip does not have
    if text:
        try:
            if str(ref) not in ref_text_cache:
                ref_text_cache[str(ref)] = {s["text"] for s in rn("text", str(ref))["spans"]}
            new = [s for s in rn("text", str(f))["spans"]
                   if len(s["text"].strip()) >= 2 and s["text"] not in ref_text_cache[str(ref)] and s.get("start", 0) < used]
            res["text"] = [{"text": s["text"], "start": s.get("start"), "end": s.get("end")} for s in new[:8]]
            if new:
                flags.append(f"text on screen the source does not have: {', '.join(repr(s['text']) for s in new[:3])}")
                fixes.append("Ask for no captions, titles, labels or written words added to the picture.")
        except RuntimeError as exc:
            res["text"] = f"skipped: {exc}"
    res["flags"], res["fixes"] = flags, fixes
    return res


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("dir", help="analyze.py output folder (has remake/plan.json)")
    ap.add_argument("results", help="results.json: plan item id -> generated file(s)")
    ap.add_argument("--only", help="unit ids to check, e.g. G1,G3 (default: every unit with a result)")
    ap.add_argument("--keyframes", help="keyframes.json, to put each keyframe on the sheet")
    ap.add_argument("--no-text", action="store_true", help="skip the OCR check")
    args = ap.parse_args()
    root = Path(args.dir)
    plan = json.loads((root / "remake" / "plan.json").read_text(encoding="utf-8"))
    rpath = Path(args.results)
    results = json.loads(rpath.read_text(encoding="utf-8"))
    kpath = Path(args.keyframes) if args.keyframes else None
    kf = json.loads(kpath.read_text(encoding="utf-8")) if kpath else {}
    only = set(args.only.split(",")) if args.only else None
    outdir = root / "remake" / "checks"
    outdir.mkdir(parents=True, exist_ok=True)
    text = not args.no_text and bool(shutil.which("tesseract"))
    # rn 0.7+: rn shots measures each result (dissolves and fades, and its camera moves) against the source shots' moves
    cameras = None
    if (rn_version() or ()) >= RN_SHOTS:
        analysis = json.loads((root / "analysis.json").read_text(encoding="utf-8"))
        aw = float(min(480, analysis["source"]["display"][0]) // 2 * 2)  # analysis.json keeps pans in analysis pixels
        cameras = {a["index"]: {"zoom": float(a["motion"]["zoom_per_s"]), "pan": float(a["motion"]["pan_px_per_s"]) / aw,
                                "dir": float(a["motion"]["pan_dir_deg"]), "fit": float(a["measured"].get("kenburns_score", 0.0)),
                                "still": a["measured"].get("camera") in ("static", "static_with_subject_motion")}
                   for a in analysis["shots"]}

    def path_of(p: str, base: Path) -> Path:
        q = Path(p) if Path(p).is_absolute() else base / p
        if not q.exists():
            sys.exit(f"✗ {q} does not exist")
        return q

    ref_text: dict = {}
    summary = []
    for u in plan["items"]:
        if u["kind"] != "generate" or (only and u["id"] not in only) or not results.get(u["id"]):
            continue
        if not u.get("ref_clip"):
            sys.exit(f"✗ {u['id']} has no source clip: run plan_units.py with --cut")
        got = results[u["id"]]
        files = [path_of(x, rpath.parent) for x in (got if isinstance(got, list) else [got])]
        report: dict = {"unit": u["id"], "shots": u["shots"], "clips": []}
        rows = []
        if u["mode"] == "split":
            if len(files) != len(u["parts"]):
                sys.exit(f"✗ {u['id']} has {len(u['parts'])} parts but results.json gives {len(files)} file(s)")
            for k, (f, p) in enumerate(zip(files, u["parts"]), 1):
                ref = root / p["ref_clip"]
                c = check_clip(f, ref, p["duration"], [], [{"shot": u["shots"][0], "t0": 0.0, "t1": p["duration"]}], text, ref_text,
                               cameras)
                c["part"] = k
                report["clips"].append(c)
                key = f"{u['shots'][0]}.{k}"
                mid = p["duration"] / 2
                rows.append((f"#{key}", [grab(ref, mid, outdir / f"{u['id']}_{k}_src.jpg"),
                                         path_of(kf[key], kpath.parent) if key in kf else None,
                                         grab(f, mid * c["speed"], outdir / f"{u['id']}_{k}_new.jpg")]))
        else:
            ref = root / u["ref_clip"]
            planned = [o["t1"] for o in u["offsets"][:-1]]
            c = check_clip(files[0], ref, u["duration"], planned, u["offsets"], text, ref_text, cameras)
            report["clips"].append(c)
            for o in u["offsets"]:
                mid = (o["t0"] + o["t1"]) / 2
                key = str(o["shot"])
                rows.append((f"#{key}", [grab(ref, mid, outdir / f"{u['id']}_{key}_src.jpg"),
                                         path_of(kf[key], kpath.parent) if key in kf else None,
                                         grab(files[0], mid * c["speed"], outdir / f"{u['id']}_{key}_new.jpg")]))
        flags = [f for c in report["clips"] for f in c["flags"]]
        report["verdict"] = "check" if flags else "pass"
        report["fixes"] = list(dict.fromkeys(x for c in report["clips"] for x in c["fixes"]))
        report["sheet"] = str(outdir / f"{u['id']}.jpg")
        sheet(rows, outdir / f"{u['id']}.jpg")
        for p in outdir.glob(f"{u['id']}_*.jpg"):
            p.unlink()
        (outdir / f"{u['id']}.json").write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
        summary.append({"unit": u["id"], "verdict": report["verdict"], "flags": flags, "fixes": report["fixes"],
                        "sheet": report["sheet"]})
    if cameras is None:
        print("note: rn older than 0.7: cuts are hard cuts only (rn cuts), and the camera check is skipped", file=sys.stderr)
    if not text:
        print("note: text check skipped (" + ("--no-text" if args.no_text else "tesseract not installed") + ")", file=sys.stderr)
    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
