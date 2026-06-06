# Contributing a skill

Skills live or die by their `description` and how tightly scoped they are. A few
guidelines.

## Anatomy

Every skill is a directory with a `SKILL.md`:

```markdown
---
name: skill-name
description: What it does and when to use it.
---

# Skill Name

Instructions for Claude.
```

### Frontmatter

| Field         | Required | Notes |
|---------------|----------|-------|
| `name`        | yes      | Lowercase, hyphen-separated. **Must match the directory name.** **Name skills as verbs** — what the skill *does* — so the invocation reads as an action: `/sharpen`, `/review`, `/summarize`, not `/sharpener` or `/reviewer`. |
| `description` | yes      | The single most important field. Write it for *triggering*: state what the skill does and the situations where Claude should reach for it. Keep it under ~1024 characters. |

### Body

The Markdown body is loaded only once the skill is triggered, so spend the
budget freely on clear, imperative instructions. Good bodies tend to:

- Open with a one-line summary of what the skill accomplishes.
- Give numbered steps for the common path.
- Call out edge cases and what *not* to do.
- Reference supporting files instead of inlining everything (progressive
  disclosure) — e.g. "See `reference.md` for the full option list."

## Supporting files

- **`reference.md`** (or any `.md`): deep detail Claude loads only when needed.
  Keep `SKILL.md` lean and point to these.
- **`scripts/`**: deterministic helpers. Prefer a script over prose when a task
  is mechanical (parsing, formatting, validation) — it's more reliable and saves
  tokens.
- **`templates/`**: boilerplate the skill fills in.

## Keep skills generic

**A skill must be project-, language-, and stack-agnostic.** It encodes a
reusable *technique*, not the specifics of any one repo. Anyone should be able to
drop the skill into an unrelated project and have it work.

Concretely, a skill must **not** hardcode:

- **A specific project's layout** — file names, directory structure, or doc paths
  that only exist in one repo (e.g. `docs/architecture.md`, `AGENTS.md`). Discover
  structure at runtime, or take it as input, instead of assuming it.
- **A specific language, framework, or toolchain** — don't bake in Rust/React/
  Tauri/etc. assumptions. If a skill genuinely needs a runtime, make that a
  plug-in point (e.g. a per-language adapter the skill calls), not a hardcoded
  branch.
- **Org- or product-specific names, services, or conventions.**

When something genuinely varies per project or per language, push it behind a
**seam** — ask the user, detect it, or read it from a config/template — rather
than embedding one project's answer. Use placeholders (`<doc-path>`,
`<test-command>`) in examples, not real paths from a private repo.

> Rule of thumb: if a skill would need editing before it worked in a *different*
> project, it isn't generic yet. Genericity lives in the skill; specifics are
> inputs.

## Writing a good `description`

This is what Claude matches against to decide whether to use the skill. Make it
concrete.

- ✅ `Generate Conventional Commits-style messages from a staged git diff. Use when the user asks to write or improve a commit message.`
- ❌ `Helps with git.` (too vague — won't trigger reliably)

Lead with the trigger condition when you can ("Use when…").

## Checklist before committing

- [ ] Directory name matches `name` in frontmatter.
- [ ] `name` is a verb (an action the skill performs).
- [ ] **Generic:** no hardcoded project layout, language, framework, or org-specific
      names — would work as-is in an unrelated repo.
- [ ] `description` says both *what* and *when*.
- [ ] `SKILL.md` body is actionable and points to supporting files instead of
      inlining large content.
- [ ] `python scripts/validate_skills.py` passes.
