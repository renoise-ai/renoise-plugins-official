#!/usr/bin/env python3
"""Archival photo -> Vox collage sticker: photocopy contrast + 45deg halftone dots + scissor-cut paper border (with a mask) or a torn photo print (rectangle).
Usage: python3 halftone.py in.jpg out.png [--mask m.png] [--w 1000] [--cell 7] [--border 12] [--mix 0.35] [--tint 1D1A16] [--crop x0,y0,x1,y1]
  --mask: foreground mask (mask.py, white = keep) -> cut along the person; without it -> rectangular torn print
  --mix: how much continuous grey to keep (0 = dots only, 1 = plain greyscale), default 0.35
  --crop: crop in 0-1 fractions, e.g. bust only: --crop 0,0,1,0.62"""
import os, sys, numpy as np
from PIL import Image, ImageFilter, ImageOps

a = sys.argv
arg = lambda k, d=None: a[a.index(k) + 1] if k in a else d
src, dst = a[1], a[2]
W, cell, border, mix = int(arg("--w", 1000)), float(arg("--cell", 7)), int(arg("--border", 12)), float(arg("--mix", 0.35))
ink = tuple(int(arg("--tint", "1D1A16")[i:i + 2], 16) for i in (0, 2, 4))
paper = (239, 231, 214); edge = (246, 241, 230)

im = Image.open(src).convert("RGB")
mk = Image.open(arg("--mask")).convert("L").resize(im.size) if arg("--mask") else None
if arg("--crop"):
    x0, y0, x1, y1 = [float(v) for v in arg("--crop").split(",")]
    box = (int(x0 * im.width), int(y0 * im.height), int(x1 * im.width), int(y1 * im.height))
    im = im.crop(box); mk = mk.crop(box) if mk else None
H = round(im.height * W / im.width)
im = im.resize((W, H), Image.LANCZOS); mk = mk.resize((W, H), Image.LANCZOS) if mk else None

g = ImageOps.autocontrast(ImageOps.grayscale(im), cutoff=1.5)
g = np.asarray(g.filter(ImageFilter.UnsharpMask(2, 80, 2))).astype(np.float32) / 255.0
g = np.clip((g - 0.5) * 1.25 + 0.52, 0, 1)                      # photocopy contrast
dark = 1 - g
yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
u = (xx + yy) / (cell * 1.4142) * 2 * np.pi; v = (xx - yy) / (cell * 1.4142) * 2 * np.pi
screen = (np.cos(u) + np.cos(v) + 2) / 4                          # 45deg dot threshold screen 0..1
dots = np.clip((dark - screen) * 6 + 0.5, 0, 1)                   # soft threshold, no jaggies
tone = mix * dark + (1 - mix) * dots
P, I = np.array(paper, np.float32), np.array(ink, np.float32)
rgb = P * (1 - tone[..., None]) + I * tone[..., None]
rng = np.random.default_rng(3)
rgb *= (1 - 0.05 * rng.random((H, W, 1)))                          # paper noise

if mk is not None:
    m = np.asarray(mk.filter(ImageFilter.GaussianBlur(1))).astype(np.float32) / 255.0
    body = (m > 0.5)
    big = Image.fromarray((body * 255).astype(np.uint8)).filter(ImageFilter.MaxFilter(border * 2 + 1))
    noise = Image.fromarray((rng.random((H // 8 + 1, W // 8 + 1)) * 255).astype(np.uint8)).resize((W, H), Image.BICUBIC)
    bm = np.asarray(big.filter(ImageFilter.GaussianBlur(2.5))).astype(np.float32) / 255.0
    bm = np.clip((bm - 0.35 - (np.asarray(noise) / 255.0 - 0.5) * 0.35) * 6, 0, 1)   # uneven scissor-cut white border
    alpha = np.maximum(bm, m)
    out = rgb * m[..., None] + np.array(edge, np.float32) * (1 - m[..., None])
    rgba = np.dstack([out, alpha * 255]).clip(0, 255).astype(np.uint8)
    ys, xs = np.where(alpha > 0.02); pad = 4
    rgba = rgba[max(ys.min() - pad, 0):ys.max() + pad, max(xs.min() - pad, 0):xs.max() + pad]
else:
    b = border
    canvas = np.ones((H + 2 * b, W + 2 * b, 3), np.float32) * np.array(edge, np.float32)
    canvas[b:b + H, b:b + W] = rgb
    Hh, Ww = canvas.shape[:2]
    alpha = np.ones((Hh, Ww), np.float32)
    for side in range(4):                                         # torn teeth on all four sides
        n = Ww if side < 2 else Hh
        prof = np.convolve(rng.random(n), np.ones(5) / 5, "same") * b * 0.6
        idx = np.arange(Hh if side < 2 else Ww)[:, None] if side < 2 else np.arange(Ww)[None, :]
        if side == 0: alpha[(np.arange(Hh)[:, None] < prof[None, :])] = 0
        if side == 1: alpha[(np.arange(Hh)[::-1][:, None] < prof[None, :])] = 0
        if side == 2: alpha[(np.arange(Ww)[None, :] < prof[:, None])] = 0
        if side == 3: alpha[(np.arange(Ww)[::-1][None, :] < prof[:, None])] = 0
    rgba = np.dstack([canvas, alpha * 255]).clip(0, 255).astype(np.uint8)
os.makedirs(os.path.dirname(os.path.abspath(dst)), exist_ok=True)
Image.fromarray(rgba, "RGBA").save(dst)
print(dst, rgba.shape[1], "x", rgba.shape[0])
