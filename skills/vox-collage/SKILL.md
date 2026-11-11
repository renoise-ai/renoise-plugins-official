---
name: vox-collage
description: >
  Vox-style paper-collage explainer films: a topic, an article or a life story becomes a 1-10 minute narrated
  documentary where every line is sourced, built from black-and-white halftone cut-outs on aged paper (archival
  public-domain photos and generated props), stepped 12 fps stop-motion, red string, typewriter labels, rubber stamps,
  halftone number cards, page-push transitions, a per-chapter music score that ducks under the narration, and an
  opening of cover frame, highlight teaser and hook. The script is built on one of four story skeletons (life, essay,
  mystery, mechanism) and checked for hook, scenes, re-hooks, midpoint twist and callback before any voice is made.
  English narration (US voices from Gemini TTS, a UK narrator from Seed Audio) or Chinese (a preset or the user's
  authorised cloned voice), with captions. Use for "Vox style video", "paper collage explainer", "collage
  documentary", "Johnny Harris style", "history / biography / money / science explainer with collage", "turn this
  article or thread into a collage video", "faceless YouTube explainer". Needs a shell (the Renoise sandbox or a local
  one). Not for talking-head videos, product promos or course series.
metadata:
  author: renoise
  version: 1.0.0
  category: video-production
  tags: [video, explainer, documentary, collage, remotion, narration, captions]
---

# Vox Collage Explainer

One topic in, one finished explainer out: `cover + teaser + hook -> title card -> chapters`, every narration line tied
to a fact with a source, 1080p MP4 + cover JPG + captions.

> Paths: `<skill>` is this folder (the one holding SKILL.md); replace `<skill>/scripts/…` with its absolute path when
> you run a command. On the Renoise sandbox, loading the skill puts the folder there and says where; on a local shell
> it is the plugin's skill folder. Every script runs from the film project root. Never ask the user for sandbox paths
> or to run anything themselves.

**Runtime.** The film is built with code: Python scripts, ffmpeg, whisper and a Remotion engine. It needs a shell:
the Renoise sandbox (Director Mode) or a local shell where `python3 <skill>/scripts/doctor.py` passes; install what it
marks ✗. Without a shell, stop before any paid step: offer the script and fact sheet, and say in one line that the
sandbox builds the film. Generation (voice, images, GIF loops, music, video shots) always goes through the host's
own Renoise tools; the scripts only write the requests and check the downloads.

**Spending.** Follow the host's estimate and approval policy: before each batch, quote it with the Renoise cost
estimate and wait for the user's clear yes in the conversation. Never swap in a paid option the user did not choose.
Read `../model-routing/SKILL.md` and the live model details before writing prompts or parameters.

Worked examples (in `<skill>/scripts/examples/`): `tesla/` (5:14, English, US voice, `life` skeleton) and
`agent-manager-zh/` (5:02, Chinese, an article adaptation; its README explains what the lint says about it).
Research behind the look and pacing: `references/research.md`. Story skeletons and retention rules: `references/narrative.md`.

## The look (do not drift from it)

- Base: aged cream paper plates (`#E8DCC4`) with torn map / newspaper / patent fragments at the edges, centre left empty.
- Subjects: **black-and-white halftone cut-outs** with an uneven scissor-cut off-white border and a soft drop shadow.
  People = real archival photos (Wikimedia Commons, public domain) run through `halftone.py`; objects and scenes =
  generated images on pure green, keyed with `greenkey.py`.
- Colour only on hand-made marks: red stamps, red string, tape, handwritten notes, highlighter. Max 2 accents per board.
- Motion: elements enter on a 12 fps step (slap, slide, pop, drop), boil slightly every 3 frames; the camera push is smooth.
- Hard cut between boards by default; page push only at chapter or topic changes.
- One recurring character or prop (the motif) returns in every chapter; the last board echoes the first.
- Details and numbers: `references/style.md`.

## Workflow

### 0 · Confirm with the user (one round of questions, recommended option first)
1. **Topic, length, language** (default 5 min; ~150 spoken words or ~330 Chinese characters per minute).
2. **Story skeleton** (`references/narrative.md`): `life` (a person or company) · `essay` (an article, an argument,
   "N lessons", told through one invented protagonist, never counted off) · `mystery` (why did X happen) ·
   `mechanism` (follow one unit through a system). Recommend one from the source material and say why in a line.
3. **Narration voice** (`references/voice.md`):
   - English, US accent: Gemini TTS, 30 preset voices (default **Charon**, male documentary), one task per beat.
   - English, UK accent: Seed Audio RP narrator (`uk_male` / `uk_female`), long takes of up to 120 s.
   - Chinese: a preset (`zh_male` / `zh_female`) or the user's cloned voice from a reference audio they uploaded and
     are authorised to use (Seed Audio long takes).
   Send a short audition first if the user has not picked before.
4. **Captions**: burned in (expected on Chinese platforms) · switchable track (YouTube) · none.
5. **Moving shots, multi-select, never default to paid ones**: code animation (free, always on) · GPT Image 2.6 GIF
   loops · Wan or Seedance video shots. See `references/motion.md`.
6. Quote the total (voice + images + GIFs + video + about one music cue per chapter) with the cost estimate and wait
   for a clear yes before spending.

### 1 · Research and script
- Run fact research first (a subagent works well): 40-60 facts, each with date or number, source URL, a short original
  quote and a confidence, plus a **myths list** (popular claims that are false: good twists) and a **do-not-use list**.
  Adapting an article: the article is the spine, but check what it says about third parties against the primary
  source, and credit the argument to its author on screen (hook and end card).
- Write `narration.json` on the chosen skeleton: `"archetype"`, `"motif"`, `"target_seconds"`; beats `B01..Bnn`,
  1-3 sentences each (<=15 s), `[[cue]]` markers where visuals land (one per ~2.5 s; names start with a letter), a
  `fact` on every beat, `"chapter"` on the first beat of each chapter, and `"role"` tags
  (`hook number twist question scene rehook midtwist callback`).
- The rules that matter most: every chapter **opens on a scene** and **closes on a re-hook**; the strongest fact sits at
  **40-60%** (and is glimpsed in the teaser), not at the end; the ending **calls back** to the opening image; no
  ordinals in the narration; end on a quote or an open question, not "subscribe".
- Title card after the main question: `pauses: {"B05": 3.0}`.
- Write numbers the way they are spoken; avoid hard-to-pronounce words rather than adding pronunciation hints.
- **Lint before voice**: `python3 <skill>/scripts/lint_script.py narration.json --target 300`. Fix every `E`; fix each
  `W` or note why not. Show the user the script with the lint's chapter table and get approval before step 3.

### 2 · Project
`python3 <skill>/scripts/new_film.py <project dir>` copies the engine, textures and sound effects, links the scripts
as `<project>/tools`, and installs Remotion with npm (re-run it to refresh `src/` after a skill update). Work from the
project root from here on.

### 3 · Voice
Every paid step below follows one loop: a script writes `build/requests/<batch>.json` → quote it → the user says yes →
create the tasks with the Renoise tools (map each request's `params` to the model's live parameter names and pass its
`references` as materials in the named role) → download each result to its `out` path →
`python3 <skill>/scripts/verify.py build/requests/<batch>.json`. Downloads can arrive truncated: download again
whatever verify marks BAD, and regenerate only if a fresh download is still bad.
- English, US: `python3 <skill>/scripts/gen_requests.py voice-gemini narration.json --voice Charon` (one request per
  beat to `build/raw/<beat>.mp3`; `gen_requests.py voices` lists the 30 voices).
- English UK and Chinese: `python3 <skill>/scripts/seed_voice.py plan narration.json build/takes --preset uk_male`
  (Chinese: `--preset zh_male`, or `--ref <material id>` for the user's cloned voice). After the takes are verified:
  `python3 <skill>/scripts/seed_voice.py split narration.json build/takes build/raw` (cuts verified by content).
  A designed preset voice can drift between takes: generate take A first, let the user approve it, then upload a
  ~30 s clip of it and plan the remaining takes with `--ref` so the whole film keeps one voice.
- Then, for every route: `python3 <skill>/scripts/align.py narration.json build/raw build` trims, sets the tempo,
  aligns every token, places the cues and reads the voice back → `build/narration.wav` + `build/timings.json`.
  Tempo: English `--tempo 1.1` (UK takes 1.2); Chinese is automatic (5.6 characters/s, at most 1.08).
- English: re-voice any beat flagged below 88% after checking it is not just digits vs spelled-out numbers.
  Chinese: listen only to beats marked `CHECK` (both transcription passes disagreed with the script); rewrite and
  re-voice those.

### 4 · Assets
- **Plates and props**: write `codex_jobs.json` (style prefixes in `references/style.md`, example in
  `scripts/examples/tesla/codex_jobs.json`), then `python3 <skill>/scripts/gen_requests.py images codex_jobs.json`
  (GPT Image 2.6, plates 16:9, props 1:1 on pure green). After the downloads verify,
  `python3 <skill>/scripts/images_key.py codex_jobs.json` scales the plates and keys the props into `public/img/`.
  About 8 plates and 20-45 props, including 4-6 poses of the motif character. Where the user has the Codex CLI on a
  local machine and asks for it, `scripts/codex_batch.py` generates the same jobs on their own plan instead.
- **Archival photos**: `python3 <skill>/scripts/commons.py search "filetype:bitmap typing pool" [--full]`, then
  `commons.py get "File:..." name` (logs the license in `assets/photo/credits.json`; public domain or CC0 for faces),
  `mask.py assets/photo/name.jpg build/masks/name.png` (rembg), and
  `halftone.py assets/photo/name.jpg public/photo/name.png --mask build/masks/name.png`.
- **Living people**: no generated likenesses. Use quote cards, name labels, objects, their own published chart or
  cover as a halftone "print"; a CC-licensed photo only with on-screen credit.
- **GIF loops, video shots** (only if chosen): `references/motion.md`.
- Show the user a contact sheet of plates and props before building boards when the topic is new.

### 5 · Music (designed per film, never a default track)
Write one Lyria brief per chapter in `music/<cue>.txt` (`references/music.md`, examples in
`scripts/examples/tesla/music/`), then `python3 <skill>/scripts/gen_requests.py music music/`, the same quote → yes →
generate → download → verify loop, and a whisper scan for vocals. Set `score` (with `start` offsets so the climax lands
on the story climax and the final chord on the last frame), `teaserMusic` + `teaserStart` (loudest 7 s),
`musicHi`/`musicLo`. A failed cue: rewrite the brief (drop unusual sound effects) and resubmit.

### 6 · Storyboard
`storyboard.py` starts with `import sys; sys.path.insert(0, "tools"); from sb import *`. One `S(...)` board per cue
cluster; 3-6 elements arriving every 1-2 s; median board 2-6 s. Element catalogue and layout rules:
`references/storyboard.md`. Include `cover_shot`, `teaser` (4-6 clips of 1.2-1.5 s), `motif="img/<character>"`, and
`subtitles=True` if captions are burned in.
- Build: `python3 storyboard.py`, then `python3 tools/resolve.py shots.json`.
- Cover: `npx remotion still src/index.ts Cover public/cover.jpg --image-format=jpeg`.
- Proof sheet, one frame per board: `npx remotion render src/index.ts Proof out/proof --sequence --image-format=jpeg --scale=0.25`.

`resolve.py` prints `!` warnings; clear them before rendering: elements outside their board · teaser clips that cross
a cut or show an empty board · boards with nothing new for more than 2.5 s · motif coverage and the opening/closing
bookend · text under the caption strip. It also writes `out/subs.srt`.
Then look at the proof frames and fix: labels cut off at the frame edge or still typing, stamps covering faces, text on
dark boards that vanished (stamps need `blend="normal"` there), overlapping cards.

### 7 · Render and finish
- Render: `npx remotion render src/index.ts Full out/raw.mp4 --crf=20` (add `--concurrency=<cores>`; about 6 min for
  5 min of film on 10 cores).
- Finish: `python3 tools/finish.py out/raw.mp4 "<delivery>.mp4" --sheet out/qa_open.jpg` (add `--srt out/subs.srt` for a
  switchable caption track).

`finish.py` sets the loudness (-16 LUFS) from the raw audio, lowers the limiter until the measured true peak is under
-1.5 dBTP, checks frames and duration, and writes a contact sheet of the first 10 s. **Look at that sheet** (cover,
every teaser clip, first board) and at a few mid-transition frames and the ending. You cannot hear the film: tell the
user which pronunciations to spot-check. Deliver MP4 + cover + script + sources (`facts.md`, `credits.json`) + `subs.srt`.

## Gotchas (full list: references/pitfalls.md)
- Downloads can be truncated: always run `verify.py` on a batch before using it.
- Gemini TTS reads any direction text aloud and ignores accent settings; Seed Audio follows written directions.
- An article adapted point by point becomes a slideshow: use the `essay` skeleton and the lint.
- Teaser clips cut from the last word of a beat run into the next board; with burned-in captions keep text centres at y<=900.
- Remotion `Freeze` did not work for proofs; the Proof composition uses a negative Sequence offset.
