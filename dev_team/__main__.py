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
                   help="Print the brief, each engineer's design, and the review — not just sign-off.")
    p.add_argument("--quick", action="store_true",
                   help="Skip the revision round (plan -> build -> review -> sign off).")
    args = p.parse_args()

    if not args.spec:
        p.error("provide a one-line project spec to build")

    print(f"\nProject: {args.spec}", file=sys.stderr)
    print(f"Model: {args.model or DEFAULT_MODEL}  |  revise: {not args.quick}\n",
          file=sys.stderr, flush=True)

    res = run(args.spec, model=args.model, revise=not args.quick)
    if args.show_work:
        _block("LEAD — brief & acceptance criteria", res.brief)
        _block("BACKEND ENGINEER" + (" (revised)" if res.revised else ""), res.backend)
        _block("FRONTEND ENGINEER" + (" (revised)" if res.revised else ""), res.frontend)
        _block("REVIEWER — blockers / improvements / tests", res.review)
    _block("LEAD — sign-off", res.final)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
