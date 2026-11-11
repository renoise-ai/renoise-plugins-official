#!/usr/bin/env python3
"""Check the downloaded results of a request batch: python3 <skill>/scripts/verify.py build/requests/<batch>.json
Audio: the decoded length must match the container length (within 0.3 s) and exceed 0.3 s. Media CDNs sometimes
truncate a download: an mp3 decodes to 3 s, a GIF stops half way, an mp4 has 100 of 240 frames. Images and GIFs must
decode completely; video must have frames for its whole duration. Prints one line per request and lists what to
download again (or regenerate); exits 1 when anything is missing or broken."""
import json, subprocess, sys, tempfile
from pathlib import Path

ROOT = Path.cwd()


def probe(path, *what):
    return subprocess.run(["ffprobe", "-v", "error", *what, "-of", "csv=p=0", str(path)], capture_output=True, text=True).stdout.strip()


def audio(p):
    box = float(probe(p, "-show_entries", "format=duration") or 0)
    with tempfile.TemporaryDirectory() as td:
        w = Path(td) / "a.wav"
        subprocess.run(["ffmpeg", "-v", "quiet", "-y", "-i", str(p), "-f", "wav", str(w)])
        dec = float(probe(w, "-show_entries", "format=duration") or 0) if w.exists() else 0.0
    if dec < 0.3: return False, f"decodes to {dec:.1f} s"
    if abs(dec - box) > 0.3: return False, f"truncated: decodes to {dec:.1f} s of {box:.1f} s"
    return True, f"{dec:.1f} s"


def image(p):
    from PIL import Image
    try:
        im = Image.open(p); n = getattr(im, "n_frames", 1)
        for k in range(n): im.seek(k); im.load()
        return True, f"{im.size[0]}x{im.size[1]}" + (f", {n} frames" if n > 1 else "")
    except Exception as e:
        return False, f"does not decode ({str(e)[:60]})"


def video(p):
    d = float(probe(p, "-show_entries", "format=duration") or 0)
    n = probe(p, "-count_packets", "-select_streams", "v:0", "-show_entries", "stream=nb_read_packets,r_frame_rate")
    try:
        rate, cnt = n.split(","); a, b = rate.split("/"); fps = float(a) / float(b); cnt = int(cnt)
    except ValueError:
        return False, "no video stream"
    want = round(d * fps)
    return (cnt >= want - 2), f"{cnt}/{want} frames"


def main(batch):
    B = json.loads(Path(batch).read_text(encoding="utf-8"))
    bad = []
    for r in B["requests"]:
        p = ROOT / r["out"]
        if not p.exists():
            ok, why = False, "missing"
        else:
            ext = p.suffix.lower()
            ok, why = (audio(p) if ext in (".mp3", ".wav", ".m4a", ".aac", ".ogg") else
                       video(p) if ext in (".mp4", ".mov", ".webm") else image(p))
        print(f"{'ok ' if ok else 'BAD'} {r['name']:<14} {r['out']}  {why}")
        if not ok: bad.append(r["name"])
    if bad:
        print(f"\n{len(bad)} to download again (regenerate only if a fresh download fails too): {', '.join(bad)}")
        sys.exit(1)
    print(f"\nall {len(B['requests'])} results verified")


if __name__ == "__main__":
    if len(sys.argv) < 2: sys.exit(__doc__)
    main(sys.argv[1])
