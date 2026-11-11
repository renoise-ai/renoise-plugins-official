"""Shared text helpers for the voice / subtitle tools. Two token models:
  en: a token is a word (letters and digits, lower-cased)        zh: a token is one character (CJK character, letter or digit)
`lang_of` picks zh when the narration contains CJK characters."""
import json, os, re, shutil, subprocess, tempfile, unicodedata
from pathlib import Path

HERE = Path(__file__).resolve().parent
CUE = re.compile(r"\[\[(\w+)\]\]")
TMP = Path(tempfile.gettempdir())
# Two whisper backends, same output:
#   whisper.cpp (`whisper-cli` + a ggml model file): DTW token times, the most stable cue landings.
#   faster-whisper (pip, any OS, the Renoise sandbox): word timestamps; models download on first use.
# VOX_WHISPER=cpp|faster forces one; by default whisper.cpp is used when whisper-cli and its model file exist.
WM = os.environ.get("WHISPER_MODEL") or os.path.expanduser("~/whisper.cpp/models/ggml-large-v3-turbo.bin")
FW_MODEL = os.environ.get("FASTER_WHISPER_MODEL", "large-v3-turbo")

def backend():
    want = os.environ.get("VOX_WHISPER")
    if want in ("cpp", "faster"): return want
    return "cpp" if shutil.which("whisper-cli") and Path(WM).is_file() else "faster"

def is_cjk(ch): return 0x4E00 <= ord(ch) <= 0x9FFF or 0x3400 <= ord(ch) <= 0x4DBF
def lang_of(text): return "zh" if any(is_cjk(c) for c in text) else "en"
def zh_data(): return json.loads((HERE / "assets/zh.json").read_text(encoding="utf-8"))
def strip_cues(s): return CUE.sub("", s)

def keep(ch):   # characters that count as spoken tokens
    return ch.isalnum() and not unicodedata.category(ch).startswith("P")

def tokens(text, lang):
    """Script text (cues already removed) -> list of normalised tokens."""
    if lang == "zh": return [c.lower() for c in text if keep(c)]
    return [w for w in (re.sub(r"[^a-z0-9]", "", x.lower()) for x in text.split()) if w]

def tokens_with_cues(narration, lang):
    """Narration with [[cue]] markers -> (tokens, {cue: index of the token it sits before})."""
    toks, cues = [], {}
    for piece in re.split(r"(\[\[\w+\]\])", narration):
        m = CUE.fullmatch(piece)
        if m: cues[m.group(1)] = len(toks)
        else: toks += tokens(piece, lang)
    return toks, cues

def dur(path):
    o = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(path)], capture_output=True, text=True).stdout.strip()
    return float(o) if o else 0.0

DTW = os.environ.get("WHISPER_DTW", "large.v3.turbo")   # alignment-head preset matching WHISPER_MODEL; set WHISPER_DTW=off to disable

def heard(path, lang, tag="tu", hint=None):
    """whisper token timestamps: [(token, start, end)] - words for en, characters for zh (a multi-character piece is spread evenly).
    Times come from DTW alignment (-dtw, needs flash attention off): stable to ~0.02 s. whisper's default segment
    timestamps jitter by +-0.4 s when the clip is trimmed 50 ms differently, which is too loose for cue landings.
    DTW gives the END of each token, so a token starts where the previous one ended - moved past any pause in between.
    Falls back to the segment timestamps if the DTW preset does not match the model.
    hint (Chinese only): the expected text, appended to the prompt so whisper writes the script's characters - useful as
    a second opinion on the text; its timestamps are unusable."""
    wav, base = str(TMP / f"_vox_{tag}16.wav"), str(TMP / f"_vox_{tag}")
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(path), "-ar", "16000", "-ac", "1", wav], check=True)
    if backend() == "faster": return _heard_faster(wav, lang, hint)
    cmd = ["whisper-cli", "-m", WM, "-f", wav, "-l", lang, "-ml", "1", "-ojf", "-of", base]
    if DTW != "off" and not hint: cmd += ["-nfa", "-dtw", DTW]
    if lang == "en": cmd += ["-sow"]                 # split on words; no --prompt for English (it makes whisper skip the first words)
    else: cmd += ["--prompt", zh_data()["whisper_prompt"] + (hint or "")]   # needed to get simplified characters
    subprocess.run(cmd, capture_output=True)
    segs = []
    for t in json.load(open(base + ".json", encoding="utf-8", errors="replace"))["transcription"]:
        tx = t["text"].strip()
        if not tx or tx.startswith("[") or not any(keep(c) for c in tx): continue      # skip pieces that are only punctuation
        # last spoken token of the piece: skip special tokens and pure punctuation (a comma's time lies after the pause that follows the word)
        d = [k.get("t_dtw", -1) for k in t.get("tokens", []) if not k.get("text", "").startswith("[_") and not (k.get("text", "").strip() and all(unicodedata.category(c).startswith("P") for c in k["text"].strip()))]
        segs.append((tx, t["offsets"]["from"] / 1000, t["offsets"]["to"] / 1000, d[-1] / 100 if d and d[-1] >= 0 else None))
    if segs and all(x[3] is not None for x in segs):
        sil = silences(wav, db=-35, d=0.1); prev = 0.0; timed = []
        for tx, a0, a1, end in segs:
            end = max(end, prev); start = prev
            for x, y in sil:                         # a pause that ends before this token ends: the token starts after it
                if y <= end + 0.02 and y > start and x < end: start = max(start, y)
            timed.append((tx, min(start, end), end)); prev = end
    else: timed = [(tx, a0, a1) for tx, a0, a1, _ in segs]
    out = []
    for tx, a0, a1 in timed:
        if lang == "zh":
            cs = [c.lower() for c in tx if keep(c)]
            for k, ch in enumerate(cs): out.append((ch, a0 + (a1 - a0) * k / len(cs), a0 + (a1 - a0) * (k + 1) / len(cs)))
        else:
            w = re.sub(r"[^a-z0-9]", "", tx.lower())
            if w: out.append((w, a0, a1))
    return out

_FW = None
def _heard_faster(wav, lang, hint=None):
    """faster-whisper backend: word timestamps -> the same [(token, start, end)] list as the whisper.cpp path."""
    global _FW
    if _FW is None:
        from faster_whisper import WhisperModel
        _FW = WhisperModel(FW_MODEL, device="auto", compute_type="int8")
    prompt = None if lang == "en" else zh_data()["whisper_prompt"] + (hint or "")
    segs, _ = _FW.transcribe(wav, language=lang, word_timestamps=True, initial_prompt=prompt,
                             condition_on_previous_text=False, vad_filter=False, beam_size=5)
    out, prev = [], 0.0
    for sg in segs:
        for w in sg.words or []:
            a1 = max(float(w.end), prev); a0 = min(max(float(w.start), prev), a1); prev = a1
            if lang == "zh":
                cs = [c.lower() for c in w.word if keep(c)]
                for k, ch in enumerate(cs): out.append((ch, a0 + (a1 - a0) * k / len(cs), a0 + (a1 - a0) * (k + 1) / len(cs)))
            else:
                x = re.sub(r"[^a-z0-9]", "", w.word.lower())
                if x: out.append((x, a0, a1))
    return out

def silences(path, db=-38, d=0.12, ss=None, to=None):
    cmd = ["ffmpeg", "-hide_banner"] + (["-ss", f"{ss:.3f}", "-to", f"{to:.3f}"] if ss is not None else []) + ["-i", str(path), "-af", f"silencedetect=n={db}dB:d={d}", "-f", "null", "-"]
    r = subprocess.run(cmd, capture_output=True, text=True).stderr
    s = [float(x) for x in re.findall(r"silence_start: ([\d.]+)", r)]; e = [float(x) for x in re.findall(r"silence_end: ([\d.]+)", r)]
    off = ss or 0.0
    return [(a + off, b + off) for a, b in zip(s, e)]
