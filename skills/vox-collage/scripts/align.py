#!/usr/bin/env python3
"""Per-beat narration clips -> trimmed, tempo-adjusted, token-aligned -> <out>/narration.wav + <out>/timings.json.
English and Chinese (detected from narration.json). resolve.py reads timings.json; the per-token times also drive subtitles.

Usage: python3 align.py narration.json raw_dir out_build [--tempo 1.1|auto] [--rate 5.6] [--gap 0.2] [--lead 0.3] [--par 3]
  raw_dir/<B01>.mp3|wav ...  one clip per beat (tts_task.py beats, or seed_voice.py split)
  --tempo  speed-up factor. Defaults: English 1.1 · Chinese "auto" = reach --rate characters per second (default 5.6),
           never slower than 1.0 or faster than 1.08. UK seed-audio takes usually want 1.2.
  --gap    silence between beats (s) · --lead silence before the first beat (s)
Read-back: every clip is transcribed and compared with the script token by token.
  English: one pass, no prompt; beats under 88% are flagged, unless every difference is a number written as digits.
  Chinese: two passes. The blind pass gives the timings and the check. The hinted pass (script in the prompt) is used
           for text only: a difference in the blind pass is cleared when the hinted pass heard the script there
           (homophones, numerals written as digits, names) or when the characters sound the same
           (assets/prompts/zh.json "homophones", pypinyin if installed). What both passes got wrong is marked CHECK:
           listen, then rewrite the sentence and re-voice. Hinted timestamps are never used (they collapse).
  Both: a beat whose timestamps look broken is marked TIMING? and its cues are spread evenly."""
import difflib, json, os, subprocess, sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from textutil import lang_of, tokens_with_cues, strip_cues, heard, dur, zh_data, is_cjk

a = sys.argv
if len(a) < 4: sys.exit(__doc__)
opt = lambda k, d: a[a.index(k) + 1] if k in a else d
N = json.loads(Path(a[1]).read_text(encoding="utf-8")); RAW = Path(a[2]); OUT = Path(a[3])
lang = lang_of("".join(b["narration"] for b in N["beats"]))
gap, lead, par = float(opt("--gap", 0.2)), float(opt("--lead", 0.3)), int(opt("--par", 3))
tempo_arg = opt("--tempo", "auto" if lang == "zh" else "1.1")
(OUT / "audio").mkdir(parents=True, exist_ok=True)
# English: hard trim (the pacing the US/UK films were tuned with). Chinese: keep 50-80 ms so soft initials and finals are not clipped.
TRIM = ("silenceremove=start_periods=1:start_threshold=-45dB:start_silence=0.05,areverse,silenceremove=start_periods=1:start_threshold=-45dB:start_silence=0.08,areverse" if lang == "zh"
        else "silenceremove=start_periods=1:start_threshold=-45dB,areverse,silenceremove=start_periods=1:start_threshold=-45dB,areverse")
NUMW = set("zero one two three four five six seven eight nine ten eleven twelve thirteen fourteen fifteen sixteen seventeen eighteen nineteen twenty thirty forty fifty sixty seventy eighty ninety hundred thousand million billion trillion and a an point percent dollars dollar cents first second third half oh".split())

def src_of(bid):
    for ext in ("mp3", "wav", "m4a"):
        if (RAW / f"{bid}.{ext}").exists(): return RAW / f"{bid}.{ext}"
    sys.exit(f"missing clip for {bid} in {RAW}")

def trim(bid, tempo):
    out = OUT / "audio" / f"{bid}.wav"
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(src_of(bid)), "-af", TRIM + (f",atempo={tempo}" if abs(tempo - 1) > 1e-3 else ""), "-ar", "48000", "-ac", "1", str(out)], check=True)
    return out

ids = [b["id"] for b in N["beats"]]
script = {b["id"]: tokens_with_cues(b["narration"], lang) for b in N["beats"]}
if tempo_arg == "auto":
    with ThreadPoolExecutor(par) as ex: clips = list(ex.map(lambda b: trim(b, 1.0), ids))
    speech = sum(dur(c) for c in clips); n = sum(len(script[b][0]) for b in ids)
    target = float(opt("--rate", 5.6 if lang == "zh" else 2.6))
    tempo = round(min(1.08, max(1.0, target / (n / speech))), 3)
    print(f"measured {n / speech:.2f} {'chars' if lang == 'zh' else 'words'}/s -> tempo {tempo}")
else: tempo = float(tempo_arg)

# homophone groups for the Chinese read-back
GROUPS = [set(g) for g in zh_data()["homophones"]] if lang == "zh" else []
try: from pypinyin import lazy_pinyin
except Exception: lazy_pinyin = None
def same_sound(x, y):
    if len(x) != len(y): return False
    for p, q in zip(x, y):
        if p == q: continue
        if lazy_pinyin and lazy_pinyin(p) == lazy_pinyin(q): continue
        if any(p in g and q in g for g in GROUPS): continue
        return False
    return True

def work(bid):
    wav = trim(bid, tempo)
    toks, cues = script[bid]
    H = heard(wav, lang, "al" + bid)                      # blind pass: the check
    sm = difflib.SequenceMatcher(None, toks, [h[0] for h in H], autojunk=False)
    hinted = set()
    if lang == "zh":                                       # hinted pass: text only, used to clear read-back differences.
        Hp = heard(wav, lang, "ah" + bid, hint=strip_cues(B[bid]["narration"]))   # its timestamps are NOT usable: with the script in the prompt whisper piles most characters onto the last second
        for i, j, n in difflib.SequenceMatcher(None, toks, [h[0] for h in Hp], autojunk=False).get_matching_blocks(): hinted.update(range(i, i + n))
    t0 = [None] * len(toks)
    for i, j, n in sm.get_matching_blocks():
        for k in range(n): t0[i + k] = H[j + k][1]
    D = dur(wav)
    got = [t for t in t0 if t is not None]
    # timing sanity: tokens piled on one instant, or a jump over 45% of the clip, means the timestamps are broken -> spread evenly and say so
    broken = len(toks) > 6 and (len(got) < len(toks) * 0.5 or max(got.count(t) for t in set(got)) > len(toks) * 0.25 or max(b2 - a2 for a2, b2 in zip([0.0] + got, got + [D])) > D * 0.45)
    if broken: t0 = [D * i / len(toks) for i in range(len(toks))]
    # fill unmatched tokens by interpolation between matched neighbours
    known = [(-1, 0.0)] + [(i, t) for i, t in enumerate(t0) if t is not None] + [(len(toks), D)]
    for (i0, a0), (i1, a1) in zip(known, known[1:]):
        for i in range(i0 + 1, i1): t0[i] = a0 + (a1 - a0) * (i - i0) / (i1 - i0)
    diffs = []
    for tag, i1, i2, j1, j2 in sm.get_opcodes():
        if tag == "equal": continue
        x, y = "".join(toks[i1:i2]) if lang == "zh" else " ".join(toks[i1:i2]), "".join(h[0] for h in H[j1:j2]) if lang == "zh" else " ".join(h[0] for h in H[j1:j2])
        ok = (lang == "zh" and ((tag == "replace" and same_sound(x, y)) or (i2 > i1 and all(i in hinted for i in range(i1, i2))) or (i2 == i1 and len(y) <= 2))) or \
             (lang == "en" and i2 > i1 and any(c.isdigit() for c in y) and all(t in NUMW for t in toks[i1:i2]))      # "sixty thousand dollars" heard as "60000": same words, written as digits
        diffs.append((x, y, ok))
    return bid, wav, D, toks, cues, t0, sm.ratio(), diffs, broken

B = {b["id"]: b for b in N["beats"]}
with ThreadPoolExecutor(par) as ex: res = list(ex.map(work, ids))

timings, cursor, parts, check = {}, lead, [], []
for bid, wav, D, toks, cues, t0, ratio, diffs, broken in res:
    cue_abs = {c: round(cursor + max(0.0, (t0[i] if i < len(t0) else D) - 0.05), 3) for c, i in cues.items()}
    timings[bid] = {"file": f"audio/{bid}.wav", "text": strip_cues(B[bid]["narration"]), "start": round(cursor, 3), "end": round(cursor + D, 3), "duration": round(D, 3),
                    "cues": cue_abs, "align": round(ratio, 3), "tok": [round(cursor + t, 3) for t in t0]}
    real = [d for d in diffs if not d[2]]
    bad = (ratio < 0.88 and bool(real)) if lang == "en" else bool(real)
    if bad: check.append(bid)
    rate = len(toks) / D
    line = f"{'CHECK' if bad else '     '} {bid} {D:5.2f}s  {rate:.2f}/s  match {ratio:.0%}  cues {len(cues)}"
    if real and (lang == "zh" or bad): line += "  heard: " + ", ".join(f"{x or '-'}>{y or '-'}" for x, y, _ in real[:4])
    if any(d[2] for d in diffs): line += f"  ({sum(1 for d in diffs if d[2])} cleared)"
    elif lang == "en" and real and not bad: line += "  heard: " + ", ".join(f"{x or '-'}>{y or '-'}" for x, y, _ in real[:3])
    if broken: line += "  TIMING? cues spread evenly - check this beat's cue landings in the proof"
    print(line)
    parts.append((cursor, wav)); cursor += D + gap

total = cursor - gap + 0.5
inputs, filt = [], []
for i, (t, w) in enumerate(parts):
    inputs += ["-i", str(w)]; filt.append(f"[{i}]adelay={int(t * 1000)}|{int(t * 1000)}[d{i}]")
fc = ";".join(filt) + ";" + "".join(f"[d{i}]" for i in range(len(parts))) + f"amix=inputs={len(parts)}:normalize=0,apad=whole_dur={total}[o]"
subprocess.run(["ffmpeg", "-v", "error", "-y", *inputs, "-filter_complex", fc, "-map", "[o]", "-ar", "48000", "-ac", "1", str(OUT / "narration.wav")], check=True)
(OUT / "timings.json").write_text(json.dumps({"voice": N.get("voice"), "lang": lang, "tempo": tempo, "beats": timings, "total": round(total, 3)}, ensure_ascii=False, indent=1), encoding="utf-8")
print(f"total {total:.1f}s -> {OUT}/timings.json · listen to: {', '.join(check) or 'nothing flagged'}")
