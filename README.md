# renoise-plugins-official

AI video production skills by Renoise — creative direction, generation, analysis, e-commerce content, and download.

## Skills

| Skill | Description |
|-------|-------------|
| **Create with Renoise** (`director`) | Portable creative direction for product ads, short films, e-commerce, drama, and comedy |
| `model-routing` | Internal task-to-model router and model-specific prompting guide |
| **Build Storyboard** (`storyboard-sheet`) | Portable script/novel adaptation into review sheets, shot lists, first frames, and video prompts |
| `video-fission` | Portable controlled-variant experiments from one owner-authorized source video |
| `video-remake` | Portable reference-video recreation with controlled character, product, brand, prop, or scene replacement |
| `digital-human-koubo` | Talking-head videos with a digital presenter (the user's photo or an AI host), packaged and edited with Remotion; fetched from the `stable` branch of [renoise-skills](https://github.com/renoise-ai/renoise-skills), runs in the Renoise sandbox or a local shell |
| `promo-video` | Promo, launch and brand films rendered with Remotion; fetched from the `stable` branch of [renoise-skills](https://github.com/renoise-ai/renoise-skills), runs in the Renoise sandbox or a local shell |
| `pixel-breakdown` | 16:9 pixel-art breakdown episodes of an authorized viral clip and its AI remake, drawn by code and rendered with Playwright; fetched from the `stable` branch of [renoise-skills](https://github.com/renoise-ai/renoise-skills), runs in the Renoise sandbox or a local shell |
| `renoise-cli` | Native CLI for your own terminal, scripts, and CI, plus local production helpers (not a generation path in conversations) |
| **Setup / Account** (`renoise-setup`) | Connect the Renoise tools (browser sign-in), optional CLI install/update, and readiness checks |
| **Renoise Annotation Board** (`canvas`) | Local image/frame annotation board for snapshots and structured revision handoff |
| `video-download` | Local-only downloader utility (yt-dlp + Douyin/TikTok fallback) |

## Installation

> **⚠️ Upgrading from an older build?** As of **1.0.0** the plugin is unified under the name **`renoise`** on every host. Older installs registered as **`video-maker`** (Codex/OpenClaw, and very early Claude Code builds) **do not auto-update** — see [Version & upgrading](#version--upgrading) for the one-time migration steps.

### Claude Code

1. Add the marketplace:

```bash
claude plugin marketplace add renoise-ai/renoise-plugins-official
```

2. Install the plugin:

```bash
claude plugin install renoise@renoise-plugins-official
```

3. Connect your Renoise account: run `/mcp`, choose `plugin:renoise:renoise`, and sign in in the browser. `/renoise:setup` walks through this and also sets up the Credits statusLine:

```
/renoise:setup
```

### Claude Desktop

In **Cowork**, open **Customize → Plugins → + → Add marketplace → Add from a repository**, enter `https://github.com/renoise-ai/renoise-plugins-official`, then install **renoise**. Cowork asks you to sign in to Renoise in the browser the first time the Renoise tools are used; no separate Terminal is required.

### OpenClaw

```bash
openclaw plugins install @renoise/plugin
```

### Codex / ChatGPT Desktop

Add the repository marketplace with the native Codex plugin command:

```bash
codex plugin marketplace add renoise-ai/renoise-plugins-official
```

Restart the ChatGPT desktop app, open **Plugins**, select the **Renoise** marketplace, and install **renoise**. Codex Desktop is available on macOS and Windows; on Linux, use the same plugin through Codex CLI.

### ChatGPT Directory package (maintainers)

`npm run build:openai` builds the ChatGPT / Codex Directory upload from this plugin's own `plugin.json` and `mcp.json`: it keeps the portable skills and the one remote MCP server (pointed at its ChatGPT entry, `https://renoise.ai/api/public/mcp/chatgpt`), checks the listing limits, and writes `dist/renoise-openai-<version>.zip` for upload at platform.openai.com. Reviewer credentials go in the dashboard, never in the package.

## How the plugin runs Renoise

Every Renoise operation in a conversation (models, estimates, generation, uploads, media analysis, results) goes through the remote **Renoise MCP server** at `https://renoise.ai/api/public/mcp`, declared once in `mcp.json` for Claude Code, Codex, and the OpenAI directories. The same server backs the claude.ai and ChatGPT connectors, so every host sees the same tools, in-chat widgets, and approval rule for paid work. You sign in once with OAuth.

## Native Renoise CLI

The native Go CLI is optional: it is for your own terminal, scripts, and CI, the annotation board, the local helpers, and the Claude Code Credits statusLine. Conversations never generate through it. Hosted Renoise Agent uses portable Skills plus its own typed capabilities and does not install or execute this CLI. To install it, select **Setup / Account** in Claude Desktop Cowork or Codex/ChatGPT Desktop, or run `/renoise:setup` in Claude Code. The Agent handles detection, installation, browser sign-in, and verification; the user only approves installation and authorizes Renoise in the browser. Setup detects macOS/Windows/Linux and x64/ARM64, compares the installed CLI contract/version with the latest release, and previews the archive and user-local target. After confirmation, the same path installs or updates the matching `.tar.gz`/`.zip`, verifies `checksums.txt` and required commands before replacement, and rolls back a failed replacement. The default targets are `~/.local/bin/renoise` on macOS/Linux and `%LOCALAPPDATA%\Renoise\bin\renoise.exe` on Windows. It never updates in the background; any binary replacement or PATH change requires approval, and PATH changes require a Desktop restart.

Manual downloads are listed in `https://download.renoise.ai/cli/latest.json`; verify the matching version directory's `checksums.txt` before extracting the binary.

Plugin updates remain owned by each host's plugin manager. CLI recovery happens on use but never replaces a binary without approval, so the two release tracks do not silently modify each other. There is no per-session setup notification. `renoise auth login --web` opens account authorization in the browser and stores the shared credential securely without terminal key entry; `RENOISE_API_KEY` remains the override for CI and containers. The local-only `renoise-cli` Skill queries live capabilities. Creative Skills keep researched routing and prompting profiles, but never duplicate availability, defaults, roles, limits, or other hard capability data; unknown models safely fall back to their live guidance and default status.

`skills/manifest.json` classifies Skills by runtime. Hosted Renoise Agent loads only portable source files whose required capabilities are available; it never loads local CLI or MCP App entries. Hosted execution uses its typed capabilities directly and does not run the native CLI or local MCP App.

### Standalone Skills package

The canonical `skills/` tree is also a dependency-free `@renoise/skills` package, so hosted runtimes can update official Skills without installing Canvas, React, or the plugin runtime. With pnpm, pin a reviewed commit and its package subdirectory:

```json
{
  "@renoise/skills": "github:renoise-ai/renoise-plugins-official#<commit>&path:/skills"
}
```

The existing `@renoise/plugin/skills/...` files remain available for plugin hosts; both packages use this same source tree. Manifest paths retain their `skills/` prefix for plugin compatibility, so subdirectory-package consumers remove exactly that one prefix when resolving files.

Interactive account and CLI defaults are available through:

```bash
renoise settings
```

## Renoise annotation board

Codex Desktop can open a focused Renoise annotation board for images and exact video frames. Media stays fixed while the user adds pen, arrow, shape, text, or numbered-pin marks, captures annotated snapshots into the intent input, and submits a structured revision request with source provenance and video timecodes.

The first render creates a pending session. The widget displays the exact project directory and does not read or write it until the user clicks **Approve**. State then stays under `<project>/.renoise/whiteboard/`; board JSON stores only opaque asset IDs and page-relative paths, while the original media bytes live under `pages/<pageId>/assets/`. Every tool call is bound to the opaque session, document writes use revision CAS, and model-facing media insertion accepts only same-session assets or validated Renoise task-result contracts.

The annotation board is an intent-capture surface rather than a replacement for the Renoise app's node graph, player, or timeline. AI HTML and Slides are intentionally not included.

The model-visible launch result contains only the exact project directory awaiting approval; the app-only approval call resolves the server-held pending session atomically, so session IDs and authorization nonces never round-trip through host-rendered tool output. Authorization does not require the optional MCP Apps initialize extension because some compatible desktop hosts render MCP Apps without declaring it; app-only tool visibility plus the server-held pending directory form the boundary. The `mcp.json` entry intentionally uses plugin-root-relative paths (`features/canvas/dist/server.mjs`, `cwd: "./"`), which Agent Plugins hosts such as Codex resolve against the installed plugin root. Claude Code launches stdio servers from the user's project directory instead, so `.claude-plugin/plugin.json` overrides only the whiteboard entry with `${CLAUDE_PLUGIN_ROOT}/features/canvas/dist/server.mjs`. `tests/canvas/build-and-package.test.mjs` locks in both launch contracts.

After approval, the MCP server issues the widget a short-lived, session-scoped capability for an ephemeral loopback media gateway. The gateway additionally rejects any request whose `Host` header is not the gateway's own loopback host:port, as a DNS-rebinding defense. Image/video imports go directly from the widget to the approved project's asset directory as raw bytes; reloads stream verified files by opaque asset ID, and video playback supports HTTP byte ranges. Whiteboard state responses therefore remain metadata-only and do not embed previews or complete media as base64. The gateway never exposes an absolute filesystem path, validates page membership, size, signature, and SHA-256, and expires with the canvas session. When the Codex app sandbox cannot reach loopback, import and reload automatically use replay-safe 24 KiB MCP chunks instead. Those chunks are transport-only: the server assembles them directly into the same project-local asset file, while board JSON continues to store only opaque relative references.

Videos are imported only through the explicit video-import action and remain opaque page-local MP4/WebM assets. Fabric renders a poster card rather than decoding video in the canvas. Selecting media changes only the effective revision target; it never opens the media inspector. Captured frames record the source video asset ID, source SHA-256, and the native player's exact millisecond timecode, then return the user to annotation and revision-intent entry. The default video limit is 250 MB.

Plugin maintainers can run `npm run validate:plugin` to execute the official plugin-creator validator. The helper uses the installed Codex validator and an isolated temporary Python environment, leaving the repository and user Python installation unchanged.

## Environment Variables

| Variable | Required By | Description |
|----------|------------|-------------|
| `RENOISE_API_KEY` | Optional override for all Renoise tools | CI/container or host-secret override. Interactive setup prefers the credential securely saved by `renoise auth login`. |
| `RENOISE_TASK_RESULTS_DIR` | Whiteboard tests only | Explicit local test adapter for `<taskId>.json` fixtures. The production server bundle compiles this adapter away; it is honored only by the unminified test build. Production insertion calls `renoise task result <id> --json`. |
| `RENOISE_WHITEBOARD_MAX_VIDEO_BYTES` | Optional whiteboard limit | Maximum imported MP4/WebM byte size. Defaults to 262144000 (250 MB); accepted range is 1 MB–2 GB. |

## Version & upgrading

### 1.15.0

- `digital-human-koubo` and `promo-video` follow the `stable` branch of renoise-skills instead of a pinned commit. renoise-skills moves `stable` to each main commit whose CI passed, so a fix to those skills reaches every agent without a release here. The agent looks up the commit `stable` is on and keeps one copy per commit in `~/.cache/renoise-skills/<commit>/`; offline or rate-limited, it uses the copy it has. A new skill or a changed description still needs a release here.
- New `pixel-breakdown` from renoise-skills: 16:9 pixel-art breakdown episodes (60–90 s plus a 3:4 cover) of a viral clip the user is authorized to use and its AI remake. It needs a shell; without one it stops before any paid step.

### 1.14.0

- Two skills from [renoise-skills](https://github.com/renoise-ai/renoise-skills): `digital-human-koubo` (talking-head videos with a digital presenter: the user's photo or an AI host, 15-second takes generated on Renoise, listen-back, word alignment and Remotion packaging) and `promo-video` (promo, launch and brand films rendered with Remotion). Their scripts, templates and assets are too large to ship in every install, so each skill here is a short pointer: on first use the agent downloads renoise-skills at a pinned commit into `~/.cache/renoise-skills/<commit>/` and follows the full skill from there, in the Renoise sandbox or the user's own shell. Without a shell, digital-human-koubo stops after the script and generation, and promo-video hands over to the director.

### 1.13.0

- model-routing routes digital-human work (talking head, presenter monologue, dubbed avatar, lip-synced song) to OmniHuman 2.0 (`omnihuman-2.0`): one portrait plus one driving voice audio, as long as the audio. Its prompting notes say to make the voice track first (usually with Seed Audio) and not to pass duration, ratio or resolution. The director's UGC scenario uses it for segments that are mostly talking to camera, need one exact or cloned voice, or run longer than a clip.
- model-routing adds Mureka Song 9 (`mureka-song-9`) for vocal songs sung from exact lyrics and ElevenLabs Sound Effects (`eleven-sfx-v2`) for single effects of an exact 1–30 second length; Lyria stays the music default and Seed Audio keeps speech-led sound scenes. FLUX 3 Video (`flux-3-video`) takes single shots delivered at 2K or 4K from text or frames, the only live 4K model; FLUX 3 Max (`flux-3-max`) is its higher-cost 720p/1080p tier, chosen when the user asks for it. ElevenLabs Music stays unrouted until its commercial licence through Renoise is confirmed.

### 1.12.0

- The director plans before it makes anything: what would make the piece good, each part with what it shows and whether it is generated or built, told to the user in a few lines; the host decides whether to wait for an OK. code-built-video adds three habits: one timeline that both picture and sound read (sound effects made from its event times), change shown as a process rather than a state swap, and one transition system for the whole piece. A host's sandbox tool may hand builds to its engineer, who reads code-built-video; the director writes that engineer's brief.
- Fewer rules, less asking. model-routing goes back to choosing and prompting generation models: the Generate or Build table is gone, and the decision is a short principle in the director (generation draws people, places, objects and their motion; code sets exact text, numbers, charts, UI and diagrams, animates graphics, and edits; keep the look the brand or source already uses). Commercial scenarios are for live-action work: ads and brand films for software, apps and services, or for brands whose own look is UI, type or illustration, go to `references/code-built-video.md`. model-routing gains References and Edits (keep identity and product anchors, keep a source's aspect ratio, convert or trim a source that breaks a live requirement with code).
- The commercial intake no longer lists questions to ask, and the narrative intake no longer ships a questionnaire: decide what the brief leaves open from the brief and its references, state the choices in the plan, and ask only for what cannot be inferred and blocks the work.

### 1.11.0

- Generate or build: model-routing decides, per layer, what to generate and what to build in code before it picks a model. Text, numbers, charts, maps, UI, diagrams, logos and slideshows of the user's media are built in code (exact, editable, no generation credits); characters, performances, places, products and worlds in any style (live action, anime, cartoon, illustration, stylized 3D) are generated; ads mix both. Without a shell, the skills generate only what generation does well and never ask a video model for exact text or numbers.
- The director routes motion graphics, kinetic typography, explainers, data, map and UI videos, logo reveals and slideshows to a new framework-free reference, `references/code-built-video.md`: a default stack (HTML/SVG/canvas rendered frame by frame with headless Chromium, Manim, ffmpeg), frame-driven timing, layout and motion rules, compositing over generated footage, and a bounded verify-before-delivery loop.

### 1.10.1

- Follows the Renoise MCP tool update: `search_materials` is now `search_media` (`query` instead of `search`), and `estimate_cost` takes the same `tasks` you will give `create_tasks` instead of flat parameters. The annotation board estimates an automatic-duration source-video edit by passing that exact task (`duration: -1` with the source video attached).
- A video the user links to (X, YouTube, TikTok, Douyin and other video pages) can be the source of a remake, variants or analysis: with a shell (the host's own or the Renoise cloud sandbox), the skills download it with yt-dlp and save it as a material instead of asking for an upload.
- The task card shows generation results; `show_result` is only for an edited cut or a final pick across several generations.
- The Renoise cloud sandbox (`sandbox_exec`, `sandbox_agent`) is for subscribers. The first sandbox call after this server update starts a fresh sandbox, so files from earlier calls are gone.

### 1.10.0

- Conversations now run Renoise through the remote Renoise MCP server on every host (`mcp.json`), the same tools and approval rule as the claude.ai and ChatGPT connectors. Sign in once with OAuth (`/mcp` in Claude Code); the CLI is no longer needed to generate.
- The annotation board uploads, estimates, and generates through the MCP tools, including automatic-duration source-video edits.
- `renoise-cli` is now the terminal/scripts skill; its CLI generation walkthroughs are removed.
- One manifest (`plugin.json`, Agent Plugins) replaces `.codex-plugin/plugin.json`, and one `mcp.json` replaces `.mcp.json`; the ChatGPT Directory upload is built from them (`npm run build:openai`).

### 1.9.6

- Music routes to Lyria 3 Pro (`lyria-pro`), which composes complete songs of up to about 3 minutes and replaces Lyria 3 Clip. The composer brief now states a target length (approximate; there is no duration parameter) and labels song sections.
- Model routing refreshed against the live lineup: Nano Banana 2 Lite and Nano Banana Pro are no longer routed (fast drafts go to `grok-image`; peak-quality and brand work stays on GPT Image 2.5 Sunburst), and Wan 3.0 / Wan 3.0 Prime are routed for budget multimodal video with a single-shot prompt style.

### 1.9.5

- A cloud sandbox tool the host exposes (such as a `sandbox_exec` MCP tool) counts as a shell, so chat-only hosts with one also edit with code. Video remakes may measure the source in a shell (cuts, beats, loudness, frames) to complement the required media analysis.

### 1.9.4

- Hosts with a shell (Claude Code, Codex, desktop agents) can now combine Renoise generation with their own code for editing, compositing, motion graphics, music and mixing. The director and video-remake Skills no longer forbid local executables; hosts without a shell are unchanged.

### 1.9.3

- Aligned model routing with live contracts: H3 Max can use image/video/audio references, Turbo cannot; generic GPT Image 2.5 routes to Sunburst, and image defaults and Seedream limits are resolved live.

### 1.9.2

- Updated local analysis guidance for CLI v0.7.5: 15–60 MiB videos use Colorist's inline-media offload path. Videos above 60 MiB still use the legacy temporary upload path; this release does not change generation approval behavior.

### 1.9.1

- Routed GPT Image requests to GPT Image 2.5 and stopped automatically selecting older model generations.

### 1.9.0

- Added Renoise Visual Edit for structured image and video-frame annotation in Codex Desktop.
- Added project-local media persistence, Renoise material references, and source-aware revision handoff.

### 1.8.0

- Refreshed model routing, removed obsolete recommendations, and added H3 Max, H3 Max Turbo, and Topaz Starlight guidance.
- Improved automatic discovery of the internal model-routing skill.

### 1.7.0

- Split reference-video recreation (`复刻视频` / `剪同款`) into the standalone portable `video-remake` skill.

### 1.6.0

- Added `video-fission` for one- or two-axis controlled experiments with one batch approval.
- Slimmed `director` into a route-first entry point with lazily loaded narrative and commercial workflows.

### 1.5.0

- Added Seedance 2.5 and MiniMax H3 routing, reference workflows, and model-specific prompting guidance.
- Standardized material references on `@material:<ID>` across generation workflows.
- Refreshed routing and prompting practices for every live image, video, and audio model.

### 1.4.0

- Added task-aware model routing across image, video, and audio generation.
- Added researched prompting profiles and replacement guidance for superseded model variants.
- Kept live capabilities authoritative for availability, defaults, roles, limits, and parameters.

### 1.3.0

- Split portable `director` / `storyboard-sheet` methodology from the local-only `renoise-cli` execution Skill.
- Removed `gemini-gen`; media-analysis guidance now lives in `director`, while local analysis commands live in `renoise-cli`.
- Added `skills/manifest.json` for Hosted capability filtering and portability checks.

### 1.1.0

- Native Go `renoise` CLI integration as the single runtime for media analysis and generation, and the model-capability source.
- Plugin commands and director scripts call the native CLI directly; model capabilities are discovered at runtime.
- Unified setup checks the shared credential plus generation, Gemini, download, storyboard, QC, and post-production tool readiness.
- Native CLI adds interactive generation/settings TUIs, secure saved credentials, model capabilities, owner-scoped tasks, shell completion, and human/JSON output.

### 1.0.0

> **⚠️ Breaking change — the plugin is now named `renoise` on all hosts.**
> Earlier builds installed under the name **`video-maker`** on Codex/OpenClaw (and the pre-rename Claude Code build). Because plugin managers key installs by name, an old `video-maker` install **will not upgrade automatically** — it stays frozen on the old version until you migrate manually:
>
> - **Claude Code** — remove any old install, then install the current one, and restart:
>   ```bash
>   claude plugin uninstall video-maker@renoise-plugins-official   # only if you have this leftover
>   claude plugin uninstall renoise@renoise-plugins-official 2>/dev/null; claude plugin install renoise@renoise-plugins-official
>   ```
> - **Codex** — remove the old `video-maker` marketplace/install, add `renoise-ai/renoise-plugins-official` as shown above, install `renoise`, and restart the ChatGPT desktop app or Codex CLI.
> - **OpenClaw** — reinstall with `openclaw plugins install @renoise/plugin`.
>
> After migrating, slash commands move from `/video-maker:*` to `/renoise:*`.

**Highlights of 1.0.0**

- Unified plugin name **`renoise`** across Claude Code / Codex / OpenClaw.
- Default models and capabilities are discovered from `renoise model --json` at runtime.
- Multi-shot narrative workflow: story gate → consistency manifest (characters / props / scenes / style bible / transitions / spoken language), post-generation QC.
- New generation kinds and workflows are exposed through live CLI model capabilities.
- Model-specific reference handling follows live CLI guidance; the plugin-side facepass/original-Seedance flow and deprecated `asset`/`character` commands are retired.

## Feedback / 反馈

Hit a bug or have feedback on the experience, generation quality, or cross-shot consistency? Open an issue — the repo ships guided forms:

- 💬 **[Experience feedback](https://github.com/renoise-ai/renoise-plugins-official/issues/new?template=feedback.yml)** — usage experience, generation quality, consistency, workflow suggestions.
- 🐞 **[Bug report](https://github.com/renoise-ai/renoise-plugins-official/issues/new?template=bug_report.yml)** — reproducible defects.

When it involves a generation, include the **Task ID** (`renoise task get <id>`) and an output link/screenshot — that helps us most. Account / credits / API-key matters go to https://www.renoise.ai/developer, not the issue tracker.

有体验反馈或遇到 bug？到 **Issues → New issue** 选「💬 体验反馈」或「🐞 Bug 报告」按表单填写；涉及生成请附 **Task ID** 和产物链接/截图。账户 / 余额 / API Key 问题请到 https://www.renoise.ai/developer。
