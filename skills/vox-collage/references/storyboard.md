# Storyboard reference

`storyboard.py`: `from sb import *`, build `shots = [S(...), ...]`, then `save(shots, pauses=..., tail=..., score=..., teaser=..., teaserMusic=..., teaserStart=..., musicHi=..., musicLo=..., cover="cover.jpg", cover_shot=...)`.

## Timing
- Board `at`: a beat or cue (`"B04:name"`). A board lasts until the next board starts.
- Element `at`: `"+0.4"` (seconds into the board) or a cue (`"B07:copper+0.3"`). resolve.py warns if it falls outside the board.
- Title card: `pauses={"B05": 3.0}` inserts 3 s of silence before B05; put a board with `TITLE(...)` at `"B05-3.0"`.

## Elements (sb.py)
| helper | what | notes |
|---|---|---|
| `IM(name,x,y,w,at,rot,mode)` | generated prop `public/img/name.png` | mode: slap (default) · slide (`**{"from":[dx,dy]}`) · pop · drop · fade |
| `PH(name,...)` | halftone photo `public/photo/name.png` | same modes |
| `L(text,x,y,at,size,rot)` | torn typewriter label | auto-speeds typing for long text |
| `ST(text,x,y,at,size,rot)` | rubber stamp | `blend="normal", color="#E4574B"` on dark boards |
| `NUM(v,x,y,at,unit,prefix)` | halftone number card, counts up | `bg=False` for no card (light boards only) |
| `NOTE(text,x,y,at)` | red handwritten note | |
| `Q(text,who,x,y,w,at)` | quote card | exact attribution |
| `TITLE(text,at,sub)` | black strip title card | chapter openers |
| `PIN`, `TP`, `STR`, `CI`, `UL`, `AR`, `MK` | pin, tape, red string (dash=True for routes), circle, underline, arrow, highlighter | |
| `LOOP(dir,x,y,w,at,path,dur_s,card)` | GIF frames in `public/gif/dir` | `path=[dx,dy]` walks it across |
| `CLIP(src,at,full=True)` | AI video | full frame or framed card |
| `SFX(src,at)` | extra sound | engine adds slap/tape/pin/stamp/key sounds itself |

## Text
- `L(...)` is the typewriter label (Latin caps). `LC(...)` is the same label in the serif display face - use it for Chinese and for mixed-case text.
- With `subtitles=True` the caption strip starts at y=975: keep the centre of labels and notes at y <= 900 and of stamps at y <= 880 (resolve.py computes each element's bottom edge and warns).

## Motif and bookend
- `save(motif="img/robot")`: the recurring character or prop (a path fragment; several poses such as `robot_type`, `robot_run` all count).
  It should be on 30% or more of the boards, in the hook and in the ending. resolve.py prints the coverage.
- The last board reuses a cut-out from the first two boards (the empty chair, the hotel door), changed by what happened in between.

## Pacing rules
- Median board 2-6 s; vary density (dense hook, slower reflective beats).
- A new element every 1-2 s of narration; never more than one thing entering at once.
- Hard cut by default; `trans="push"` at chapter/topic changes (with page sound); `flip=True` reuses a plate mirrored.
- Teaser: 4-6 clips of 1.2-1.5 s from the strongest moments (AI video, a stamp verdict, a big number, a quote), hard cut, music only.
  A clip must start after the board's first element has landed and end before the board's cut - pick a cue with at least
  `len + 0.5` s of board left (a stamp on the last word of a beat is too late). resolve.py warns about both cases.
- Idle check: resolve.py lists boards where nothing new arrives for more than 2.5 s (3.5 s for the final hold). Fix by adding an
  underline / circle / stamp / note on a spoken word, by splitting the board at a cue, or by cutting to the next board sooner.
  Quote boards count too: bring in the attribution, then a highlighter sweep, then a stamp.

## Captions
`out/subs.srt` is written on every resolve (timed for the Full composition; `out/subs_main.srt` for Main). Lines break at
punctuation, one sentence never runs into the next, 20 characters (Chinese) or 42 (English) per line.
`save(subtitles=True)` burns them in as a torn ink strip at the bottom; `finish.py --srt out/subs.srt` adds them as a
switchable track instead. Chinese platforms expect burned-in captions; YouTube prefers the track.

## Proof checklist (out/proof sheet, one frame per board)
labels fully typed and inside the frame · nothing under the caption strip · nothing important under a stamp · text readable on dark boards · max 2 accents · no two cards overlapping text · faces not cut by the frame edge.
