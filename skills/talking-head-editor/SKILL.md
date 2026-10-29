---
name: talking-head-editor
description: >
  Edit talking-head footage the user filmed (口播剪辑) into a finished vertical or landscape video
  (MP4) or a JianYing (剪映) draft: media check, transcription, filler and pause removal, a
  sentence-by-sentence edit plan, B-roll from the user, code-drawn graphics, free stock or Renoise,
  captions and word art, picture-in-picture, keyframes, sound effects and music, and blurring of
  sensitive information, in a refined (高级感) or variety-show (综艺感) style. Use for 剪口播,
  口播视频剪辑, 知识博主视频, 真人出镜剪辑, 加字幕花字, 剪映草稿, B-roll, 去气口, 粗剪精剪, or
  when the user hands over a clip of themselves talking to camera and asks to cut it into a short.
  Not for generating a digital presenter from a script (digital-human-koubo).
metadata:
  author: renoise
  version: 0.1.0
  category: video-production
  tags: [video, talking-head, editing, captions]
---

# talking-head-editor

This skill lives in [renoise-ai/renoise-skills](https://github.com/renoise-ai/renoise-skills/tree/stable/skills/talking-head-editor) with its scripts, templates and assets. Use its `stable` branch, which only moves to commits that passed CI. It runs in a shell: the Renoise sandbox (the `sandbox` tool) or the user's own machine.

1. Find the commit `stable` is on: `curl -fsSL -H 'Accept: application/vnd.github.sha' https://api.github.com/repos/renoise-ai/renoise-skills/commits/stable` prints it. If that fails (offline or rate-limited), use the newest folder in `~/.cache/renoise-skills/` that has `skills/talking-head-editor/SKILL.md` and go to step 3; if there is none, use `stable` as the commit.
2. Get the files once per commit. Skip this step when `~/.cache/renoise-skills/<commit>/skills/talking-head-editor/SKILL.md` already exists. Otherwise download the archive `https://codeload.github.com/renoise-ai/renoise-skills/tar.gz/<commit>` and unpack it into `~/.cache/renoise-skills/<commit>/` without its top folder (for example `mkdir -p ~/.cache/renoise-skills/<commit> && curl -fsSL <archive> | tar -xz -C ~/.cache/renoise-skills/<commit> --strip-components=1`), then delete the other folders in `~/.cache/renoise-skills/`.
3. Read `~/.cache/renoise-skills/<commit>/skills/talking-head-editor/SKILL.md` and follow it; its `<skill>` is that folder's absolute path. Read its references from there as it asks.
4. Renoise rules still apply: load model-routing before choosing a model, and before create_tasks show the estimate_cost total and the balance and wait for the user's explicit OK in the chat.

Without a shell this skill cannot edit or render: say so and stop before any paid step.
