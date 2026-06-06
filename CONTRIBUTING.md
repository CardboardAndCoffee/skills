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
| `name`        | yes      | Lowercase, hyphen-separated. **Must match the directory name.** |
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

## Writing a good `description`

This is what Claude matches against to decide whether to use the skill. Make it
concrete.

- ✅ `Generate Conventional Commits-style messages from a staged git diff. Use when the user asks to write or improve a commit message.`
- ❌ `Helps with git.` (too vague — won't trigger reliably)

Lead with the trigger condition when you can ("Use when…").

## Checklist before committing

- [ ] Directory name matches `name` in frontmatter.
- [ ] `description` says both *what* and *when*.
- [ ] `SKILL.md` body is actionable and points to supporting files instead of
      inlining large content.
- [ ] `python scripts/validate_skills.py` passes.
