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

This skill lives in [renoise-ai/renoise-skills](https://github.com/renoise-ai/renoise-skills/tree/stable/skills/digital-human-koubo) with its scripts, templates and assets. Use its `stable` branch, which only moves to commits that passed CI. It runs in a shell: the Renoise sandbox (the `sandbox` tool) or the user's own machine.

1. Find the commit `stable` is on: `curl -fsSL -H 'Accept: application/vnd.github.sha' https://api.github.com/repos/renoise-ai/renoise-skills/commits/stable` prints it. If that fails (offline or rate-limited), use the newest folder in `~/.cache/renoise-skills/` that has `skills/digital-human-koubo/SKILL.md` and go to step 3; if there is none, use `stable` as the commit.
2. Get the files once per commit. Skip this step when `~/.cache/renoise-skills/<commit>/skills/digital-human-koubo/SKILL.md` already exists. Otherwise download the archive `https://codeload.github.com/renoise-ai/renoise-skills/tar.gz/<commit>` and unpack it into `~/.cache/renoise-skills/<commit>/` without its top folder (for example `mkdir -p ~/.cache/renoise-skills/<commit> && curl -fsSL <archive> | tar -xz -C ~/.cache/renoise-skills/<commit> --strip-components=1`), then delete the other folders in `~/.cache/renoise-skills/`.
3. Read `~/.cache/renoise-skills/<commit>/skills/digital-human-koubo/SKILL.md` and follow it; its `<skill>` is that folder's absolute path. Read its references from there as it asks.
4. Renoise rules still apply: load model-routing before choosing a model, and before create_tasks show the estimate_cost total and the balance and wait for the user's explicit OK in the chat.

Without a shell, follow its script and generation steps through the Renoise tools and deliver the takes with the cut plan; say that the edit needs a shell.
