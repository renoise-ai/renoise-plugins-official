#!/usr/bin/env python3
"""Write the paid generation requests of a film as one JSON file per batch. The scripts never generate or spend:
the agent quotes a batch with the Renoise cost estimate, waits for the user's yes in the conversation, creates the
tasks with the Renoise MCP tools, and downloads each result to the request's `out` path. Then `verify.py` checks them.

Usage (from the film project root):
  python3 <skill>/scripts/gen_requests.py voice-gemini narration.json [--voice Charon] [--raw build/raw]
  python3 <skill>/scripts/gen_requests.py images codex_jobs.json [--only a,b]        # plates + props (GPT Image 2.6)
  python3 <skill>/scripts/gen_requests.py gifs gif/ [--size 512x512] [--frames 12] [--ms 100]
  python3 <skill>/scripts/gen_requests.py music music/                              # one Lyria cue per music/<cue>.txt
  python3 <skill>/scripts/gen_requests.py voices                                    # the 30 Gemini TTS voices
seed-audio long takes are planned by `seed_voice.py plan`, which writes build/requests/voice.json the same way.

Every batch lands in build/requests/<batch>.json:
  {"batch": "...", "requests": [{"name", "model", "type", "prompt", "params", "references", "out"}]}
`params` are this skill's intent (voice, ratio, GIF size...): map them to the live parameter names that the model
details report. `references` are Renoise material ids with the role they play. Requests whose `out` file already
exists are left out, so re-running after a partial batch lists only what is missing."""
import json, os, re, sys
from pathlib import Path

ROOT = Path.cwd()
REQ = ROOT / "build/requests"
CUE = re.compile(r"\[\[\w+\]\]")

VOICES = ("Zephyr F bright|Puck M upbeat|Charon M informative|Kore F firm|Fenrir M excitable|Leda F youthful|Orus M firm|"
          "Aoede F breezy|Callirrhoe F easy-going|Autonoe F bright|Enceladus M breathy|Iapetus M clear|Umbriel M easy-going|"
          "Algieba M smooth|Despina F smooth|Erinome F clear|Algenib M gravelly|Rasalgethi M informative|Laomedeia F upbeat|"
          "Achernar F soft|Alnilam M firm|Schedar M even|Gacrux F mature|Pulcherrima F forward|Achird M friendly|"
          "Zubenelgenubi M casual|Vindemiatrix F gentle|Sadachbia M lively|Sadaltager M knowledgeable|Sulafat F warm").split("|")

# GPT Image 2.6 GIF contract (checked 2026-11; the live model details win if they differ)
GIF_SIZES = {"288x288": (5, 16), "384x384": (5, 16), "512x288": (4, 16), "288x512": (4, 16), "512x512": (3, 16),
             "768x768": (2, 12), "960x960": (2, 9)}
GIF_MS = {20, 100, 200, 500, 1000, 2000}

TTS = "gemini-3.8-flash-tts"
SEED = "seed-audio-1.0"
IMAGE = "gpt-image-2.6-sunburst"
MUSIC = "lyria-pro"


def arg(k, d=None): return sys.argv[sys.argv.index(k) + 1] if k in sys.argv else d


def rel(p): return Path(p).as_posix()


def write(batch, reqs, note=""):
    """Save a batch, leaving out requests whose output exists. Returns the path."""
    REQ.mkdir(parents=True, exist_ok=True)
    todo = [r for r in reqs if not (ROOT / r["out"]).exists()]
    path = REQ / f"{batch}.json"
    path.write_text(json.dumps({"batch": batch, "note": note, "requests": todo}, ensure_ascii=False, indent=1), encoding="utf-8")
    by = {}
    for r in todo: by[r["model"]] = by.get(r["model"], 0) + 1
    print(f"{path.relative_to(ROOT).as_posix()}: {len(todo)} request(s) to generate"
          + (f" ({len(reqs) - len(todo)} already on disk)" if len(todo) < len(reqs) else "")
          + "".join(f"\n  {n} x {m}" for m, n in by.items()))
    print("  next: quote this batch with the Renoise cost estimate and wait for the user's yes before creating tasks")
    return path


def req(name, model, kind, prompt, out, params=None, refs=None):
    return {"name": name, "model": model, "type": kind, "prompt": prompt, "params": params or {},
            "references": refs or [], "out": rel(out)}


def voice_gemini(narr):
    voice = arg("--voice", "Charon")
    if voice not in [v.split()[0] for v in VOICES]: sys.exit(f"unknown voice {voice}; see `gen_requests.py voices`")
    raw = Path(arg("--raw", "build/raw"))
    beats = json.loads(Path(narr).read_text(encoding="utf-8"))["beats"]
    reqs = [req(b["id"], TTS, "audio", CUE.sub("", b["narration"]).strip(), raw / f"{b['id']}.mp3", {"voice": voice})
            for b in beats]
    write("voice", reqs, "Gemini TTS reads everything in the prompt aloud: send the text only, no directions.")


def images(jobs_file):
    J = json.loads(Path(jobs_file).read_text(encoding="utf-8")); S = J["style"]
    only = set(arg("--only").split(",")) if arg("--only") else None
    reqs = []
    for j in J["jobs"]:
        if only and j["name"] not in only: continue
        if (ROOT / "public/img" / f"{j['name']}.png").exists(): continue
        bg = j["kind"] == "bg"
        pre, tail = (S["bg"], S["bg_tail"]) if bg else (S["cut"], S["cut_tail"])
        reqs.append(req(j["name"], IMAGE, "image", f"{pre} {j['prompt']} {tail}", f"build/img_raw/{j['name']}.png",
                        {"ratio": j.get("ratio", "16:9" if bg else "1:1")}))
    write("images", reqs, "Renoise images are opaque: cut-outs are drawn on pure green and keyed by `images_key.py`.")


def gifs(folder):
    size, frames, ms = arg("--size", "512x512"), int(arg("--frames", 12)), int(arg("--ms", 100))
    reqs = []
    for p in sorted(Path(folder).glob("*.txt")):
        o = json.loads(p.with_suffix(".json").read_text(encoding="utf-8")) if p.with_suffix(".json").exists() else {}
        sz, fr, m = o.get("size", size), int(o.get("frames", frames)), int(o.get("ms", ms))
        if sz not in GIF_SIZES: sys.exit(f"{p.name}: size {sz} not in {' · '.join(GIF_SIZES)}")
        lo, hi = GIF_SIZES[sz]
        if not lo <= fr <= hi: sys.exit(f"{p.name}: {sz} takes {lo}-{hi} frames")
        if m not in GIF_MS: sys.exit(f"{p.name}: frame duration must be one of {sorted(GIF_MS)} ms")
        refs = [{"material": str(x), "role": "reference_image"} for x in o.get("refs", [])]
        reqs.append(req(p.stem, IMAGE, "image", p.read_text(encoding="utf-8").strip(), f"build/gif/{p.stem}.gif",
                        {"outputFormat": "gif", "gifSize": sz, "frameCount": fr, "frameDurationMs": m}, refs))
    write("gifs", reqs, "Reference images raise the price of a GIF; quote again if any request has references.")


def music(folder):
    reqs = [req(p.stem, MUSIC, "audio", p.read_text(encoding="utf-8").strip(), f"music/{p.stem}.mp3")
            for p in sorted(Path(folder).glob("*.txt"))]
    write("music", reqs, "Lyria has no duration parameter: the brief asks for about 10 s more than the chapter.")


if __name__ == "__main__":
    if len(sys.argv) < 2: sys.exit(__doc__)
    cmd = sys.argv[1]
    if cmd == "voices": print("\n".join(VOICES))
    elif cmd == "voice-gemini": voice_gemini(sys.argv[2])
    elif cmd == "images": images(sys.argv[2])
    elif cmd == "gifs": gifs(sys.argv[2])
    elif cmd == "music": music(sys.argv[2])
    else: sys.exit(__doc__)
