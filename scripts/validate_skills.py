#!/usr/bin/env python3
"""Validate every skill in this repository.

A skill is any directory (excluding the template and dotfiles) that contains a
``SKILL.md``. For each one we check:

  * the file has YAML-style frontmatter delimited by ``---`` lines;
  * required fields ``name`` and ``description`` are present and non-empty;
  * ``name`` is lowercase/hyphenated and matches the directory name;
  * ``description`` is within a sensible length.

Exits non-zero if any skill is invalid. No third-party dependencies required.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
NAME_RE = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")
MAX_DESCRIPTION = 1024

# Directories that may contain a SKILL.md but should not be validated as a
# shippable skill (the template is intentionally a placeholder).
EXEMPT_DIRS = {"_template"}


def parse_frontmatter(text: str) -> dict[str, str] | None:
    """Extract a minimal key: value frontmatter block. Returns None if absent."""
    if not text.startswith("---"):
        return None
    lines = text.splitlines()
    # find the closing delimiter
    end = None
    for i in range(1, len(lines)):
        if lines[i].strip() == "---":
            end = i
            break
    if end is None:
        return None

    fields: dict[str, str] = {}
    for line in lines[1:end]:
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        if ":" not in line:
            continue
        key, _, value = line.partition(":")
        fields[key.strip()] = value.strip().strip('"').strip("'")
    return fields


def find_skill_dirs() -> list[Path]:
    # Skills are bundled under skills/ (the plugin convention). The _template
    # placeholder lives at the repo root and is intentionally not shipped.
    dirs = []
    for skill_md in REPO_ROOT.glob("skills/*/SKILL.md"):
        if skill_md.parent.name in EXEMPT_DIRS:
            continue
        dirs.append(skill_md.parent)
    return sorted(dirs)


def validate_skill(skill_dir: Path) -> list[str]:
    errors: list[str] = []
    skill_md = skill_dir / "SKILL.md"
    text = skill_md.read_text(encoding="utf-8")

    fm = parse_frontmatter(text)
    if fm is None:
        return [f"{skill_md}: missing or malformed frontmatter (--- ... ---)"]

    name = fm.get("name", "")
    description = fm.get("description", "")

    if not name:
        errors.append(f"{skill_md}: missing 'name' in frontmatter")
    else:
        if not NAME_RE.match(name):
            errors.append(
                f"{skill_md}: name '{name}' must be lowercase, hyphen-separated"
            )
        if name != skill_dir.name:
            errors.append(
                f"{skill_md}: name '{name}' does not match directory "
                f"'{skill_dir.name}'"
            )

    if not description:
        errors.append(f"{skill_md}: missing 'description' in frontmatter")
    elif len(description) > MAX_DESCRIPTION:
        errors.append(
            f"{skill_md}: description is {len(description)} chars "
            f"(max {MAX_DESCRIPTION})"
        )
    elif description.startswith("REPLACE"):
        errors.append(f"{skill_md}: description is still a placeholder")

    return errors


def main() -> int:
    skill_dirs = find_skill_dirs()
    if not skill_dirs:
        print("No skills found (looked for skills/*/SKILL.md).")
        return 0

    all_errors: list[str] = []
    for skill_dir in skill_dirs:
        errors = validate_skill(skill_dir)
        status = "OK" if not errors else "FAIL"
        print(f"[{status}] {skill_dir.name}")
        all_errors.extend(errors)

    print()
    if all_errors:
        print(f"{len(all_errors)} problem(s) found:")
        for err in all_errors:
            print(f"  - {err}")
        return 1

    print(f"All {len(skill_dirs)} skill(s) valid.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
