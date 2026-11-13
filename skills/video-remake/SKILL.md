---
name: video-remake
description: >
  Recreate or remix one supplied reference video (a file or a link) with replacement characters,
  products, branding, props, or scenes. Use when the user asks to replicate a
  video, remake a clip, 复刻视频, 剪同款, 换脸, or make a version of a supplied
  video with controlled replacements. The source video must remain attached.
metadata:
  author: renoise
  version: 0.3.0
  category: video-production
  tags: [video, remake, replication, replacement, portable, measured]
---

# Reference Video Remake / 复刻视频 / 剪同款

This workflow fills replacement slots, then makes the final generation with the source attached.

## Choose the Route

Choose by the source, once the media analysis (Phase 1) has its length, timeline and on-screen text. The route is about
the task; a shell only makes the measured route possible.

- **Single-generation route** (the phases below: one generation with the whole source as reference) when all of these
  hold: the whole source fits one generation of a model that takes it as reference video; it is one continuous scene or
  a few cuts the model makes in one call; no titles, captions, UI or graphics have to be set again; and one or two
  subjects are replaced. It is faster and cheaper, so it is the default whenever it fits.
- **Measured route** (`references/measured.md`) when any of these holds and you have a shell with `rn` (renoise-kit),
  that is the cloud sandbox (the `sandbox` tool, Director Mode) or a local shell where this skill's `scripts/doctor.py`
  passes:
  - the source is longer than one generation;
  - it has many cuts or several scenes;
  - text, UI or graphics over the picture have to be set again;
  - several replaced subjects must stay the same person or product across shots;
  - the user asks for the source's exact timing (cuts on the beat, frame-exact).

  It measures the source shot by shot, opens every generated shot on an approved keyframe, generates in units that each
  carry their own source clip, and puts the pieces back on the source's timeline with rn, checked against the source. It
  takes longer and costs more, so use it only for what the single generation would visibly get wrong.
- Without such a shell, take the single-generation route for every source. When the measured route would have suited
  it, say in one line that the sandbox (Director Mode) remakes such sources shot by shot.
- When it is borderline, take the single-generation route, and switch only if its result misses what the list names.

## Before You Start

Read `../model-routing/SKILL.md` before choosing a model or writing prompts. With a shell (the host's own or the cloud sandbox), your own code (editing, compositing, motion graphics, music) works alongside generation; use it wherever it brings the remake closer to the source.

**A linked source.** When the source is a link (X, YouTube, TikTok, Douyin, Instagram, Bilibili and other video pages) and you have a shell, download it with yt-dlp, save it as a material, and use that material from then on. Ask the user to upload the file only when the download fails or you have no shell.

Write analysis, plans and results in the user's language. Retained or replacement speech keeps the requested or safely inferable spoken language, every line verbatim.

## Source Policy

The source video is always attached to the final generation as reference video. Choose a video model whose live capabilities take the source as reference video together with every image reference the slots need, within its counts, duration and role combinations. If none can, stop and explain; never drop the source.

The final prompt states that the source supplies timing, camera motion, composition, transitions, effects, pacing and emotional beats, and that the slot materials supply identity, product, wardrobe, props and other replaced content. This reduces accidental copying but is not a guarantee.

## Phase 1 — Analyze and Plan

Run `analyze_media` in template/video mode on the source: it watches and listens, so it carries content, dialogue, music and mood. With a shell, also inspect the source yourself: exact cuts, beats, durations and loudness, and close frames of transitions, typography and grading. Without either, stop.

The plan holds the factual analysis (summary, timeline, composition, style, subjects, audio), a model-neutral prompt with `{{slot_id}}` placeholders, every replaceable slot with a reference-image prompt, and warnings for what is inferred. Keep it in the conversation:

```json
{
  "source": { "materialId": null },
  "videoModel": null,
  "imageModel": null,
  "prompt": "template containing {{slot_id}} placeholders",
  "slots": [
    { "id": "subject_1", "type": "character", "description": "replacement lead", "prompt": "English reference-image prompt", "source": "user|library|generated|missing", "materialId": null, "taskId": null }
  ],
  "videoTaskId": null
}
```

## Phase 2 — Fill the Slots

Fill each slot, in this order: the user's material that clearly matches it; a library material the user confirms; an image generated from the slot prompt. Never let a filename alone choose a character or product. Ask only when a mapping is truly ambiguous.

Show the plan with the source summary, each slot and where it comes from, the chosen models and the cost of the slot images, then generate the missing slots in one round. Show the slot images: this is the remake's review checkpoint, where the user can replace or regenerate any slot before the video is made.

## Phase 3 — Final Generation

Replace every `{{slot_id}}` with its slot's `@material:{id}` token, attach the source as reference video and every slot as an image reference, check the combined counts and roles against the model's live limits, and add the source lock above. Keep the source's dialogue only when the user wants it. No placeholder may remain. Show the final prompt, the source and slot mapping, the parameters and the estimate, then generate.

Deliver the result with the source and slot mapping and any warning. For revisions, keep the approved slot materials and change only the named dimension unless the user replaces an asset.

## Failure Rules

Do not pre-screen the source, replacement materials or prompts. Continue normally unless a tool returns an explicit content-review error.

| Failure | Action |
|---|---|
| No analysis and no shell | Stop and explain. |
| No model takes the source video with the slot images | Stop; never omit the source or invent roles. |
| Source exceeds the model's limits | Take the measured route where you have a shell; otherwise ask for a shorter source. Never clamp it silently. |
| A slot image fails | Keep the others and redo only that slot. |
| `INPUT_*` / `OUTPUT_*` content-review error | Report the actual error and stop; do not retry the paid create or suggest bypasses. |
| Output copies the source identity | Strengthen the source lock or replace the conflicting source; never claim text guarantees isolation. |
