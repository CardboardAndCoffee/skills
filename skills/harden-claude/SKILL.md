---
name: harden-claude
description: Post-session knowledge-base hardening that keeps the docs lean. Use when the user says "harden", "harden-claude", or asks to improve the project's docs / agent instructions based on what went wrong or was inefficient in this conversation. Every run pays rent — it removes, merges, and trims as well as adds, aiming to come out net-neutral or smaller, especially in always-loaded files. Works in any repo and any language; it discovers the knowledge base at runtime rather than assuming a layout.
tools: Read, Edit, Grep, Glob, Bash
disable-model-invocation: true
---

# harden-claude

Improve the project's knowledge base from this session's friction — **while
keeping it lean**. The goal is the *smallest, freshest* set of durable notes that
prevents these problems, not an ever-growing pile. This skill is not a
write-only log: every run **pays rent**, removing and consolidating as well as
adding, and aims to come out **net-neutral or smaller**.

Why this matters: the cost of the knowledge base compounds. Notes that are loaded
into every future session are paid for again every session, forever — so an
append-only habit quietly explodes context over time. Each run must leave the
knowledge base at least as cheap to carry as it found it.

## The one principle: hot vs cold

Not all knowledge costs the same.

- **Hot path** — files auto-loaded into *every* session (the agent-instructions
  file: `CLAUDE.md` / `AGENTS.md` / equivalent). Tokens here are paid on every
  session forever. **Budget these hardest.** Keep them a thin index of behavioral
  rules and pointers.
- **Cold path** — on-demand docs (`docs/…`). Paid only when something reads them.
  Detail lives here.

**Default new knowledge to cold.** Only a rule the agent must *always* have in
context earns a hot slot — and then prefer a one-line pointer to a cold doc over
the full text. Protecting the hot path is the single biggest lever against
context bloat.

## Phase 0: Discover and measure

Map where *this* project keeps durable knowledge — don't assume a layout — and
**measure it**, because size is the forcing function for the rest of the run.

- Knowledge files + sizes: !`bash -c 'wc -l CLAUDE.md AGENTS.md README* .cursorrules docs/* doc/* documentation/* 2>/dev/null'`
- Recent commits: !`git log --oneline -10`

Also look for `.github/copilot-instructions.md` or a wiki dir if the above finds
little. Then for each file you find:

1. **Classify hot or cold** (agent-instructions file = hot; everything else =
   cold).
2. **Check it against its budget** (soft caps — triggers, not hard limits):
   - **Hot / agent-instructions file: ≈ 150–200 lines.**
   - **Any single cold doc: ≈ 400–500 lines.**

   A file **over budget** means consolidation is **required this run** for that
   file (see Phase 2), before any addition to it is allowed.

The **routing principle** says which *kind* of file owns a topic; the layout you
just found gives the *path*; the budgets say how hard to push back on growth.

## Routing principle

Each change goes to the file that owns the topic — never a catch-all — and
defaults to the **cold** path:

| Knowledge type | Typical home | Path |
|---|---|---|
| Agent/tool behavioral rules the assistant must always follow here | agent-instructions file (`CLAUDE.md` / `AGENTS.md`) | **hot** (keep as pointers) |
| Project overview, tech stack, entry points | README or overview doc | cold |
| Architecture, data flow, module/component boundaries, managed state | architecture doc | cold |
| Directory/file map, package/module structure | repository-map / structure doc | cold |
| Cross-module dependencies, non-obvious coupling | dependency or architecture doc | cold |
| Build, test, lint, CI commands | workflows / contributing doc | cold |
| Conventions, patterns, style rules | conventions doc | cold |
| Failure modes, gotchas, debugging recipes (app and CI) | debugging / troubleshooting doc | cold |

If a topic has no home and the gap is real, prefer a new *section* in an existing
cold doc; only create a new file as a last resort.

## Phase 1: Session analysis

Review the full conversation for what actually cost time. Produce a concrete,
numbered list across these categories; skip any with no real findings — do not
pad. If the session was clean, say so and stop.

- **A. Failures and retries** — commands that errored and needed correction, tool
  calls rejected or retried, misapplied conventions that caused a
  build/compile/type/lint failure.
- **B. Navigation friction** — files that took two or more Grep/Glob/Read calls to
  locate, directories whose purpose wasn't obvious, docs that pointed to the wrong
  file.
- **C. Architecture or convention gaps** — assumptions that proved wrong (module
  boundaries, serialization / data-format rules, ordering or locking
  constraints), facts that had to be dug out of source rather than docs.
- **D. Context waste** — files read in full when a section would do, the same file
  read twice, searches repeated due to ambiguous structure guidance.

## Phase 2: Pay rent — audit existing knowledge (do this *before* drafting additions)

Review the files you're about to touch, **plus any file over budget**, and draft
removal/consolidation candidates. Look for:

- **Stale / obsolete** — an entry references a symbol, path, or command that no
  longer exists. **Verify by grepping the repo**; if the referent is gone, propose
  deleting the entry.
- **Redundant** — a near-duplicate of another entry (same file or across files).
  Propose merging into the owning file and leaving a cross-reference, not a copy.
- **Low-value** — general language/framework knowledge, or a one-off incident with
  no recurring project-specific cause. Propose deletion.
- **Bloated** — a section that caused confusion by being vague or verbose. Propose
  a tighter rewrite, not an append.

Over-budget files **must** net-shrink this run (merge, split a hot file's detail
into a cold doc, or trim) until they're back under cap.

## Phase 3: Draft additions (sparingly)

For each Phase 1 observation, before proposing an addition, run these gates —
discard the candidate if it fails any:

- **De-dupe first.** Grep the knowledge base for the concept. If it already
  exists, *strengthen the existing entry* instead of adding a new one.
- **Durability gate.** Add only if the knowledge is **recurring**,
  **project-specific**, and **non-obvious**. One-off or generally-derivable → drop.
- **Placement.** Default to a cold doc. Use the hot file only for an
  always-needed behavioral rule, and prefer a one-line pointer.
- **No general advice**, nothing derivable in one step from the relevant source,
  no restating what existing docs already cover.

Then **cap the run**: keep only the few highest-value additions, ranked by
expected future token savings. If a session surfaced ten notes, the best two or
three are almost always the whole win — drop the marginal rest.

Format each candidate (removals and additions alike):

- **Observation:** the specific thing that happened, one sentence.
- **Action:** add / merge / rewrite / delete.
- **Target:** exact file + section, marked **hot** or **cold** (or "new
  section: \<name\>").
- **Proposed text:** the minimal change — quoted block or diff.
- **Why it helps:** one sentence.
- **Net line delta:** e.g. `+4`, `-12`, `+6/-9`.

## Phase 4: Present and apply

Present **removals/consolidations and additions together** as one numbered list,
led by a summary:

- **Total net line delta** for the run (target: ≤ 0, or clearly justified if
  positive).
- **Per-hot-file before → after line count** (a hot file must not grow without an
  offsetting removal).

Ask the user which to apply (e.g. "apply all", "apply 1 3 4", "skip"). After
confirmation, apply one at a time: Read the target (use offset+limit if you know
the section), then Edit. When done, state which candidates were applied, which
skipped, and the resulting file sizes.

Do not add a "last updated" timestamp or any meta-commentary to any file.
