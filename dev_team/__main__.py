"""CLI for dev_team.

Usage:
    python -m dev_team "Build a URL shortener with click analytics."
    python -m dev_team "Build a to-do app with accounts." --show-work
"""

from __future__ import annotations

import argparse
import sys

from . import __version__
from .core import run
from .llm import DEFAULT_MODEL


def _block(title: str, body: str) -> None:
    print("\n" + "=" * 64)
    print(title)
    print("=" * 64)
    print(body)


def main() -> int:
    p = argparse.ArgumentParser(
        prog="dev_team",
        description="A multi-agent engineering team (Lead + Backend + Frontend) that "
                    "designs a project from a one-line spec.",
    )
    p.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    p.add_argument("spec", nargs="?", help="One-line description of what to build.")
    p.add_argument("--model", default=None, help=f"Model slug (default: {DEFAULT_MODEL}).")
    p.add_argument("--show-work", action="store_true",
                   help="Print the brief and each engineer's design, not just the final review.")
    args = p.parse_args()

    if not args.spec:
        p.error("provide a one-line project spec to build")

    print(f"\nProject: {args.spec}", file=sys.stderr)
    print(f"Model: {args.model or DEFAULT_MODEL}\n", file=sys.stderr, flush=True)

    res = run(args.spec, model=args.model)
    if args.show_work:
        _block("LEAD — brief", res.brief)
        _block("BACKEND ENGINEER", res.backend)
        _block("FRONTEND ENGINEER", res.frontend)
    _block("LEAD — integration & review", res.final)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
