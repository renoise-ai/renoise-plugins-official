#!/usr/bin/env python3
"""GIF -> numbered PNG frames for the engine's Loop element.
Usage: python3 gif2frames.py <in.gif> <public/gif/name> [--up 4] [--model anime|x4plus|lanczos] [--bounce] [--key] [--fit 1000]
- fps comes from the GIF frame duration (GPT Image 2.6: 100 ms -> 10 fps); writes 0001.png... and info.json {n, fps, w, h, src}
- --up: upscale factor. GPT Image GIFs are at most 512x288 (16:9) / 960x960, so upscale before using them as cards:
    anime (default, Real-ESRGAN illustration model) · x4plus (photographic, best for halftone collage) · lanczos (plain resampling)
  uses realesrgan-ncnn-vulkan when it is on PATH (or REALESRGAN_BIN / REALESRGAN_MODELS are set); otherwise lanczos.
  Use --up 4 (other factors are scaled from 4x)
- --key: green-screen key every frame (cut-out loops drawn on pure green), keeping one size for all frames
- --fit N: scale frames down so the longer side is at most N px
- --bounce: for actions whose ends do not meet (raise hand, stamp), play 1->n->1 so the loop does not jump
- GIFs have 256 colours: light denoise (hqdn3d) before upscaling so dither noise is not enlarged into grain"""
import json, os, re, shutil, subprocess, sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
UP_BIN = Path(os.environ.get("REALESRGAN_BIN") or shutil.which("realesrgan-ncnn-vulkan") or "/nonexistent")
UP_MODELS = Path(os.environ.get("REALESRGAN_MODELS") or UP_BIN.parent.parent / "models")


def arg(k, d=None): return sys.argv[sys.argv.index(k) + 1] if k in sys.argv else d


src, out = Path(sys.argv[1]), Path(sys.argv[2])
up, model, bounce = int(arg("--up", "1")), arg("--model", "anime"), "--bounce" in sys.argv
if out.exists(): shutil.rmtree(out)
raw = out / "_raw"; raw.mkdir(parents=True)

# frame duration (GIF pkt_duration, seconds)
pk = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries", "packet=duration_time", "-of", "csv=p=0", str(src)], capture_output=True, text=True).stdout
durs = [float(x.strip().rstrip(",")) for x in pk.split() if re.match(r"^[\d.]+,?$", x.strip())]
dt = sorted(durs)[len(durs) // 2] if durs else 0.1
fps = round(1 / dt, 3) if dt > 0 else 10

subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(src), "-vsync", "0", "-vf", "hqdn3d=1.2:1.2:2:2,format=rgb24", str(raw / "%04d.png")], check=True)
frames = sorted(raw.glob("*.png"))
if not frames: sys.exit("no frames decoded from the GIF")

done = out / "_up"; done.mkdir()
if up > 1 and model != "lanczos" and UP_BIN.exists():
    name = {"anime": "realesrgan-x4plus-anime", "x4plus": "realesrgan-x4plus"}.get(model, "realesrgan-x4plus-anime")
    subprocess.run([str(UP_BIN), "-i", str(raw), "-o", str(done), "-n", name, "-s", "4", "-m", str(UP_MODELS), "-f", "png"], capture_output=True, check=True)
    if up != 4:   # the model is fixed at x4; scale down to the requested factor
        for f in sorted(done.glob("*.png")):
            subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(f), "-vf", f"scale=iw*{up}/4:ih*{up}/4:flags=lanczos", str(f)], check=True)
else:
    for f in frames:
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(f), "-vf", f"scale=iw*{up}:ih*{up}:flags=lanczos", str(done / f.name)], check=True)

seq = sorted(done.glob("*.png"))
if bounce and len(seq) > 2: seq = seq + seq[-2:0:-1]
for i, f in enumerate(seq, 1): shutil.copy(f, out / f"{i:04d}.png")
shutil.rmtree(raw); shutil.rmtree(done)
if "--key" in sys.argv or arg("--fit"):
    from PIL import Image
    for f in sorted(out.glob("*.png")):
        if "--key" in sys.argv:
            subprocess.run([sys.executable, str(HERE / "greenkey.py"), str(f), str(f), "--nocrop"], capture_output=True, check=True)
        if arg("--fit"):
            im = Image.open(f); im.thumbnail((int(arg("--fit")), int(arg("--fit"))), Image.LANCZOS); im.save(f)
w, h = map(int, subprocess.run(["ffprobe", "-v", "error", "-show_entries", "stream=width,height", "-of", "csv=p=0", str(out / "0001.png")], capture_output=True, text=True).stdout.strip().rstrip(",").split(",")[:2])
info = dict(n=len(seq), fps=fps, w=w, h=h, src=str(src), up=up, bounce=bounce)
(out / "info.json").write_text(json.dumps(info), encoding="utf-8")
print(f"n={info['n']} fps={fps} {w}x{h}  → LOOP(\"{out.name}\", x, y, w) in storyboard.py (frames in public/gif/{out.name})")
