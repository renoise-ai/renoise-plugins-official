# Commercial Video — Router and Shared Prompt Rules

Use this index for live-action e-commerce, advertising and brand work. Software, apps, services, and brands whose own look is UI, type or illustration use `references/code-built-video.md` instead.

## Route

1. Reference video to replicate → stop and use `video-remake`
2. Presenter speaking on camera (`口播`, `带货`, `测评`, `主播出镜`) → `commercial/scenario-d-ugc.md`
3. Everything else, from one product shot to a multi-shot brand film → `commercial/scenario-c-tvc.md`

## Six-Dimension Formula

Build every commercial prompt in this order:

```text
Subject + Selling-Point Action + Scene & Tone + Camera Language + Audio + Post-Production Constraints
```

| Dimension | Question |
|---|---|
| Subject | What must the viewer see first? |
| Selling-Point Action | What visible action proves the selling point? |
| Scene & Tone | What specific light, environment, palette, and physical atmosphere create the feeling? |
| Camera Language | Which framing or movement creates the hook? |
| Audio | Which ambient, speech, effect, or beat must align with the action? |
| Post-Production | Which likely failures must be prohibited or reserved for later overlays? |

## References

Look at every image or video the user gave and give each one job: subject anchor, scene calibration, camera reference, or beat-sync control. Reuse the same material for a recurring person or product, and put its token beside what it controls:

```text
the serum glass bottle from @material:101
use @material:202 only for camera movement, not identity or product
```

## Writing the Prompt

Draft the generation arguments in the user's language. A non-dialogue final generation prompt may be translated to concise professional English before submission. Any spoken line stays verbatim in the resolved spoken language; dialogue-dense prompts stay entirely in that language.

Required:

- Replace abstract claims such as “premium” or “hydrating” with concrete light, material, motion, and reaction.
- Put each material token directly beside the controlled subject.
- For reference video, state which traits to use and which identities/content not to copy.
- Include at least two negative constraints for the most likely failures.
- Cover all six dimensions, organized according to the matched scenario.

### Physical Continuity

A product cannot silently teleport from packaged/stored to in-use state. Choose one:

- Start with the product already ready for use and never mention packaging nearby; or
- Dedicate a visible beat to opening/preparing it, then demonstrate it in the following beat.

This applies to caps, pouches, boxes, tags, wrappers, folded clothing, and similar state changes.

### Action Granularity

Never compress a multi-step physical process into one sentence. Give each demonstration at least three visible sub-steps, each describing an incomplete mid-action state and pace:

1. A small pump lands on the cheekbone and remains pooled.
2. One fingertip gently taps the center; it is not spread yet.
3. Slow outward circles spread it halfway; the unblended edge stays visible.
