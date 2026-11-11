#!/usr/bin/env python3
"""One-step finishing: raw Remotion render -> delivery MP4 at the target loudness with a safe true peak, verified.
Usage: python3 finish.py out/raw.mp4 "<delivery.mp4>" [--lufs -16] [--peak -1.5] [--crf 27] [--srt out/subs.srt] [--sheet out/qa_open.jpg]
What it does:
  1. measures the raw integrated loudness and applies one gain (volume) + limiter, always from the raw audio
     (AAC on AAC pushes peaks up; the true peak after AAC varies run to run, so it is measured, not assumed)
  2. encodes the picture once (x264, --crf), then re-does only the audio with a lower limiter ceiling until the
     measured true peak is under --peak (up to 6 tries)
  3. --srt: muxes the captions as a soft subtitle track (players can switch them on); burned-in captions come from
     shots.json "subtitles": true instead
  4. verifies frame count and duration against the raw file and prints loudness, peak and size
  5. --sheet: writes a contact sheet of the first 10 seconds (every 0.5 s) - look at it: the cover, every teaser
     clip (none empty), the first board"""
import json, os, re, subprocess, sys
a = sys.argv
if len(a) < 3: sys.exit(__doc__)
raw, out = a[1], a[2]
opt = lambda k, d: a[a.index(k) + 1] if k in a else d
LUFS, PEAK, CRF = float(opt("--lufs", -16)), float(opt("--peak", -1.5)), opt("--crf", "27")
srt, sheet = opt("--srt", None), opt("--sheet", None)

def loud(path):
    r = subprocess.run(["ffmpeg", "-hide_banner", "-i", path, "-vn", "-af", "loudnorm=print_format=json", "-f", "null", "-"], capture_output=True, text=True).stderr
    j = json.loads(r[r.rindex("{"):r.rindex("}") + 1]); return float(j["input_i"]), float(j["input_tp"])
def probe(path, what):
    return subprocess.run(["ffprobe", "-v", "error", *what, "-of", "csv=p=0", path], capture_output=True, text=True).stdout.strip().strip(",")

i0, tp0 = loud(raw)
gain = LUFS - i0
print(f"raw: {i0:.1f} LUFS, true peak {tp0:.1f} dBTP -> gain {gain:+.1f} dB")
os.makedirs(os.path.dirname(os.path.abspath(out)), exist_ok=True)
pic = out + ".pic.mp4"
subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", raw, "-an", "-c:v", "libx264", "-crf", CRF, "-preset", "medium", "-pix_fmt", "yuv420p", pic], check=True)
ceiling = PEAK - 1.5                                   # limiter ceiling in dBFS; AAC overshoots it by 1-3 dB
for attempt in range(6):
    lim = 10 ** (ceiling / 20)
    cmd = ["ffmpeg", "-v", "error", "-y", "-i", pic, "-i", raw] + (["-i", srt] if srt else []) + ["-map", "0:v", "-map", "1:a"] + (["-map", "2:0", "-c:s", "mov_text", "-metadata:s:s:0", "language=und"] if srt else []) + \
          ["-c:v", "copy", "-af", f"volume={gain:.2f}dB,alimiter=limit={lim:.4f}:attack=5:release=80:level=false", "-c:a", "aac", "-b:a", "192k", "-movflags", "+faststart", out]
    subprocess.run(cmd, check=True)
    i1, tp1 = loud(out)
    print(f"  try {attempt + 1}: limiter {ceiling:.1f} dBFS -> {i1:.1f} LUFS, true peak {tp1:.1f} dBTP")
    if tp1 <= PEAK: break
    ceiling -= (tp1 - PEAK) + 0.4
os.remove(pic)
fr = lambda p: probe(p, ["-count_packets", "-select_streams", "v:0", "-show_entries", "stream=nb_read_packets"])
d0, d1 = float(probe(raw, ["-show_entries", "format=duration"])), float(probe(out, ["-show_entries", "format=duration"]))
f0, f1 = fr(raw), fr(out)
ok = f0 == f1 and abs(d0 - d1) < 0.2 and tp1 <= PEAK and abs(i1 - LUFS) < 1.5
print(f"{'OK' if ok else 'CHECK'}: {out}  {d1:.1f}s  frames {f1}/{f0}  {i1:.1f} LUFS  {tp1:.1f} dBTP  {os.path.getsize(out) / 1e6:.0f} MB" + ("  +soft captions" if srt else ""))
if sheet:
    from PIL import Image
    tmp = out + ".qa"; os.makedirs(tmp, exist_ok=True); ims = []
    for k in range(20):
        p = f"{tmp}/{k:02d}.jpg"
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", f"{0.25 + k * 0.5:.2f}", "-i", out, "-frames:v", "1", "-vf", "scale=480:-1", p])
        if os.path.exists(p): ims.append(Image.open(p).copy()); os.remove(p)
    os.rmdir(tmp)
    if ims:
        w, h = ims[0].size; S = Image.new("RGB", (w * 5, h * ((len(ims) + 4) // 5)))
        for k, im in enumerate(ims): S.paste(im, ((k % 5) * w, (k // 5) * h))
        S.save(sheet, quality=85); print(f"opening sheet (0-10 s, every 0.5 s): {sheet}")
sys.exit(0 if ok else 1)
