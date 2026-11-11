# Narrative: pick a skeleton, then keep the viewer

A collage film fails in the script, not in the picture. The first two films show it: the Tesla biography held attention
because a life is already a story; the essay adaptation ("Your coding agents made you a manager") opened well and then
counted off ten habits for three minutes. Same engine, same look. The difference was the skeleton.

Decide the skeleton in step 0, write `"archetype"` into narration.json, tag the beats, and run
`<skill>/scripts/lint_script.py narration.json` before any voice is generated.

## 1 · Four skeletons

| archetype | use it for | spine | hook | midpoint | ending |
|---|---|---|---|---|---|
| `life` | a person, a company, an invention | rise - peak - fall - echo, in time order | the lowest or strangest moment of the life, as a scene | the fall begins, or a famous story turns out to be false | who carries it today; back to the opening room |
| `essay` | an article, an argument, "N lessons", an opinion | **one invented protagonist, one day or one project**; each point is something that goes wrong for them | the thesis as a paradox that touches the viewer ("you were promoted and nobody told you") | where the thesis breaks: limits, counter-evidence, the cost | the protagonist, changed; back to the opening image |
| `mystery` | crime, money trails, "why did X happen" | a question and suspects; each chapter eliminates one | the anomaly, with a number | the clue that reverses the leading theory | the answer at 75-85%, then what it means; an open question |
| `mechanism` | how something works, a number explained | follow **one unit** (one dollar, one packet, one grain) through the system | the surprising output number | the hidden step or hidden cost | zoom out; the unit arrives where it started |

### `essay` in detail (the one that goes wrong most often)
An article is a list. A film of a list is a slideshow. Convert it:
1. **Invent the protagonist.** Generic and clearly not a real person ("an engineer", "Lin", "you"). One day, one project, one deadline.
2. **Reorder by story time, not by the article's order.** Morning: hands off a vague task. Noon: five parallel workers collide. Night: approves a diff unread. The article's ranking can appear once as a label.
3. **Group 8-12 points into 3-5 chapters.** Each chapter = one scene -> the mistake -> the principle in one sentence (also shown as a stamp or label) -> what it cost. Minor points get one line or are dropped. Never more than two principles in a chapter.
4. **No ordinals in the narration** ("first", "number seven"). A small `NO.7` label on screen is fine; the voice tells the story.
5. **Midpoint = the author's own caveat or the strongest evidence.** In the agent film the 73% "cognitive surrender" number sat at 4:00 of 5:00; it belonged at 2:30.
6. **Attribution.** Name the author and source in the hook and on the end card. The claims stay the author's ("Osmani argues"). Quote at most two short lines verbatim; everything else is retold in your own words.

Before / after (same content):
- List beat: "Number seven: delegate the task, never the judgment. A six-hundred-line diff, the names look fine, the tests are green, so you approve."
- Scene beat: "11:40 pm. Six hundred lines land in her inbox. The names look fine. The tests are green. She is tired. She clicks approve. - That is not a code review. That is a signature."
The second is the same fact with a person, a time and a consequence, and it needs no number.

### `life`, `mystery`, `mechanism` notes
- `life`: open each chapter on a dated scene (place + year on a typewriter label); debunk one popular myth (viewers share corrections); the last chapter is about other people (heirs, fans, rivals), not a summary.
- `mystery`: keep one red-string board that grows through the film; every chapter ends by crossing out a suspect ("so it wasn't the money"); do not reveal the answer in the title.
- `mechanism`: the unit is the motif - it is on screen in every chapter; each stage answers "where does it go next, and who takes a cut"; one number per stage.

## 2 · Retention rules (all skeletons)

| where | rule |
|---|---|
| 0-3 s | a proposition or a strange image, already moving. No greeting, no "in this video". |
| 3-12 s | a hard number or a rapid list (one cut per item). |
| 12-25 s | the twist: the thing that makes the opening stranger. |
| 25-45 s | the main question, then the title card (3 s pause). |
| every chapter | **opens on a scene** (who, where, when, doing what), principle within the next two beats. **Closes on a rehook**: an open question or an unresolved turn. Never answer a question in the beat that asks it. |
| 40-60% | the **midtwist**: the strongest fact or reversal. Also put a 1.3 s glimpse of it in the teaser. |
| chapter joins | link with "but" / "so", never "and then" or "next". |
| last 20 s | the **callback**: the opening image returns, changed. End on a quote, an image or an open question - never a summary list, never "subscribe". |
| whole film | one **motif**: a character or prop that returns in every chapter (the pigeon, the tin robot, the one dollar). Name it in narration.json and in `save(motif=...)`. |

Smaller rules:
- One number, once. Say it the way it is spoken; put the digits on screen.
- Chapters 30-75 s; beats 1-3 sentences, 15 s at most; one `[[cue]]` per ~2.5 s of speech.
- Sources on screen for any claim a viewer might doubt (small label: author, year).
- If a fact comes from a secondary source, say so ("as Osmani quotes it"), as in facts.md.

Length budgets:

| film | hook + title | chapters | ending |
|---|---|---|---|
| 3 min | 35 s | 3 x 40 s | 20 s |
| 5 min | 45 s | 4-5 x 45-55 s | 30 s |
| 8 min | 50 s | 6 x 60-65 s | 40 s |

## 3 · Tags and the lint

narration.json:
```json
{"archetype": "essay", "target_seconds": 300, "motif": "a tin-toy robot clerk",
 "beats": [
  {"id": "B01", "chapter": "hook", "role": "hook scene", "fact": "A1", "narration": "[[desk]]Nobody told you. ..."},
  {"id": "B02", "role": "number", "fact": "A1", "narration": "..."},
  {"id": "B03", "role": "twist", "fact": "A2", "narration": "..."},
  {"id": "B04", "role": "question", "fact": "S1", "narration": "..."},
  {"id": "B05", "chapter": "9 am: the vague task", "role": "scene", "fact": "P2", "narration": "..."},
  {"id": "B08", "role": "rehook", "fact": "P2", "narration": "... So why did it still come back wrong?"}
 ]}
```
Roles: `hook` `number` `twist` `question` `scene` `rehook` `midtwist` `callback` (several per beat allowed).

`python3 <skill>/scripts/lint_script.py narration.json --target 300` prints the chapter table and:
- errors (must fix): a beat without `fact`, a cue name that starts with a digit;
- warnings: hook parts missing or late, a chapter that opens without a scene or closes without a rehook, chapter length,
  no midtwist or one outside 40-60%, no callback, list narration (4+ beats starting with an ordinal), long beats, too few cues,
  length off target.
Tags are the author's claim; the lint checks the structure, not the writing. Tag honestly - a beat is a `scene` only if
it has a person or object, a place or time, and an action.

Show the user the lint table together with the script when asking for approval.

## 4 · Adapting someone else's text
- Tell the viewer whose argument it is, early and at the end. Link the source in the description.
- Retell; do not translate paragraph by paragraph. Verbatim quotes: two short lines at most, on quote cards with attribution.
- Check the claims the source makes about third parties (studies, books, numbers) against the primary source, and keep
  the wording honest when only the secondary source supports it.
- No generated likeness of the author. Name label, their own cover image or chart as a "print" (with credit), objects.
