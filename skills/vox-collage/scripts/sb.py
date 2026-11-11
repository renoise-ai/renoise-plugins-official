"""Storyboard helpers. In a film's storyboard.py:  from sb import *  then build `shots` and call save(...).
Times: "B03" beat start · "B03:cue" a [[cue]] in the narration · "+0.4" seconds after the shot starts · "B03:cue+0.3".
Canvas is 1920x1080; x/y are element centres; w is width in px."""
import json
FPS = 30
def P(src, x, y, w, at="+0.2", rot=0, mode="slap", **k): return dict(t="piece", src=src, x=x, y=y, w=w, at=at, rot=rot, mode=mode, seed=src + str(x), **k)
def PH(n, *a, **k): return P(f"photo/{n}.png", *a, **k)          # halftoned archival photo (tools/halftone.py)
def IM(n, *a, **k): return P(f"img/{n}.png", *a, **k)            # Codex cutout / prop (tools/codex_batch.py)
def L(text, x, y, at="+0.4", size=40, rot=-2, **k): return dict(t="label", text=text, x=x, y=y, at=at, size=size, rot=rot, **k)   # torn typewriter label
def LC(text, x, y, at="+0.4", size=52, rot=-2, **k): return L(text, x, y, at, size, rot, cn=True, **k)   # label in the serif display face - use it for Chinese (and any non-typewriter label)
def ST(text, x, y, at, size=80, rot=-8, **k): return dict(t="stamp", text=text, x=x, y=y, at=at, size=size, rot=rot, **k)        # rubber stamp (blend="normal" on dark boards)
def PIN(x, y, at): return dict(t="pin", x=x, y=y, at=at)
def TP(x, y, at, rot=-32, w=150): return dict(t="tape", x=x, y=y, at=at, rot=rot, w=w)
def STR(a, b, at, sag=60, dur=14, **k): return dict(t="string", a=a, b=b, at=at, sag=sag, dur=dur, **k)   # red string (dash=True for a route)
def CI(x, y, rx, ry, at, **k): return dict(t="circle", x=x, y=y, rx=rx, ry=ry, at=at, **k)               # hand-drawn red circle
def UL(x, y, w, at): return dict(t="underline", x=x, y=y, w=w, at=at)
def AR(a, b, at): return dict(t="arrow", a=a, b=b, at=at)
def MK(x, y, w, at, h=60): return dict(t="marker", x=x, y=y, w=w, h=h, at=at)                             # highlighter sweep
def NUM(v, x, y, at, unit="", prefix="", size=170, rot=-3, **k): return dict(t="num", value=v, x=x, y=y, at=at, unit=unit, prefix=prefix, size=size, rot=rot, **k)
def NOTE(text, x, y, at, size=48, rot=-4, **k): return dict(t="note", text=text, x=x, y=y, at=at, size=size, rot=rot, **k)        # handwritten red note
def Q(text, who, x, y, w, at, size=52): return dict(t="quote", text=text, who=who, x=x, y=y, w=w, at=at, size=size)
def TITLE(text, at, sub=None, x=960, y=540, size=120): return dict(t="title", text=text, sub=sub, at=at, x=x, y=y, size=size)
def LOOP(d, x, y, w, at="+0.2", path=None, dur_s=4, card=False, rot=0, **k):                              # GIF frames in public/gif/<d>
    o = dict(t="loop", dir=f"gif/{d}", n=12, fps=10, x=x, y=y, w=w, at=at, card=card, rot=rot, **k)
    if path: o.update(path=path, dur=dur_s * FPS)
    return o
def CLIP(src, at="+0", full=True, start=0, **k): return dict(t="clip", src=src, at=at, full=full, startFrom=int(start * FPS), **k)  # AI video (Wan/Seedance)
def SFX(src, at, vol=0.5): return dict(t="sfx", src=src, at=at, vol=vol)
def S(id, at, bg, els, trans="cut", push=(1, 1.04), flip=False, origin="50% 50%"):
    """One board. trans: cut (default, Vox hard cut) · push (page push, use at chapter/topic changes) · drop."""
    return dict(id=id, at=at, bg=f"img/{bg}.png", trans=trans, push=list(push), flip=flip, origin=origin, els=els)
def save(shots, path="shots.json", **top):
    """top: pauses={"B05": 3.0}, tail=3.0, score=[...], teaser=[...], teaserMusic, teaserStart (frames), teaserVol,
    musicHi, musicLo, cover="cover.jpg", coverFrames=15, cover_shot=dict(bg="img/bg_dark.png", els=[...]),
    motif="img/robot" (recurring character: resolve.py reports its coverage), subtitles=True (burn captions in; keep text centres at y<=900)."""
    json.dump(dict(shots=shots, **top), open(path, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print(f"{len(shots)} shots -> {path}")
