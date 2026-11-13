# Narrative, Short Drama and Storyboards

Use for drama, comedy, short film, short drama, montage, MV and adaptation, and for a plan or storyboard on its own. Write prompts with `../references/prompt-craft.md`.

## Intake

Decide what the brief leaves open (characters, action, mood, setting, duration, speech, references) and state your choices in the plan. Ask only for what cannot be inferred and blocks the work. Choose the video model before deciding whether this is one clip or several: when the duration fits one clip, write one prompt and generate it.

## Story

- **Logline:** `When [INCITING INCIDENT], a [CHARACTER] must [GOAL], but [OBSTACLE] threatens [STAKES].`
- **Treatment:** two or three sentences per scene, what the viewer sees and feels, dialogue embedded.
- Connect scenes with consequence (**THEREFORE**) or complication (**BUT**), not **AND THEN**; at least a third of the transitions complicate.
- Do not target the same emotion in adjacent scenes. Put the peak at about 70–80% of the running time.
- **Short drama** (vertical, episodic): each episode runs hook → setup → conflict → escalation → reversal → cliffhanger, the first three seconds strong; prefer faces, reactions, hands, phones, doors, documents, money and wounds over narration; 8–12 shots per 60–90 second episode.

## Anchors

**Characters.** A character in two or more segments gets one design sheet, generated once and reused as the same material everywhere:

```text
Character design sheet for [NAME].
[Full appearance: age, face, hair shade and length, skin tone, build,
each garment as texture + cut + color, accessories, signature details]
Layout: 2 rows × 3 columns on a clean background.
Row 1: front, three-quarter, side profile. Row 2: two expressions, one full-body pose.
[PROJECT STYLE LINE]
Consistent appearance across every panel. No labels or background elements.
```

**Props and wardrobe.** One fixed description per recurring item, copied verbatim wherever it appears; a plot-driven change gets its own transformation shot:

```text
Item                 Fixed description                         Type
Engagement token     translucent green jade, one broken shard  Constant
Hero robe, Act II    black silk, gold embroidery, high collar  Plot-driven from S4
```

**Locations.** A recurring location gets an environment-only image (layout, light, palette, key props) when words will not hold it.

## Manifest

Before generating video, set out:

| Item | Lock |
|---|---|
| Characters | The design-sheet material, constant traits, plot-driven changes |
| Style Bible | One verbatim `art style + camera language + color grade` line, prepended to every segment, plus an exclusion only for a style the model drifts into |
| Transition Table | Every cut: the previous segment's last frame, the next one's first frame, and how they link |
| Spoken language | The language of each speaking segment |
| Shot mapping | The materials and reference roles each segment uses |
| Segment prompts | The full prompt for every segment, with its parameters and the summed cost |

- Link cuts by matching composition, continuing a motion, carrying the light and grade, or completing a gesture; a gaze that leads to the next reveal and a sound that bleeds across also work. A matched grade plus matched framing is the strongest join.
- Intermediate segments end on a hook the next can catch; only the last may settle into `frame holds steady`, and only S1 needs an establishing open.
- Start each segment after S1 with `Continuing from the previous shot: [position, pose, prop state, emotion, light, environment].`
- Carry identity, product and location through the same material in an image-reference role; motion through a previous result only where the next model takes reference video; an exact opening state through the previous clip's last frame as the first frame.

## Plan Only

When the user wants the plan or storyboard rather than the video, deliver what the request implies:

- **Storyboard sheet** (review, pitch): one image per episode, 6 panels in a 2 × 3 grid, small P1–P6 labels and no other text, characters matching their references. Not an input for video models.
- **Shot list** (for generation): per shot, its id, duration, framing, one action, emotion, camera, a first-frame image prompt and a video prompt. First frames are generated one per shot, never cut from a sheet.

Check each against the story (hook, order, no invented plot, reveals as adapted, inner thought made visible) and the anchors (faces, age, wardrobe, location, props), and redo only what fails.

## Generate, Check, Assemble

Generate every segment that does not depend on another in one round. Check every segment and cut against the manifest: same identity, wardrobe, props and location state; same style and grade; joins matching the Transition Table; the right spoken language; no failed action or unusable frame. Regenerate only what fails, together, then cut the piece with the music added at the edit.

| Problem | Adjustment |
|---|---|
| Character drifts | Same design-sheet material and role, identifying details repeated in the shot |
| Actions are ignored | One main action per shot, fewer shots per clip |
| Clip is incoherent | One mood, one camera move per shot |
| Segments do not connect | Repair the Transition Table and the opening-state bridge; a short dissolve at the edit |
