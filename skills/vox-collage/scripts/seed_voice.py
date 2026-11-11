#!/usr/bin/env python3
"""Narration via Renoise seed-audio-1.0 in long takes, split back into beats. English (UK/US presets, or a cloned voice)
and Chinese (cloned voice or text-designed presets); the language is detected from narration.json.

Usage (from the film project root):
  python3 <skill>/scripts/seed_voice.py plan  narration.json build/takes [--preset uk_male] [--ref <material id>] [--words 150] [--chars 330]
      -> build/takes/take<A..>.txt + plan.json + build/requests/voice.json (one seed-audio request per take, out = takeA.mp3 ...)
      The agent quotes that batch, waits for the user's yes, creates the tasks with the Renoise tools, downloads each
      take to its `out`, and runs verify.py on the batch.
  python3 <skill>/scripts/seed_voice.py split narration.json build/takes build/raw [--cut B09=6.5,B30=25.67]
Then run align.py on build/raw.

Presets: uk_male, uk_female, us_male (English) · zh_male, zh_female (Chinese, assets/prompts/zh.json). --ref clones the
speaker of a reference audio the user uploaded to Renoise (then the preset is ignored). Only clone a voice the user
owns or is authorised to use. Delivery direction comes from
narration.json -> voice.style (free text, in the narration language).

Why long takes: one seed-audio task is priced the same for any length up to 120 s, so ~60 s per take is several times
cheaper than one task per beat, and the delivery stays consistent. seed-audio follows written directions.

How split finds a beat boundary: whisper token times over the whole take -> match to the script -> take the real pause
(silencedetect) closest to the gap between the last token of one beat and the first token of the next -> verify by
content: listen to 1.8 s on each side of the cut and step to the neighbouring pause when words sit on the wrong side
(a connective such as "so," followed by a long pause is the classic trap). VOX_DEBUG=1 prints every decision.
--cut pins a boundary by hand: "B09=6.5" = B09 starts 6.5 s into its take (use when the read-back in align.py shows words on the
wrong side of a boundary)."""
import difflib, json, os, subprocess, sys, tempfile
from pathlib import Path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from textutil import lang_of, tokens, strip_cues, heard, silences, dur, zh_data
from gen_requests import write as write_requests, req, SEED

HERE = Path(__file__).resolve().parent
PRESETS = {
    "uk_male": "A male British documentary narrator with a clear Received Pronunciation (standard Southern British English) accent, like a BBC documentary voice-over: calm, authoritative, warm, measured but brisk pace, about 150 words per minute.",
    "uk_female": "A female British documentary narrator with a clear Received Pronunciation (standard Southern British English) accent, like a BBC documentary voice-over: calm, authoritative, warm, measured but brisk pace, about 150 words per minute.",
    "us_male": "A male American documentary narrator with a neutral General American accent: confident, curious, brisk explainer pace.",
}
TAIL = "Clean dry studio voice, no background music, no sound effects, no room noise. Read the paragraphs in order, one after another, with a short natural pause between paragraphs."

def arg(k, d=None): return sys.argv[sys.argv.index(k) + 1] if k in sys.argv else d

def load(narr):
    N = json.loads(Path(narr).read_text(encoding="utf-8"))
    beats = [(b["id"], strip_cues(b["narration"]).strip()) for b in N["beats"]]
    return N, beats, lang_of("".join(t for _, t in beats))

def head(lang, preset, ref, style):
    if lang == "zh":
        Z = zh_data()
        who = Z["clone_head"] if ref else Z["presets"][preset if preset in Z["presets"] else "zh_male"]
        txt = f"{who}{style or Z['default_style']}{Z['mixed_english']}{Z['tail']}\n{Z['say']}\n"
    else:
        who = "Single narrator. Use exactly the voice, timbre and rhythm of the speaker in reference audio 1." if ref else f"Single narrator, one speaker only. {PRESETS[preset if preset in PRESETS else 'uk_male']}"
        txt = f"{who} {style + ' ' if style else ''}{TAIL}\nThe narrator says exactly this, word for word, nothing added:\n"
    return (f"@material:{ref}\n" if ref else "") + txt

def plan(narr, tdir):
    tdir = Path(tdir); tdir.mkdir(parents=True, exist_ok=True)
    N, beats, lang = load(narr)
    voice = N.get("voice") or {}
    ref = arg("--ref") or str(voice.get("ref", "")).replace("material:", "") or None
    preset = arg("--preset", voice.get("preset") or ("zh_male" if lang == "zh" else "uk_male"))
    limit = int(arg("--chars", 330)) if lang == "zh" else int(arg("--words", 150))
    size = lambda t: len(tokens(t, lang))
    groups, cur, n = [], [], 0
    for bid, txt in beats:
        w = size(txt)
        if cur and n + w > limit: groups.append(cur); cur, n = [], 0
        cur.append((bid, txt)); n += w
    groups.append(cur)
    H = head(lang, preset, ref, voice.get("style"))
    P = []
    for i, g in enumerate(groups):
        k = chr(65 + i)
        (tdir / f"take{k}.txt").write_text(H + "\n".join(t for _, t in g) + "\n", encoding="utf-8")
        P.append({"take": k, "beats": [b for b, _ in g], "size": sum(size(t) for _, t in g)})
    (tdir / "plan.json").write_text(json.dumps({"lang": lang, "preset": preset, "ref": ref, "takes": P}, indent=1), encoding="utf-8")
    rate = 5.2 if lang == "zh" else 2.5
    for p in P: print(f"take{p['take']}: {p['beats'][0]}-{p['beats'][-1]}  {p['size']} {'chars' if lang == 'zh' else 'words'}  ~{p['size'] / rate:.0f}s")
    print(f"{lang} · {'clone of material ' + ref if ref else preset} · {len(P)} takes (one seed-audio-1.0 task each, up to 120 s)")
    refs = [{"material": ref, "role": "reference_audio"}] if ref else []
    write_requests("voice", [req(f"take{p['take']}", SEED, "audio", (tdir / f"take{p['take']}.txt").read_text(encoding="utf-8"),
                                 tdir / f"take{p['take']}.mp3", {}, refs) for p in P],
                   "seed-audio follows the written direction in the prompt. One task per take keeps the delivery consistent.")

def _leak(clip_tokens, script_tokens, at_end, lang):
    """True when script_tokens (the start of the next beat, or the end of the previous one) are audible at the edge of a clip."""
    if not clip_tokens or not script_tokens: return False
    need = 2 if lang == "zh" else 1
    m = difflib.SequenceMatcher(None, clip_tokens, script_tokens, autojunk=False)
    for i, j, n in m.get_matching_blocks():
        if n < need or (lang == "en" and n == 1 and len(clip_tokens[i]) < 4): continue
        if at_end and i + n >= len(clip_tokens) - 1 and j <= 1: return True              # clip ends with the first tokens of the next beat
        if not at_end and i <= 1 and j + n >= len(script_tokens) - 1: return True       # clip starts with the last tokens of the previous beat
    return False

def _listen(take, a, b, lang):
    w = os.path.join(tempfile.gettempdir(), "_vox_svw.wav")
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", f"{max(0, a):.3f}", "-to", f"{b:.3f}", "-i", str(take), "-c:a", "pcm_s16le", w], check=True)
    return [x[0] for x in heard(w, lang, "svl")]

def split(narr, tdir, rdir):
    tdir, rdir = Path(tdir), Path(rdir); rdir.mkdir(parents=True, exist_ok=True)
    N, beats, lang = load(narr); text = dict(beats)
    P = json.loads((tdir / "plan.json").read_text(encoding="utf-8"))
    over = {k: float(v) for k, v in (x.split("=") for x in (arg("--cut") or "").split(",") if x)}
    edge = 6 if lang == "zh" else 3          # script tokens on each side used to verify a boundary
    dbg = os.environ.get("VOX_DEBUG")
    for p in P["takes"]:
        take = tdir / f"take{p['take']}.mp3"; D = dur(take)
        T = [tokens(text[b], lang) for b in p["beats"]]
        A, own = [], []
        for bi, t in enumerate(T): A += t; own += [bi] * len(t)
        H = heard(take, lang, "sv")
        st, en = [None] * len(A), [None] * len(A)
        sm = difflib.SequenceMatcher(None, A, [h[0] for h in H], autojunk=False)
        for i, j, n in sm.get_matching_blocks():
            for k in range(n): st[i + k], en[i + k] = H[j + k][1], H[j + k][2]
        sil = [(x, y) for x, y in silences(take) if x > 0.2 and y < D - 0.2]
        mids = [(x + y) / 2 for x, y in sil]
        cuts, notes = [0.0], []
        for bi in range(len(p["beats"]) - 1):
            nb = p["beats"][bi + 1]
            if nb in over: cuts.append(over[nb]); continue
            last = max((en[k] for k in range(len(A)) if own[k] == bi and en[k] is not None), default=None)
            first = min((st[k] for k in range(len(A)) if own[k] == bi + 1 and st[k] is not None), default=None)
            if last is None or first is None:
                sys.exit(f"take{p['take']}: cannot find the boundary before {nb} - a whole sentence may be missing; listen to the take")
            lo, hi = min(last, first), max(last, first)
            # 1) the pause closest to the gap between the last token of this beat and the first token of the next (ties: the longer pause)
            gap = lambda k: (max(0.0, sil[k][0] - hi, lo - sil[k][1]), -(sil[k][1] - sil[k][0]))
            cand = sorted((k for k in range(len(sil)) if gap(k)[0] < 1.5), key=gap)
            if not cand:
                cuts.append((lo + hi) / 2); notes.append(f"no clear pause before {nb}: cut at the estimate, listen to it"); continue
            k = cand[0]
            # 2) verify by content, not by timestamps (whisper times drift in long takes and short windows can hallucinate):
            #    listen to 1.8 s before and after the cut; if the next beat's first tokens are before it, or this beat's last tokens after it, step to the neighbouring pause
            for _ in range(3):
                c = mids[k]
                before, after = _listen(take, max(cuts[-1], c - 1.8), c, lang), _listen(take, c, min(D, c + 1.8), lang)
                fwd, back = _leak(before, T[bi + 1][:edge], True, lang), _leak(after, T[bi][-edge:], False, lang)
                if dbg: print(f"  {nb}: try {c:.2f}  before=...{''.join(before[-8:]) if lang == 'zh' else ' '.join(before[-4:])} | after={''.join(after[:8]) if lang == 'zh' else ' '.join(after[:4])}...  leak fwd={fwd} back={back}")
                if fwd and not back and k > 0 and mids[k - 1] > cuts[-1] + 0.3: k -= 1
                elif back and not fwd and k + 1 < len(sil): k += 1
                else: break
            cuts.append(mids[k])
        cuts.append(D)
        for bi, b in enumerate(p["beats"]):
            subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", f"{cuts[bi]:.3f}", "-to", f"{cuts[bi + 1]:.3f}", "-i", str(take), "-c:a", "libmp3lame", "-q:a", "2", str(rdir / f"{b}.mp3")], check=True)
        print(f"take{p['take']}: match {sm.ratio():.0%}  cuts " + " ".join(f"{b}={c:.2f}" for b, c in zip(p["beats"][1:], cuts[1:-1])))
        for n in notes: print("  ! " + n)

if __name__ == "__main__":
    c = sys.argv[1] if len(sys.argv) > 1 else ""
    if c == "plan": plan(sys.argv[2], sys.argv[3])
    elif c == "split": split(sys.argv[2], sys.argv[3], sys.argv[4])
    else: sys.exit(__doc__)
