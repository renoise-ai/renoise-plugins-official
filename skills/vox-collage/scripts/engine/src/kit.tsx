// Vox collage motion kit: elements step at 12 fps (camera stays smooth); SFX mount as Sequences at each element's entry time
import React from "react";
import { AbsoluteFill, Img, Sequence, Audio, OffthreadVideo, staticFile, useCurrentFrame, interpolate, Easing, random } from "remotion";

export const C = { paper: "#E8DCC4", ink: "#1D1A16", red: "#C8312B", teal: "#2F6F6A", mustard: "#D9A441", blue: "#3D5A8A", tape: "rgba(236,222,180,0.82)", label: "#F2EBDD" };
export const FONT_TYPE = "'American Typewriter', 'Courier New', 'Courier Prime', 'Songti SC', 'Noto Serif CJK SC', 'SimSun', serif";
export const FONT_CN = "'Georgia', 'Songti SC', 'STSong', 'Noto Serif SC', 'Noto Serif CJK SC', 'SimSun', serif";   // serif display font (Latin in Georgia; CJK falls back to Songti)
export const FONT_SANS = "'Helvetica Neue', 'PingFang SC', 'Noto Sans SC', 'Noto Sans CJK SC', 'Microsoft YaHei', sans-serif";

const clamp = { extrapolateLeft: "clamp", extrapolateRight: "clamp" } as const;
const outQuint = Easing.bezier(0.22, 1, 0.36, 1);
const outBack = Easing.bezier(0.34, 1.56, 0.64, 1);
export const STEP = 2.5; // 12 fps stepping on a 30 fps timeline

// Element-local frame relative to its entry time `at`, quantised to 12 fps; -1 before entry
export const useLocal = (at: number, step = STEP) => {
  const f = useCurrentFrame() - at;
  return f < 0 ? -1 : Math.floor(f / step) * step;
};

export const Sfx: React.FC<{ at: number; src: string; vol?: number; dur?: number }> = ({ at, src, vol = 0.5, dur = 30 }) => (
  <Sequence from={Math.round(at)} durationInFrames={dur} layout="none"><Audio src={staticFile("sfx/" + src)} volume={vol} /></Sequence>
);

const jitter = (seed: string, k: number, amp: number, rot: number) => [
  (random(`${seed}x${k}`) - 0.5) * 2 * amp, (random(`${seed}y${k}`) - 0.5) * 2 * amp, (random(`${seed}r${k}`) - 0.5) * 2 * rot,
];

// Paper piece: slap down / slide in / pop / drop from above / fade; boil = tiny stop-motion jitter every 3 frames
export type PieceP = {
  src?: string; at: number; x: number; y: number; w?: number; rot?: number; mode?: "slap" | "slide" | "pop" | "drop" | "fade"; from?: [number, number];
  seed?: string; boil?: boolean; z?: number; sfx?: string | false; out?: number; children?: React.ReactNode; shadow?: boolean;
};
export const Piece: React.FC<PieceP> = ({ src, at, x, y, w, rot = 0, mode = "slap", from = [0, 900], seed = "p", boil = true, z = 5, sfx, out, children, shadow = true }) => {
  const f = useLocal(at);
  const raw = useCurrentFrame() - at;
  const snd = sfx === false ? null : sfx ?? ({ slide: "swish-2.wav", pop: "pop.wav", drop: "paper-place-2.wav", fade: null, slap: "paper-place-1.wav" } as Record<string, string | null>)[mode];
  const sound = snd ? <Sfx at={at} src={snd} vol={0.5} /> : null;
  if (f < 0) return sound;
  const dur = mode === "slide" ? 10 : 7.5;
  const t = interpolate(f, [0, dur], [0, 1], { ...clamp, easing: mode === "pop" ? outBack : outQuint });
  let s = 1, r = rot, ox = 0, oy = 0, op = 1;
  if (mode === "slap") { s = interpolate(t, [0, 1], [1.16, 1]); r = rot + interpolate(t, [0, 1], [-5, 0]); }
  if (mode === "pop") { s = interpolate(t, [0, 1], [0.55, 1]); op = Math.min(1, t * 3); }
  if (mode === "slide") { ox = interpolate(t, [0, 1], [from[0], 0]); oy = interpolate(t, [0, 1], [from[1], 0]); }
  if (mode === "drop") { oy = interpolate(t, [0, 1], [-260, 0]); r = rot + interpolate(t, [0, 1], [8, 0]); }
  if (mode === "fade") op = t;
  if (out !== undefined && raw >= out) {
    const to = interpolate(Math.floor((raw - out) / STEP) * STEP, [0, 7.5], [0, 1], { ...clamp, easing: Easing.in(Easing.cubic) });
    oy += to * 1200; r += to * 10;
  }
  const lift = interpolate(t, [0, 1], [26, 6]);
  const [bx, by, br] = boil ? jitter(seed, Math.floor(raw / 3), 1.2, 0.25) : [0, 0, 0];
  return (
    <>
      {sound}
      <div style={{ position: "absolute", left: x, top: y, width: w, zIndex: z, opacity: op,
        transform: `translate(-50%,-50%) translate(${ox + bx}px,${oy + by}px) rotate(${r + br}deg) scale(${s})`,
        filter: shadow ? `drop-shadow(${lift * 0.35}px ${lift * 0.6}px ${lift * 0.5}px rgba(30,20,10,0.38))` : undefined }}>
        {src ? <Img src={staticFile(src)} style={{ width: "100%", display: "block" }} /> : children}
      </div>
    </>
  );
};

export const Tape: React.FC<{ at: number; x: number; y: number; w?: number; rot?: number }> = ({ at, x, y, w = 150, rot = -32 }) => {
  const f = useLocal(at, 2);
  const sound = <Sfx at={at} src="tap.wav" vol={0.35} dur={10} />;
  if (f < 0) return sound;
  const sx = interpolate(f, [0, 4], [0, 1], { ...clamp, easing: outQuint });
  return (
    <>{sound}
      <div style={{ position: "absolute", left: x, top: y, width: w, height: 40, zIndex: 40, transform: `translate(-50%,-50%) rotate(${rot}deg) scaleX(${sx})`, transformOrigin: "left center",
        background: C.tape, boxShadow: "0 1px 3px rgba(0,0,0,0.18)",
        clipPath: "polygon(0 6%,4% 0,8% 8%,12% 1%,100% 0,96% 10%,100% 22%,97% 40%,100% 60%,96% 78%,100% 100%,6% 100%,2% 88%,0 70%,3% 50%,0 30%)" }} />
    </>
  );
};

export const Pin: React.FC<{ at: number; x: number; y: number; color?: string }> = ({ at, x, y, color = "#B8892E" }) => {
  const f = useLocal(at, 2);
  const sound = <Sfx at={at} src="click.wav" vol={0.45} dur={10} />;
  if (f < 0) return sound;
  const s = interpolate(f, [0, 4], [1.8, 1], { ...clamp, easing: outQuint });
  return (
    <>{sound}
      <div style={{ position: "absolute", left: x, top: y, width: 30, height: 30, zIndex: 45, borderRadius: "50%", transform: `translate(-50%,-50%) scale(${s})`,
        background: `radial-gradient(circle at 35% 30%, #F5DC9A 0 18%, ${color} 45%, #6E4D12 100%)`, boxShadow: `${3 * s}px ${5 * s}px ${4 * s}px rgba(0,0,0,0.4)` }} />
    </>
  );
};

// Red string: a sagging curve between two points, drawn on at 12 fps
export const RedString: React.FC<{ at: number; a: [number, number]; b: [number, number]; sag?: number; dur?: number; color?: string; dash?: boolean }> = ({ at, a, b, sag = 40, dur = 14, color = C.red, dash }) => {
  const f = useLocal(at);
  if (f < 0) return null;
  const p = interpolate(f, [0, dur], [0, 1], { ...clamp, easing: Easing.inOut(Easing.cubic) });
  const mx = (a[0] + b[0]) / 2, my = (a[1] + b[1]) / 2 + sag;
  const d = `M${a[0]},${a[1]} Q${mx},${my} ${b[0]},${b[1]}`;
  return (
    <svg style={{ position: "absolute", left: 0, top: 0, zIndex: 42, overflow: "visible" }} width={1920} height={1080}>
      <path d={d} fill="none" stroke="rgba(0,0,0,0.22)" strokeWidth={5} transform="translate(3,6)" pathLength={1} strokeDasharray={1} strokeDashoffset={1 - p} />
      <path d={d} fill="none" stroke={color} strokeWidth={dash ? 6 : 4} strokeLinecap="round" pathLength={1} strokeDasharray={dash ? undefined : 1} strokeDashoffset={dash ? undefined : 1 - p}
        style={dash ? { strokeDasharray: "0.02 0.015", clipPath: `inset(0 ${100 - p * 100}% 0 0)` } : undefined} />
    </svg>
  );
};

const TORN = "polygon(1% 4%,8% 0,20% 5%,33% 1%,47% 4%,60% 0,74% 4%,88% 0,99% 5%,100% 30%,98% 55%,100% 80%,98% 100%,85% 96%,70% 100%,55% 95%,40% 100%,25% 96%,10% 100%,0 96%,2% 70%,0 45%,2% 20%)";

// Torn paper label with typewriter reveal (2 frames per character, key clicks)
export const Label: React.FC<{ at: number; x: number; y: number; text: string; size?: number; rot?: number; cps?: number; bg?: string; color?: string; font?: string; z?: number; out?: number; type?: boolean; mode?: PieceP["mode"] }> = ({ at, x, y, text, size = 46, rot = -2, cps = 2, bg = C.label, color = C.ink, font = FONT_TYPE, z = 30, out, type = true, mode = "slap" }) => {
  const f = useCurrentFrame() - at;
  const chars = Array.from(text);
  cps = Math.min(cps, Math.max(0.6, 24 / chars.length));   // long labels type faster: the whole label finishes within 24 frames (0.8 s)
  const n = type ? Math.max(0, Math.min(chars.length, Math.floor(f / cps) + 1)) : chars.length;
  const keys = type ? chars.map((c, i) => ({ c, t: at + 4 + i * cps })).filter((k, i) => k.c.trim() && i % Math.max(1, Math.round(2 / cps)) === 0) : [];
  return (
    <>
      {keys.filter((_, i) => i % 2 === 0).map((k, i) => <Sfx key={i} at={k.t} src={`key-${(i % 8) + 1}.wav`} vol={0.28} dur={6} />)}
      <Piece at={at} x={x} y={y} rot={rot} seed={"lb" + text} sfx={type ? false : undefined} z={z} out={out} mode={mode}>
        <div style={{ background: bg, padding: `${size * 0.26}px ${size * 0.55}px ${size * 0.3}px`, fontFamily: font, fontSize: size, fontWeight: 700, color, letterSpacing: 2, whiteSpace: "nowrap", clipPath: TORN }}>
          <span>{chars.slice(0, n).join("")}</span><span style={{ visibility: "hidden" }}>{chars.slice(n).join("")}</span>
        </div>
      </Piece>
    </>
  );
};

// Rubber stamp: slams down from 1.7x, multiply blend, grunge mask (use blend="normal" on dark boards)
export const Stamp: React.FC<{ at: number; x: number; y: number; text: string; size?: number; rot?: number; color?: string; z?: number; blend?: string }> = ({ at, x, y, text, size = 64, rot = -8, color = C.red, z = 48, blend = "multiply" }) => {
  const f = useLocal(at, 2);
  const sound = <Sfx at={at} src="slam-2.wav" vol={0.5} />;
  if (f < 0) return sound;
  const s = interpolate(f, [0, 4], [1.7, 1], { ...clamp, easing: Easing.in(Easing.quad) });
  const o = interpolate(f, [0, 2], [0, 0.9], clamp);
  return (
    <>{sound}
      <div style={{ position: "absolute", left: x, top: y, zIndex: z, transform: `translate(-50%,-50%) rotate(${rot}deg) scale(${s})`, opacity: o, mixBlendMode: blend as any }}>
        <div style={{ border: `${size * 0.09}px solid ${color}`, outline: `${size * 0.04}px solid ${color}`, outlineOffset: size * 0.06, padding: `${size * 0.08}px ${size * 0.38}px`,
          color, fontFamily: FONT_CN, fontWeight: 900, fontSize: size, letterSpacing: size * 0.16, whiteSpace: "nowrap",
          WebkitMaskImage: "url(" + staticFile("img/grunge.png") + ")", WebkitMaskSize: "300px" }}>{text}</div>
      </div>
    </>
  );
};

export const Circle: React.FC<{ at: number; x: number; y: number; rx: number; ry: number; dur?: number; rot?: number; color?: string }> = ({ at, x, y, rx, ry, dur = 12, rot = -6, color = C.red }) => {
  const f = useLocal(at);
  const sound = <Sfx at={at} src="swish-1.wav" vol={0.25} dur={15} />;
  if (f < 0) return sound;
  const p = interpolate(f, [0, dur], [0, 1], { ...clamp, easing: Easing.out(Easing.cubic) });
  const pts: string[] = [];
  for (let i = 0; i <= 64; i++) {
    const a = (i / 64) * Math.PI * 2.12 - 0.4, w = 1 + 0.06 * Math.sin(i * 0.7);
    pts.push(`${x + Math.cos(a) * rx * w},${y + Math.sin(a) * ry * w}`);
  }
  return (
    <>{sound}
      <svg style={{ position: "absolute", left: 0, top: 0, zIndex: 46, overflow: "visible", transform: `rotate(${rot}deg)`, transformOrigin: `${x}px ${y}px` }} width={1920} height={1080}>
        <polyline points={pts.join(" ")} fill="none" stroke={color} strokeWidth={7} strokeLinecap="round" strokeLinejoin="round" pathLength={1} strokeDasharray={1} strokeDashoffset={1 - p} opacity={0.92} />
      </svg>
    </>
  );
};

// Marker underline
export const Underline: React.FC<{ at: number; x: number; y: number; w: number; color?: string; dur?: number }> = ({ at, x, y, w, color = C.red, dur = 8 }) => {
  const f = useLocal(at);
  if (f < 0) return null;
  const p = interpolate(f, [0, dur], [0, 1], { ...clamp, easing: Easing.out(Easing.cubic) });
  return (
    <svg style={{ position: "absolute", left: 0, top: 0, zIndex: 46, overflow: "visible" }} width={1920} height={1080}>
      <path d={`M${x - w / 2},${y} q${w / 2},-10 ${w},4`} fill="none" stroke={color} strokeWidth={9} strokeLinecap="round" pathLength={1} strokeDasharray={1} strokeDashoffset={1 - p} opacity={0.9} />
    </svg>
  );
};

// Halftone-dot display type
export const Halftone: React.FC<{ text: string; size: number; color?: string; dot?: number }> = ({ text, size, color = C.red, dot = 7 }) => (
  <div style={{ fontFamily: FONT_SANS, fontWeight: 900, fontSize: size, lineHeight: 1, letterSpacing: -2,
    backgroundImage: `radial-gradient(circle, ${color} 0 ${dot * 0.42}px, transparent ${dot * 0.48}px)`, backgroundSize: `${dot}px ${dot}px`,
    WebkitBackgroundClip: "text", backgroundClip: "text", color: "transparent", WebkitTextStroke: `2px ${color}` }}>{text}</div>
);

// Number nail: big halftone number on a paper card + unit; counts up at 12 fps
export const Num: React.FC<{ at: number; x: number; y: number; value: number; prefix?: string; unit?: string; size?: number; rot?: number; roll?: number; decimals?: number; color?: string; z?: number; bg?: string | false }> = ({ at, x, y, value, prefix = "", unit = "", size = 170, rot = -3, roll = 18, decimals = 0, color = C.red, z = 32, bg = C.label }) => {
  const f = useLocal(at);
  const v = f < 0 ? 0 : interpolate(f, [0, roll], [0, value], { ...clamp, easing: Easing.out(Easing.cubic) });
  const txt = prefix + (decimals ? v.toFixed(decimals) : Math.round(v).toLocaleString("en-US"));
  return (
    <Piece at={at} x={x} y={y} rot={rot} mode="pop" seed={"num" + value} sfx="slam-1.wav" z={z}>
      <div style={{ display: "flex", alignItems: "baseline", gap: size * 0.08, background: bg || undefined, padding: bg ? `${size * 0.04}px ${size * 0.2}px ${size * 0.1}px` : 0, boxShadow: bg ? "0 4px 10px rgba(0,0,0,0.2)" : undefined, clipPath: bg ? TORN : undefined }}>
        <Halftone text={txt} size={size} color={color} />
        {unit && <span style={{ fontFamily: FONT_CN, fontWeight: 900, fontSize: size * 0.36, color: C.ink, whiteSpace: "nowrap" }}>{unit}</span>}
      </div>
    </Piece>
  );
};

// Looping frame sequence (a GPT Image GIF split into frames); `path` moves it along a line (paper-puppet walk)
export const Loop: React.FC<{ at: number; dir: string; n: number; fps?: number; x: number; y: number; w: number; path?: [number, number]; dur?: number; z?: number; rot?: number; card?: boolean; mode?: PieceP["mode"] }> = ({ at, dir, n, fps = 10, x, y, w, path, dur = 120, z = 20, rot = 0, card, mode = "pop" }) => {
  const raw = useCurrentFrame() - at;
  const i = raw < 0 ? 1 : (Math.floor((raw / 30) * fps) % n) + 1;
  const dx = path && raw >= 0 ? interpolate(Math.floor(raw / STEP) * STEP, [0, dur], [0, path[0]], clamp) : 0;
  const dy = path && raw >= 0 ? interpolate(Math.floor(raw / STEP) * STEP, [0, dur], [0, path[1]], clamp) : 0;
  return (
    <Piece at={at} x={x + dx} y={y + dy} w={w} rot={rot} mode={mode} seed={"loop" + dir} z={z} boil={!path} sfx={mode === "pop" ? "pop.wav" : undefined}>
      <div style={card ? { background: "#F2EBDD", padding: 10, boxShadow: "0 3px 8px rgba(0,0,0,0.25)" } : undefined}>
        <Img src={staticFile(`${dir}/${String(i).padStart(4, "0")}.png`)} style={{ width: "100%", display: "block" }} />
      </div>
    </Piece>
  );
};

// Video card: an AI video shot inside a paper frame (or full frame)
export const Clip: React.FC<{ at: number; src: string; x?: number; y?: number; w?: number; full?: boolean; rot?: number; z?: number; startFrom?: number }> = ({ at, src, x = 960, y = 540, w = 1500, full, rot = 0, z = 15, startFrom = 0 }) => {
  if (full) return (
    <Sequence from={Math.round(at)} layout="none">
      <AbsoluteFill style={{ zIndex: z }}><OffthreadVideo src={staticFile(src)} muted startFrom={startFrom} style={{ width: "100%", height: "100%", objectFit: "cover" }} /></AbsoluteFill>
    </Sequence>
  );
  return (
    <Sequence from={Math.round(at)} layout="none">
      <Piece at={0} x={x} y={y} w={w} rot={rot} mode="slap" seed={"clip" + src} z={z} boil={false}>
        <div style={{ background: "#F2EBDD", padding: 14, boxShadow: "0 4px 12px rgba(0,0,0,0.3)" }}>
          <OffthreadVideo src={staticFile(src)} muted startFrom={startFrom} style={{ width: "100%", display: "block", filter: "sepia(0.25) contrast(1.05)" }} />
        </div>
      </Piece>
    </Sequence>
  );
};

// Paper stage: background plate + smooth slow push (camera is not stepped) + grain refreshed every 2 frames + vignette
export const PaperStage: React.FC<{ bg: string; push?: [number, number]; dur: number; flip?: boolean; origin?: string; children: React.ReactNode }> = ({ bg, push = [1, 1.04], dur, flip, origin = "50% 50%", children }) => {
  const f = useCurrentFrame();
  const s = interpolate(f, [0, dur], push, clamp);
  const g = Math.floor(f / 2) % 4;
  return (
    <AbsoluteFill style={{ background: C.paper, overflow: "hidden" }}>
      <AbsoluteFill style={{ transform: `scale(${s})`, transformOrigin: origin }}>
        <Img src={staticFile(bg)} style={{ width: "100%", height: "100%", objectFit: "cover", transform: flip ? "scaleX(-1)" : undefined }} />
        {children}
      </AbsoluteFill>
      <AbsoluteFill style={{ backgroundImage: `url(${staticFile("img/grain.png")})`, backgroundPosition: `${g * 137}px ${g * 71}px`, mixBlendMode: "multiply", opacity: 0.32, pointerEvents: "none", zIndex: 90 }} />
      <AbsoluteFill style={{ background: "radial-gradient(ellipse at center, transparent 55%, rgba(60,40,20,0.28) 100%)", pointerEvents: "none", zIndex: 91 }} />
    </AbsoluteFill>
  );
};
