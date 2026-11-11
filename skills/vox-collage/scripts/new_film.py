#!/usr/bin/env python3
"""Scaffold a Vox collage film project: python3 <skill>/scripts/new_film.py <project dir>
Copies the Remotion engine and SFX, generates the paper textures (textures.py), links (or copies) the scripts as <project>/tools, and installs
node_modules with npm. Set VOX_NODE_MODULES=<path to an existing node_modules with the same Remotion version> to copy
that instead of downloading. Re-run on an existing project to refresh src/ after the skill is updated."""
import os, shutil, subprocess, sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ENGINE = HERE / "engine"
if len(sys.argv) < 2: sys.exit(__doc__)
dst = Path(os.path.expanduser(sys.argv[1])).resolve(); dst.mkdir(parents=True, exist_ok=True)
for item in ["src", "public", "package.json", "remotion.config.ts", "tsconfig.json"]:
    s, d = ENGINE / item, dst / item
    if s.is_dir(): shutil.copytree(s, d, dirs_exist_ok=True)
    else: shutil.copy(s, d)
subprocess.run([sys.executable, str(HERE / "textures.py"), str(dst / "public/img")], check=True)   # grain + grunge
for sub in ["public/img", "public/photo", "public/gif", "public/vid", "public/music", "assets/photo", "build", "music", "gif", "out"]:
    (dst / sub).mkdir(parents=True, exist_ok=True)
tools = dst / "tools"
if not tools.exists():
    try: tools.symlink_to(HERE, target_is_directory=True)
    except OSError: shutil.copytree(HERE, tools, ignore=shutil.ignore_patterns("engine", "examples", "__pycache__"))
if not (dst / "public/film.json").exists():
    (dst / "public/film.json").write_text('{"fps":30,"total":30,"vo":"vo.wav","shots":[{"id":"S00","s":0,"e":30,"bg":"img/grain.png","els":[]}]}', encoding="utf-8")
if not (dst / "node_modules").exists():
    nm = os.environ.get("VOX_NODE_MODULES")
    if nm and Path(nm).is_dir():
        shutil.copytree(nm, dst / "node_modules", symlinks=True); print("node_modules copied from", nm)
    else:
        npm = shutil.which("npm") or sys.exit("npm not found: install Node.js 20+ (python3 <skill>/scripts/doctor.py)")
        subprocess.run([npm, "install", "--no-audit", "--no-fund"], cwd=dst, check=True)
print(f"ready: {dst}\n  next: narration.json, storyboard.py (from sb import *), assets, then tools/resolve.py")
