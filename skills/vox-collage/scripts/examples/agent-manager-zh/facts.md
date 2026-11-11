# Fact list - "Your coding agents made you a manager" (Chinese film)

Spine: Addy Osmani, "Your coding agents made you a manager", X article, 2026-11-08
https://x.com/addyosmani/status/2119332146485891501

## S - author and article
- **S1** X bio: "Claude Code @anthropicai"; the article says "what we've learned from using and creating Claude Code". (profile fetched 2026-11-10)
- **S2** Posted 2026-11-08 07:32 UTC; 503,542 views, 4,081 likes, 464 reposts when fetched on 2026-11-10 (fxtwitter API).

## A - opening argument (article lead)
- **A1** "If you're spending all day with a coding agent, you are managing. You're repeatedly selecting tasks, writing instructions, delegating, following up, evaluating results, and deciding what ships."
- **A2** "The engineers who get the most out of agents aren't necessarily the ones who are best at prompt engineering. They're the ones who learned how to manage, intentionally or otherwise."
- **A3** "Every gripe you have about bad managers is a bug report for interacting with agents."
- **A4** "The sections are roughly ordered by impact." Ten sections precede "Where the analogy breaks".

## P - the ten habits (article sections)
- **P1** Give it a way to check its work: "looks done" is the only validation without a check; new managers without guardrails are "the bottleneck" "within a quarter"; a check "yields a definitive pass/fail result"; "have it show you the results as proof".
- **P2** Set clear context: commander's intent; Netflix "context, not control"; the dashboard example (p95 under 2 s, top support ticket, no schema changes, run the perf script and show before/after - numbers are illustrative in the article); "have the agent interview you until it could write the spec".
- **P3** Make every correction compound: "Anything you've corrected twice" goes into CLAUDE.md; "It outlasts people changing teams and models getting replaced."
- **P4** Let it decide: Andy Grove, High Output Management, task-relevant maturity; prompts and CLAUDE.md are requests, hooks and deny rules are requirements; habits to stop: ALL CAPS, "think harder", "don't be lazy"; "over-process is the new micromanagement".
- **P5** Plan before it builds: "Five agents taking on overlapping tasks won't lead to five times the output, it leads to one merge conflict with five authors."
- **P6** Steer early, reset fast: Esc at the first wrong turn; after two failed corrections clear the session and rewrite the prompt; /rewind makes it "low-risk to try a more ambitious approach first".
- **P7** Delegate the task, never the judgment: "a 600-line diff, the names look reasonable, the tests are green, approve"; "This is not code review, this is code ratification"; the author nearly pushed changes that "added complexity for users for little gain"; "Treat every diff like you're going to get paged for it."
- **P8** Design the run that doesn't need you: five questions (done / self-verification / boundaries / guardrails / who approves); pilot on three files; "probation period".
- **P9** Scale verification, not attention: "orchestration tax"; "Most days I run four or five background agents ... and some days that's too many"; measure cycle time, reverts, rework - not the share of AI-written code.
- **P10** Decide what not to build: "The most important word a manager says is often 'no.'"; "by lunch"; "Review and validation are the scarce resources now."

## X - where the analogy breaks
- **X1** Anti-pattern: "Thinking that an agent is just like a junior developer".
- **X2** Good engineers push back; "Agents are more likely to do what you ask"; counter: ask "the agent to argue against its own answer".
- **X3** "Agents don't have experience, just a notebook."
- **X4** "You're not prepared to manage five people because you've run five agents."

## E - external sources (checked separately)
- **E1** Andy Grove, High Output Management (1983): task-relevant maturity.
- **E2** Shaw & Nave (Wharton), "Thinking-Fast, Slow, and Artificial", SSRN DOI 10.2139/ssrn.6097646. Abstract: "three preregistered experiments ... (N = 1,372; 9,593 trials)"; "Engaging System 3 also increased confidence, even following errors." (Crossref, checked 2026-11-10)
- **E3** "73%" comes from Osmani's blog post "Cognitive Surrender" (2026-05-05), not from the abstract - so the film says "a number Osmani quotes".

## D - Claude Code best-practices guide (cited by the article, checked)
- **D1** "Claude stops when the work looks done ... In practice that makes you the test suite". https://code.claude.com/docs/en/best-practices
- **D2** The guide lists habits to stop, including "don't be lazy"-style instructions.

## Z - ending
- **Z1** "You get feedback in minutes, not quarters. You can undo your own mistakes."
- **Z2** "The job is becoming less about writing the code and more about being the reason good code gets written."
- **Z3** "Nobody's born a great manager ... But with agents, practice is cheap."

## Do not use / careful
- The article says agents are not "a substitute for managers or colleagues" - the film never says they replace people.
- No generated likeness of the author: name label and the article's own cover image (credited).
- The "2 seconds" in the dashboard example is illustrative.
- Habit seven is "the easiest trap", not "the most important" (the article ranks by impact; the first habit ranks highest).
