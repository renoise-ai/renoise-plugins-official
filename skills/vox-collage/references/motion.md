# Moving shots: options (the user multi-selects; code animation is always on)

| option | price | best for |
|---|---|---|
| Code animation (engine) | free | everything: slaps, string, typing, stamps, numbers, page pushes |
| GPT Image 2.6 GIF loop | per GIF (more with reference images) | one small looping action: pigeon flapping, rotor spinning, puppet walk, lights twinkling, coil arcs, waterfall |
| Wan video, 720p 8 s | per shot | 1-2 hero shots made from a composed first frame (a photo on a plate): explosion, arcs flaring |
| Seedance video | per shot, the most expensive | complex motion or long takes; rarely needed |

Quote each option separately with the cost estimate; never swap in a paid option the user did not tick. Read
`../model-routing/SKILL.md` for the current model names and prompting rules before writing these prompts.

## GIF loops
1. Write one prompt per loop in `gif/<name>.txt`; optional `gif/<name>.json` overrides `size`, `frames`, `ms` and adds
   `refs` (reference image material ids, which raise the price).
2. `python3 <skill>/scripts/gen_requests.py gifs gif/ --size 512x512 --frames 12 --ms 100` writes
   `build/requests/gifs.json` (it rejects sizes, frame counts and frame durations outside the GIF contract), then the
   quote → yes → generate → download → `verify.py` loop. Results land in `build/gif/<name>.gif`.
3. Frames for the engine:
   - Cut-out loops (composited on a board): 512x512, the prompt ends with the green-background tail;
     `python3 <skill>/scripts/gif2frames.py build/gif/name.gif public/gif/name --up 4 --model x4plus --key --fit 1000`
     (`--key` keys every frame at one size so the loop does not jump).
   - Card loops (a scene inside a pinned photo): 512x288, `--up 4 --fit 1400`, then `LOOP(..., card=True)`.
- Prompt: "A seamless looping stop-motion animation of a black-and-white halftone newspaper-photo paper cutout with a
  thin off-white paper border, slightly jittery like hand-moved stop motion: <subject> <one action>. ... same position
  and size in every frame, the last frame flows back into the first, no text, no letters, no watermark".
- Paper-puppet walk: "a paper puppet of <person>, side view, walking to the right in place (walk cycle), arms and legs
  are separate cut pieces joined with brass split pins" + `LOOP(..., path=[1200,0], dur_s=4)`.

## First-frame video shots (Wan)
1. Compose the first frame (1280x720) with PIL: a plate and a halftone photo centred and fully inside the frame
   (anything cropped stays cropped).
2. Upload it as a material with the host's upload tool.
3. One video request: 720p, 8 s, the material in the model's first-frame role. Prompt only the change: "Stop-motion
   paper collage animation at 12 frames per second: <what happens>, <camera: static with a slight slow push-in>. Keep
   the photo border, the map and the paper texture unchanged. No text, no subtitles."
4. Quote, generate, download to `public/vid/w1.mp4`, and check its frame count (a JSON batch with that `out` lets
   `verify.py` do it). Use it with `CLIP("vid/w1.mp4")`.
Worked: a tower dynamited into paper flames and halftone smoke; lab arcs flaring blue-white.
