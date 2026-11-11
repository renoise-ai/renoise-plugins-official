// Data-driven film: film.json (resolve.py turns shots.json cue times into frames) -> shot sequence
// Structure: cover frame -> highlight teaser -> main film (narration + shots + score)
import React from "react";
import { AbsoluteFill, Sequence, Audio, Img, staticFile, useCurrentFrame, interpolate, Easing } from "remotion";
import { PaperStage, Piece, Tape, Pin, RedString, Label, Stamp, Circle, Underline, Num, Loop, Clip, C, FONT_CN, FONT_TYPE, FONT_SANS, Sfx } from "./kit";

export type El = { t: string; at: number; [k: string]: any };
export type Shot = { id: string; s: number; e: number; bg: string; flip?: boolean; push?: [number, number]; origin?: string; trans?: "push" | "cut" | "drop"; els: El[] };
export type Cue = { src: string; at: number; len: number; start: number; gain: number; fade: number };
export type FilmData = { fps: number; total: number; vo: string; bgm?: string; bgmVol?: number; duck?: number[]; score?: Cue[]; musicHi?: number; musicLo?: number; teaserStart?: number; teaserVol?: number; shots: Shot[]; cover?: string; coverFrames?: number; teaser?: { src: number; len: number }[]; teaserMusic?: string; title?: { text: string; sub?: string; len: number }; subs?: { s: number; e: number; text: string }[] };

const clamp = { extrapolateLeft: "clamp", extrapolateRight: "clamp" } as const;
const TR = 9; // page-push transition length in frames

// Chapter title card: big type on a torn black paper strip
const Title: React.FC<{ at: number; text: string; sub?: string; x?: number; y?: number; size?: number }> = ({ at, text, sub, x = 960, y = 540, size = 120 }) => (
  <>
    <Piece at={at} x={x} y={y} mode="slap" seed={"t" + text} sfx="slam-3.wav" z={35}>
      <div style={{ background: C.ink, color: "#F2EBDD", fontFamily: FONT_CN, fontWeight: 900, fontSize: size, padding: `${size * 0.12}px ${size * 0.4}px`, letterSpacing: size * 0.08, whiteSpace: "nowrap",
        clipPath: "polygon(0 3%,6% 0,30% 4%,55% 0,80% 3%,100% 0,99% 50%,100% 97%,70% 100%,45% 96%,20% 100%,0 97%,1% 50%)" }}>{text}</div>
    </Piece>
    {sub && <Label at={at + 8} x={x} y={y + size * 1.15 + 20} text={sub} size={size * 0.32} rot={-1.5} />}
  </>
);

const Quote: React.FC<{ at: number; text: string; who?: string; x?: number; y?: number; w?: number; size?: number }> = ({ at, text, who, x = 960, y = 540, w = 1100, size = 54 }) => (
  <Piece at={at} x={x} y={y} w={w} mode="slap" seed={"q" + text} z={30} rot={-1}>
    <div style={{ background: "#F7F1E3", padding: "34px 46px 30px", boxShadow: "0 4px 12px rgba(0,0,0,0.22)", fontFamily: FONT_CN, fontSize: size, lineHeight: 1.45, color: C.ink, fontWeight: 700 }}>
      <span style={{ color: C.red, fontSize: size * 1.6, lineHeight: 0, verticalAlign: "-0.35em", marginRight: 8 }}>“</span>{text}
      {who && <div style={{ fontFamily: FONT_TYPE, fontSize: size * 0.5, marginTop: 14, color: "#5A5045", textAlign: "right" }}>—— {who}</div>}
    </div>
  </Piece>
);

const Note: React.FC<{ at: number; text: string; x: number; y: number; size?: number; color?: string; rot?: number }> = ({ at, text, x, y, size = 40, color = C.red, rot = -4 }) => (
  <Piece at={at} x={x} y={y} mode="fade" seed={"n" + text} z={44} rot={rot} shadow={false} boil>
    <div style={{ fontFamily: "'Bradley Hand', 'Kaiti SC', 'STKaiti', " + FONT_CN, fontWeight: 700, fontSize: size, color, whiteSpace: "nowrap" }}>{text}</div>
  </Piece>
);

const Arrow: React.FC<{ at: number; a: [number, number]; b: [number, number]; color?: string }> = ({ at, a, b, color = C.red }) => {
  const f = useCurrentFrame() - at;
  if (f < 0) return null;
  const st = Math.floor(f / 2.5) * 2.5;
  const p = interpolate(st, [0, 10], [0, 1], { ...clamp, easing: Easing.out(Easing.cubic) });
  const ang = Math.atan2(b[1] - a[1], b[0] - a[0]);
  const hx = b[0], hy = b[1], L = 30;
  const d = `M${a[0]},${a[1]} Q${(a[0] + b[0]) / 2 + 30},${(a[1] + b[1]) / 2 - 40} ${b[0]},${b[1]}`;
  return (
    <svg style={{ position: "absolute", left: 0, top: 0, zIndex: 46, overflow: "visible" }} width={1920} height={1080}>
      <path d={d} fill="none" stroke={color} strokeWidth={7} strokeLinecap="round" pathLength={1} strokeDasharray={1} strokeDashoffset={1 - p} />
      {p >= 1 && <path d={`M${hx - L * Math.cos(ang - 0.45)},${hy - L * Math.sin(ang - 0.45)} L${hx},${hy} L${hx - L * Math.cos(ang + 0.45)},${hy - L * Math.sin(ang + 0.45)}`} fill="none" stroke={color} strokeWidth={7} strokeLinecap="round" strokeLinejoin="round" />}
    </svg>
  );
};

// Highlighter sweep (yellow block left to right)
const Marker: React.FC<{ at: number; x: number; y: number; w: number; h?: number; color?: string }> = ({ at, x, y, w, h = 60, color = "rgba(234,241,48,0.55)" }) => {
  const f = useCurrentFrame() - at;
  if (f < 0) return null;
  const p = interpolate(Math.floor(f / 2.5) * 2.5, [0, 10], [0, 1], { ...clamp, easing: Easing.out(Easing.cubic) });
  return <div style={{ position: "absolute", left: x - w / 2, top: y - h / 2, width: w * p, height: h, background: color, mixBlendMode: "multiply", zIndex: 33 }} />;
};

export const renderEl = (el: El, i: number) => {
  const { t, ...p } = el as any;
  switch (t) {
    case "piece": return <Piece key={i} {...p} />;
    case "label": return <Label key={i} {...p} font={p.cn ? FONT_CN : p.font} />;
    case "stamp": return <Stamp key={i} {...p} />;
    case "pin": return <Pin key={i} {...p} />;
    case "tape": return <Tape key={i} {...p} />;
    case "string": return <RedString key={i} {...p} />;
    case "circle": return <Circle key={i} {...p} />;
    case "underline": return <Underline key={i} {...p} />;
    case "num": return <Num key={i} {...p} />;
    case "loop": return <Loop key={i} {...p} />;
    case "clip": return <Clip key={i} {...p} />;
    case "title": return <Title key={i} {...p} />;
    case "quote": return <Quote key={i} {...p} />;
    case "note": return <Note key={i} {...p} />;
    case "arrow": return <Arrow key={i} {...p} />;
    case "marker": return <Marker key={i} {...p} />;
    case "sfx": return <Sfx key={i} at={p.at} src={p.src} vol={p.vol} dur={p.dur} />;
    default: return null;
  }
};

// Shot entry: page pushed in from the right (trans=push) or dropped from the top; the next shot covers the exit
const ShotView: React.FC<{ shot: Shot }> = ({ shot }) => {
  const f = useCurrentFrame();
  const len = shot.e - shot.s;
  const tr = shot.trans ?? "cut";
  let style: React.CSSProperties = {};
  if (tr === "push") {
    const t = interpolate(f, [0, TR], [0, 1], { ...clamp, easing: Easing.inOut(Easing.cubic) });
    style = { transform: `translateX(${(1 - t) * 100}%) rotate(${(1 - t) * 1.5}deg)`, boxShadow: t < 1 ? "-24px 0 48px rgba(0,0,0,0.4)" : undefined };
  }
  if (tr === "drop") {
    const t = interpolate(Math.floor(f / 2.5) * 2.5, [0, 7.5], [0, 1], { ...clamp, easing: Easing.out(Easing.cubic) });
    style = { transform: `translateY(${(1 - t) * -100}%) rotate(${(1 - t) * -3}deg)`, boxShadow: t < 1 ? "0 30px 48px rgba(0,0,0,0.4)" : undefined };
  }
  return (
    <AbsoluteFill style={style}>
      {tr === "push" && <Sfx at={0} src="page-1.wav" vol={0.45} />}
      {tr === "cut" && <Sfx at={0} src="cut.wav" vol={0.18} dur={8} />}
      <PaperStage bg={shot.bg} dur={len} push={shot.push} flip={shot.flip} origin={shot.origin}>
        {shot.els.map(renderEl)}
      </PaperStage>
    </AbsoluteFill>
  );
};

// Picture + SFX only (no narration, no score) - the teaser reuses this
export const Visual: React.FC<{ data: FilmData }> = ({ data }) => (
  <AbsoluteFill style={{ background: C.ink }}>
    {data.shots.map((sh, i) => {
      const next = data.shots[i + 1];
      const extra = next && (next.trans === "push" || next.trans === "drop") ? TR : 0; // keep this shot a few frames longer under the next one while it pushes in
      return (
        <Sequence key={sh.id} from={sh.s} durationInFrames={sh.e - sh.s + extra} name={sh.id}>
          <ShotView shot={sh} />
        </Sequence>
      );
    })}
  </AbsoluteFill>
);

// Per-chapter score: each cue crossfades at chapter boundaries; volume follows the narration envelope (musicLo while speaking, musicHi in pauses and title cards)
const Score: React.FC<{ data: FilmData }> = ({ data }) => {
  const hi = data.musicHi ?? 0.42, lo = data.musicLo ?? 0.14, env = data.duck ?? [];
  const duckAt = (g: number) => { const i = Math.floor(g / 3); const e = env[Math.min(i, env.length - 1)] ?? 0; return hi + (lo - hi) * e; };
  return (
    <>
      {(data.score ?? []).map((c, i) => {
        const from = Math.max(0, c.at - c.fade), len = c.len + c.fade * 2;
        return (
          <Sequence key={i} from={from} durationInFrames={len} layout="none">
            <Audio src={staticFile(c.src)} startFrom={Math.max(0, c.start - (c.at - from))}
              volume={(f) => c.gain * duckAt(from + f) * interpolate(f, [0, c.fade * 2, len - c.fade * 2, len], [0, 1, 1, 0], clamp)} />
          </Sequence>
        );
      })}
    </>
  );
};

// Burned-in captions (shots.json "subtitles": true): one line on a torn ink strip at the bottom, hard switch, no animation
export const Subs: React.FC<{ subs: NonNullable<FilmData["subs"]> }> = ({ subs }) => {
  const f = useCurrentFrame();
  const cur = subs.find((c) => f >= c.s && f < c.e);
  if (!cur) return null;
  return (
    <AbsoluteFill style={{ justifyContent: "flex-end", alignItems: "center", zIndex: 90, pointerEvents: "none" }}>
      <div style={{ marginBottom: 34, background: "rgba(29,26,22,0.92)", color: "#F2EBDD", fontFamily: FONT_SANS, fontWeight: 600, fontSize: 42, lineHeight: 1.25, letterSpacing: 1,
        padding: "8px 30px 10px", maxWidth: 1560, whiteSpace: "nowrap", clipPath: "polygon(0 6%,4% 0,35% 5%,70% 0,100% 4%,99.4% 50%,100% 96%,60% 100%,30% 95%,0 100%,0.6% 50%)" }}>{cur.text}</div>
    </AbsoluteFill>
  );
};

export const Main: React.FC<{ data: FilmData }> = ({ data }) => (
  <AbsoluteFill>
    <Visual data={data} />
    {data.subs && <Subs subs={data.subs} />}
    <Audio src={staticFile(data.vo)} />
    {data.score && <Score data={data} />}
    {!data.score && data.bgm && <Audio loop src={staticFile(data.bgm)} volume={(f) => interpolate(f, [0, 20, data.total - 60, data.total], [0, data.bgmVol ?? 0.14, data.bgmVol ?? 0.14, 0], clamp)} />}
  </AbsoluteFill>
);

// Cover frame + teaser (hard-cut highlights over music, no narration) + main film
export const Full: React.FC<{ data: FilmData }> = ({ data }) => {
  const cf = data.coverFrames ?? 15;
  const teaser = data.teaser ?? [];
  let t = cf;
  const segs = teaser.map((c) => { const s = t; t += c.len; return { ...c, at: s }; });
  const titleAt = t, titleLen = data.title?.len ?? 0;
  const mainAt = titleAt + titleLen;
  return (
    <AbsoluteFill style={{ background: C.ink }}>
      {data.cover && <Sequence from={0} durationInFrames={cf}><Img src={staticFile(data.cover)} style={{ width: "100%", height: "100%", objectFit: "cover" }} /></Sequence>}
      {segs.map((c, i) => (
        <Sequence key={i} from={c.at} durationInFrames={c.len} name={`teaser${i}`}>
          <Sequence from={-c.src}><Visual data={data} /></Sequence>
        </Sequence>
      ))}
      {data.teaserMusic && <Sequence from={cf} durationInFrames={mainAt - cf + 20}><Audio src={staticFile(data.teaserMusic)} startFrom={data.teaserStart ?? 0} volume={(f) => interpolate(f, [0, 4, mainAt - cf - 6, mainAt - cf + 20], [data.teaserVol ?? 0.45, data.teaserVol ?? 0.45, data.teaserVol ?? 0.45, 0], clamp)} /></Sequence>}
      {data.title && (
        <Sequence from={titleAt} durationInFrames={titleLen}>
          <PaperStage bg={data.shots[0].bg} dur={titleLen} push={[1.08, 1.0]}>
            <Title at={2} text={data.title.text} sub={data.title.sub} size={150} />
          </PaperStage>
        </Sequence>
      )}
      <Sequence from={mainAt}><Main data={data} /></Sequence>
    </AbsoluteFill>
  );
};
