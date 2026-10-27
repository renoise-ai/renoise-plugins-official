---
name: promo-video
description: >
  Promo, product-launch, explainer and brand films rendered with Remotion (宣传片, 产品发布视频,
  产品介绍动画): storyboard-driven templates or cinematic shots with 3D logos, real product UI
  demos, motion design and beat-matched music; also motion-graphics showreels and one-shape UI
  loops. Use when the user asks for a 宣传视频, 宣传片, 片头, promo video, product launch video,
  explainer video, brand video or motion graphics showreel.
metadata:
  author: renoise
  version: 0.1.0
  category: video-production
  tags: [video, promo, motion-graphics, remotion]
---

# promo-video

This skill lives in [renoise-ai/renoise-skills](https://github.com/renoise-ai/renoise-skills/tree/stable/skills/promo-video) with its scripts, templates and assets. Use its `stable` branch, which only moves to commits that passed CI. It runs in a shell: the Renoise sandbox (the `sandbox` tool) or the user's own machine.

1. Find the commit `stable` is on: `curl -fsSL -H 'Accept: application/vnd.github.sha' https://api.github.com/repos/renoise-ai/renoise-skills/commits/stable` prints it. If that fails (offline or rate-limited), use the newest folder in `~/.cache/renoise-skills/` that has `skills/promo-video/SKILL.md` and go to step 3; if there is none, use `stable` as the commit.
2. Get the files once per commit. Skip this step when `~/.cache/renoise-skills/<commit>/skills/promo-video/SKILL.md` already exists. Otherwise download the archive `https://codeload.github.com/renoise-ai/renoise-skills/tar.gz/<commit>` and unpack it into `~/.cache/renoise-skills/<commit>/` without its top folder (for example `mkdir -p ~/.cache/renoise-skills/<commit> && curl -fsSL <archive> | tar -xz -C ~/.cache/renoise-skills/<commit> --strip-components=1`), then delete the other folders in `~/.cache/renoise-skills/`.
3. Read `~/.cache/renoise-skills/<commit>/skills/promo-video/SKILL.md` and follow it; its `<skill>` is that folder's absolute path. Read its references from there as it asks.
4. Renoise rules still apply: load model-routing before choosing a model, and before create_tasks show the estimate_cost total and the balance and wait for the user's explicit OK in the chat.

Without a shell this skill cannot render: say so and use the director skill instead.
