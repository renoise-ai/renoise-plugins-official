# Narrative / Short-Film Workflow

Use for drama, comedy, short film, montage, MV, and story adaptation. Read `references/prompt-craft.md` before drafting prompts.

## Intake

Decide what the brief leaves open (characters, action, mood, setting, duration, speech, references) from the brief and its references, and state your choices in the plan. Ask only for what cannot be inferred and blocks the work. Choose the video model before deciding whether this is one clip or several.

## Single Clip

When the duration fits one clip of the selected model: write one high-density prompt with `model-routing` and `prompt-craft.md`, and generate it.

## Multi-Clip

```text
brief → story → anchors → manifest and prompts → generate video → check → assemble
```

### 1. Story

- **Logline:** `When [INCITING INCIDENT], a [CHARACTER] must [GOAL], but [OBSTACLE] threatens [STAKES].`
- **Treatment:** two or three sentences per scene describing what the viewer sees and feels, with dialogue embedded naturally.
- Connect scenes with consequence (**THEREFORE**) or complication (**BUT**), not a sequence of **AND THEN** events; at least 30% of transitions complicate the story.
- Do not target the same viewer emotion in adjacent scenes.
- For adaptations, keep visual, emotional, self-contained scenes; cut exposition and externalize internal thought through action.

### 2. Anchors

**Characters.** An invented character in two or more segments gets one design sheet, generated once and reused as the same material in every segment:

```text
Character design sheet for [NAME].

[FULL appearance description — age, face, hair, skin tone, body type,
wardrobe with texture/cut/color, accessories, signature details]

Layout: 2 rows × 3 columns on a clean background.
Row 1: front, three-quarter, side profile.
Row 2: two expressions, one full-body pose.

[PROJECT STYLE LINE]
Consistent appearance across every panel. No labels or background elements.
```

**Props and wardrobe.** Give every recurring item one fixed description and copy it verbatim wherever it appears; a plot-driven change gets its own transformation shot and Transition Table row:

```text
Item                 Fixed description                         Type
Engagement token     translucent green jade, one broken shard  Constant
Hero robe, Act I     coarse grey hemp, loose, frayed hem       Constant until S4
Hero robe, Act II    black silk, gold embroidery, high collar  Plot-driven from S4
```

**Locations.** A recurring location gets an environment-only concept image (layout, light, palette, key props) when a written description will not hold it.

**Storyboard grid** (optional, for many segments): one image of all key moments in the project style, after the character sheets exist. Split it into per-segment references only where you can edit images and the video model takes image references.

### 3. Manifest

Present the manifest in one block before generating video:

| Item | Lock |
|---|---|
| Characters | The design-sheet material for each recurring character, plus constant traits and plot-driven changes |
| Props/wardrobe | Fixed descriptions; explicit state changes |
| Scenes | Environment reference or one fixed location description |
| Style Bible | One verbatim `art style + camera language + color grade + NEGATIVE line` string |
| Transition Table | Every cut's previous OUT state, next IN state, and linking technique |
| Spoken language | The language of each speaking segment |
| Shot Mapping | The materials and reference roles each segment uses |
| Segment prompts | The full prompt for every segment, with its parameters and the summed cost |

Prompt construction:

- Apply the selected model's prompting profile.
- Prepend the Style Bible verbatim to every segment and copy full character and prop blocks verbatim.
- Start each segment after S1 with `Continuing from the previous shot: [position, pose, prop state, emotion, light, environment].`
- Give each intermediate segment an ending hook matching the Transition Table.

Continuity routing between segments is in `prompt-craft.md`.

## Generate, Check, Assemble

Generate every segment that does not depend on another in one round. Then check every segment and cut against the manifest: same identity, wardrobe, props and location state; same style and grade; boundaries matching the Transition Table; the right spoken language; no failed action or unusable frame. Regenerate only what fails, together. Cut the piece where you have editing; otherwise deliver the ordered clips with the transition plan. Music or enhancement goes through `model-routing` like any other generation.

## Creative Recovery

| Problem | Adjustment |
|---|---|
| Character drifts | Verify the same design-sheet material, reference role, and verbatim character block |
| Actions are ignored | Reduce to three or four actions per clip |
| Clip is incoherent | Use one mood, at most two camera stages, and fewer actions |
| Segments do not connect | Repair OUT/IN states and continuity routing; a short cross-dissolve where you can edit |
