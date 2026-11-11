# Pitfalls (hit while making the Tesla, agent-manager and cough films, 2026-11)

## Downloads and services
- Downloads of generated media can arrive truncated (an mp3 decoding to 3 s, a GIF "image file is truncated", an mp4
  with 100 of 240 frames). Run `verify.py` on every batch; download again whatever it marks BAD, and regenerate only if
  a fresh download is still bad.
- Commons API rate-limits bursts: pause 3-6 s between calls. Multi-word searches return scanned PDFs: add
  `filetype:bitmap` and keep the query to 2-4 words; `search --full` prints untruncated titles for `get`.
- python.org Python builds on macOS have no CA store: `commons.py` sets `SSL_CERT_FILE` from certifi when it is installed.
- A Lyria task can fail; rewrite the brief and resubmit.
- Renoise images are opaque: props are drawn on pure green and keyed (`images_key.py`, `greenkey.py`), never promised
  as transparent PNGs.
- Optional Codex route: `codex exec` hangs without stdin closed and cannot write into the project, so
  `codex_batch.py` copies from `~/.codex/generated_images/<session>/`.

## Voice
- Gemini TTS reads stage directions aloud and ignores accent; Seed Audio follows directions.
- A preset (text-designed) Seed Audio voice can sound different from take to take. Approve take A, upload a ~30 s
  clip of it, and clone it with `--ref` for the other takes.
- Pronunciation hints in Seed Audio prompts made misreads worse: rewrite the sentence instead.
- whisper with a prompt skips the first words of English clips (alignment drifted to 17%): English aligns without one.
- English long takes: whisper turns "sixty thousand dollars" into "$60,000"; a lower match % is not an error.
- Long takes: a connective followed by a long pause ("so, ...") used to be cut onto the wrong beat; `seed_voice.py split`
  verifies each cut by content. `VOX_DEBUG=1` prints the decisions; `--cut B09=6.5` pins one by hand.
- A re-listen of a 4 s window can hallucinate a repeat of the last phrase: never trust timestamps from one short
  window; verify by what is said on each side of the cut.
- whisper.cpp's default word timestamps jitter by ±0.4 s when the same clip is trimmed 50 ms differently (cues landed
  early or late at random). With whisper.cpp the scripts use DTW token times (`-dtw large.v3.turbo -nfa`; flash
  attention must be off or DTW is silently disabled) and move word starts past detected pauses: stable to ~0.02 s.
  `WHISPER_DTW` sets the preset for another model. faster-whisper's word timestamps are used as they come.
- whisper with the script as a prompt returns the right Chinese characters but useless timestamps (most characters
  piled on the last second; cues landed 5 s late). Timings come from the blind pass only; resolve.py's "element falls
  outside the shot" warnings are the alarm for this.
- Chinese read-back without a hint flags homophones and numerals on every other beat; with the script as a hint it can
  hide real misreads. `align.py` uses both passes. Without `pypinyin` installed, the homophone list in
  `scripts/assets/zh.json` is the fallback; extend it when a homophone raises a false alarm.

## Script
- An article adapted point by point becomes a slideshow (the agent-manager film: a strong 40 s hook, then ten habits
  counted off). Use the `essay` skeleton in `references/narrative.md` and run `lint_script.py` first.
- The strongest fact sat at 80% of that film. It belongs at 40-60% and in the teaser.

## Engine
- Cue names must start with a letter (`[[y1903]]`).
- Stamps use multiply blend: invisible on dark boards unless `blend="normal"`.
- Long labels typing 2 frames per character were still half-typed at the cut: Label finishes within 24 frames.
- Keyed loop frames must keep one size (`gif2frames.py --key`, or `greenkey.py --nocrop`), or the loop jumps.
- Sounds must be mounted as `Sequence from={at}`; an `<Audio>` rendered only on the entry frame plays for one frame.
- Background music must `loop` if shorter than the film (only when using a single bed track).
- Remotion `Freeze` did not work for proof sheets; Proof uses `<Sequence from={f - target}>`.
- Wan first frames: keep the photo fully inside 1280x720; anything cropped stays cropped.
- Teaser clips are cut blind from the main timeline: a clip taken at the last word of a beat ran into the next (empty)
  board. resolve.py warns; choose a moment with board time left.
- With burned-in captions, a label centred at y=950 still touches the strip (its bottom edge is ~35 px lower); keep
  text centres at y <= 900.
- Fonts: the look is tuned on macOS fonts (Georgia, Songti SC, American Typewriter). Linux falls back to Noto Serif /
  Noto Sans CJK (install `fonts-noto-cjk` for Chinese films); check the proof sheet for missing glyphs.
- Re-running `new_film.py <project>` refreshes `src/` from the skill's engine (film.json, shots and assets are untouched).

## Finishing
- Use `finish.py`: the true peak after AAC varied by 2.5 dB between two encodes with the same limiter setting (-1.9 and
  -0.1 dBTP), so it is measured and the limiter lowered until it passes.
- Loudness: measure the raw render, apply `volume` + `alimiter` once from the raw audio. Re-encoding AAC on AAC pushed
  peaks above 0 dBFS.
- The 30 fps grain makes files huge at crf 20 (~900 MB / 5 min); deliver at crf 27 (~150 MB).
