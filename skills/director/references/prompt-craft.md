# Prompt Craft

Rules that hold across the current generation models. The selected model's brief in `../../model-routing/SKILL.md` decides structure, length, timestamps and reference wording; where they differ, it wins.

## Say what the camera sees

- Write like a director dictating on set, not a screenwriter summarizing: a subject, a visible action with a physical result, and objects with material, size and color. Replace abstract words ("premium", "cinematic", "emotional") with light, material, motion and reaction.
- Start with the essentials (subject, action, scene) and add a section only to control something that matters or that went wrong. Longer is not better: the first sentences carry the most weight.
- One main action per shot, two at most; no shot under about 1.5 seconds when a person or product moves.
- One named camera move per shot with its duration ("dolly push-in over 3 seconds") and one focal length. Adjectives such as "dramatic zoom" give erratic motion.
- Soft motion words ("slowly", "glides") pull toward slow motion; when speed matters, say "real-time motion".
- From a first frame or a still: write only what moves and what the camera does; restating the picture works against it.

## Shots

Several models cut on their own by default. For one take, open with "single continuous shot, no cuts". For several, number the shots with seconds that add up to the clip and name the cut or transition between them.

## References

- Give each reference one job and say what not to take from it: "the woman's face from @material:101 only; do not copy its framing, background or light". A whole-scene image gets copied, flaws included: prefer tight face crops and clean product shots, and state proportions in words.
- Put each `@material:{id}` beside what it controls and repeat it every time that subject appears; separate tokens with a space or punctuation. The server maps tokens to each model's own syntax and drops a token whose material is not attached.
- To change a video rather than make a new one from it, say edit, name the one change, and add "keep everything else unchanged".

## Characters

A character block is the reference plus two or three identifying details (hair shade and length, skin tone, each garment as texture + cut + color) plus what the character is like: "she always has an explanation" changes her body language in every frame, "brown hair, blue vest" does not. Repeat the identifying details in every shot, never just a name, and keep screen direction from shot to shot.

## Sound

- With native audio, write sound per beat and by material ("a hollow metal ring as the thermos lands"), layering ambience, action and voices.
- When the piece will be cut, ask for no music ("no background music") and add music at the edit: models add music unasked, and generated music cannot be cut cleanly.
- Dialogue: the exact words in quotes with the speaker ("she says to camera: '…'"), in the spoken language, one or two short lines per 5–8 seconds, the face in medium close-up or closer, and "no subtitles". A line that must be exact, or speech longer than a clip, gets its voice made first and the picture driven by it (see model-routing, digital human).

## Exclusions

Say what should be there ("locked-off tripod, the camera does not move", "exactly one bicycle") rather than listing what should not; negative lists can raise errors, and naming a thing can summon it. Keep only targeted exclusions for what commonly slips: no subtitles, no background music, and a style the model drifts into ("not anime", "not photorealistic").

## Adapting a Source

Keep scenes that are visual, emotionally intense and self-contained; cut exposition and transitions; externalize inner thought as action and expression; merge scenes that do the same job.
