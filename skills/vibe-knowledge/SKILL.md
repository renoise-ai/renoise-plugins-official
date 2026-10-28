---
name: vibe-knowledge
description: >
  Narrated knowledge shorts with sourced facts (知识短片 / 知识科普视频, 45 s – 5 min, 16:9 1080p60):
  one knowledge point becomes a script from six viral explainer templates, a sourced fact sheet,
  a Renoise voiceover aligned word by word and one of 44 code-drawn visual styles, with optional stills,
  shots and sound effects generated on Renoise. Use for 知识短片, 知识科普视频, 冷知识视频, 历史科普,
  一口气讲清楚某个原理, Vibe知识大赏 or a narrated explainer short with sources. Not for courses,
  finance talking heads, brand promos or digital-human presenters.
metadata:
  author: renoise
  version: 0.1.0
  category: video-production
  tags: [video, explainer, knowledge, narration]
---

# vibe-knowledge

This skill lives in [renoise-ai/renoise-skills](https://github.com/renoise-ai/renoise-skills/tree/stable/skills/vibe-knowledge) with its scripts, templates and assets. Use its `stable` branch, which only moves to commits that passed CI. It runs in a shell: the Renoise sandbox (the `sandbox` tool) or the user's own machine.

1. Find the commit `stable` is on: `curl -fsSL -H 'Accept: application/vnd.github.sha' https://api.github.com/repos/renoise-ai/renoise-skills/commits/stable` prints it. If that fails (offline or rate-limited), use the newest folder in `~/.cache/renoise-skills/` that has `skills/vibe-knowledge/SKILL.md` and go to step 3; if there is none, use `stable` as the commit.
2. Get the files once per commit. Skip this step when `~/.cache/renoise-skills/<commit>/skills/vibe-knowledge/SKILL.md` already exists. Otherwise download the archive `https://codeload.github.com/renoise-ai/renoise-skills/tar.gz/<commit>` and unpack it into `~/.cache/renoise-skills/<commit>/` without its top folder (for example `mkdir -p ~/.cache/renoise-skills/<commit> && curl -fsSL <archive> | tar -xz -C ~/.cache/renoise-skills/<commit> --strip-components=1`), then delete the other folders in `~/.cache/renoise-skills/`.
3. Read `~/.cache/renoise-skills/<commit>/skills/vibe-knowledge/SKILL.md` and follow it; its `<skill>` is that folder's absolute path. Read its references from there as it asks.
4. Renoise rules still apply: load model-routing before choosing a model, and before create_tasks show the estimate_cost total and the balance and wait for the user's explicit OK in the chat.

Without a shell this skill cannot render: say so and stop before any paid step.
