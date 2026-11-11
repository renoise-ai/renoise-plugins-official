# Research summary (2026-11)

Three studies of YouTube "Vox-style collage" explainers (2026-11): A AI workflows, B visual grammar, C viral films.

## A · How AI creators make it (8 tutorials, 30k-430k views)
- Four routes: (1) all-code (Claude Code + Remotion), (2) AI image -> image-to-video (Flow/Veo, Seedance, Kling), (3) AI image + manual parallax in an editor, (4) one-shot multimodal (Gemini Omni). The top two tutorials use (2) and (1). Creators who tried both conclude **hybrid**: AI images for collage texture, code for numbers, maps, labels and timing.
- The universal image-to-video prompt: the generated image is the *last* frame; elements assemble from an empty page in order background -> subject -> secondary -> tape/stamps -> red string -> underline; locked camera; stepped "2-3 frames per pose" motion; only paper foley. Video models garble small text and add stray objects ("80-90% usable").
- Style lock: write the style once (STYLE / ACTION / AUDIO / AVOID blocks) and reuse it in every prompt; a reference sheet alone drifts.
- Pacing in AI samples: one AI shot 5-6 s, a new element every 1.5-2 s; ~27 beats per spoken minute in one master prompt.
- Celebrity faces get blocked; creators put black bars over eyes. Do not generate living people's likenesses at all.
- The "expensive" look comes from real photo texture inside paper shapes plus one global finish (paper multiply + film grain + dust + reduced frame rate).
- All-code critiques: "no texture, only bouncy scale, a white flash every 2 s" - texture and restraint matter more than motion.

## B · Visual grammar (Vox / Johnny Harris breakdowns, Chris Moran, Mapal, Motion Street)
- Elements move at **12 fps** everywhere measured; camera pushes may be 12 or 24 fps; no motion blur.
- Boil: lines ~4 Hz, shapes ~3 Hz, text ~5 Hz - different rates so the frame never jumps as one; whole-frame wiggle 2 px at 2 Hz with 101% scale.
- Paper never pure white (#F0EFEA / #EEDEC7); crumpled paper multiply; texture holds 12 frames.
- Cut-outs: greyscale halftone, uneven paper border 6-9 px, soft shadow (~4/10 px offset, 18 px blur, 28% opacity). Optional red offset silhouette (#C44C48, -8 px).
- Colour only on drawn marks; max 2 accents per board. Vox red #E03C42, Vox blue #6273E1, highlighter #EAF130.
- One centred subject, lots of empty paper, 3 shallow depth layers, small camera moves (push 1.00 -> 1.05-1.10).
- Attention tools: highlighter sweep, red circle/underline, contrast dim (lift blacks around the subject), text dim to 20% + 10% push, focal blur, radar ring.
- Default transition is a hard cut with a click; page push / brush wipe ~1 s for topic changes.
- Why audiences like it: it breaks the "template 3D news" look, 12 fps reads as hand-made and trustworthy, shallow depth keeps attention on information.
- Ugly-making mistakes: pure white backgrounds, everything entering at once, fast/strong wiggle, mixed archival looks, motion blur, glossy 3D, too-clean cut-outs, too many colours, deep parallax.

## C · Viral films (Vox, Johnny Harris, AI faceless channels)
| | cuts/min | median shot | words/min | length |
|---|---|---|---|---|
| Vox / Johnny Harris | 14-17 | 2.0-2.3 s | 141-165 | 8-21 min |
| AI faceless channels | 3-11 | 5-10 s | 173-176 | 19-31 min |
- Original channels vary pace (0-16 cuts per 30 s); AI channels are flat (3-8). Vary density: dense openings, breathing room in reflective beats.
- In AI channels the collage is mostly in the **thumbnail** (right-side B&W cut-out, torn map, bottom-left white title strip, red only).
- Hot topics: WWII "real reason" stories, money and power, "How X became Y", "How [power] stole/starved [group]". Title patterns: "The Real Reason ...", "The True Origin of X: What Historians Get Wrong".
- Opening 30 s template: 0-3 s proposition or familiar image · 3-12 s a hard number or rapid list · 12-25 s twist + visual anomaly · 25-40 s number/analogy + protagonist · 30-90 s main question + title card. AI channels add "the usual story -> that's wrong".
- Endings: originals use an open question or a quote; avoid generic "subscribe".
