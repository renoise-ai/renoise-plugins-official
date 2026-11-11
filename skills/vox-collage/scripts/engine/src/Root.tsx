import React from "react";
import { Composition, Sequence, useCurrentFrame } from "remotion";
import { Full, Main, FilmData, Visual, Subs, renderEl } from "./Film";
import { PaperStage } from "./kit";
import film from "../public/film.json";

const data = film as unknown as FilmData & { cover_shot?: { bg: string; els: any[] } };
const fullLen = (data.coverFrames ?? 15) + (data.teaser ?? []).reduce((a, c) => a + c.len, 0) + data.total;

// Cover still: the `cover_shot` from shots.json, every element already landed (at = -30)
export const Cover: React.FC = () => {
  const c = data.cover_shot;
  if (!c) return null;
  return (
    <PaperStage bg={c.bg} dur={1} push={[1, 1]}>
      {c.els.map((el, i) => renderEl({ ...el, at: -30, boil: false, sfx: false }, i))}
    </PaperStage>
  );
};

// Proof sheet: one frame per shot, 8 frames before it ends (all elements on screen)
const Proof: React.FC = () => {
  const f = useCurrentFrame();
  const sh = data.shots[Math.min(f, data.shots.length - 1)];
  return <Sequence from={f - (sh.e - 8)}><Visual data={data} />{data.subs && <Subs subs={data.subs} />}</Sequence>;   // captions included so overlaps show up
};

export const Root: React.FC = () => (
  <>
    <Composition id="Full" component={Full} durationInFrames={fullLen} fps={30} width={1920} height={1080} defaultProps={{ data }} />
    <Composition id="Main" component={Main} durationInFrames={data.total} fps={30} width={1920} height={1080} defaultProps={{ data }} />
    <Composition id="Proof" component={Proof} durationInFrames={data.shots.length} fps={30} width={1920} height={1080} />
    <Composition id="Cover" component={Cover} durationInFrames={1} fps={30} width={1920} height={1080} />
  </>
);
