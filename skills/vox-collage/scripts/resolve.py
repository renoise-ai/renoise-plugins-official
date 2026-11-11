#!/usr/bin/env python3
"""shots.json + <build>/timings.json -> public/film.json (everything in frames) + public/vo.wav (with optional pauses before beats).
Usage: python3 resolve.py shots.json [--fps 30] [--build build] [--film film.json] [--vo vo.wav]
Time specs (shot `at` and element `at`):
  "B03"        = start of beat B03        "B03:grid" = the [[grid]] cue inside B03
  "B03:grid+0.4" / "B03-0.2"       = plus/minus seconds
  "+1.2" (elements only)           = 1.2 s after the shot starts
  number (elements only)           = seconds after the shot starts
shots.json top level: {"pauses": {"B05": 3.0}, "score": [...], "teaser": [...], "shots": [{"id","at","bg",...,"els":[...]}], "tail": 3.0,
                       "subtitles": true, "motif": "img/robot"}
  pauses: insert seconds of silence before a beat (for a title card); everything after shifts.
  subtitles: burn captions into the picture (bottom strip). out/subs.srt (timed for the Full composition) is written either way.
  motif: path fragment of the recurring character/prop; resolve reports how many boards carry it.
Checks printed as "!" lines (warnings, the build still completes):
  elements outside their board · teaser clips that cross a cut or show an empty board · boards with nothing new for
  more than --idle seconds (default 2.5; 3.5 for the hold after the last element) · motif coverage and the
  opening/closing bookend · with subtitles on, text elements whose bottom edge reaches the caption strip (top edge y=975)."""
import json, os, re, subprocess, sys
from pathlib import Path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from textutil import keep, lang_of, zh_data

ROOT = Path.cwd()   # run from the film project root
S = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
fps = int(sys.argv[sys.argv.index("--fps") + 1]) if "--fps" in sys.argv else 30
opt = lambda k, d: sys.argv[sys.argv.index(k) + 1] if k in sys.argv else d
BUILD, FILM, VO = opt("--build", "build"), opt("--film", "film.json"), opt("--vo", "vo.wav")   # e.g. a second voice: --build build_uk --film film_uk.json --vo vo_uk.wav
T = json.loads((ROOT / BUILD / "timings.json").read_text(encoding="utf-8"))
beats = T["beats"]
pauses = S.get("pauses", {})
order = list(beats.keys())

# per-beat offset after inserted pauses
shift, acc = {}, 0.0
for b in order:
    acc += pauses.get(b, 0.0); shift[b] = acc

def tsec(spec):
    m = re.fullmatch(r"(B\d+)(?::(\w+))?([+-][\d.]+)?", spec.strip())
    if not m: raise SystemExit(f"unknown time spec: {spec}")
    b, cue, off = m.group(1), m.group(2), float(m.group(3) or 0)
    if b not in beats: raise SystemExit(f"no such beat: {b}")
    B = beats[b]
    base = float(B["start"]) if not cue else float(B["cues"].get(cue, -1) if isinstance(B["cues"], dict) else -1)
    if base < 0: raise SystemExit(f"[[{cue}]] not found in {b}")
    return base + shift[b] + off

total = float(T["total"]) + acc + S.get("tail", 2.0)
shots = S["shots"]
starts = [0.0 if i == 0 else tsec(sh["at"]) for i, sh in enumerate(shots)]  # first shot starts at 0 to cover the narration lead-in
out = []
for i, sh in enumerate(shots):
    s = starts[i]; e = starts[i + 1] if i + 1 < len(shots) else total
    if e <= s: raise SystemExit(f"{sh['id']} has length <= 0 ({s:.2f}->{e:.2f})")
    els = []
    for el in sh.get("els", []):
        el = dict(el); a = el.get("at", 0)
        if isinstance(a, (int, float)): rel = float(a)
        elif a.startswith("+"): rel = float(a[1:])
        else: rel = tsec(a) - s
        if rel < -0.01 or rel > e - s + 0.01: print(f"! {sh['id']} element {el.get('t')} at {a} falls outside the shot ({rel:.2f}s / shot {e - s:.2f}s)")
        el["at"] = round(max(rel, 0) * fps, 1)
        for k in ("out",):
            if k in el and isinstance(el[k], str): el[k] = round((tsec(el[k]) - s) * fps, 1) if not el[k].startswith("+") else round(float(el[k][1:]) * fps, 1)
            elif k in el: el[k] = round(float(el[k]) * fps, 1)
        els.append(el)
    o = {k: v for k, v in sh.items() if k not in ("at", "els")}
    o.update(s=round(s * fps), e=round(e * fps), els=els)
    out.append(o)

# vo.wav: insert silence before the beats listed in pauses
src = ROOT / BUILD / "narration.wav"; dst = ROOT / "public" / VO
cuts = [(float(beats[b]["start"]) - 0.12, d) for b, d in pauses.items()]
if not cuts:
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(src), "-ar", "48000", "-ac", "1", str(dst)], check=True)
else:
    cuts.sort(); parts, prev, filt = [], 0.0, []
    for i, (t, d) in enumerate(cuts):
        filt.append(f"[0]atrim={prev}:{t},asetpts=PTS-STARTPTS[a{i}];anullsrc=r=48000:cl=mono,atrim=0:{d}[s{i}]"); parts += [f"[a{i}]", f"[s{i}]"]; prev = t
    filt.append(f"[0]atrim={prev},asetpts=PTS-STARTPTS[z]"); parts.append("[z]")
    fc = ";".join(filt) + ";" + "".join(parts) + f"concat=n={len(parts)}:v=0:a=1[o]"
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(src), "-filter_complex", fc, "-map", "[o]", "-ar", "48000", "-ac", "1", str(dst)], check=True)

# score: one cue per chapter (at / to are beat or cue specs), crossfaded; duck = narration envelope (one 0-1 value per 3 frames) used to dip the music under speech
score = []
for c in S.get("score", []):
    a0 = tsec(c["at"]) if c["at"] != "0" else 0.0
    a1 = tsec(c["to"]) if c.get("to") else total
    score.append({"src": c["src"], "at": round(a0 * fps), "len": round((a1 - a0) * fps), "start": round(c.get("start", 0) * fps), "gain": c.get("gain", 1.0), "fade": round(c.get("fade", 1.0) * fps)})
import numpy as np
raw = subprocess.run(["ffmpeg", "-v", "error", "-i", str(dst), "-ac", "1", "-ar", "8000", "-f", "f32le", "-"], capture_output=True).stdout
x = np.frombuffer(raw, np.float32); hop = int(8000 * 3 / fps)
rms = np.array([np.sqrt((x[i:i + hop] ** 2).mean()) if i < len(x) else 0 for i in range(0, int(total * 8000), hop)])
on = (rms > 0.02).astype(float)
env, v = [], 0.0
for o in on:   # 0.1 s attack, 0.6 s release: short gaps between sentences do not lift the music, long pauses do
    v = v + (o - v) * (0.9 if o > v else 0.17); env.append(round(v, 2))

# ---- checks -------------------------------------------------------------------------------------------------
warn = []
idle_max = float(opt("--idle", 2.5))
VIS = lambda el: el.get("t") not in ("sfx",)
idle = []
for o in out:
    L = (o["e"] - o["s"]) / fps
    if any(el.get("t") == "title" for el in o["els"]): continue
    ts = sorted({round(el["at"] / fps, 2) for el in o["els"] if VIS(el)})
    pts = [0.0] + ts + [L]
    gaps = [(pts[i + 1] - pts[i], pts[i], i == len(pts) - 2) for i in range(len(pts) - 1)]
    g, at, hold = max(gaps)
    if g > (idle_max + 1.0 if hold else idle_max): idle.append((g, o["id"], at, L, hold))
for g, sid, at, L, hold in sorted(idle, reverse=True)[:12]:
    warn.append(f"{sid}: nothing new for {g:.1f}s (from {at:.1f}s of a {L:.1f}s board{', final hold' if hold else ''}) - add an element, split the board or cut sooner")
if len(idle) > 12: warn.append(f"... and {len(idle) - 12} more idle boards")

def shot_at(fr): return next((o for o in out if o["s"] <= fr < o["e"]), None)
for i, c in enumerate(S.get("teaser", [])):
    f0 = round(tsec(c["at"]) * fps); f1 = f0 + round(c["len"] * fps)
    o = shot_at(f0)
    if not o: warn.append(f"teaser {i + 1} ({c['at']}) starts outside the film"); continue
    if f1 > o["e"] - 2: warn.append(f"teaser {i + 1} ({c['at']}) runs {((f1 - o['e']) / fps):+.1f}s past the cut after {o['id']} - start earlier or shorten it")
    landed = [el for el in o["els"] if VIS(el) and o["s"] + el["at"] <= f0 + 0.3 * fps]
    if not landed: warn.append(f"teaser {i + 1} ({c['at']}) starts on an empty board ({o['id']}) - pick a moment after the first element lands")

pieces = lambda o: {el.get("src") or el.get("dir") for el in o["els"] if el.get("t") in ("piece", "loop", "clip")} - {None}
body = [o for o in out if not any(el.get("t") == "title" for el in o["els"])]
motif = S.get("motif")
if motif:
    ms = [motif] if isinstance(motif, str) else list(motif)
    has = [o for o in body if any(m in src for src in pieces(o) for m in ms)]
    share = len(has) / max(1, len(body))
    print(f"motif {', '.join(ms)}: on {len(has)}/{len(body)} boards ({share:.0%})")
    if share < 0.25: warn.append(f"motif appears on only {share:.0%} of boards - a recurring character should return in every chapter (aim for 30%+)")
    if not any(o in has for o in body[:3]): warn.append("motif is missing from the first three boards - introduce it in the hook")
    if not any(o in has for o in body[-3:]): warn.append("motif is missing from the last three boards - bring it back for the ending")
else: warn.append('no "motif" set - name the recurring character/prop in save(motif="img/...") so every chapter returns to it')
if len(body) > 4 and not (pieces(body[0]) | pieces(body[1])) & (pieces(body[-1]) | pieces(body[-2])):
    warn.append("no bookend: the last boards share no cut-out with the opening - end on the opening image, changed")

# ---- subtitles ----------------------------------------------------------------------------------------------
def sub_lines(text, lang):
    """Split a beat into caption lines: break at punctuation, pack phrases up to the line width, hard-split overlong ones."""
    if lang == "zh":
        Z = zh_data(); brk, stop, width = set(Z["sub_break"]) | set(",.;:?!"), set(Z["sub_stop"]) | set(".?!"), 20
        wid = lambda s: sum(1 if ord(c) > 0x2E7F else 0.5 for c in s)
    else:
        brk, stop, width, wid = set(",.;:?!"), set(".?!"), 42, len
    phrases, cur = [], ""
    for ch in text:
        cur += ch
        if ch in brk and cur.strip(): phrases.append(cur); cur = ""
    if cur.strip(): phrases.append(cur)
    lines, cur = [], ""
    for ph in phrases:
        if cur and (wid(cur + ph) > width or cur.rstrip()[-1:] in stop): lines.append(cur); cur = ""   # never run two sentences into one line
        cur += ph
        while wid(cur) > width:                              # one phrase longer than a line
            cut = len(cur)
            while wid(cur[:cut]) > width: cut -= 1
            if lang == "en": cut = cur.rfind(" ", 0, cut) if cur.rfind(" ", 0, cut) > 0 else cut
            lines.append(cur[:cut]); cur = cur[cut:]
    if cur.strip(): lines.append(cur)
    return lines

def n_tokens(s, lang): return sum(1 for c in s if keep(c)) if lang == "zh" else sum(1 for w in s.split() if re.sub(r"[^A-Za-z0-9]", "", w))
def tidy(s, lang):
    s = s.strip()
    if lang == "zh":
        Z = zh_data()
        while s and s[-1] in Z["sub_drop_end"] + ",.;:": s = s[:-1]
        for c in Z["sub_soften"]: s = s.replace(c, " ")
    return re.sub(r"\s+", " ", s).strip()

subs = []
lang = T.get("lang") or lang_of("".join(B["text"] for B in beats.values()))
for b in order:
    B = beats[b]; tok = B.get("tok"); i = 0
    n_all = max(1, n_tokens(B["text"], lang))
    t_of = (lambda k: tok[min(k, len(tok) - 1)]) if tok else (lambda k: float(B["start"]) + (float(B["end"]) - float(B["start"])) * k / n_all)   # older timings: spread evenly
    lines = [(ln, n_tokens(ln, lang)) for ln in sub_lines(B["text"], lang)]
    lines = [(ln, n) for ln, n in lines if n]
    for k, (ln, n) in enumerate(lines):
        s0 = float(B["start"]) if k == 0 else t_of(i)
        e0 = float(B["end"]) if k == len(lines) - 1 else t_of(i + n)
        i += n
        subs.append((s0 + shift[b], max(e0, s0 + 0.4) + shift[b], tidy(ln, lang)))
for k in range(len(subs) - 1):                                # no overlaps; close gaps shorter than 0.25 s
    s0, e0, tx = subs[k]; nx = subs[k + 1][0]
    subs[k] = (s0, nx if (e0 > nx or 0 < nx - e0 < 0.25) else e0, tx)
head_frames = S.get("coverFrames", 15) + sum(round(c["len"] * fps) for c in S.get("teaser", []))
def srt(path, off):
    stamp = lambda t: "%02d:%02d:%02d,%03d" % (t // 3600, t % 3600 // 60, t % 60, round(t % 1 * 1000) % 1000)
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    Path(path).write_text("".join(f"{k + 1}\n{stamp(s0 + off)} --> {stamp(e0 + off)}\n{tx}\n\n" for k, (s0, e0, tx) in enumerate(subs)), encoding="utf-8")
srt(ROOT / "out/subs.srt", head_frames / fps); srt(ROOT / "out/subs_main.srt", 0.0)
if S.get("subtitles"):
    for o in out:
        for el in o["els"]:
            half = {"label": 0.85 * el.get("size", 40), "note": 0.7 * el.get("size", 48), "stamp": 0.95 * el.get("size", 80), "num": 0.65 * el.get("size", 170), "underline": 8}.get(el.get("t"))
            if half and el.get("y", 0) + half > 968:      # the strip's top edge is at y=975
                warn.append(f"{o['id']}: {el['t']} \"{str(el.get('text', el.get('value', '')))[:16]}\" reaches y={el['y'] + half:.0f} and touches the caption strip (top edge 975) - move it up to y<={968 - half:.0f}")

film = {k: v for k, v in S.items() if k not in ("shots", "pauses", "tail", "score")}
if S.get("subtitles"): film["subs"] = [{"s": round(s0 * fps), "e": round(e0 * fps), "text": tx} for s0, e0, tx in subs]
if score: film["score"] = score; film["duck"] = env
film.update(fps=fps, total=round(total * fps), vo=VO, shots=out)
for k in ("teaser",):
    if k in S: film[k] = [{"src": round(tsec(c["at"]) * fps), "len": round(c["len"] * fps)} for c in S[k]]
(ROOT / "public" / FILM).write_text(json.dumps(film, ensure_ascii=False, indent=1), encoding="utf-8")
for w in warn: print("! " + w)
lens = sorted((o["e"] - o["s"]) / fps for o in out)
print(f"{len(out)} shots · {total:.1f}s · median shot {lens[len(lens) // 2]:.2f}s · {sum(1 for x in lens if x > 6) * 100 // len(lens)}% of boards over 6s · {len(subs)} caption lines -> out/subs.srt · {len(warn)} warnings")
