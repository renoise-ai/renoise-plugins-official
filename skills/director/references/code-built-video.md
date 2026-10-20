# Code-Built Video

Read this when the frames show text, numbers, UI, diagrams, logos, geometric motion graphics or the user's own media, or when you build those layers over generated footage. Characters, scenes and organic motion in any style (live action, anime, cartoon, stylized 3D) are generated, not built. It needs a shell: the host's own or a cloud sandbox tool the host exposes. It names no framework: use what the shell already has, and add one only when the user asks for it.

## Default Stack

- **Typography, UI, charts, logo motion:** an HTML/CSS/SVG or canvas page whose every frame is a pure function of the frame number, rendered frame by frame with headless Chromium (Playwright) at the output size, then encoded with ffmpeg.
- **Math, geometry, diagrams:** Manim.
- **Cutting, transitions, pans over stills, audio mixing:** ffmpeg (or MLT melt for many layers).
- **Data:** compute values in code from the data the user gave; never type a number into a scene by hand.
- A host may ship helpers (the Renoise sandbox has the `rn` kit for frames, contact sheets, assembly, finishing and QA): use them where they fit.

## Frame-Driven Timing

- Derive every position, opacity and value from the frame index and fps. CSS transitions and animations, timers and wall-clock time do not render the same frame by frame.
- Wait until fonts, images and data have loaded before capturing the first frame.
- Keep scenes as separate functions or files with an explicit start and duration, so one scene can change without retiming the rest.

## Layout

- Decide what the viewer should notice first in each scene and build the frame around that one thing. Leave out anything that does not serve it.
- Keep key content in a safe area: for a 1080 px wide frame, at least 80 px from the sides and 100 px from the top and bottom. Scale with the width.
- Minimum sizes at 1080 px wide: headline 84 px, supporting text 44 px. Text that must be read on a phone gets larger, not smaller.
- Use the brand's exact colors, fonts and logo files when the user gave them; otherwise pick one type family and a palette of a few colors and keep them for the whole video.
- Check contrast: text over footage gets a scrim, shadow or solid band.

## Motion

- Hold each line long enough to read it twice: about 0.4 s per word, and never under 1.5 s.
- Ease every move; vary duration and easing by an element's size and role. Identical springs on every element, or perfectly even stagger delays, read as a template.
- Bring elements in in reading order, and move only what the viewer should look at.
- Carry motion across a cut: the next scene enters along the axis and direction the last one left, at about the same speed. Do not reverse direction between consecutive scenes without a visible cause.
- No idle wobble: when nothing should change, hold still. A beat of stillness before the key reveal makes it land.

## Mixing With Generated Footage

- Generate the footage first. In its prompt, ask for clean space where text will go and for no on-screen text: video models garble text you will set in code.
- Match the footage's resolution and frame rate in the code-built layers.
- Composite overlays with ffmpeg (`overlay`), rendering them on a transparent background as a PNG sequence or an alpha-capable codec.
- For a code-built video that needs a background, texture or hero visual, generate that one image or short clip and build the rest in code.

## Audio

- Music comes from the user, an audio model, or code (synthesized beds and hits). Cut on the beats: detect beat times (librosa) and place cuts and reveals on them.
- Mix voice above music; deliver about −14 LUFS integrated for social platforms.

## Verify Before Delivering

You cannot watch or hear the result, so check it this way, fix, and re-render at most three times; then deliver and name what still looks off.

1. The render exits cleanly; ffprobe shows the planned duration, resolution and frame rate.
2. Export the first, middle and last frame of every scene and a contact sheet, and look at them: every word spelled right and fully inside the safe area, nothing clipped or overlapping, numbers matching the data, colors and logo correct.
3. Measure loudness and confirm the audio covers the full duration.
4. Ask the user to review motion and sound, which stills cannot show.

## Examples

- **Quote video (code only):** one line per beat in large type, words entering in reading order on the music's beats, a still hold on the last line, the author's name as the end card.
- **Revenue explainer (code only):** bars grow from the user's spreadsheet values, the leading value counts up, a one-line takeaway holds for three seconds, the source cited in small type.
- **Product ad (both):** three generated product shots with clean negative space and no text, then code-built title, price, offer and end card composited over them and cut to the music.
