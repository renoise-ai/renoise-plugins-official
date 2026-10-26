---
name: digital-human-koubo
description: >
  Talking-head videos with a digital presenter (数字人口播): the user's own photo or an
  AI-generated host speaks a script cut into short takes, checked by ear, aligned word by
  word and edited with Remotion in a caption-heavy vertical, launch, tutorial or multi-host
  style with packaging (hooks, number punches, text behind the presenter, maps, danmaku).
  Use for 数字人口播, 口播视频, AI 主播, 数字人带货 / 解读 / 教程 / 种草, talking-head or AI
  presenter videos. Not for impersonating real people.
metadata:
  author: renoise
  version: 0.1.0
  category: video-production
  tags: [video, talking-head, digital-human, remotion]
---

# digital-human-koubo

This skill lives in [renoise-ai/renoise-skills](https://github.com/renoise-ai/renoise-skills/tree/8ac1ca146caf802d895b7a3722be93d02fc8837c/skills/digital-human-koubo) with its scripts, templates and assets, pinned to commit `8ac1ca146caf802d895b7a3722be93d02fc8837c`. It runs in a shell: the Renoise sandbox (the `sandbox` tool) or the user's own machine.

1. Get the files once per commit. Skip this step when `~/.cache/renoise-skills/8ac1ca146caf802d895b7a3722be93d02fc8837c/skills/digital-human-koubo/SKILL.md` already exists. Otherwise download the archive `https://codeload.github.com/renoise-ai/renoise-skills/tar.gz/8ac1ca146caf802d895b7a3722be93d02fc8837c` and unpack it into `~/.cache/renoise-skills/8ac1ca146caf802d895b7a3722be93d02fc8837c/` without its top folder (for example `mkdir -p ~/.cache/renoise-skills/8ac1ca146caf802d895b7a3722be93d02fc8837c && curl -fsSL <archive> | tar -xz -C ~/.cache/renoise-skills/8ac1ca146caf802d895b7a3722be93d02fc8837c --strip-components=1`).
2. Read `~/.cache/renoise-skills/8ac1ca146caf802d895b7a3722be93d02fc8837c/skills/digital-human-koubo/SKILL.md` and follow it; its `<skill>` is that folder's absolute path. Read its references from there as it asks.
3. Renoise rules still apply: load model-routing before choosing a model, and before create_tasks show the estimate_cost total and the balance and wait for the user's explicit OK in the chat.

Without a shell, follow its script and generation steps through the Renoise tools and deliver the takes with the cut plan; say that the edit needs a shell.
