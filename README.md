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
├── .claude-plugin/
│   ├── plugin.json      # makes this repo an installable plugin
│   └── marketplace.json # lists the plugin so consumers can /plugin install it
├── skills/              # the shippable skills (each is one directory)
│   ├── harden-claude/   # post-session: keep project docs lean & fresh from what went wrong
│   ├── sharpen/         # make code faster while proving behavior is unchanged
│   └── write-a-tutorial/# write a step-by-step, learn-by-doing walkthrough (+ interactive HTML)
├── agents/              # bundled subagents (deep-reasoner, quick-lookup)
├── .mcp.json            # bundled MCP servers (Linear)
├── _template/           # copy this to start a new skill (not shipped)
├── scripts/
│   └── validate_skills.py
└── .github/workflows/   # CI validation
```

Each directory under `skills/` containing a `SKILL.md` is a shippable skill.

## Consuming these skills

This repo is both a **plugin** and a **plugin marketplace**, so other projects
can install the skills and auto-update when this repo changes. (Availability is
governed by this repo's GitHub visibility — it's private, so only accounts with
access to it can install.)

### Install via the marketplace (recommended)

In any project, once per machine:

```
/plugin marketplace add CardboardAndCoffee/skills
/plugin install cardboard-skills@cardboard-skills
```

This marketplace also re-publishes a curated third-party plugin:

```
/plugin install mattpocock-skills@cardboard-skills
```

`mattpocock-skills` is [Matt Pocock's skills](https://github.com/mattpocock/skills)
(aihero.dev) — TDD, diagnose, triage, to-issues, to-prd, handoff, and more. It is
**referenced, not copied**: the marketplace entry points at his GitHub repo, so it
tracks his upstream and updates when he does. His repo is MIT-licensed; no files are
vendored here, so his copyright/license stay with his repo.

### Bundled MCP: Linear

The `cardboard-skills` plugin bundles the official [Linear MCP
server](https://linear.app/docs/mcp) (declared in `.mcp.json`), so installing the
plugin gives Claude live access to your Linear workspace — list/create/update issues,
read comments, move statuses, etc. After installing, run `/mcp` once to complete
Linear's OAuth sign-in:

```
/mcp        # authenticate the "linear" server (OAuth, in-browser)
```

It's a hosted remote server (`https://mcp.linear.app/mcp`, OAuth 2.1) — **no API
tokens are stored in this repo**; each user authenticates with their own Linear
account. Working directly in *this* repo also picks up the same `.mcp.json` as a
project-scoped server.

### Bundled agents

The `cardboard-skills` plugin also ships two general-purpose subagents (in
`agents/`), which Claude can delegate to automatically based on a task's needs:

- **`deep-reasoner`** (Opus) — hard, multi-file reasoning: non-obvious bug
  diagnosis, architectural trade-offs, invariant design, migration/concurrency
  review. Returns analysis, not code (unless asked).
- **`quick-lookup`** (Haiku) — cheap, mechanical lookups: find a file, locate a
  symbol, list a module's exports, read a config field. Terse, read-only.

Both are project-agnostic: they lean on whatever conventions your repo already
documents (`CLAUDE.md`, `adr/`/`docs/`, README) rather than assuming a layout.

### Auto-install for a project (no manual commands)

Commit this to a project's `.claude/settings.json`; teammates who trust the repo
get the skills installed automatically:

```json
{
  "extraKnownMarketplaces": {
    "cardboard-skills": {
      "source": { "source": "github", "repo": "CardboardAndCoffee/skills" },
      "autoUpdate": true
    }
  },
  "enabledPlugins": ["cardboard-skills@cardboard-skills"]
}
```

With `"autoUpdate": true`, Claude Code refreshes from this repo at startup and
updates the plugin to the latest version (prompting `/reload-plugins`). Push
here → consumers get it next session.

### Local dev (instant updates)

While editing skills, clone the repo and symlink individual skills into your
personal skills dir so changes show up without a release:

```bash
git clone https://github.com/CardboardAndCoffee/skills ~/src/skills
ln -s ~/src/skills/skills/sharpen ~/.claude/skills/sharpen
```

`SKILL.md` edits take effect immediately; a `git pull` is reflected at once.

Claude Code invokes a skill when a task matches its `description`; you can also
run one explicitly, e.g. `/sharpen`.

## Recommended workflow

The pieces in and around this marketplace are designed to compose into one loop.
A typical pass:

**Planning** — `PRD → grill it → /to-issues → grill each issue`

Draft a PRD and interrogate it with Claude until it's tight. Run **`/to-issues`**
(from `mattpocock-skills`) to break it into issues — which can land straight in
**Linear** via the bundled MCP. Then grill each issue for edge cases before you
start building.

**Development** — `/triage → plan → /tdd → /simplify → PR`

Use **`/triage`** to scope the work, have Claude draft a plan, execute with
**`/tdd`**, tidy with **`/simplify`**, then open the PR.

The `/…` steps come from the referenced **`mattpocock-skills`** plugin (TDD,
triage, to-issues, to-prd, handoff, …); the **Linear MCP** ships with
`cardboard-skills`. The grilling and plan-drafting steps are deliberately
human-in-the-loop — keep them interactive rather than scripting the whole chain.

## Adding a new skill

1. Copy the template: `cp -r _template skills/my-new-skill`
2. Edit `skills/my-new-skill/SKILL.md` — set `name` (matching the directory) and
   a crisp `description`.
3. Validate: `python scripts/validate_skills.py`
4. Commit and push.

See [CONTRIBUTING.md](CONTRIBUTING.md) for authoring guidance.

## Validating

```bash
python scripts/validate_skills.py
```

This checks every skill for required frontmatter, a name that matches its
directory, and other common mistakes. CI runs the same check on every push.
