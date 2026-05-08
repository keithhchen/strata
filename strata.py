#!/usr/bin/env python3
"""
strata — initialize the Strata testing harness in your project.

Usage:
    python3 strata.py init [target_dir]
    python3 strata.py init .
    python3 strata.py init ../my-project
"""

import argparse
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).parent


def _copy_dir(src: Path, dst: Path, label: str) -> None:
    if dst.exists():
        print(f"  skip  {label} (already exists)")
        return
    shutil.copytree(src, dst)
    print(f"  copy  {label}")


def _append_gitignore(target: Path) -> None:
    snippet = (ROOT / "gitignore.snippet").read_text()
    gi = target / ".gitignore"
    if gi.exists() and snippet.strip() in gi.read_text():
        print("  skip  .gitignore (snippet already present)")
        return
    with gi.open("a") as f:
        f.write("\n" + snippet)
    action = "edit" if gi.exists() else "create"
    print(f"  {action}  .gitignore")


def cmd_init(target_dir: str) -> None:
    target = Path(target_dir).resolve()
    target.mkdir(parents=True, exist_ok=True)
    print(f"Initializing Strata in {target}\n")

    _copy_dir(ROOT / "strata",              target / "strata",            "strata/")
    _copy_dir(ROOT / "browser-tests",       target / "browser-tests",     "browser-tests/")
    _copy_dir(ROOT / "templates" / "features", target / "features",       "features/")
    _copy_dir(ROOT / "templates" / "issues",   target / "issues",         "issues/")
    _append_gitignore(target)

    for skill in ["static", "unit", "browser"]:
        _copy_dir(
            ROOT / "skills" / skill,
            target / ".claude" / "skills" / skill,
            f".claude/skills/{skill}/",
        )

    print(f"\nDone. Next: cd {target} && ./strata/testing.sh all")


def main() -> None:
    parser = argparse.ArgumentParser(
        prog="strata",
        description="Initialize the Strata testing harness in your project.",
    )
    sub = parser.add_subparsers(dest="command")

    init_cmd = sub.add_parser("init", help="Copy harness, browser-tests, templates, and skills into a project directory")
    init_cmd.add_argument(
        "target",
        nargs="?",
        default=".",
        help="Target project directory (default: current directory)",
    )

    args = parser.parse_args()

    if args.command == "init":
        cmd_init(args.target)
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
