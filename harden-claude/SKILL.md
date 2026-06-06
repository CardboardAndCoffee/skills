---
name: harden-claude
description: Post-session knowledge-base hardening. Use when the user says "harden", "harden-claude", or asks to improve the project's docs / agent instructions based on what went wrong or was inefficient in this conversation. Works in any repo and any language — it discovers the project's knowledge base at runtime rather than assuming a layout.
tools: Read, Edit, Grep, Glob, Bash
disable-model-invocation: true
---

# harden-claude

Improve the project's knowledge base based on what actually went wrong or was
inefficient in this session. Works in any repo and any language: **discover the
project's existing docs first**, then route each fix to whichever file already
owns that topic.

## Phase 0: Discover the knowledge base

Before analyzing anything, map where *this* project keeps durable knowledge.
Don't assume a layout — find it. Look for:

- **Agent / assistant instruction files** at the repo root and standard
  locations: `CLAUDE.md`, `AGENTS.md`, `.cursorrules`,
  `.github/copilot-instructions.md`, and the top-level `README`.
- **A docs tree** — `docs/`, `doc/`, `documentation/`, a wiki dir, or whatever
  this repo uses.

Enumerate what actually exists, then build a short "topic → owning file" map from
the result:

- Knowledge files: !`ls CLAUDE.md AGENTS.md README* .cursorrules 2>/dev/null; ls docs/ doc/ documentation/ 2>/dev/null`
- Recent commits: !`git log --oneline -10`

The **routing principle** below says *which kind* of file owns a topic; the
project's actual layout (what you just found) says the *path*. If a project has
only a `README`, route everything sensible there.

## Routing principle

Each change goes to the file that owns the relevant knowledge — never a
catch-all. Map the topic to the file this project already uses for it:

| Knowledge type | Typical home |
|---|---|
| Agent/tool behavioral rules — how the assistant should act in this repo | the agent-instructions file (`CLAUDE.md` / `AGENTS.md` / equivalent) |
| Project overview, tech stack, entry points | top-level `README` or overview doc |
| Architecture, data flow, module/component boundaries, managed state | architecture doc |
| Directory/file map, package/module structure | repository-map / structure doc |
| Cross-module dependencies, non-obvious coupling | dependency or architecture doc |
| Build, test, lint, CI commands | workflows / contributing doc |
| Conventions, patterns, style rules | conventions doc |
| Failure modes, gotchas, debugging recipes (app and CI) | debugging / troubleshooting doc |

Keep the **agent-instructions file thin** — only assistant-behavioral rules
belong there; everything a human would also want lives in the docs. If a topic
has no home and the gap is real, propose a new section (or, only if necessary, a
new file) in the project's existing docs location.

## Phase 1: Session Analysis

Review the full conversation history for this session. Produce a concrete,
numbered list of observations across these four categories. Skip any category
with no real findings — do not pad.

**A. Failures and retries**
Commands that errored and needed correction, tool calls that were rejected or
retried, misapplied conventions that caused a build/compile/type/lint failure.

**B. Navigation friction**
Files that required two or more Grep/Glob/Read calls to locate, directories whose
purpose was not obvious from the docs, cases where the docs pointed to the wrong
file.

**C. Architecture or convention gaps**
Assumptions that turned out to be wrong (e.g. module boundaries, serialization /
data-format rules, ordering or locking constraints), information that had to be
discovered by reading source code rather than consulting the docs.

**D. Context waste**
Files read in full when only a section was needed, the same file read more than
once, searches run multiple times due to ambiguous project-structure guidance.

If the session was clean and there are no observations, say so and stop here.

## Phase 2: Draft Candidate Changes

For each observation from Phase 1, produce exactly one candidate change. Each
candidate must have:

- **Observation:** the specific thing that happened, one sentence.
- **Target file + section:** the exact file and section heading this belongs
  under (using the routing principle and the layout you discovered) — or
  "new section: \<name\>" in the appropriate file.
- **Proposed text:** the minimal addition, clarification, or deletion — as a
  quoted block or diff.
- **Why it helps:** one sentence on how this prevents the problem next session.

Hard constraints — discard any candidate that fails these:

- No general programming-language or framework advice that applies to any
  project.
- No information derivable in one step by reading the relevant source file.
- No restating of what is already covered in any docs file.
- No new sections unless the gap genuinely has no existing home.
- Trim, don't just add: if an existing section caused confusion by being too
  vague or too verbose, propose a rewrite rather than appending.
- Do not put in the agent-instructions file anything that belongs in a docs file.
- If a fact appears in more than one doc, update only the file that owns it and
  add (or preserve) a cross-reference in the other rather than duplicating.
- **Prefer removal over addition for debugging entries.** If a failure mode is
  resolvable from general language/framework knowledge (e.g. "add the missing
  import", "silence the deprecation"), do not add it. Only document failures that
  are non-obvious due to **project-specific** constraints (ordering/locking
  semantics, module boundaries, CI infrastructure quirks, parser/tool behavior).

## Phase 3: Present and Apply

Present all candidates as a numbered list with their full details. Ask the user
to confirm which to apply (e.g. "apply all", "apply 1 3 4", or "skip").

After confirmation, for each approved candidate: read the target file with the
Read tool (use offset+limit if you already know the section), then apply the
change with Edit. Work one candidate at a time. After all edits, state which
candidates were applied and which were skipped.

Do not add a "last updated" timestamp or any meta-commentary to any file.
