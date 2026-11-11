# Narration voices (English and Chinese)

Ask once per film: **language**, then for English the **accent** (US / UK / the user's cloned voice), then the voice.
Send a short audition if the user has not chosen before: the same sentence per voice, with words that reveal the
accent ("schedule, laboratory, either, water"). An audition is a paid request like any other: quote it first.

Every route ends the same way: the requests land in `build/requests/voice.json`, the user approves the quote, the
tasks are created with the Renoise tools, each result is downloaded to its `out`, and
`python3 <skill>/scripts/verify.py build/requests/voice.json` checks them before anything else runs.

## US accent: Gemini TTS (default for English)
`python3 <skill>/scripts/gen_requests.py voice-gemini narration.json --voice Charon`: one request per beat.
- 30 preset voices; the accent is always American (a language setting is ignored).
- **Everything in the prompt is read aloud**: no stage directions. Shape delivery with the voice and punctuation (full
  stops for weight, commas for flow). The request's `voice` param is the preset name.
- Then `align.py ... --tempo 1.1` (~150 wpm).

| use | voice | character |
|---|---|---|
| documentary, history, biography (default) | **Charon** | male, informative |
| hard science, lecture feel | Sadaltager | male, knowledgeable |
| news explainer | Rasalgethi | male, informative |
| crisp and clear | Iapetus | male, clear |
| investigative / news, female | Kore | female, firm |
| human stories, female | Sulafat | female, warm |
| others | the other 24 | `gen_requests.py voices` |

To redo one beat: delete `build/raw/B07.mp3`, run `voice-gemini` again (it lists only missing beats), quote, generate.

## UK accent: Seed Audio RP documentary narrator
`python3 <skill>/scripts/seed_voice.py plan narration.json build/takes --preset uk_male`, then the request loop, then
`seed_voice.py split narration.json build/takes build/raw`, then `align.py ... --tempo 1.2`.
- Presets: `uk_male`, `uk_female`, `us_male`. The voice is designed from text, so it is consistent within a take but can
  drift between takes: generate take A alone, get the user's approval, upload a ~30 s clip of it as a material, then
  re-plan with `--ref <that material id>` for the remaining takes.
- ~150 words per take (<=120 s, one task each). Whole takes keep the delivery consistent and cost several times less
  than one task per beat.
- `split` matches whisper words to the script and cuts at real pauses. Check each beat's first and last words.
- Seed Audio follows written direction (accent, tone, pace), unlike Gemini TTS.

## The user's cloned voice
`seed_voice.py plan ... --ref <material id>`: a reference audio the user uploaded and is authorised to use. Same flow
as UK. Never clone a voice from a recording the user does not own or have permission for.

## Chinese (Mandarin): Seed Audio long takes
The scripts detect Chinese from narration.json; nothing else changes in the workflow.
1. `python3 <skill>/scripts/seed_voice.py plan narration.json build/takes --ref <material id>` (the user's cloned
   voice), or `--preset zh_male` / `--preset zh_female`.
2. The request loop on `build/requests/voice.json`.
3. `python3 <skill>/scripts/seed_voice.py split narration.json build/takes build/raw`.
4. `python3 <skill>/scripts/align.py narration.json build/raw build` (tempo auto: reaches 5.6 characters/s, capped at 1.08).

- ~330 characters per take (~60 s); 5 min ≈ 1,550 characters ≈ 5 takes.
- Delivery direction goes in `narration.json -> voice.style`, written in Chinese. The fixed parts of the prompt (clone
  instruction, "no music", mixed-English handling) live in `scripts/assets/zh.json`.
- Pace: a cloned voice reads ~5.1 characters/s; the target for explainers is 5.5-6. `align.py` speeds up to reach
  `--rate` (default 5.6) but never past 1.08: beyond that the voice sounds rushed. Ask the user if they want it faster.
- English terms inside Chinese ("Agent", "Claude Code") read fine. File names and acronyms do not ("CLAUDE.md",
  "/goal", "PR"): say what the thing is in Chinese and show the literal string on screen.
- Write numbers as Chinese numerals in the narration (the way they are spoken); digits go on screen.
- Read-back is two passes (see `align.py`): only beats marked `CHECK` need a listen. Tested on 35 beats: no false
  alarms, and two deliberately wrong words were both caught.
- `split` picks the pause between two beats and verifies it by content. The classic trap is a connective followed by a
  long pause ("so, ... "): it used to end up glued to the previous beat. If `align.py` still shows words on the wrong
  side, pin that boundary: `split ... --cut B09=6.5`.
- Gemini TTS can read Chinese but its accent and pacing are not controllable; use it only if the user asks.

## Timing accuracy
Cue landings come from whisper token times (`scripts/textutil.py`). Two backends give the same output:
- **whisper.cpp** (`whisper-cli` with a ggml model; `WHISPER_MODEL=<file>`): DTW token times snapped past the pauses in
  the clip, stable to about 0.02 s. Used automatically when both are present.
- **faster-whisper** (`pip install faster-whisper`; any OS and the Renoise sandbox): word timestamps from model
  `large-v3-turbo` (`FASTER_WHISPER_MODEL` to change it; it downloads on first use).
- `VOX_WHISPER=cpp|faster` forces one.
A beat marked `TIMING?` by `align.py` had unusable timestamps and got evenly spread cues: check it in the proof.

## Fixing misreads
- English: check flagged beats (<88%); digits vs spelled-out numbers lower the score without being errors. Chinese:
  listen to `CHECK` beats only (you cannot hear: ask the user, naming the beat and time).
- If a word is mispronounced, rewrite the sentence to avoid it; pronunciation hints in Seed Audio prompts made things
  worse in testing.
