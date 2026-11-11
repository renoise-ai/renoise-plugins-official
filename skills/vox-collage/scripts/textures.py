#!/usr/bin/env python3
"""Paper textures for the engine, generated (deterministic, seed 7): python3 textures.py <public/img dir>
  grain.png  1024x1024 RGB: mid-grey paper grain with fibres (multiplied over every board)
  grunge.png  600x600 RGBA: blotchy rubber-stamp mask
new_film.py runs it; existing files are kept."""
import sys
from pathlib import Path
import numpy as np
from PIL import Image, ImageFilter

out = Path(sys.argv[1] if len(sys.argv) > 1 else "public/img"); out.mkdir(parents=True, exist_ok=True)
rng = np.random.default_rng(7)
n = rng.normal(0, 1, (1024, 1024))
fib = np.asarray(Image.fromarray(((rng.random((1024, 1024)) > 0.997) * 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(1.2))) / 255
if not (out / "grain.png").exists():
    Image.fromarray(np.clip(235 + n * 14 - fib * 60, 0, 255).astype(np.uint8)).convert("RGB").save(out / "grain.png")
m = Image.fromarray((rng.random((256, 256)) * 255).astype(np.uint8)).resize((600, 600), Image.BICUBIC).filter(ImageFilter.GaussianBlur(2))
a = np.asarray(m).astype(float); a = np.where(a > 70, 255, np.clip((a - 40) * 8, 0, 255)).astype(np.uint8)
a[rng.random((600, 600)) > 0.985] = 0
if not (out / "grunge.png").exists():
    Image.fromarray(np.dstack([np.zeros_like(a)] * 3 + [a]).astype(np.uint8), "RGBA").save(out / "grunge.png")
print(f"textures in {out}")
