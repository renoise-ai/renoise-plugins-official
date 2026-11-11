#!/usr/bin/env python3
"""Narrative lint for narration.json - run it before spending anything on voice.
Usage: python3 lint_script.py narration.json [--target 300]

narration.json fields it reads (see references/narrative.md):
  top level   "archetype": life | essay | mystery | mechanism      "target_seconds": 300      "motif": "one recurring character/prop"
  per beat    "chapter": "name"  on the first beat of every chapter (the opening chapter is the hook)
              "role": space-separated tags -
                 hook      the opening proposition or strange image (first beat)
                 number    a hard number or rapid list in the hook
                 twist     the reversal that ends the hook
                 question  the main question the film answers (just before the title card)
                 scene     a concrete moment: a person, a place, a time, an action
                 rehook    the open question / unresolved turn that closes a chapter
                 midtwist  the strongest fact or reversal, placed at 40-60% of the running time
                 callback  the ending returns to the opening image
Checks: E = must fix, W = fix unless you can say why not.
  E every beat has a "fact" · cue names start with a letter
  W beat longer than ~15 s · too few [[cues]] for its length (one per ~2.5 s) · total length off target by >10%
  W hook: hook + number + twist all inside the first 25 s, main question before 45 s
  W chapters: at least 3 after the hook, 25-80 s each, each opens on a scene, each (except the last) closes on a rehook
  W midtwist missing or outside 40-60% · no callback at the end · ends on a call to subscribe
  W list narration: 4 or more beats that start with an ordinal ("First", "No. 3", ...)"""
import json, os, re, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from textutil import lang_of, tokens, strip_cues, zh_data, CUE

if len(sys.argv) < 2: sys.exit(__doc__)
N = json.load(open(sys.argv[1], encoding="utf-8")); beats = N["beats"]
lang = lang_of("".join(b["narration"] for b in beats))
rate = 5.6 if lang == "zh" else 2.6
target = float(sys.argv[sys.argv.index("--target") + 1]) if "--target" in sys.argv else float(N.get("target_seconds", 0))
Z = zh_data() if lang == "zh" else {}
ORD = re.compile(Z["ordinal"]) if lang == "zh" else re.compile(r"^(first|second|third|fourth|fifth|sixth|seventh|eighth|ninth|tenth|number \w+|no\. ?\d+|\d+[.)]|rule \w+|habit \w+|lesson \w+)\b", re.I)
SUB = re.compile(Z["subscribe"]) if lang == "zh" else re.compile(r"\b(subscribe|like and|smash that|hit the bell|follow for)\b", re.I)

E, W = [], []
t, rows, chapters = 0.0, [], []
for b in beats:
    txt = strip_cues(b["narration"]); n = len(tokens(txt, lang)); d = n / rate
    cues = CUE.findall(b["narration"]); roles = set(str(b.get("role", "")).split())
    if not b.get("fact"): E.append(f"{b['id']}: no \"fact\" - every line needs a source id")
    for c in cues:
        if not c[0].isalpha(): E.append(f"{b['id']}: cue [[{c}]] must start with a letter")
    if d > 15.5: W.append(f"{b['id']}: about {d:.0f}s - split it (15 s max per beat)")
    if d > 4 and len(cues) < int(d / 2.5): W.append(f"{b['id']}: {len(cues)} cue(s) for ~{d:.0f}s - mark one visual landing per ~2.5 s")
    if b.get("chapter") or not chapters: chapters.append({"name": b.get("chapter") or "(unnamed opening)", "beats": []})
    rows.append({"id": b["id"], "t0": t, "t1": t + d, "roles": roles, "text": txt, "ord": bool(ORD.search(txt.strip()))})
    chapters[-1]["beats"].append(rows[-1]); t += d + 0.2
total = t
at = lambda role: next((r for r in rows if role in r["roles"]), None)

if target and abs(total - target) > target * 0.1: W.append(f"estimated {total:.0f}s vs target {target:.0f}s - {'cut' if total > target else 'add'} about {abs(total - target):.0f}s")
if not N.get("archetype"): W.append('no "archetype" (life | essay | mystery | mechanism) - pick the skeleton before writing, see references/narrative.md')
if not N.get("motif"): W.append('no "motif" - name the one character or prop that returns in every chapter')
# hook
for role, limit, why in (("hook", 4, "the first beat states a proposition or shows a strange image"), ("number", 25, "a hard number or rapid list inside the first 25 s"),
                         ("twist", 25, "the reversal that ends the hook, inside the first 25 s"), ("question", 45, "the main question, right before the title card")):
    r = at(role)
    if not r: W.append(f"hook: no beat tagged \"{role}\" - {why}")
    elif r["t0"] > limit: W.append(f"hook: \"{role}\" ({r['id']}) starts at {r['t0']:.0f}s - it belongs before {limit}s")
# chapters
body = chapters[1:] if len(chapters) > 1 else []
if len(chapters) < 2: W.append('no "chapter" marks - put "chapter": "name" on the first beat of each chapter (the hook is chapter one)')
elif len(body) < 3: W.append(f"only {len(body)} chapter(s) after the hook - plan 3 to 6")
for k, ch in enumerate(body):
    L = ch["beats"][-1]["t1"] - ch["beats"][0]["t0"]; first, last = ch["beats"][0], ch["beats"][-1]
    if L > 80 or L < 25: W.append(f"chapter \"{ch['name']}\": about {L:.0f}s - aim for 30-75 s")
    if "scene" not in first["roles"]: W.append(f"chapter \"{ch['name']}\": opens with {first['id']} which is not a scene - start on a person, place and moment, then give the principle")
    if k < len(body) - 1 and "rehook" not in last["roles"]: W.append(f"chapter \"{ch['name']}\": {last['id']} closes it without a rehook - end on an open question or an unresolved turn")
m = at("midtwist")
if not m: W.append("no \"midtwist\" - put the strongest fact or reversal at 40-60% of the running time, not near the end")
elif not 0.38 <= m["t0"] / total <= 0.62: W.append(f"midtwist ({m['id']}) sits at {m['t0'] / total:.0%} - move it to 40-60%")
if not any("callback" in r["roles"] for r in rows[-3:]): W.append("ending: no \"callback\" in the last three beats - return to the opening image, changed")
if SUB.search(rows[-1]["text"]): W.append("ending: do not close on a call to subscribe - end on a quote, an image or an open question")
ords = [r["id"] for r in rows if r["ord"]]
if len(ords) >= 4: W.append(f"list narration: {len(ords)} beats start with an ordinal ({', '.join(ords[:6])}{'...' if len(ords) > 6 else ''}) - carry the items inside one story (essay skeleton) instead of counting them off")

print(f"{lang} · {len(beats)} beats · about {total:.0f}s ({total / 60:.1f} min) · archetype {N.get('archetype', '-')} · motif {N.get('motif', '-')}")
for ch in chapters:
    L = ch["beats"][-1]["t1"] - ch["beats"][0]["t0"]
    tags = " ".join(sorted(set().union(*[r["roles"] for r in ch["beats"]]))) or "-"
    print(f"  {ch['beats'][0]['t0']:5.0f}s  {L:4.0f}s  {ch['beats'][0]['id']}-{ch['beats'][-1]['id']}  {ch['name'][:36]:36}  [{tags}]")
for x in E: print("E " + x)
for x in W: print("W " + x)
print(f"{len(E)} errors, {len(W)} warnings")
sys.exit(1 if E else 0)
