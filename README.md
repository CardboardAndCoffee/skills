# skills

A collection of [Agent Skills](https://code.claude.com/docs/en/skills) for
Claude Code. Each skill is a self-contained directory that teaches Claude how to
perform a specific task — extending what it can do without bloating the base
prompt.

## What is a skill?

A skill is a folder containing a `SKILL.md` file with YAML frontmatter and
Markdown instructions. Claude reads the frontmatter (`name` + `description`) up
front, and loads the full body only when the skill is relevant — a pattern
called *progressive disclosure*. A skill can also ship supporting files:
reference docs, scripts, and templates that Claude pulls in on demand.

```
my-skill/
├── SKILL.md          # required: frontmatter + instructions
├── reference.md      # optional: detailed docs loaded when needed
└── scripts/          # optional: helper scripts the skill can run
    └── do_thing.py
```

A minimal `SKILL.md`:

```markdown
---
name: my-skill
description: One or two sentences on WHAT this does and WHEN to use it, so Claude knows when to reach for it.
---

# My Skill

Step-by-step instructions for Claude...
```

## Repository layout

```
.
├── _template/           # copy this to start a new skill
├── sharpen/             # make code faster while proving behavior is unchanged
├── write-a-tutorial/    # write a step-by-step, learn-by-doing walkthrough (+ interactive HTML)
├── scripts/
│   └── validate_skills.py
└── .github/workflows/   # CI validation
```

Each top-level directory containing a `SKILL.md` is a skill.

## Using these skills

Skills are discovered from a few locations. To use a skill from this repo:

**Personal (all your projects):**

```bash
mkdir -p ~/.claude/skills
cp -r sharpen ~/.claude/skills/
# or symlink to keep it in sync with this repo:
ln -s "$PWD/sharpen" ~/.claude/skills/sharpen
```

**Project-scoped (one repo, shared with your team via git):**

```bash
mkdir -p .claude/skills
cp -r /path/to/this/repo/sharpen .claude/skills/
```

Claude Code picks up skills automatically and invokes them when a task matches
the skill's `description`. You can also invoke one explicitly with `/sharpen`.

## Adding a new skill

1. Copy the template: `cp -r _template my-new-skill`
2. Edit `my-new-skill/SKILL.md` — set `name` (matching the directory) and a
   crisp `description`.
3. Validate: `python scripts/validate_skills.py`
4. Commit and push.

See [CONTRIBUTING.md](CONTRIBUTING.md) for authoring guidance.

## Validating

```bash
python scripts/validate_skills.py
```

This checks every skill for required frontmatter, a name that matches its
directory, and other common mistakes. CI runs the same check on every push.
