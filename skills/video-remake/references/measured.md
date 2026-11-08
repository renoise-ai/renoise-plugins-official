# Measured Remake (the shell route of `video-remake`)

> Paths: `<skill>` is the `video-remake` folder, the one holding SKILL.md (this file is in its `references/`); replace
> `<skill>/scripts/…` with its absolute path when you run a command. On the Renoise sandbox, loading the skill puts the
> folder there and says where; on a local shell it is the plugin's own skill folder.

A remake keeps the source's timing, camera, cutting, pacing and look, and swaps what the user asked to swap. This
skill measures the source first, then makes each shot the way it is best made again:

| Route | What | Made by |
|-|-|-|
| `generate` | footage, AI video, 3D, animation | a video model, with the source clip of those shots as reference video. Consecutive same-scene shots share one call (a **generation unit**); a shot longer than one call is split into parts |
| `code` | titles, cards, UI, charts, screen recordings | code (or the user's own file); never redrawn by a video model |
| `still` | a held photo, or a pan / zoom over one | one image (the user's, or generated), moved locally with the measured zoom / pan |
| `keep` | footage the user owns and keeps as it is | cut from the source |

Each generated shot opens on a **keyframe**: the source frame with the user's elements swapped in by an image model,
approved before any video is generated. The units are generated in one batch, each checked against its own source clip,
and the ones that fail are regenerated together. Text laid over the picture (titles, subtitles, labels) is set in code over text-free footage. The
pieces go back on the source's timeline as an rn edit (`edit.json`), rendered, checked and compared with the source by
`rn` before delivery.

The current host owns authorized media analysis, materials, live capabilities, costs, spending approvals and tasks.
This skill owns the measurements, routes, slot matching, creative decisions and resumable plan state.

## Where It Runs

- **Renoise sandbox** (the `sandbox` tool): a remote Linux machine with ffmpeg, `rn` (renoise-kit), Python, numpy, OpenCV
  and Pillow. It is a
  Director Mode (subscription) feature: `get_account` shows `commerce.sandbox: true`, otherwise sandbox calls fail with
  `SUBSCRIPTION_REQUIRED`. Read `~/TOOLBOX.md` before the first piece of work there. Work in a project folder of its own,
  `~/projects/<yyyy-mm-dd>-remake-<slug>/`. The scripts use every CPU the sandbox may use (they read its CPU limit, which
  differs between sandboxes), so their run time varies: start `analyze.py`, `check_units.py` and `build_edit.py
  --render` in the background, as anything that may take longer than about 45 seconds. When the host reports background
  jobs back to you, go on with other work or end the turn and wait for that report. Otherwise wait with one bounded loop
  that returns as soon as the job ends (check its `.exit` file every 2 s, up to about 100 s) and then read the log tail;
  never sleep a fixed time.
  `analyze.py --jobs N` caps the CPUs it uses. You
  cannot watch or listen: look at the storyboard, contact sheets and stills as images.
- **A local shell**: the same scripts; run `python3 <skill>/scripts/doctor.py` first and install what it marks ✗.
- **No shell, or no sandbox for this account**: follow SKILL.md's single-generation route instead.

Never ask the user for paths inside the sandbox or to run anything themselves.

**Waiting is most of a remake's time** (generation rounds of 3 to 10 minutes each), then your own turns. So:
- generate in as few rounds as possible: all keyframes in one batch, all units in one batch once the keyframes are
  approved, and every failing unit regenerated together;
- put the commands of one step into one call (measure and storyboard; check and sheet), since every call costs a turn.

## Runtime Boundary

Use only capabilities and references exposed by the host: `get_account`, `analyze_media`, `list_models`,
`estimate_cost`, `create_tasks`, `wait_tasks`, `download_results`, `upload_files`, `show_result`, and the material tools.
Do not emulate missing analysis, material or task operations. Before selecting a model or writing prompts,
`load_skill model-routing` and inspect live capabilities.

Use the user's language for analysis, plans, approvals and results. If retained or replacement content contains
dialogue, voiceover or narration, use the explicitly requested or safely inferable spoken language; clarify only when
ambiguous, and keep every spoken line verbatim in that language.

**A linked source.** When the user gives the source as a link (X, YouTube, TikTok, Douyin, Instagram, Bilibili and other
video pages), download it in the sandbox with yt-dlp, save it as a material with `upload_files`, and use that material from
then on. Ask the user to upload the file only when the download is blocked or fails.

## Non-Negotiable Source Policy

Every generation call carries the source: each unit gets **its own source clip** (the unit's shots, inserts removed,
cut by `plan_units.py --cut`) through a compatible video role advertised by the selected model.

1. Query live video-model capabilities.
2. Select a model that advertises a compatible source / reference-video role and every image role the replacement
   slots need, and whose reference-video length limit covers the longest unit clip.
3. Check guidance, reference counts, duration, ratio, audio behavior and role combinations.
4. If no model supports the complete source-clip + replacement-image combination, stop and explain. Never omit the
   source clip or invent a role.

Each prompt states that the source clip supplies timing, camera motion, composition, transitions, effects, pacing and
emotional beats, and the replacement materials supply identity, product, wardrobe, props and other slotted content. This
text reduces accidental copying but is not a security boundary; normal moderation rules still apply.

## Phase 1 — Measure and Look

1. **Get the source into the project.** `download_results` gives a curl command for a material or attachment; run it in
   the project folder. Run `python3 <skill>/scripts/doctor.py` once per sandbox.
2. **Measure.** `python3 <skill>/scripts/analyze.py src.mp4 -o an` in the background; it prints each shot as it is
   measured by `rn shots` (renoise-kit 0.7 or newer). It writes `an/analysis.json` (every shot: start, end, how it begins, measured route,
   what it looks like, evidence, and a `check` reason when the measurement is borderline), `an/storyboard.jpg`,
   `an/shots/` (first, middle, last frame and a contact sheet per shot) and `an/review.json` to fill. With rn 0.7+ each
   shot also has its `transition` (a dissolve's or wipe's frames, a wipe's side, a fade's colour and frames out, held and
   in), its `speed` (how much the picture changes in each quarter, the longest hold) and its first frame against the beat
   of the source's sound (`beat`, with the whole film's `beats`), and its `open_frame`: the first frame clear of a
   dissolve or fade into it (`an/shots/open/`), which is the frame its keyframe opens on. Add `--text` when the source has titles or captions to
   set again: `an/overlays_draft.json` lists the text rn reads on screen and the places it keeps appearing (a caption
   band: where, how big, what colours, when). It costs about 2 s per second of video.
3. **Analyze.** Use the host's media-analysis capability in template / video mode on the source material: content,
   subjects, dialogue, music and mood. If that capability is unavailable, stop.
4. **Look, then reconcile.**
   - Open `storyboard.jpg`, then the contact sheet of every shot marked `?` and of any shot whose route you doubt; pull
     more frames with ffmpeg where needed. Decide those routes from the frames yourself before reading the analysis's
     wording about them: image readers state wrong reasons confidently.
   - Timing comes from the measurements: cut points, shot lengths and transitions in `analysis.json` win over times or
     counts in the analysis text. Where they disagree, look at the frames around that moment.
   - The routes: `code` only for pictures made of text, UI, charts, cards or a screen; a rendered 3D or flat-shaded
     scene with characters or objects in motion is `generate`. `still` only when one image is held or panned with
     nothing inside it moving. `keep` only when the user says that footage is theirs and should stay.
5. **Fill `an/review.json`.** Under `shots`, by shot number, set only what you change or add:
   - `route` when the measured one is wrong;
   - `description` (what is on screen) and `prompt`: the English video prompt for **this shot alone**: subject,
     action from start to end state, camera. Unit prompts are joined from these, so no shared style here;
   - `image_prompt` for stills; `supply` when the user must provide something (their screen recording, a product photo).
   Top level: `cast` (characters, products and props across shots, described so each can be drawn again; each becomes a
   replacement slot or a fixed element) and `overlays`: every line of text laid over the picture in the source (titles,
   subtitles, labels), rewritten for the remake when the user's content changes it, as
   `{"t0", "t1", "text", "x", "y", "size", "color", "outline", "box"}` (positions and size as fractions of the frame,
   colours `#RRGGBB`, `box` `#RRGGBBAA`). Take the style (place, size, colours) from `overlays_draft.json` when you ran
   `--text`, and the words from the frames: OCR reads styled type in pieces. Text on things inside the scene (signs,
   packaging, an app's own UI) stays in the shot's prompt.

## Phase 2 — Plan the Remake

1. **Model.** From `model-routing` and `list_models`, pick the video model under the source policy. Note its longest and
   shortest generation, whether its live guidance says it makes several shots with hard cuts in one generation, and
   which image roles it takes next to a reference video (first frame, reference images). Pick an image model for slots
   and keyframes too: one that edits a given image with reference images.
2. **Units.** `python3 <skill>/scripts/plan_units.py an --max <longest s> --min <shortest s> [--multi-shot] --cut`. It
   groups consecutive same-scene generated shots into units (inserted code, still and kept shots do not break a unit;
   at most about 8–10 s of hard cuts per unit), splits shots longer than one call, cuts each unit's source clip into
   `an/remake/units/`, exports the source frame every keyframe starts from into `an/remake/keyframes/`, and writes
   `an/remake/plan.json` and `plan.md`. Re-run it after any change to `review.json`. With rn 0.7+ `plan.md` also lists
   the source's transitions (the edit makes them again; a unit or code part followed by a dissolve or wipe is planned
   that much longer, since the two overlap), each generated shot's pace (one that settles, speeds up or holds: put it in
   that shot's prompt), and whether the source cuts to the beat of its sound.
3. **One generation.** When `plan.json` says `single_generation: true`, the remake is one unit covering the whole source:
   the steps below still apply, with one call and nothing to assemble.
4. **Slots.** Each replaceable element in `cast` becomes a slot with an English reference-image prompt. Fill slots in this
   order: host-authorized user material that clearly matches; existing owner-scoped Renoise material the user confirms;
   a generated image from the slot prompt. Never let filename similarity alone choose a character or product. The same
   slot material goes into every unit where that element appears.
5. **Plan and cost.** Present in the user's language:
   - the source summary and warnings, with the `plan.md` table: units, calls, seconds, code parts, stills, kept shots;
   - the routes you changed from the measurement and why;
   - every slot with its proposed source; what the user must supply;
   - the overlay lines; the audio plan (below);
   - the selected image and video models; the live estimate for slot images, keyframes and every unit, plus a retry
     allowance of one regeneration per unit (Phase 3), and the balance;
   - that each unit carries its own source clip and opens on approved keyframes.

   Ask only when a slot mapping is ambiguous. Otherwise hand each missing slot image and its complete parameters to the
   host execution workflow, register each approved result as a material once, and record its material ID and full server
   filename. Show the slot images; let the user replace or regenerate any slot.
6. **Keyframes.** Every generated shot (each part of a split shot) and every still opens on a keyframe: its source frame
   (`plan.json` `keyframes[].source_frame`) with the slotted elements swapped in by the image model, everything else (framing,
   pose, camera, light, set) as in the source frame, and the overlay text (titles, subtitles, labels) removed, since it is
   set again in code. Register each source frame once, hand every keyframe to the host execution workflow, save the results
   and list them in `keyframes.json` (`{"7": "kf/kf_7.png", "12.2": "kf/kf_12_2.png"}`). Mark a shot `"keyframe": false` in
   `review.json` when nothing in it changes. Then `python3 <skill>/scripts/keyframes.py an keyframes.json` draws source |
   keyframe pairs (`an/remake/keyframes/sheet*.jpg`); show them and let the user approve, replace a slot or redo any
   keyframe. Pictures are cheap and video is not: settle the look here. Do not generate video until every required slot
   and keyframe is approved.

**Audio plan.** By default each generated or built piece keeps its own sound. When there are several units and the source
is music-driven, mute the units and lay one music bed under the whole film (the user's track, or one generated through
`model-routing`'s music route), because each unit's music would restart at its boundary. Use the source's own track only
when the user owns it. Dialogue units keep their generated voices. When `plan.md` says the source cuts to the beat, a new
bed keeps that: `build_edit.py --music` moves those cuts onto the bed's beats (Phase 4).

Keep the plan in the conversation so retries resume known task and material IDs instead of recreating charges: source
material, models, slot and keyframe materials, and per unit its clip material ID, prompt, task ID, result file and check
verdict. Do not store API keys, signed URLs, credential contents or arbitrary host paths.

## Phase 3 — Make the Pieces

**Generation units.** Inspect the model again right before generating. For each unit (and each part of a split unit):

1. Register its source clip (`an/remake/units/G1_ref.mp4`, or `G1_partN_ref.mp4`) once with `upload_files`.
2. Write the prompt: the source lock; one style line shared by all units (from `cast.style` and the analysis); the
   unit's `prompt_lines` with their timestamps, in order; every slot and keyframe as the exact `@material:{id}` token of
   its registered material ("Shot 2 opens exactly as @material:…"). Ask for no added captions, titles or labels, since
   overlays are set in code (text on things in the scene stays as the shot prompt describes it). No unresolved placeholder.
3. Assign the source clip a compatible reference-video role. The unit's first keyframe takes the first-frame role when the
   model advertises one that combines with a reference video; otherwise it and the unit's other keyframes go in as
   reference images, each tied to its shot in the prompt. Slot materials take image roles. Check combined counts and
   combinations; when references are limited, keep the source clip, then the keyframes, then the slots. Duration: the
   unit's `request_s`, or the nearest supported length at or above it. Ratio: the source's.
4. Continuity: for a unit that `continues` the previous one, or the next part of a split shot, start from the previous
   result's last frame (`rn frame prev.mp4 --last -o last.png`) when no keyframe is approved for it.

Submit every unit (and every part of a split unit) in one batch: the approved keyframes already settled the look, and one
batch waits for its slowest unit once instead of once per unit. Request a live estimate with the full material set for the batch and hand the complete arguments to the host execution workflow; record every task ID
immediately; `wait_tasks`, then `download_results` into `gen/` and add the file to `results.json` (`{"G1": "gen/G1.mp4",
"G2": ["gen/G2_part1.mp4", "gen/G2_part2.mp4"]}`).

**Check the units together when the batch is done.** `python3 <skill>/scripts/check_units.py an results.json --keyframes
keyframes.json` compares each result with its own source clip (`--only G1,G3` for some): length, cuts against the planned shot boundaries (a missing cut
merged two shots, an extra one split a shot), how the motion follows the source, a frozen tail, black frames, and words
on screen the source does not have. With rn 0.7+ it also reports a dissolve or fade where the source cuts, and a shot
whose camera clearly moves otherwise than the source's (a push-in that came out as a pull-out, a pan the other way, a
locked-off shot that drifts); each comes with the prompt change that addresses it. It also measures the result's tone
and colour against the source clip (`rn look`): a `far` grade is fixed in the edit, not by regenerating: `rn grade
result.mp4 --ref <source clip> -o G1.cube` and `"vf": "lut3d=file=G1.cube"` on that unit's clips. It writes `an/remake/checks/G1.json` and `G1.jpg` (per shot: source, keyframe,
result). Look at the sheet as well: identity, product and wardrobe are yours to judge. List every unit that fails (`check`, or a wrong subject on
its sheet), then regenerate all of them in one batch, once within the retry allowance, each with the same references and the
prompt changes its report lists (`fixes`) or its sheet calls for. If it fails again, stop spending: show the user both attempts and the
report and ask how to go on.

**Code parts.** Build each `C` part at the source's size and frame rate, exactly its length (plus its `tail_s`, when
`plan.json` has one: the next shot's dissolve or wipe runs over it), following
`director`'s `references/code-built-video.md` (`load_skill director` to read it): layout, timing and colours measured from
its contact sheet. A screen recording the user owns comes from the user; otherwise rebuild the screen in code.

**Stills.** Use the approved keyframe (or the user's image). The edit moves it with the zoom / pan measured on the source.

## Phase 4 — Assemble and Check

1. Complete `results.json` with the code parts and stills (`"C1": "code/C1.mp4"`, `"P1": "kf/kf_9.png"`). Kept shots
   need no entry; anything still missing becomes a placeholder card, so the film can be looked at before every piece exists.
2. `python3 <skill>/scripts/build_edit.py an results.json [--audio units|source|none] [--music bed.m4a]
   --render` (background). The cut comes out at the generated footage's own resolution in the source's shape, never
   larger, even when the source is 1080p: the lowest resolution unless the user asks for more (then `--width N`).
   It writes an rn edit, `an/remake/edit.json`: one main-track clip per source shot, each exactly
   the source shot's frames, taken from its unit at the planned offset (snapped to the cuts the model made, slowed when the
   generation came out short), with the overlay lines as subtitles, a short sound fade at every cut and the mix at
   -14 LUFS / -1 dBTP. The source's transitions are made again between different pieces: a dissolve or wipe overlaps
   the two for its measured frames (the wipe from the same side), a fade goes through black or white with the measured
   frames out, held and in. With `--music` and a source that cuts to the beat, each cut that was on a beat moves onto
   the bed's nearest beat, by at most `--beat-max` (0.2 s), lengthening one neighbour from its spare frames or by
   playing it up to 6% slower (`--beat-sync off` keeps the source's cut points). With `--render` it runs `rn assemble`,
   `rn qa` and `rn compare --cuts` (with rn 0.7+ `rn qa --edl` against edit.json and `rn compare --shots` too) and writes
   `an/remake/out/remake.mp4`, `compare.mp4` (source | remake), `compare-p*.jpg` and `qc.json`.
3. Check before delivering:
   - the compare sheets: every shot shows the intended subject, slot identities hold across units, overlays readable and
     inside the frame;
   - `qc.json`: `placeholders` must be empty; `qa_status` and `qa_findings` from `rn qa`; `cuts_only_in_remake` (cuts the
     source does not have) and `cuts_missing_in_remake`; `retimed` shots play slower than generated; `transitions`
     made again (`late_by_s`: the overlap sits later than the source's because a generation has no frames before its
     first) and `transitions_not_rebuilt` with the reason (a piece with no frames to spare: make it longer; a kept shot
     whose frames already hold half of the source's dissolve; a piece still missing); `rhythm` with `--music` (cuts
     moved, cuts that could not move and why, and the share of cuts on a beat: source, remake before and after). With
     rn 0.7+ also `shots_begin_differently` (a shot that begins with another transition than the source's),
     `transitions_differ` (the same transition with clearly other frames, side or colour) and `camera_differs` (every
     shot, code and still shots included, whose camera move clearly differs from the source's).
   List every failing shot first, then regenerate their units in one batch as in Phase 3. After two rounds, deliver and
   name what still looks off.
4. **Deliver.** `upload_files` the remake (and the comparison when useful), `show_result` by material ID. Return the task
   IDs, the source-clip, keyframe and slot mapping per unit, generation parameters and warnings. Keep `edit.json` with the
   project: later changes (a new overlay line, a different take for one shot) are an edit to it and one `rn assemble`.
   For revisions, keep approved slot materials, keyframes and successful units; change only the identified unit or prompt
   dimension unless the user asks for more.

## Failure Rules

Do not pre-screen the source, replacement materials or prompts. Continue normally unless the host returns an explicit
content-review error.

| Failure | Action |
|---|---|
| No shell with rn, or no sandbox for this account | Follow SKILL.md's single-generation route. |
| Media analysis unavailable | Stop and explain; do not fall back to a command or copied model code. |
| `analyze.py` fails on the file | Re-encode it with ffmpeg (`-c:v libx264 -pix_fmt yuv420p`) and retry once; then report the error. |
| No model supports source clip + slot images | Stop; do not omit the source or invent roles. |
| A unit clip exceeds the model's reference-video limit | Re-plan with a lower `--max`; do not trim the clip silently. |
| Slot or keyframe generation fails | Keep successful images and retry only the failed one after approval. |
| A unit fails its check twice | Stop spending; show both attempts and the check report and ask the user. |
| `rn` is missing or older than 0.7 | In the sandbox, report it (the sandbox image should carry it); locally, install renoise-kit. |
| A unit fails or times out | Resume the recorded task ID; retry only that unit after approval. |
| Host returns `INPUT_*` / `OUTPUT_*` content-review error | Report the actual error and stop; do not retry paid create or suggest bypasses. |
| Output copies source identity despite slots | Strengthen the source lock or replace the conflicting source; never claim text guarantees isolation. |
