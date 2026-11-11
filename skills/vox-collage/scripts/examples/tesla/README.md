# Example: "Nikola Tesla - He died broke. We live in his future." (5:14, English, US voice Charon)

| file | what |
|---|---|
| narration.json | 35 beats, ~820 words, `[[cue]]` markers, fact ids, `archetype: life`, chapter marks and role tags |
| shots.json | 52 boards + cover_shot + teaser + per-chapter score (resolve-ready; times are cues) |
| codex_jobs.json | image jobs (`gen_requests.py images`): 8 background plates + 32 cut-out props with the style prefixes |
| music/*.txt | Lyria Pro briefs per chapter (teaser.txt failed to generate; the teaser reuses ch2 at 56 s) |

Assets not bundled (rebuild with the tools): Commons photos (Tesla by Sarony c.1895, Colorado Springs lab 1899, Wardenclyffe 1904, Edison 1878, Westinghouse 1906, J.P. Morgan 1902, Marconi 1908, Ferraris; all public domain / CC0), 7 GIF loops (pigeon, boat, motor, walk, coil, bulbs, falls), 2 Wan 3.0 shots (tower dynamited, lab arcs).

Generated: one Gemini TTS request per beat, 7 GIF loops, 2 Wan shots, 6 Lyria cues, plates and props as images.
Facts were checked against Wikipedia, the 1943 Supreme Court opinion (Justia), ETHW, IEA, Rutgers Edison Papers, ECB, National Bank of Serbia; notable corrections: Musk said "I'm a bigger fan of Edison than Tesla" (2008), "be more like Edison" is Larry Page's line, the 1943 ruling did not declare Tesla the inventor of radio, Edison did not electrocute Topsy the elephant (dogs, yes - by Harold Brown with Edison's lab support).

Narrative lint (`tools/lint_script.py narration.json`): 0 errors. Honest warnings that remain, kept as written because
the film was made before the rules: three chapters close on a statement rather than a rehook, the ending quotes Tesla
instead of returning to room 3327 (no callback), and several 10-14 s beats carry only three cues.
