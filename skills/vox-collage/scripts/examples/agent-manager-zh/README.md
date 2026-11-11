# Example: "Your coding agents made you a manager" (5:02, Chinese, burned-in captions)

An X article by Addy Osmani (2026-11-08) adapted into a Chinese collage explainer. It is the reference for the
**Chinese route** (long takes -> content-verified split -> two-pass read-back -> captions) and a cautionary example
for the **narrative rules**: it was written before they existed.

| file | what |
|---|---|
| narration.json | 35 beats, ~1,550 characters, cues, fact ids, chapter marks; `archetype: essay` in name only |
| facts.md | source list: the article, the Claude Code best-practices guide it cites, the Wharton preprint (checked via Crossref) |
| storyboard.py / shots.json | 45 boards, `LC()` Chinese labels, `motif="img/robot"`, `subtitles=True`, cover_shot, teaser |
| codex_jobs.json | image jobs (`gen_requests.py images`): 8 plates + 46 props (five poses of the tin-robot motif) |
| music/*.txt | six Lyria Pro briefs (hook, chA, chB, chC, chD, end) - mid-century office jazz turning dark for the caveat chapter |

Assets not bundled: Commons photos (US Navy typing pool 1918, SKF foreman 1942 by Marjory Collins / OWI, P-51 briefing
1944 NARA, card puncher c.1940 NARA: public domain; Andy Grove in his office, Intel Free Press, CC BY 2.0 with on-screen credit).

Generated: 5 Seed Audio takes (the author's cloned voice; this copy uses the `zh_male` preset), 6 Lyria cues, plates and props as images. Voice came out at 5.18 characters/s; tempo 1.08.

## What the lint says (and it is right)
`python3 tools/lint_script.py narration.json` -> 0 errors, 26 warnings. The ones that matter:
- **list narration: 9 beats start with an ordinal.** The film counts ten habits off. Minutes 0:45-3:45 play like slides.
- **five chapters open without a scene and close without a rehook.** Only "600 lines, tests green, approve" (B20) is a scene - and it is the best 20 seconds of the film.
- **no midtwist.** The strongest fact (73% accepted the AI's wrong answer, and grew more confident) sits at 4:00.

## How it should be rebuilt on the `essay` skeleton
One engineer, one day. 9:00 she hands off "make the dashboard faster" and gets the wrong thing back (context) ->
11:00 it says "done" and nothing runs (give it a check) -> 14:00 five agents, one merge conflict (plan) ->
**midpoint: the Wharton number - why she keeps trusting it** -> 23:40 six hundred lines, green tests, approve
(judgment) -> the next morning: what she writes into the instructions file (corrections compound) -> the empty
chair from the opening, now with her name on the plate. Same facts, no ordinals, about the same length.

resolve.py still prints 9 idle-board warnings for this storyboard (2.6-3.6 s with nothing new): boards built on one
long beat. They are left in as examples of what the check reports.
