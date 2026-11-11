# Third-party notices

The Renoise annotation whiteboard bundles the following runtime libraries in its generated distribution. Their copyrights remain with their respective authors.

| Package | Version | License | Project |
|---|---:|---|---|
| Fabric.js | 7.4.0 | MIT | https://github.com/fabricjs/fabric.js |
| React | 19.2.4 | MIT | https://github.com/facebook/react |
| React DOM | 19.2.4 | MIT | https://github.com/facebook/react |
| Lexical (`lexical`, `@lexical/react`, `@lexical/utils`) | 0.31.2 | MIT | https://github.com/facebook/lexical |
| Konva | 10.3.0 | MIT | https://github.com/konvajs/konva |
| React Konva | 19.2.5 | MIT | https://github.com/konvajs/react-konva |
| Lucide React | 0.536.0 | ISC | https://github.com/lucide-icons/lucide |
| MCP Apps SDK | 1.7.5 | Apache-2.0 | https://github.com/modelcontextprotocol/ext-apps |
| Model Context Protocol TypeScript SDK | 1.30.0 | MIT | https://github.com/modelcontextprotocol/typescript-sdk |
| Zod | 4.4.3 | MIT | https://github.com/colinhacks/zod |
| Ajv | 8.20.0 | MIT | https://github.com/ajv-validator/ajv |
| ajv-formats | 3.0.1 | MIT | https://github.com/ajv-validator/ajv-formats |
| fast-deep-equal | 3.1.3 | MIT | https://github.com/epoberezkin/fast-deep-equal |
| fast-uri | 3.1.4 | BSD-3-Clause | https://github.com/fastify/fast-uri |
| json-schema-traverse | 1.0.0 | MIT | https://github.com/epoberezkin/json-schema-traverse |
| Scheduler | 0.26.0 | MIT | https://github.com/facebook/react |
| zod-to-json-schema | 3.25.2 | ISC | https://github.com/StefanTerdell/zod-to-json-schema |

Build-only dependencies are declared in `package.json`. The annotation board includes Konva and React Konva for its focused frame-annotation overlay; it does not include tldraw, `@tldraw/*`, Excalidraw, or React Flow.

## vox-collage

`skills/vox-collage/scripts/engine/public/sfx/` bundles sound effects that are all CC0 (no attribution required); the
per-file list is in `skills/vox-collage/scripts/engine/SFX_SOURCES.md`.

| Assets | License | Project |
|---|---|---|
| Kenney UI Audio, Interface Sounds, Impact Sounds, RPG Audio (selected files) | CC0 1.0 | https://kenney.nl/assets |
| "Keyboard Sounds" by unicaegames | CC0 1.0 | https://opengameart.org/content/keyboard-sounds |

The film engine is installed with npm when a project is created and is not bundled here: Remotion 4.0.408
(https://www.remotion.dev, Remotion License: free for individuals and companies of up to three people, a company
license otherwise), React 19.0.0 (MIT) and TypeScript 5.8.2 (Apache-2.0). The scripts call ffmpeg and, depending on the
host, whisper.cpp (MIT) or faster-whisper (MIT) and rembg (MIT); none of them is bundled.
