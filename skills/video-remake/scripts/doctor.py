#!/usr/bin/env python3
"""Check what the remake scripts need: ffmpeg / ffprobe, rn (renoise-kit 0.7+: rn shots), Python 3.10+, numpy,
OpenCV, Pillow. With rn 0.7+, `rn doctor` checks rn's own parts, and this lists the optional ones the remake uses.

    python3 <skill>/scripts/doctor.py
"""
from __future__ import annotations

import importlib
import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

OPTIONAL = (("librosa", "beats: whether the source cuts to the beat, and build_edit.py --music keeping it"),
            ("tesseract", "the text on screen: analyze.py --text and check_units.py"),
            ("yunet model", "faces in each shot (rn shots --faces)"))

ok = True


def report(good: bool, what: str, fix: str = "") -> None:
    global ok
    ok &= good
    print(("✓ " if good else "✗ ") + what + ("" if good or not fix else f"  → {fix}"))


report(sys.version_info >= (3, 10), f"Python {sys.version.split()[0]}", "Python 3.10 or newer")
for tool in ("ffmpeg", "ffprobe"):
    report(bool(shutil.which(tool)), tool, "install ffmpeg (with libass)")
if shutil.which("ffmpeg"):
    filters = subprocess.run(["ffmpeg", "-hide_banner", "-filters"], capture_output=True, text=True).stdout
    for f in ("ass",):  # rn burns overlay text with it
        report(f" {f} " in filters, f"ffmpeg filter {f}", "an ffmpeg build with libass (ffmpeg 6+)")
rn = shutil.which("rn")
if rn:
    v = subprocess.run([rn, "--version"], capture_output=True, text=True).stdout.split()[-1:] or ["0"]
    parts = tuple(int(x) for x in v[0].split(".")[:2] if x.isdigit())
    report(parts >= (0, 7), f"rn {v[0]} (renoise-kit): rn shots measures the shots, transitions and beats",
           "renoise-kit 0.7 or newer: uv tool install \"renoise-kit[all]\"")
    if parts >= (0, 7):
        with tempfile.TemporaryDirectory() as tmp:
            subprocess.run([rn, "doctor", "--json", str(Path(tmp) / "d.json")], capture_output=True, text=True)
            found = json.loads((Path(tmp) / "d.json").read_text(encoding="utf-8")) if (Path(tmp) / "d.json").exists() else None
        if found is None:
            report(False, "rn doctor", "rn doctor did not run: reinstall renoise-kit")
        else:
            checks = {c["name"]: c for c in found["checks"]}
            broken = [c for c in found["checks"] if c["core"] and c["status"] == "missing"]
            report(found["ok"], "rn doctor: rn's core parts", "; ".join(f"{c['name']}: {c['fix']}" for c in broken))
            for c in found["checks"]:
                if c["status"] == "warn":
                    print(f"! {c['name']}: {c['detail']}" + (f"  → {c['fix']}" if c.get("fix") else ""))
            for name, use in OPTIONAL:
                c = checks.get(name) or {}
                good = c.get("status") == "ok"
                print(("✓ " if good else "· ") + f"{name}: {use}" + ("" if good else f" (optional: {c.get('fix') or 'not found'})"))
else:
    report(False, "rn (renoise-kit)", 'uv tool install "renoise-kit[all]"')
if not rn or parts < (0, 7):
    print(("✓ " if shutil.which("tesseract") else "· ") + "tesseract (optional: check_units.py reads on-screen text with it)")
for mod, pkg in (("numpy", "numpy"), ("cv2", "opencv-python-headless"), ("PIL", "Pillow")):
    try:
        importlib.import_module(mod)
        report(True, pkg)
    except ImportError:
        report(False, pkg, f"python3 -m pip install {pkg}")
sys.exit(0 if ok else 1)
