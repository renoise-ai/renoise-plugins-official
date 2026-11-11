# Music: a score designed for each film

Never reuse one default track. Write the emotional arc from the script, one cue per chapter.

## Brief template (Lyria, one request per cue)
Save each brief as `music/<cue>.txt`:

```text
Instrumental only, no vocals. Documentary underscore for a Vox-style paper-collage explainer about <topic>.
Leave the low-mid frequencies clean for a narrator's voice; no busy melody in 200-2000 Hz while it plays under speech.
Clean ending, no fade-out tail longer than 2 seconds.
Genre: <...>. Mood: <...>. Tempo: <BPM>. Instruments: <...>.
Structure: 0:00-0:30 <...>, 0:30-0:50 <...>, 0:50-1:10 <...>. Target length: about <chapter length + 10> seconds.
```

`python3 <skill>/scripts/gen_requests.py music music/` writes `build/requests/music.json` (outputs `music/<cue>.mp3`);
then quote → yes → generate → download → `verify.py`.
Duration is approximate (no duration parameter): ask for ~10 s more than the chapter. Run a whisper pass over each cue
to confirm there are no vocals. If a cue fails, rewrite the brief (drop unusual sound effects) or reuse the strongest
part of another cue.

Tesla arc (`scripts/examples/tesla/music/`): hook = lonely mystery 70 BPM (felt piano, ticking clock, cello drone) ·
ch1 = playful period chamber 104 BPM · ch2 = driving rivalry 124 BPM building to triumph · ch3 = wonder turning to
tragedy 84 BPM with a dark hit at the tower demolition · ch4 = hopeful modern electronic 110 BPM · ch5 = reflective to
uplifting finale 92 BPM resolving on the last frame.

## Placement (shots.json)

```python
score=[dict(src="music/hook.mp3", at="0",   to="B05", start=0.0),
       dict(src="music/ch2.mp3",  at="B10", to="B18", start=0.0),
       dict(src="music/ch5.mp3",  at="B29", to=None,  start=3.0)],   # start: seconds into the track
musicHi=0.26, musicLo=0.11, teaserMusic="music/ch2.mp3", teaserStart=56*30, teaserVol=0.45
```

- Choose `start` so the cue's climax lands on the story's climax and its final chord on the last frame (cue length -
  chapter length - tail).
- Teaser: the loudest 7 s window of the most energetic cue (RMS scan).
- The engine crossfades cues over 1 s at boundaries and follows the narration envelope: `musicLo` while speaking,
  `musicHi` in long pauses and title cards (~7 dB difference). Measured target: speech sections about -27 dB RMS, title
  pause about -23 dB, teaser about -16 dB.
