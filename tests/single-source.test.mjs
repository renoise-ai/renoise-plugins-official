import assert from 'node:assert/strict';
import { execFileSync, spawnSync } from 'node:child_process';
import { existsSync, mkdtempSync, readFileSync, rmSync, symlinkSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { join, resolve } from 'node:path';
import test from 'node:test';
import { compareVersions, expectedChecksum, hasRequiredCommands, planFromManifest, platformInfo, selectArchive } from '../skills/renoise-setup/scripts/install-cli.mjs';

const readJSON = (path) => JSON.parse(readFileSync(path, 'utf8'));

const removed = [
  'skills/renoise-gen',
  'skills/gemini-gen',
  'skills/renoise-cli/renoise-cli.mjs',
  'skills/renoise-cli/renoise-cli-legacy.mjs',
  'skills/renoise-cli/credential.mjs',
  'skills/renoise-cli/references/api-endpoints.md',
  'skills/renoise-cli/references/video-capabilities.md',
  'skills/renoise-cli/scripts/upload.mjs',
  'skills/director/scripts',
  'skills/director/examples',
  'skills/director/commercial/scenario-a-viral.md',
  'hooks/hooks.json',
  'hooks/session-start.sh',
  'skills/renoise-cli/examples',
  '.mcp.json',
  '.codex-plugin/plugin.json',
  'openai-plugin',
  'skills/video-download',
  'skills/renoise-cli/scripts',
  'skills/director/commercial/scenario-b-brand.md',
  'skills/director/references/visual-dev.md',
];

test('skill manifest separates portable creative methods from local execution', () => {
  const manifest = readJSON('skills/manifest.json');
  assert.equal(manifest.schemaVersion, 1);
  assert.equal(manifest.pluginVersion, readJSON('package.json').version);

  const byId = new Map(manifest.skills.map((skill) => [skill.id, skill]));
  assert.deepEqual([...byId.keys()].sort(), [
    'canvas',
    'creative-direction',
    'director',
    'model-routing',
    'renoise-cli',
    'renoise-setup',
    'storyboard-sheet',
    'video-fission',
    'video-remake',
  ]);
  assert.equal(byId.get('director').runtime, 'portable');
  assert.equal(byId.get('creative-direction').runtime, 'portable');
  assert.deepEqual(byId.get('creative-direction').requires, []);
  assert.equal(byId.get('model-routing').runtime, 'portable');
  assert.equal(byId.get('storyboard-sheet').runtime, 'portable');
  assert.equal(byId.get('video-fission').runtime, 'portable');
  assert.equal(byId.get('video-remake').runtime, 'portable');
  for (const id of ['renoise-cli', 'renoise-setup']) {
    assert.equal(byId.get(id).runtime, 'local-cli');
  }
  assert.equal(byId.get('canvas').runtime, 'local-mcp-app');
  assert.ok(byId.get('canvas').requires.includes('mcp-apps'));
  assert.ok(byId.get('director').requires.includes('tasks.create'));
  assert.ok(byId.get('director').optional.includes('media.analyze'));
  assert.ok(byId.get('storyboard-sheet').optional.includes('tasks.create'));
  assert.ok(byId.get('video-fission').requires.includes('media.analyze'));
  assert.ok(byId.get('video-fission').requires.includes('tasks.create'));
  assert.ok(byId.get('video-remake').requires.includes('media.analyze'));
  assert.ok(byId.get('video-remake').requires.includes('tasks.create'));
});

test('standalone skills package is dependency-free and reproducible', () => {
  const pkg = readJSON('skills/package.json');
  const manifest = readJSON('skills/manifest.json');
  assert.equal(pkg.name, '@renoise/skills');
  assert.equal(pkg.private, true);
  assert.equal(pkg.dependencies, undefined);
  assert.equal(pkg.devDependencies, undefined);
  assert.equal(pkg.scripts, undefined);

  const pack = () => JSON.parse(execFileSync('npm', ['pack', '--dry-run', '--json'], {
    cwd: 'skills',
    encoding: 'utf8',
  }))[0];
  const first = pack();
  const second = pack();
  assert.deepEqual(first.files, second.files);
  assert.equal(first.size, second.size);

  const packedFiles = new Set(first.files.map(({ path }) => path));
  assert.ok(packedFiles.has('manifest.json'));
  for (const skill of manifest.skills) {
    for (const file of new Set([skill.entry, ...(skill.files ?? []), ...(skill.sandboxFiles ?? [])])) {
      assert.match(file, /^skills\//);
      const packageFile = file.slice('skills/'.length);
      assert.ok(packedFiles.has(packageFile), `${packageFile} missing from @renoise/skills`);
    }
  }
  assert.ok([...packedFiles].every(file => !/^(?:features|src)\//.test(file)));
});

test('sandbox files of a portable skill are its own scripts, installed only where a shell runs them', () => {
  // A portable skill stays runtime-neutral in its text (files); scripts it can use where a shell with rn exists
  // (the Renoise sandbox, a local shell) are sandboxFiles, which hosts without a shell never load.
  const manifest = readJSON('skills/manifest.json');
  for (const skill of manifest.skills.filter((entry) => entry.sandboxFiles)) {
    assert.equal(skill.runtime, 'portable', `${skill.id}: sandboxFiles belong to portable skills`);
    for (const path of skill.sandboxFiles) {
      assert.ok(path.startsWith(`skills/${skill.id}/scripts/`), `${path} must be under skills/${skill.id}/scripts/`);
      assert.ok(existsSync(path), `${path} must exist`);
      assert.ok(!skill.files.includes(path), `${path} is a sandbox file, not a text file`);
    }
  }
  const remake = manifest.skills.find((entry) => entry.id === 'video-remake');
  assert.ok(remake.files.includes('skills/video-remake/references/measured.md'));
  assert.match(readFileSync('skills/video-remake/SKILL.md', 'utf8'), /## Choose the Route/);
});

test('portable skill files contain no local execution instructions', () => {
  const manifest = readJSON('skills/manifest.json');
  const forbidden = [
    /allowed-tools:[^\n]*(?:Bash|Write|Edit)/i,
    /```(?:bash|sh|shell|powershell)/i,
    /(?:^|\n)\s*(?:renoise|ffmpeg|curl|wget|node|python|docker)\s+/i,
    /\$\{(?:CLAUDE_SKILL_DIR|CLAUDE_PLUGIN_ROOT)\}/,
    /command -v|Get-Command|prompt-file|Managed Agent Runtime/,
    /`renoise_[a-z]/,
    /\bcreate_(?:task|video_fission)\b|spending card|\bRun all\b/i,
  ];

  for (const skill of manifest.skills.filter((entry) => entry.runtime === 'portable')) {
    assert.ok(skill.files?.length, `${skill.id} must list its portable source files`);
    assert.ok(skill.files.includes(skill.entry), `${skill.id} entry must be portable`);
    for (const path of skill.files) {
      assert.ok(existsSync(path), `${path} must exist`);
      const instructions = readFileSync(path, 'utf8');
      for (const pattern of forbidden) {
        assert.doesNotMatch(instructions, pattern, `${path} must stay runtime-neutral`);
      }
    }
  }
});

test('conversations use the Renoise MCP tools; renoise-cli is for terminals, scripts, and local helpers', () => {
  for (const path of removed) assert.equal(existsSync(path), false, `${path} must not return`);
  const cli = readFileSync('skills/renoise-cli/SKILL.md', 'utf8');
  assert.match(cli, /^name: renoise-cli$/m);
  assert.match(cli, /local-only/i);
  assert.match(cli, /user-invocable: false/);
  assert.match(cli, /every Renoise operation goes through the Renoise MCP tools/i);
  assert.match(cli, /Never create a paid task from a conversation through `renoise task create`/);
  assert.match(cli, /do not fall back to the CLI/i);
  assert.match(cli, /renoise-setup\/SKILL\.md/);
  assert.doesNotMatch(cli, /## Cost Gate|--prompt-file|Managed Agent Runtime|renoise_[a-z]/);
  assert.match(cli, /uv tool install "renoise-kit\[all\]"/, 'local editing and checks use the rn kit');
});

test('annotation-board source-video edits keep the Seedance edit contract on the MCP tools', () => {
  const canvas = readFileSync('skills/canvas/SKILL.md', 'utf8');
  assert.match(canvas, /`duration: -1`, `ratio: "adaptive"`/);
  assert.match(canvas, /passing that exact task in `estimate_cost` `tasks`/);
  assert.doesNotMatch(canvas, /`edit: true`|hasVideoReference/);
  assert.match(canvas, /\[Edit the video as instructed above\]/);
  assert.match(canvas, /source-video edit trigger paired with `duration: -1`/i);
  assert.match(canvas, /`scope: "mask"`/);
  assert.doesNotMatch(canvas, /renoise (?:task|upload)|--prompt-file|--materials/);
  assert.match(canvas, /do not append it to forward\/backward extension or ordinary reference generation prompts/i);
  assert.match(canvas, /Seedance 2\.5-only time adapter/i);
  assert.match(canvas, /floor\(sourceTimeMs \/ 1000\)/);
  assert.match(canvas, /Do not apply this normalization to any other image or video model/i);
});

test('annotation-board paid generation requires post-preview approval bound to the exact prompt and arguments', () => {
  const canvas = readFileSync('skills/canvas/SKILL.md', 'utf8');
  
  assert.match(canvas, /Pressing \*\*Send annotation\*\* approves only the structured annotation intent/i);
  assert.match(canvas, /Do not call `create_tasks` in the same turn that first presents the proposal/i);
  assert.match(canvas, /Any prompt, model, parameter, material, or price change invalidates the approval/i);
  assert.match(canvas, /follow the Renoise tools' approval rule for paid work/i);
  assert.match(canvas, /直接生成/);
});

test('model routing keeps only useful specialists without replacing capabilities', () => {
  const routing = readFileSync('skills/model-routing/SKILL.md', 'utf8');
  for (const model of [
    'seedance-2.5-byteplus',
    'nano-banana-2.1', 'wan3.0-video', 'wan3.0-video-prime',
    'mj-v8.2', 'gpt-image-2.6-sunburst', 'gpt-image-2.6-flare',
    'lyria-pro', 'seed-audio-1.0', 'grok-image', 'grok-image-quality',
    'grok-video-1.5', 'gemini-omni-flash', 'hailuo-h3', 'hailuo-h3-max', 'h3-max-turbo',
    'upscale-video-topaz-starlight-2.5', 'omnihuman-2.0', 'mureka-song-9', 'eleven-sfx-v2', 'gemini-3.8-flash-tts',
    'flux-3-video', 'flux-3-max', 'kling-4.0', 'kling-4.0-omni', 'vidu-q4',
  ]) assert.ok(routing.includes(`\`${model}\``), `${model} routing missing`);
  for (const obsolete of [
    'seedance-2.0-byteplus', 'seedance-2.0-fast-byteplus', 'seedance-2.0-mini-byteplus',
    'gpt-image-2', 'gpt-image-2.5-sunburst', 'gpt-image-2.5-flare', 'grok-video', 'midjourney-v7', 'mj-v8.1', 'happyhorse-1.0', 'kling-3.0-omni', 'lyria-clip',
    'nano-banana-2', 'nano-banana-2-lite', 'nano-banana-pro', 'seedream-5-0-lite',
  ]) assert.ok(!routing.includes(`\`${obsolete}\``), `${obsolete} should not be routed`);
  assert.match(routing, /Route only to the newest live generation/);
  assert.match(routing, /OmniHuman 2\.0 — the audio drives the performance/);
  assert.match(readFileSync('skills/director/commercial/scenario-d-ugc.md', 'utf8'), /`omnihuman-2\.0`/);
  assert.match(routing, /generic GPT Image request to GPT Image 2\.6 Sunburst/);
  assert.match(routing, /`gpt-image-2\.6-sunburst` with `outputFormat: "gif"`/);
  assert.match(routing, /use Flare when explicitly requested/i);
  assert.match(routing, /H3 Max[\s\S]*live image\/video\/audio reference roles/);
  assert.match(routing, /source video needs `reference_video`; `first_frame` alone is not equivalent/);
  assert.match(routing, /H3 Max Turbo supports text and first\/last-frame modes, not generic references/);
  assert.match(routing, /Live model capabilities are authoritative/);
  // model-routing only picks and prompts generation models; the generate-or-build decision lives in the director
  assert.doesNotMatch(routing, /Generate or Build/);
  assert.match(routing, /## References and Edits/);
});

test('prompt examples use canonical material ID tokens', () => {
  const promptCraft = readFileSync('skills/director/references/prompt-craft.md', 'utf8');
  const directorFiles = [
    promptCraft,
    readFileSync('skills/video-remake/SKILL.md', 'utf8'),
    ...['INDEX.md', 'scenario-c-tvc.md', 'scenario-d-ugc.md']
      .map((file) => readFileSync(`skills/director/commercial/${file}`, 'utf8')),
  ].join('\n');
  assert.match(promptCraft, /@material:101/);
  assert.doesNotMatch(directorFiles, /@(?:Image|Video)\s*\d/i);
  assert.doesNotMatch(directorFiles, /@[\w-]+\.(?:png|jpe?g|webp|mp4|mov)\b/i);
});

test('package metadata is the manifest source of truth', () => {
  const pkg = readJSON('package.json');
  const portable = readJSON('plugin.json');
  const manifests = [readJSON('.claude-plugin/plugin.json'), portable, readJSON('openclaw.plugin.json')];
  for (const manifest of manifests) {
    assert.equal(manifest.version, pkg.version);
    assert.equal(manifest.description, pkg.description);
  }

  const claudeMarketplacePlugin = readJSON('.claude-plugin/marketplace.json').plugins[0];
  assert.equal(claudeMarketplacePlugin.version, pkg.version);
  assert.equal(claudeMarketplacePlugin.description, pkg.description);

  // One listing for Codex, ChatGPT, and the OpenAI directories (root plugin.json, Agent Plugins).
  const listing = portable.extensions['com.openai'].interface;
  assert.deepEqual(listing.capabilities, ['Interactive', 'Read', 'Write']);
  assert.ok(existsSync(listing.composerIcon));
  assert.ok(existsSync(listing.logo));
  assert.match(readFileSync(listing.logo, 'utf8'), /<rect[^>]+fill="#2B2B2B"/);

  // One MCP config for every host: Claude Code reads it through its manifest, Codex and ChatGPT natively.
  // Claude Code launches stdio servers from the project directory and ignores a plugin-relative `cwd`,
  // so its manifest overrides only the whiteboard entry with a ${CLAUDE_PLUGIN_ROOT} path.
  assert.deepEqual(manifests[0].mcpServers, [
    './mcp.json',
    {
      'renoise-whiteboard': {
        type: 'stdio',
        command: 'node',
        args: ['${CLAUDE_PLUGIN_ROOT}/features/canvas/dist/server.mjs'],
      },
    },
  ]);
  const servers = readJSON('mcp.json').mcpServers;
  assert.deepEqual(servers.renoise, { type: 'streamable-http', url: 'https://renoise.ai/api/public/mcp' });

  const marketplace = readJSON('.agents/plugins/marketplace.json');
  assert.equal(marketplace.plugins[0].name, portable.name);
  assert.equal(marketplace.plugins[0].source.url, pkg.repository.url);
  assert.equal(marketplace.plugins[0].policy.authentication, 'ON_USE');
});

test('desktop metadata exposes portable entries plus setup', () => {
  const entries = {
    director: 'Create with Renoise',
    'storyboard-sheet': 'Build Storyboard',
    'renoise-setup': 'Setup / Account',
  };
  for (const [skill, displayName] of Object.entries(entries)) {
    const metadata = readFileSync(`skills/${skill}/agents/openai.yaml`, 'utf8');
    assert.match(metadata, new RegExp(`display_name: "${displayName.replace('/', '\\/')}"`));
    assert.match(metadata, new RegExp(`\\$${skill}`));
  }
  assert.match(readFileSync('skills/renoise-setup/agents/openai.yaml', 'utf8'), /allow_implicit_invocation: true/);
  const openclawSkills = readJSON('openclaw.plugin.json').skills;
  assert.ok(openclawSkills.includes('skills/renoise-cli'));
  assert.ok(openclawSkills.includes('skills/video-fission'));
  assert.ok(openclawSkills.includes('skills/video-remake'));
  assert.ok(!openclawSkills.includes('skills/renoise-gen'));
  assert.ok(!openclawSkills.includes('skills/gemini-gen'));
});

test('installer selects and verifies macOS, Windows, and Linux archives', () => {
  const assets = [
    { name: 'renoise-cli_0.2.0_darwin_amd64.tar.gz' },
    { name: 'renoise-cli_0.2.0_darwin_arm64.tar.gz' },
    { name: 'renoise-cli_0.2.0_linux_amd64.tar.gz' },
    { name: 'renoise-cli_0.2.0_linux_arm64.tar.gz' },
    { name: 'renoise-cli_0.2.0_windows_amd64.zip' },
    { name: 'renoise-cli_0.2.0_windows_arm64.zip' },
  ];
  const targets = [
    ['darwin', 'x64'], ['darwin', 'arm64'],
    ['linux', 'x64'], ['linux', 'arm64'],
    ['win32', 'x64'], ['win32', 'arm64'],
  ];
  targets.forEach(([platform, arch], index) => {
    assert.equal(selectArchive(assets, platformInfo(platform, arch, { LOCALAPPDATA: 'C:\\Users\\test' })).name, assets[index].name);
  });
  const plan = planFromManifest({
    schemaVersion: 1,
    version: 'v0.2.0',
    assets: assets.map(({ name }) => name),
    checksums: 'checksums.txt',
  }, platformInfo('darwin', 'arm64'));
  assert.equal(plan.archive.browser_download_url, `https://download.renoise.ai/cli/v0.2.0/${assets[1].name}`);
  assert.equal(expectedChecksum(`${'a'.repeat(64)}  ${assets[0].name}\n`, assets[0].name), 'a'.repeat(64));
  const createHelp = 'Usage: renoise task create\nFlags:\n      --prompt-file string';
  const costHelp = 'Usage: renoise task cost\nFlags:\n      --edit';
  const waitHelp = 'Usage: renoise task wait';
  const analyzeHelp = 'Usage: renoise analyze <image-or-video>\nFlags:\n      --mode string';
  assert.equal(hasRequiredCommands(createHelp, costHelp, waitHelp, 'Usage: renoise auth exec', 'Flags:\n      --web', analyzeHelp), true);
  assert.equal(hasRequiredCommands(createHelp, 'Usage: renoise task cost', waitHelp, 'Usage: renoise auth exec', 'Flags:\n      --web', analyzeHelp), false);
  assert.equal(hasRequiredCommands('Usage: renoise task create', costHelp, waitHelp, 'Usage: renoise auth exec', 'Flags:\n      --web', analyzeHelp), false);
  assert.equal(hasRequiredCommands(createHelp, costHelp, waitHelp, 'Usage: renoise auth exec', 'Usage: renoise auth login', analyzeHelp), false);
  assert.equal(hasRequiredCommands(createHelp, costHelp, waitHelp, 'Usage: renoise auth exec', 'Flags:\n      --web', 'Usage: renoise analyze'), false);
  assert.ok(compareVersions('0.3.0', '0.2.0') > 0);
  assert.equal(compareVersions('0.2.0', '0.2.0'), 0);
});

test('installer runs when invoked through a symlink', () => {
  const dir = mkdtempSync(join(tmpdir(), 'renoise-install-cli-'));
  try {
    const link = join(dir, 'install-cli.mjs');
    symlinkSync(resolve('skills/renoise-setup/scripts/install-cli.mjs'), link);
    const result = spawnSync(process.execPath, [link, '--bogus'], { encoding: 'utf8' });
    assert.equal(result.status, 1);
    assert.match(result.stderr, /Usage: install-cli\.mjs/);
  } finally {
    rmSync(dir, { recursive: true, force: true });
  }
});

test('setup keeps managed CLI current and still gates manual install', () => {
  const setup = readFileSync('skills/renoise-setup/SKILL.md', 'utf8');
  const cli = readFileSync('skills/renoise-cli/SKILL.md', 'utf8');
  const installer = readFileSync('skills/renoise-setup/scripts/install-cli.mjs', 'utf8');
  assert.match(setup, /https:\/\/download\.renoise\.ai\/cli\/latest\.json/);
  assert.doesNotMatch(setup, /GitHub Releases|go install/);
  assert.match(setup, /--check/);
  assert.match(setup, /--ensure/);
  assert.match(setup, /ask for explicit confirmation/i);
  assert.match(setup, /--install/);
  assert.match(setup, /renoise auth login --web --json/);
  assert.match(setup, /never ask them to open a terminal/);
  assert.match(setup, /## 1\. Connect the Renoise Tools[\s\S]*https:\/\/renoise\.ai\/api\/public\/mcp[\s\S]*`get_account`[\s\S]*## 2\. Optional: the Native CLI/);
  assert.match(cli, /install-cli\.mjs" --ensure/);
  assert.match(installer, /--ensure/);
  assert.match(installer, /needsManagedUpdate/);
});

test('director stays a thin router of craft', () => {
  const director = readFileSync('skills/director/SKILL.md', 'utf8');
  const narrative = readFileSync('skills/director/workflows/narrative.md', 'utf8');
  const index = readFileSync('skills/director/commercial/INDEX.md', 'utf8');
  const files = readJSON('skills/manifest.json').skills.find(({ id }) => id === 'director').files;
  assert.ok(Buffer.byteLength(director) < 8_000, 'director entry point should stay under 8 KB');
  assert.ok(files.includes('skills/director/workflows/narrative.md'));
  assert.ok(files.includes('skills/director/references/code-built-video.md'));
  assert.match(director, /commercial\/INDEX\.md/);
  assert.match(director, /workflows\/narrative\.md/);
  assert.match(director, /references\/code-built-video\.md/);
  assert.match(director, /storyboard-sheet/);
  assert.match(director, /\*\*Generate or build\.\*\*[\s\S]*never ask a video model for exact text or numbers/);
  assert.match(director, /multiple controlled variants from one supplied source/i);
  assert.match(index, /scenario-d-ugc\.md[\s\S]*scenario-c-tvc\.md/);
  assert.match(narrative, /Character design sheet for \[NAME\]/, 'the anchors live in the narrative workflow');
  assert.doesNotMatch([director, narrative].join('\n'), /wait for (?:explicit )?(?:approval|confirmation)/i);
});

test('portable skills hold craft, not host plumbing or capability limits', () => {
  // Approval, task tracking and delivery format belong to the agent's instructions and the Renoise tools; the agent
  // checks picture and sound itself instead of handing checks to the user.
  const manifest = readJSON('skills/manifest.json');
  for (const skill of manifest.skills.filter((entry) => entry.runtime === 'portable')) {
    for (const path of skill.files) {
      const text = readFileSync(path, 'utf8');
      assert.doesNotMatch(text, /active host|host execution workflow|host's (?:approval|review) policy|text-confirmation pause/i, `${path}: host plumbing`);
      assert.doesNotMatch(text, /(?:cannot|can't|unable to) (?:watch|hear|listen)/i, `${path}: capability limit`);
      assert.doesNotMatch(text, /ask the user to (?:review|watch|listen)/i, `${path}: check handed to the user`);
      assert.doesNotMatch(text, /full server filename/i, `${path}: materials are named by @material tokens`);
    }
  }
});

test('video fission analyzes first and generates one batch of variants on the source', () => {
  const fission = readFileSync('skills/video-fission/SKILL.md', 'utf8');
  const director = readFileSync('skills/director/SKILL.md', 'utf8');
  assert.match(fission, /owner-authorized source video/i);
  assert.match(fission, /Analyze the source before deciding what varies/);
  assert.match(fission, /request already names a usable axis[\s\S]*without asking/);
  assert.match(fission, /Use \*\*4 outputs\*\*[\s\S]*do not ask to confirm the default/);
  assert.match(fission, /one axis, or at most two/);
  assert.match(fission, /genuinely distinct hypothesis/);
  assert.match(fission, /model-routing[\s\S]*`reference_video`/, 'the model is routed, not hardcoded');
  assert.match(fission, /sole `reference_video` and call it `Video 1`/);
  assert.match(fission, /Do not replace it with an extracted frame/);
  assert.match(fission, /one `create_tasks` call/);
  assert.match(director, /explicit video fission or multiple controlled variants/i);
  assert.match(director, /use (?:the )?video-fission/i);
});

test('reference-video remake keeps the source attached and fills slots first', () => {
  const director = readFileSync('skills/director/SKILL.md', 'utf8');
  const remake = readFileSync('skills/video-remake/SKILL.md', 'utf8');
  assert.match(director, /剪同款[\s\S]*video-remake/);
  assert.match(remake, /^name: video-remake$/m);
  assert.match(remake, /source video is always attached/i);
  assert.match(remake, /`analyze_media` in template\/video mode/);
  assert.match(remake, /review checkpoint/);
  assert.match(remake, /No placeholder may remain/);
  assert.doesNotMatch(remake, /renoise analyze|prompt-file|remake-plan\.json/);
});

test('moderation waits for an explicit host error', () => {
  const director = readFileSync('skills/director/SKILL.md', 'utf8');
  const cli = readFileSync('skills/renoise-cli/SKILL.md', 'utf8');
  const remake = readFileSync('skills/video-remake/SKILL.md', 'utf8');
  for (const skill of [director, cli, remake]) {
    assert.match(skill, /Do not pre-screen/);
    assert.match(skill, /INPUT_\*/);
    assert.match(skill, /OUTPUT_\*/);
    assert.doesNotMatch(skill, /hard blocks|First check whether the prompt or materials/);
  }
});
