#!/usr/bin/env python3
"""Optional local route: batch image generation with the Codex CLI on the user's own ChatGPT plan, instead of the Renoise
image requests (gen_requests.py images). Only where the user has `codex` installed and asks for it. jobs.json -> parallel `codex exec` -> copy from ~/.codex/generated_images/<session>/ -> auto-key green-screen cutouts.
Usage: python3 codex_batch.py jobs.json [--par 4] [--only name1,name2]
jobs.json: {"style": {bg, bg_tail, cut, cut_tail}, "jobs": [{"name": "pigeon", "kind": "cut|bg|rect", "prompt": "..."}]}
  bg   = 16:9 background plate (style prefix "bg") -> public/img/<name>.png
  cut  = sticker on pure green -> greenkey -> public/img/<name>.png (raw kept in build/codex/)
  rect = torn-edge photo print on green -> same as cut
Existing outputs are skipped (delete to redo). Gotcha: codex exec needs </dev/null or it hangs reading stdin."""
import json, os, re, subprocess, sys, time, glob, shutil
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

ROOT = Path.cwd()   # run from the film project root
HERE = Path(__file__).resolve().parent
a = sys.argv
J = json.loads(Path(a[1]).read_text(encoding="utf-8"))
par = int(a[a.index("--par") + 1]) if "--par" in a else 4
only = set(a[a.index("--only") + 1].split(",")) if "--only" in a else None
GEN = Path.home() / ".codex/generated_images"
RAW = ROOT / "build/codex"; RAW.mkdir(parents=True, exist_ok=True)
OUT = ROOT / "public/img"; OUT.mkdir(parents=True, exist_ok=True)
PY = sys.executable
S = J["style"]

def run(job):
    name, kind = job["name"], job["kind"]
    out = OUT / f"{name}.png"
    if out.exists(): return f"skip {name}"
    pre = S["bg"] if kind == "bg" else S["cut"]
    tail = S["bg_tail"] if kind == "bg" else S["cut_tail"]
    prompt = f"Generate one image with your image generation tool. {pre} {job['prompt']} {tail}"
    log = RAW / f"{name}.log"
    for attempt in range(2):
        t0 = time.time()
        with open(log, "w") as lf:
            subprocess.run(["codex", "exec", "--skip-git-repo-check", "-c", "model_reasoning_effort=low", prompt], stdin=subprocess.DEVNULL, stdout=lf, stderr=subprocess.STDOUT, timeout=900)
        txt = log.read_text(errors="ignore")
        sid = re.findall(r"session id: ([0-9a-f-]+)", txt)
        pngs = sorted(glob.glob(str(GEN / sid[-1] / "*.png")), key=os.path.getmtime) if sid else []
        if pngs: break
    if not pngs: return f"FAIL {name} (see {log})"
    raw = RAW / f"{name}.png"; shutil.copy(pngs[-1], raw)
    if kind == "bg":
        shutil.copy(raw, out)
    else:
        env = {**os.environ, "PYTHONPATH": ""}
        subprocess.run([PY, str(HERE / "greenkey.py"), str(raw), str(out)], env=env, capture_output=True)
    return f"ok {name} {time.time() - t0:.0f}s"

jobs = [j for j in J["jobs"] if not only or j["name"] in only]
with ThreadPoolExecutor(par) as ex:
    for r in ex.map(run, jobs): print(r, flush=True)
