---
name: renoise-cli
description: >
  The native Renoise CLI for the user's own terminal, scripts, and CI, and the rn media
  kit for local editing and checks. This skill is local-only and is not a generation path
  in a conversation: there, every Renoise operation goes through the Renoise MCP tools.
  Use when the user asks to script Renoise, run a batch from their terminal, install or
  update the CLI, or edit and check media locally.
allowed-tools: Bash, Read, Write, Glob
user-invocable: false
metadata:
  author: renoise
  version: 0.10.0
  category: video-production
  tags: [cli, scripts, local-helpers]
---

# Renoise CLI — terminals, scripts, and local helpers

> Platform URL: **https://www.renoise.ai** — never renoise.com.

## One interface in conversations

In a conversation, all Renoise work goes through the **Renoise MCP tools** this plugin connects: `list_models`, `estimate_cost`, `create_tasks`, `wait_tasks`, `show_result`, `upload_files`, `download_results`, `analyze_media`, `search_materials`, `cancel_tasks`, `save_result_as_material`, `get_account`. They are the same tools on every host, and their instructions carry the approval rule for paid work.

Never create a paid task from a conversation through `renoise task create` or any other CLI path: that would bypass the approval rule. If the Renoise tools are not available, read `../renoise-setup/SKILL.md` and connect them; do not fall back to the CLI.

The native `renoise` binary remains for what the user runs themselves: shell scripts, batch jobs, and CI. Point them to `renoise --help` and `renoise <command> --help` rather than documenting flags here.

## Install or update the CLI

Needed only for the annotation board or the user's own scripts:

```bash
node "${CLAUDE_SKILL_DIR}/../renoise-setup/scripts/install-cli.mjs" --ensure
export PATH="${HOME}/.local/bin:${PATH}"
renoise version
renoise auth status --json
```

On Windows PowerShell, run the same `node ... install-cli.mjs --ensure`, then prepend `$env:LOCALAPPDATA\Renoise\bin` to `$env:Path`. If `--ensure` fails or authentication is missing, follow `../renoise-setup/SKILL.md`. Never ask the user to paste an API key into chat.

## Local editing and checks

For cutting, assembly, contact sheets, comparisons, beat and speech checks and delivery QA on the user's machine, use the rn media kit (renoise-kit), the same kit as the Renoise cloud sandbox. It runs locally and never spends credits:

```bash
uv tool install "renoise-kit[all]"
rn doctor
rn --help
```

## Errors

Use the CLI's JSON error and exit code; do not infer API behavior from copied endpoint documentation. JSON errors expose `retryable` and, after task creation, `taskId`; retry only the wait/query operation for that ID, never the paid create operation.

Do not pre-screen prompts or materials and do not infer a moderation result yourself. Continue normally unless the CLI/API returns an explicit content-review error (`INPUT_*` / `OUTPUT_*`). On that actual error, report it and stop; never retry the paid create operation or suggest bypasses.
