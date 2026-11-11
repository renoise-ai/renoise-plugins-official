#!/usr/bin/env python3
"""Foreground mask of an archival photo for halftone.py --mask: python3 <skill>/scripts/mask.py in.jpg build/masks/name.png [--model u2net_human_seg]
Uses rembg (pip install "rembg[cpu]"; the model downloads on first use). u2net_human_seg suits people; use
--model isnet-general-use for objects. White = keep. Check the mask: a hand or hat cut off here is cut off in the film."""
import sys
from pathlib import Path

if len(sys.argv) < 3: sys.exit(__doc__)
model = sys.argv[sys.argv.index("--model") + 1] if "--model" in sys.argv else "u2net_human_seg"
from PIL import Image
from rembg import new_session, remove

im = Image.open(sys.argv[1]).convert("RGB")
m = remove(im, session=new_session(model), only_mask=True, post_process_mask=True)
out = Path(sys.argv[2]); out.parent.mkdir(parents=True, exist_ok=True)
m.convert("L").save(out)
print(out, m.size)
