#!/usr/bin/env python3
"""Check what vox-collage needs on this machine or sandbox: python3 <skill>/scripts/doctor.py
Required: Python 3.9+, numpy, Pillow, ffmpeg/ffprobe, Node.js 20+ with npm/npx (Remotion), a whisper backend
(whisper.cpp `whisper-cli` + a ggml model, or faster-whisper), and a CJK font for Chinese films on Linux.
Optional: rembg (cut people out of archival photos), realesrgan-ncnn-vulkan (sharper GIF upscales), certifi.
Prints ✓ / ✗ with the fix; exits 1 when something required is missing."""
import importlib, os, platform, shutil, subprocess, sys
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
ok = True


def report(good, what, fix="", required=True):
    global ok
    if required: ok &= good
    mark = "✓" if good else ("✗" if required else "–")
    print(f"{mark} {what}" + ("" if good or not fix else f"  → {fix}"))


def has(mod):
    try: importlib.import_module(mod); return True
    except Exception: return False


report(sys.version_info >= (3, 9), f"Python {sys.version.split()[0]}", "Python 3.9 or newer")
report(has("numpy"), "numpy", "pip install numpy")
report(has("PIL"), "Pillow", "pip install pillow")
for tool in ("ffmpeg", "ffprobe"):
    report(bool(shutil.which(tool)), tool, "install ffmpeg (brew / apt / winget)")
node = shutil.which("node")
v = subprocess.run([node, "--version"], capture_output=True, text=True).stdout.strip() if node else ""
report(bool(v) and int(v.lstrip("v").split(".")[0]) >= 20, f"Node.js {v or 'missing'}", "Node.js 20 or newer")
report(bool(shutil.which("npx") and shutil.which("npm")), "npm / npx", "comes with Node.js")

from textutil import backend, WM, FW_MODEL
b = backend()
if b == "cpp":
    report(True, f"whisper: whisper.cpp ({Path(WM).name}, DTW token times)")
else:
    report(has("faster_whisper"), f"whisper: faster-whisper (model {FW_MODEL}, downloads on first use)",
           'pip install faster-whisper   (or whisper.cpp: whisper-cli + WHISPER_MODEL=<ggml model file>)')

if platform.system() == "Linux":
    fc = subprocess.run(["fc-list", ":lang=zh"], capture_output=True, text=True).stdout if shutil.which("fc-list") else ""
    report(bool(fc.strip()), "CJK font (Chinese films)", "install fonts-noto-cjk", required=False)

report(has("rembg"), "rembg (masks for archival photos: mask.py)", 'pip install "rembg[cpu]"', required=False)
report(bool(os.environ.get("REALESRGAN_BIN") or shutil.which("realesrgan-ncnn-vulkan")),
       "realesrgan-ncnn-vulkan (sharper GIF upscales)", "optional; gif2frames.py falls back to lanczos", required=False)
report(has("certifi"), "certifi (Wikimedia downloads on python.org builds)", "pip install certifi", required=False)
print("ready" if ok else "fix the ✗ lines first")
sys.exit(0 if ok else 1)
