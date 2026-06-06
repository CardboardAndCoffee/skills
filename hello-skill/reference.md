# Anatomy of a skill (reference)

This file exists to demonstrate *progressive disclosure*: `SKILL.md` stays
short, and the deeper detail lives here, loaded by Claude only when needed.

## The three parts

1. **Frontmatter** (`name`, `description`) — always in Claude's context. The
   `description` is the trigger; write it for matching against user intent.

2. **Body** — the Markdown after the frontmatter. Loaded when the skill fires.
   Keep it imperative and scannable: a summary, when-to-use bullets, numbered
   steps, and notes.

3. **Supporting files** — anything else in the directory:
   - `reference.md` (this file): detailed docs.
   - `scripts/`: deterministic helpers Claude can execute.
   - `templates/`: boilerplate to fill in.

## Why scripts?

For mechanical work (parsing, formatting, validation), a script is more reliable
than asking Claude to do it by hand, and it keeps token usage low. `scripts/greet.py`
is a trivial stand-in — your real skills will do something useful here.

## Naming rules

- `name` must be lowercase, hyphen-separated, and match the directory name.
- Keep names short and descriptive: `pdf-extract`, `commit-message`, `changelog`.
