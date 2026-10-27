---
name: pixel-breakdown
description: >
  16:9 pixel-art breakdown episodes (像素风拆解视频, 60–90 s): a reference clip the user is
  authorized to use next to its AI remake, a pixel diagram of its measured cuts and timing, a
  simulated agent chat showing how the remake was made, and a 3:4 cover. Use for 像素拆解, 爆款拆解,
  复刻过程讲解, pixel breakdown or "how this viral clip was remade" videos.
metadata:
  author: renoise
  version: 0.1.0
  category: video-production
  tags: [video, breakdown, pixel-art, remake]
---

# pixel-breakdown

This skill lives in [renoise-ai/renoise-skills](https://github.com/renoise-ai/renoise-skills/tree/stable/skills/pixel-breakdown) with its scripts, templates and assets. Use its `stable` branch, which only moves to commits that passed CI. It runs in a shell: the Renoise sandbox (the `sandbox` tool) or the user's own machine.

1. Find the commit `stable` is on: `curl -fsSL -H 'Accept: application/vnd.github.sha' https://api.github.com/repos/renoise-ai/renoise-skills/commits/stable` prints it. If that fails (offline or rate-limited), use the newest folder in `~/.cache/renoise-skills/` that has `skills/pixel-breakdown/SKILL.md` and go to step 3; if there is none, use `stable` as the commit.
2. Get the files once per commit. Skip this step when `~/.cache/renoise-skills/<commit>/skills/pixel-breakdown/SKILL.md` already exists. Otherwise download the archive `https://codeload.github.com/renoise-ai/renoise-skills/tar.gz/<commit>` and unpack it into `~/.cache/renoise-skills/<commit>/` without its top folder (for example `mkdir -p ~/.cache/renoise-skills/<commit> && curl -fsSL <archive> | tar -xz -C ~/.cache/renoise-skills/<commit> --strip-components=1`), then delete the other folders in `~/.cache/renoise-skills/`.
3. Read `~/.cache/renoise-skills/<commit>/skills/pixel-breakdown/SKILL.md` and follow it; its `<skill>` is that folder's absolute path. Read its references from there as it asks.
4. Renoise rules still apply: load model-routing before choosing a model, and before create_tasks show the estimate_cost total and the balance and wait for the user's explicit OK in the chat.

Without a shell this skill cannot render: say so and stop before any paid step.
