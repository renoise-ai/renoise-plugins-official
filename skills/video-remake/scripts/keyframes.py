#!/usr/bin/env python3
"""Show the keyframes for approval: each source frame next to the keyframe made from it.

    python keyframes.py <analysis folder> keyframes.json [-o sheet.jpg]

keyframes.json maps a keyframe key from remake/plan.json ("7", or "7.2" for the second part of a split shot) to the
image the image model made, paths relative to keyframes.json or absolute: {"2": "kf/kf_2.png", "7.1": "kf/kf_7_1.png"}.
Keys without an image show the source frame alone, marked missing. Writes remake/keyframes/sheet.jpg (or -o), pages of
at most six pairs (sheet.jpg, sheet_2.jpg, ...) so each page stays readable, and prints what is missing.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

PER_PAGE = 6
CELL_H = 360


def main() -> None:
    from PIL import Image, ImageDraw

    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("dir", help="analyze.py output folder (has remake/plan.json)")
    ap.add_argument("keyframes", help="keyframes.json: keyframe key -> image")
    ap.add_argument("-o", "--out", help="sheet path (default <dir>/remake/keyframes/sheet.jpg)")
    args = ap.parse_args()
    root = Path(args.dir)
    plan = json.loads((root / "remake" / "plan.json").read_text(encoding="utf-8"))
    kpath = Path(args.keyframes)
    made = json.loads(kpath.read_text(encoding="utf-8"))
    out = Path(args.out) if args.out else root / "remake" / "keyframes" / "sheet.jpg"
    out.parent.mkdir(parents=True, exist_ok=True)

    def fit(p: Path):
        im = Image.open(p).convert("RGB")
        return im.resize((max(1, round(im.width * CELL_H / im.height)), CELL_H))

    missing, unknown = [], sorted(set(made) - {k["key"] for k in plan["keyframes"]})
    pairs = []
    for k in plan["keyframes"]:
        src = fit(root / k["source_frame"])
        img = made.get(k["key"])
        if img:
            q = Path(img) if Path(img).is_absolute() else kpath.parent / img
            if not q.exists():
                sys.exit(f"✗ {q} (keyframe {k['key']}) does not exist")
            new = fit(q)
        else:
            missing.append(k["key"])
            new = None
        pairs.append((k, src, new))
    pages = []
    for p0 in range(0, len(pairs), PER_PAGE):
        chunk = pairs[p0:p0 + PER_PAGE]
        cw = max(src.width for _, src, _ in chunk)
        sheet = Image.new("RGB", (len(chunk) * (cw + 8) + 8, 2 * CELL_H + 44), (24, 24, 24))
        d = ImageDraw.Draw(sheet)
        for n, (k, src, new) in enumerate(chunk):
            x = 8 + n * (cw + 8)
            d.text((x, 6), f"#{k['key']} ({k['item']}, {k['at']:.1f}s)  source / keyframe", fill=(235, 235, 235))
            sheet.paste(src, (x, 22))
            if new is not None:
                sheet.paste(new.resize((src.width, CELL_H)) if abs(new.width - src.width) > 2 else new, (x, 26 + CELL_H))
            else:
                d.text((x + 8, 30 + CELL_H + CELL_H // 2), "missing", fill=(255, 120, 120))
        page = out if not pages else out.with_name(f"{out.stem}_{len(pages) + 1}{out.suffix}")
        sheet.save(page, quality=88)
        pages.append(str(page))
    print(json.dumps({"sheets": pages, "keyframes": len(plan["keyframes"]), "missing": missing,
                      "not_in_plan": unknown}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
