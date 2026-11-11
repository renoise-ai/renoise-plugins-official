#!/usr/bin/env python3
"""Key a green-screen sticker: python3 greenkey.py in.png out.png [--pad 12] [--nocrop]
Pure #00FF00 -> transparent; soft edge + green-spill removal; crops to content (pad px) unless --nocrop (use --nocrop for loop frames so every frame keeps the same size)."""
import sys, numpy as np
from PIL import Image, ImageFilter
src, dst = sys.argv[1], sys.argv[2]
pad = int(sys.argv[sys.argv.index('--pad') + 1]) if '--pad' in sys.argv else 12
im = np.asarray(Image.open(src).convert('RGB')).astype(np.float32)
r, g, b = im[..., 0], im[..., 1], im[..., 2]
excess = g - np.maximum(r, b)                      # green excess: pure green ~255, paper/grey ~0
a = np.clip(1 - (excess - 40) / 80, 0, 1)          # <40 opaque, >120 fully transparent
a = np.asarray(Image.fromarray((a * 255).astype(np.uint8)).filter(ImageFilter.MinFilter(3)).filter(ImageFilter.GaussianBlur(0.8))) / 255.0
spill = np.maximum(r, b)                           # despill: clamp green to max(red, blue)
g2 = np.where(excess > 0, spill + 0.15 * (g - spill) * (a > 0.98), g)
out = np.dstack([r, g2, b, a * 255]).clip(0, 255).astype(np.uint8)
if '--nocrop' in sys.argv:
    Image.fromarray(out, 'RGBA').save(dst); print(dst, out.shape[1::-1]); sys.exit()
ys, xs = np.where(out[..., 3] > 8)
y0, y1, x0, x1 = max(ys.min() - pad, 0), ys.max() + pad, max(xs.min() - pad, 0), xs.max() + pad
Image.fromarray(out[y0:y1, x0:x1], 'RGBA').save(dst)
print(dst, out[y0:y1, x0:x1].shape[1::-1])
