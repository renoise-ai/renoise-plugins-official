# Scenario C — Product Shot, Brand Film, TVC

**Trigger**: Any live-action product or brand video without a presenter: a single product shot, a lifestyle, outdoor, fashion or sports film, an aspirational campaign, a product film with a story.

**Not Scenario C if**: the user wants a presenter speaking to camera → Scenario D. The user has a reference video to replicate → `video-remake`.

---

## Six-Dimension Emphasis

| Dimension | Emphasis |
|-----------|----------|
| **Subject** | Person + product exist together as storytelling elements — neither dominates; anchor both with `@` references |
| **Selling-Point Action** | Replace feature callouts with cinematic micro-moments: product interacting with environment (boot crushing wet grass, jacket catching wind), body language conveying effort or freedom |
| **Scene & Tone** | Rich, specific environments — anchor with the scene's `@material:{id}` token; describe light quality (golden morning haze, blue-hour ridge glow), atmosphere, and how the environment feels physically |
| **Camera Language** | Follow the user's shot ideas if specified. If unspecified, use and disclose a coherent shot plan before writing prompts. |
| **Audio** | No dialogue — music-driven. Write a **unified audio direction** spanning the entire video, with per-shot accents. |
| **Post-Production** | Person consistency across all shots; end frame reserved for slogan/logo (fade to black + centered text); no jump cuts |

---

## Two Modes Based on Total Duration

### Mode A: Single clip within the selected model's live maximum — PREFERRED

Generate as **one single task**. Write all visual stages into one prompt plus a unified audio direction at the end. The model renders them as a continuous flowing video with coherent audio. No assembly is needed.

**The prompt has three parts:**
1. **Shot descriptions** — each shot as its own paragraph, labeled `[Shot N | Xs | label]`. Camera, subject, action, environment per shot. The model flows between shots as smooth transitions, not hard cuts.
2. **Unified audio direction** — one paragraph describing the overall soundscape across the entire video, plus per-shot audio accents tied to specific visual moments.
3. **Post-production constraints** — consistency rules, negative constraints.

**How to determine the shot plan:**
- User has clear shots → use them directly and polish
- Brief is vague → use the default arc below, adapt it to the brief, and disclose the shot plan before writing the prompt

**Default arc when unspecified** (adjust freely):
```
[Shot 1 | 5s | Establishing] Ultra-wide panoramic of [environment], [light quality], camera slowly pushing forward.
[Shot 2 | 5s | Character Intro] [Person] wearing [product], [action], follow-cam tracking, [environmental detail].
[Shot 3 | 5s | Product Detail] Macro close-up of [product interacting with environment], camera orbiting. Fade to black.
```

**Example prompt** (hiking boot TVC; timing shown for one example duration):

> Ultra-wide panoramic of mountain ranges and open ridge, referencing the environment from @material:101. Golden morning mist drifts across the slopes, camera slowly and steadily pushes forward through the landscape. **[Shot 1 | 5s | Establishing]**
>
> A man wearing the hiking boots from @material:102 strides along a mountain trail with purpose, follow-cam tracking alongside him at ground level. Wind moves his clothing and the surrounding tall grass, natural and unposed. **[Shot 2 | 5s | Character in Motion]**
>
> Macro slow-motion close-up of the hiking boots stepping into wet grass — grass blades bending under the sole, morning dew splashing in soft arcs. Camera orbits slowly to reveal the boot from multiple angles. Frame holds, then fades to black. **[Shot 3 | 5s | Product Detail]**
>
> **[Audio]** Background soundscape of crisp birdsong and wind rustling through pine trees throughout. When the hiker appears in Shot 2, a gentle acoustic guitar strum fades in. During the boot close-up in Shot 3, the music swells softly with a warm bass note as the dewdrops splash. No dialogue, no sudden loud sounds.
>
> **[Post-Production]** Person's appearance and boot design must remain consistent throughout. No visible product logos until the final fade. No frame flickering, no distorted faces.

---

### Mode B: Multi-clip — when the duration exceeds one clip of the selected model

Split into segments the model can make; each follows the Mode A format. Cut them together with the unified audio direction where you have editing; otherwise deliver the ordered clips with the cut plan. If a segment fails, regenerate only that one.

---

## Product-Only Shot

When the product is the sole subject (no person, no story), it is one clip:

- The product stays centered, stable and in frame; lock its look and proportions with its `@material:{id}`.
- Every selling point becomes a visible micro-action, never an adjective: "hydrating" → droplets condensing and sliding down the bottle; "premium" → a named lighting setup (rim light angle, color temperature, shadow softness); "durable" → the material under stress, recovering.
- Camera: steady, slow and refined, macro close-up with a slow orbit; never handheld.
- Reserve the last 2 seconds for the logo or slogan when the brand wants one.

> Display the men's serum glass bottle from @material:101 at the center of the frame, translucent, proportions strictly matching the original. Crystalline droplets condense on the surface and slowly slide down the bottle. @material:102's minimalist modern space, high-contrast cool blue; a sidelight sculpts a sharp rim. The camera starts on a macro close-up and orbits slowly while pushing in. In the final 2 seconds a soft chime marks the beat as a silver logo fades in at center. No flicker, the logo never distorts, the droplets move realistically.

---

## Example

**Brief**: Push an ultra-thin diaper. First 3 seconds must hook moms on the pain point (baby with diaper rash crying), then cut to the product and demonstrate breathability. Fast pace.

**Assets**:
- `@material:101` (product flat-lay photo) → subject anchor
- Viral reference video (host media analysis only — not registered as a generation material)

**Media analysis**:
- Camera: fast whip-pan at 3s, handheld close-up in opening
- Expression: mother's anxious close-up, furrowed brows
- Pacing: rapid cuts every 1–2s, tension builds in first half
- Scene: warm-toned home nursery, soft natural light

**Prompt**:

> Close-up of a young mother with furrowed brows, holding a crying baby, expressing extreme anxiety — handheld camera, slightly shaky, tight on face. **[Visual Hook (Opening)]**
>
> At the 3-second mark, camera whip-pans horizontally to the baby diaper product from @material:101. **[Subject]**
>
> Product lies flat on a table surface as a burst of steam instantly penetrates from the bottom through the top layer, viscerally demonstrating breathability. **[Selling-Point Action]**
>
> Warm, bright home nursery environment, high-saturation warm color palette, soft natural light. Fast cuts every 1–2 seconds, tension building through the first half. **[Scene & Tone + Camera Language]**
>
> Actions must not drag, steam effect must be natural without exaggeration, packaging text must be clearly readable, facial features must remain stable and undistorted. **[Post-Production Constraints]**

**Why it works**: The reference video was analyzed first—camera, pacing, and expression are encoded as text without registering the video as a generation material. "Breathable" is translated into the visible action of steam penetrating.
