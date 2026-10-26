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

This skill lives in [renoise-ai/renoise-skills](https://github.com/renoise-ai/renoise-skills/tree/8ac1ca146caf802d895b7a3722be93d02fc8837c/skills/promo-video) with its scripts, templates and assets, pinned to commit `8ac1ca146caf802d895b7a3722be93d02fc8837c`. It runs in a shell: the Renoise sandbox (the `sandbox` tool) or the user's own machine.

1. Get the files once per commit. Skip this step when `~/.cache/renoise-skills/8ac1ca146caf802d895b7a3722be93d02fc8837c/skills/promo-video/SKILL.md` already exists. Otherwise download the archive `https://codeload.github.com/renoise-ai/renoise-skills/tar.gz/8ac1ca146caf802d895b7a3722be93d02fc8837c` and unpack it into `~/.cache/renoise-skills/8ac1ca146caf802d895b7a3722be93d02fc8837c/` without its top folder (for example `mkdir -p ~/.cache/renoise-skills/8ac1ca146caf802d895b7a3722be93d02fc8837c && curl -fsSL <archive> | tar -xz -C ~/.cache/renoise-skills/8ac1ca146caf802d895b7a3722be93d02fc8837c --strip-components=1`).
2. Read `~/.cache/renoise-skills/8ac1ca146caf802d895b7a3722be93d02fc8837c/skills/promo-video/SKILL.md` and follow it; its `<skill>` is that folder's absolute path. Read its references from there as it asks.
3. Renoise rules still apply: load model-routing before choosing a model, and before create_tasks show the estimate_cost total and the balance and wait for the user's explicit OK in the chat.

Without a shell this skill cannot render: say so and use the director skill instead.
