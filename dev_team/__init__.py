"""dev_team — a from-scratch multi-agent software engineering team, zero deps.

Role-specialized LLM agents collaborate on a project spec: a Lead Developer briefs the
work, a Backend Engineer designs the API, a Frontend Engineer designs the UI against
that API, and the Lead integrates and reviews. Inspired by role-based agent frameworks
(MetaGPT, ChatDev), implemented from scratch over any OpenAI-compatible backend.

    from dev_team import run

    result = run("Build a to-do app with user accounts.")
    print(result.final)        # the Lead's integrated review
    print(result.backend)      # the Backend Engineer's API design
"""

from __future__ import annotations

__version__ = "0.2.0"

from .agents import Agent, build_team
from .core import TeamResult, run

__all__ = ["__version__", "Agent", "build_team", "TeamResult", "run"]
