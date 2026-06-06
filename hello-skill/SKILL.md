---
name: hello-skill
description: A minimal worked example of an Agent Skill. Use as a reference when authoring new skills, or invoke it to print a friendly greeting and confirm skills are wired up correctly.
---

# Hello Skill

A tiny, self-contained skill that demonstrates the structure of a well-formed
skill: frontmatter, a clear body, a supporting reference doc, and a helper
script. Use it as a template you can read, and as a smoke test that skill
discovery works.

## When to use

- The user wants to confirm that skills are installed and being picked up.
- You're authoring a new skill and want a concrete, working example to copy.

## Steps

1. Run the helper script to produce the greeting:

   ```bash
   python scripts/greet.py --name "$USER"
   ```

2. Show the user the output.
3. If they're learning the skill format, point them at `reference.md` for the
   anatomy of a skill and at this file as the canonical minimal example.

## Notes

- This skill has no side effects beyond printing — safe to run anytime.
- See [`reference.md`](reference.md) for a deeper explanation of each part.
