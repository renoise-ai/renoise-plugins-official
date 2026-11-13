---
name: video-fission
description: >
  Create controlled variants from one owner-authorized source video. Use when
  the user explicitly asks for video fission, multiple video variants,
  controlled variations, or several hypotheses from the same clip. Analyze the
  source first, then resolve what should vary before proposing any generation.
metadata:
  author: renoise
  version: 0.3.0
  category: video-production
  tags: [video, fission, variants, experimentation, portable]
---

# Video Fission

Create a controlled batch of variants from one source video. This is an experiment, not a multi-shot production: vary one axis, or at most two, and lock everything else.

## Source

One owner-authorized source video: an attachment, a material, a task result, or a link (with a shell, download it with yt-dlp and save it as a material; ask for the file only when that fails or you have no shell). Never use more than one source video.

## 1. Analyze First

Analyze the source before deciding what varies, and report in the user's language: subject, setting, actions, camera, composition, lighting, style, pacing and edit structure, duration, aspect ratio, audio and dialogue; what looks fixed and what could plausibly vary; and what is uncertain. With a shell, measure duration and cuts yourself as well.

If the request already names a usable axis, map the analysis to it and go on without asking. Ask one focused question only when the axis is missing or ambiguous, offering axes this clip supports (action, camera, pacing, atmosphere and light, performance, transformation) with your recommendation. Allow a second axis only when the user needs it.

Use **4 outputs** unless the user names another count of at least two; do not ask to confirm the default.

## 2. One Model, the Source as Reference

Choose the model with `../model-routing/SKILL.md` among those whose live capabilities take `reference_video` (MiniMax H3 Max suits variants of one source). Use the analyzed source as every variant's sole `reference_video` and call it `Video 1` in every prompt. Do not replace it with an extracted frame. If the source is longer than the model accepts, trim it to the limit where you have a shell, keeping the part that matters most, say which part you kept, and analyze the trimmed version; otherwise give its duration and the limit and ask the user for a shorter source.

## 3. The Variant Matrix

Show it before generating:

| Variant | Axis value(s) | Distinct hypothesis | Locked dimensions |
|---|---|---|---|
| V1 | ... | If ..., then ... because ... | ... |

- Every variant tests a genuinely distinct hypothesis; no cosmetic synonyms.
- Lock everything outside the axis across all variants: model, source, subject identity, composition, duration, ratio, resolution, audio mode, dialogue and output settings.
- Keep one prompt skeleton and change only the clauses that carry the axis values.
- With two axes, choose intentional combinations, not the full product.

## Dialogue and Language

Write analysis, questions, the matrix and results in the user's language. Prompts without speech may be English. Speech keeps the requested or safely inferable spoken language, verbatim, with the whole prompt in that language when it is dialogue-dense; unless dialogue is the axis, lock its text, speaker, delivery and language across variants.

## 4. Generate as One Batch

Generate all variants in one `create_tasks` call with the source aspect ratio (or the closest the model takes), in matrix order. For revisions, change only the named axis value or failed variant and keep the rest.
