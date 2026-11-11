#!/usr/bin/env python3
"""Turn downloaded plate/prop images into engine assets: python3 <skill>/scripts/images_key.py codex_jobs.json [--only a,b]
Reads build/img_raw/<name>.png (the `out` of `gen_requests.py images`, or the Codex route's raw files in build/codex/):
  bg        -> public/img/<name>.png, scaled to 1920 px wide
  cut, rect -> green-screen keyed by greenkey.py (soft edge, despill, cropped) -> public/img/<name>.png
Existing outputs are skipped (delete one to redo it)."""
import json, subprocess, sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = Path.cwd()


def arg(k, d=None): return sys.argv[sys.argv.index(k) + 1] if k in sys.argv else d


if len(sys.argv) < 2: sys.exit(__doc__)
J = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
only = set(arg("--only").split(",")) if arg("--only") else None
out_dir = ROOT / "public/img"; out_dir.mkdir(parents=True, exist_ok=True)
for j in J["jobs"]:
    name, kind = j["name"], j["kind"]
    if only and name not in only: continue
    out = out_dir / f"{name}.png"
    if out.exists(): continue
    raw = next((p for p in (ROOT / "build/img_raw" / f"{name}.png", ROOT / "build/codex" / f"{name}.png") if p.exists()), None)
    if not raw: print(f"missing {name}: no build/img_raw/{name}.png"); continue
    if kind == "bg":
        from PIL import Image
        im = Image.open(raw).convert("RGB")
        if im.width != 1920: im = im.resize((1920, round(im.height * 1920 / im.width)), Image.LANCZOS)
        im.save(out); print(f"ok {name} (plate)")
    else:
        r = subprocess.run([sys.executable, str(HERE / "greenkey.py"), str(raw), str(out)], capture_output=True, text=True)
        print(f"{'ok' if r.returncode == 0 else 'FAIL'} {name} {r.stdout.strip() or r.stderr.strip()[-200:]}")
