# Style: black-and-white halftone collage

## Palette and type
- Paper `#E8DCC4` (never pure white) · ink `#1D1A16` · signal red `#C8312B` (stamps, string, numbers) · tape `rgba(236,222,180,.82)` · label paper `#F2EBDD`.
- Teal `#2F6F6A` and mustard `#D9A441` only as torn paper scraps at plate edges.
- Labels: American Typewriter caps. Titles/quotes: Georgia bold. Handwritten notes: Bradley Hand, red.
- Dark boards (`bg_dark`) for death, loss, quotes, "the twist": stamps need `blend="normal"` and a lighter red (`#E4574B`); numbers keep their paper card.

## Background plates (generated, 16:9, ~8 per film)
Prefix (`style.bg` in codex_jobs.json):
> Vox-style editorial paper collage background plate, top-down flat lay on an aged cream-beige paper desk (#E8DCC4), subtle paper fibers, faint creases, risograph grain, muted palette of beige paper, ink black, a touch of signal red #C8312B, teal #2F6F6A and mustard #D9A441.

Tail (`style.bg_tail`): keep the centre empty, decoration only at edges and corners, no readable text, no people, 16:9.
Make one plate per place/era/chapter (city map, ocean map, patent sheets, river map, coastline + ticker tape, modern graph paper, dark board, banknote engravings).

## Cut-out props (generated on green)
Prefix (`style.cut`): "A single black-and-white halftone newspaper-print style cutout (photocopy contrast, visible halftone dots, slight risograph grain), cut out with a 8px uneven off-white paper border like a scissor-cut sticker,"
Tail (`style.cut_tail`): "on a PURE FLAT SOLID GREEN #00FF00 background, no shadow on the background, centered with generous green margin, nothing else in the image, no readable text, no letters, no watermark."
- `kind: rect` for scenes as torn photo prints (city street, world's fair, waterfall).
- Generic designs for brands and products (no logos). Banknotes/coins: invented engravings, illegible text.

## Archival photos
- Commons, public domain / CC0 for people; record credits. `mask.py` -> `halftone.py --cell 7 --border 12` for portraits, `--cell 6 --border 18` (no mask) for rectangular prints.
- Halftone makes mixed sources look like one archive — always run it, never place raw photos.

## Element rules
- 3-6 elements per board, entering every 1-2 s, each tied to a word in the narration via a cue.
- Labels are short (<= 32 characters); long ones run off-frame or are still typing at the cut.
- Max 2 colour accents per board; one hero element; at least 40% empty paper.
- Numbers as `NUM` cards (they count up); dates and places as typewriter labels; verdicts as stamps ("MYTH", "UNVERIFIED").
- Quotes in `Q` cards with the exact source line ("Elon Musk · 2008, The Henry Ford interview").

## Thumbnail / cover
`cover_shot` in shots.json: dark board, hero portrait cut-out left, key photo right, black title strip bottom-right, a one-line hook strip under it, a stamp top-left. The cover is overlaid on the first 0.5 s of the film.
