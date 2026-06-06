#!/usr/bin/env python3
"""Print a friendly greeting. A trivial example of a skill helper script."""

import argparse


def main() -> None:
    parser = argparse.ArgumentParser(description="Print a friendly greeting.")
    parser.add_argument(
        "--name",
        default="world",
        help="Who to greet (default: world).",
    )
    args = parser.parse_args()

    name = args.name.strip() or "world"
    print(f"Hello, {name}! 👋  Your skills are wired up correctly.")


if __name__ == "__main__":
    main()
