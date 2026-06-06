---
name: write-a-tutorial
description: Write a step-by-step, learn-by-doing tutorial walkthrough for a hands-on task — the kind a human follows to do GUI/Editor/creative work an agent can't do blind (e.g. Unity setup, design tooling, a new toolchain). Produces a canonical Markdown guide and, optionally, a self-contained interactive HTML view (TOC, dark/light, saved progress). Use when the user wants a "walkthrough", "tutorial", "how-to guide", "teach me how to do X", a HITL hand-off doc, or the "step-by-step tutorial-style walkthrough" deliverable from a triage/HITL brief.
---

# Write a Tutorial

Produce a walkthrough that takes a reader from nothing to a working result. The **depth** of
explanation is set by a **level** — beginner, intermediate, or expert — tied to the reader's
experience **in the specific vertical** (the tool/tech/domain this teaches), *not* to their
engineering seniority. A staff engineer who's never touched ClickHouse wants the beginner
level. General engineering competence is assumed at every level; only vertical-specific
scaffolding scales. See **[STRUCTURE.md](STRUCTURE.md) → Levels** for the rubric.

Optimized for **hybrid HITL work**: an agent writes the code/glue; a human does the
manual GUI/creative steps and follows this to learn how.

## Output convention

- **Canonical Markdown** lives in the project's docs tree — `docs/walkthroughs/<slug>.md` is the
  default; if the repo keeps docs elsewhere (e.g. `docs/guides/`, `documentation/`, a wiki dir),
  match the existing layout instead.
- **Interactive HTML** (optional but default) is *generated from* the Markdown — never hand-edited.
  Build it with the bundled script (path is stable wherever the skill is installed):
  ```
  python3 .claude/skills/write-a-tutorial/scripts/build_tutorial.py <path>/<slug>.md
  ```
  It writes `<slug>.html` beside the source: a single offline file with a TOC sidebar,
  scrollspy, copy buttons, checkable task lists with saved progress, and a theme toggle.
  Title, kicker, and storage key are derived from the doc's first `# H1`. The script is
  self-contained (Python 3 stdlib only — no pip installs, no network).

> If the project already has its own walkthrough builder, prefer matching its conventions
> over the bundled script.

## Workflow

1. **Ask the user for the level — always, before drafting.** This is a blocking first step:
   use `AskUserQuestion` to ask which level to write at, even if you could guess. Offer
   **beginner / intermediate / expert**, each labelled by *vertical experience* (e.g. "Beginner —
   new to <vertical>", "Expert — fluent, wants the project-specific runbook"), naming the inferred
   vertical in the options. Do **not** silently default; the only time you skip the question is
   when the user has already named a level explicitly in the conversation.
2. **Gather the rest from the session.** **Infer the vertical** — this skill runs *after* the
   plan is set, so the conversation already establishes what tech/domain is being taught; don't
   re-interrogate the user about it. Then identify: the end state ("what you'll have built"), the
   environment/tool, and — for HITL briefs — the **acceptance criteria** the tutorial must let the
   reader satisfy. If a seam exists between code (already done) and manual work (the reader's job),
   state it explicitly.
3. **Draft the Markdown** following the required spine and voice in
   [STRUCTURE.md](STRUCTURE.md). Read it before writing — it is not optional boilerplate.
4. **Walk it yourself, mentally.** Every step must be executable in order with no forward
   references. If a step needs a decision or can go wrong, attach a callout.
5. **Build the HTML** (unless the user said Markdown-only) and report both paths.
6. **Review with the user.** Confirm the end state matches, the steps are complete, and the
   depth is right. Tutorials are verified by someone *following* them — invite that.

## The spine (enforced — see STRUCTURE.md for detail)

The spine has a **fixed floor** (mandatory at every level) and a **variable shape** (sections
that scale with — or drop at — higher levels). A tutorial is not done until it has, in order:

- [ ] **Title** (`# H1`) naming the thing built, one-line promise of the end state. *(all levels)*
- [ ] **Level subtitle** — one line under the title stating the assumed vertical experience,
      e.g. *"For readers new to ClickHouse — assumes you've not used it before."* *(all levels)*
- [ ] **Not-yet-verified banner** — a `⚠️` warning callout noting the steps weren't dry-run
      end-to-end and may need adjusting. The skill doesn't execute what it writes. *(all levels)*
- [ ] **"What you're building"** — the mental model. *(full → brief → omitted at expert)*
- [ ] **Vocabulary** — terms the guide and the tool/code must agree on. *(full → slice-only → omitted at expert)*
- [ ] **Prerequisites** — exact versions, installs, accounts. *(spelled out → lighter → version/project-specific only)*
- [ ] **Numbered Parts → Steps** — `## Part N`, `### Step N.M`. *(all levels; granularity scales: every UI element named → commands + key fields → terse decisive commands)*
- [ ] **"Why" callouts** (`>` blockquotes). *(every fork → non-obvious forks → counterintuitive gotchas only)*
- [ ] **Troubleshooting** — the errors they're most likely to hit and the exact fix. *(all levels)*
- [ ] **Verify** — a checklist that maps 1:1 to the acceptance criteria / definition of done. *(all levels)*

## Don'ts

- Don't conflate level with engineering seniority — it's experience **in the vertical**. Never
  explain general engineering (shells, env vars, config files) even at beginner.
- Don't let the dial govern adjacent tools — the level scales only the **named vertical**;
  a second tool the slice happens to need gets a one-line pointer at every level, never a full teach.
- Don't assume vertical knowledge beyond the chosen level (at beginner, define it in Vocabulary first).
- Don't forward-reference ("we'll wire this later" without a back-link when you do).
- Don't hand-edit the generated HTML — edit the Markdown and rebuild.
- Don't put time-sensitive phrasing ("the new X", "recently") in the guide.
