---
name: harden-claude
description: Post-session docs hardening. Use when the user says "harden-claude", "harden", or asks to improve the docs based on what happened in this conversation.
tools: Read, Edit, Grep, Glob, Bash
disable-model-invocation: true
---

# harden-claude

Improve the project knowledge base based on what actually went wrong or was inefficient in this session.

## File Routing

Changes go to the file that owns the relevant knowledge — not always CLAUDE.md:

| Content type | Target file |
|---|---|
| Claude Code behavioral rules (subagents, tool quirks) | `CLAUDE.md` |
| Project overview, tech stack, GitHub CLI | `AGENTS.md` |
| Architecture, IPC commands, data flows, managed state | `docs/architecture.md` |
| Directory/file map, crate structure | `docs/repository-map.md` |
| Cross-module dependencies, non-obvious coupling | `docs/dependency-graph.md` |
| Build, test, lint, CI commands | `docs/workflows.md` |
| Branching, serde rules, state patterns, conventions | `docs/conventions.md` |
| App failure modes, gotchas, useful commands | `docs/debugging.md` § App Debugging |
| CI failure modes, pipeline gotchas | `docs/debugging.md` § CI Debugging |
| Icon pipeline, branding, platform requirements | `docs/icon-branding.md` |

`CLAUDE.md` must stay thin — only Claude Code-specific behavioral rules belong there.

## Dynamic Context

- Recent commits: !`git log --oneline -10`
- Docs file sizes: !`wc -l CLAUDE.md AGENTS.md docs/*.md 2>/dev/null`

## Phase 1: Session Analysis

Review the full conversation history for this session. Produce a concrete, numbered list of observations across these four categories. Skip any category that has no real findings — do not pad.

**A. Failures and retries**
Commands that errored and needed correction, tool calls that were rejected or retried, misapplied conventions that caused a Rust compile error or linting failure.

**B. Navigation friction**
Files that required two or more Grep/Glob/Read calls to locate, directories whose purpose was not obvious from the docs, cases where the architecture table sent you to the wrong file.

**C. Architecture or convention gaps**
Assumptions made that turned out to be wrong (e.g., lock ordering, crate boundaries, IPC serialization rules), information that had to be discovered by reading source code rather than consulting the docs.

**D. Context waste**
Files read in full when only a section was needed, the same file read more than once, searches run multiple times due to ambiguous project structure guidance.

If the session was clean and there are no observations, say so and stop here.

## Phase 2: Draft Candidate Changes

For each observation from Phase 1, produce exactly one candidate change. Each candidate must have:

- **Observation:** (the specific thing that happened, one sentence)
- **Target file + section:** (the exact file and section heading this belongs under, using the routing table above — or "new section: \<name\>" in the appropriate file)
- **Proposed text:** (the minimal addition, clarification, or deletion — as a quoted block or diff)
- **Why it helps:** (one sentence explaining how this prevents the problem in future sessions)

Hard constraints — discard any candidate that fails these:

- No general Rust, React, TypeScript, or Tauri advice that applies to any project.
- No information derivable in one step by reading the relevant source file.
- No restating of what is already covered in any docs file.
- No new sections unless the gap genuinely has no existing home.
- Trim, don't just add: if an existing section caused confusion by being too vague or too verbose, propose a rewrite rather than appending.
- Do not add anything to `CLAUDE.md` that belongs in a `docs/` file.
- If a fact appears in more than one `docs/` file, update only the file that owns it (per the routing table). Add or preserve a cross-reference in the other file rather than duplicating the content.
- **Prefer removal over addition for debugging entries.** If a failure mode is resolvable from general language/framework knowledge (e.g. "add the missing import", "use `#[allow(deprecated)]`"), do not add it. Only document failures that are non-obvious due to project-specific constraints (lock semantics, crate boundaries, CI infrastructure quirks, parser behavior).

## Phase 3: Present and Apply

Present all candidates as a numbered list with their full details. Ask the user to confirm which candidates to apply (e.g., "apply all", "apply 1 3 4", or "skip").

After confirmation, for each approved candidate: read the target file with the Read tool (use offset+limit if you already know which section to target), then apply the change with Edit. Work one candidate at a time. After all edits, state which candidates were applied and which were skipped.

Do not add a "last updated" timestamp or any meta-commentary to any file.
