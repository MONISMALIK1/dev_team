"""The collaboration pipeline: brief -> backend -> frontend -> integrate.

A small multi-agent software team, inspired by role-based agent frameworks like
MetaGPT and ChatDev: the Lead writes a brief, the Backend Engineer designs the API
against it, the Frontend Engineer designs the UI *against that backend*, and the Lead
integrates and reviews the two. Context flows forward at each step, so the frontend is
built to the backend it will actually call. Only the model calls touch the network
(injectable ``chat_fn``).
"""

from __future__ import annotations

from dataclasses import dataclass

from .agents import Agent, build_team
from .llm import chat
from .prompts import BACKEND_TASK, BRIEF_TASK, FRONTEND_TASK, INTEGRATE_TASK


@dataclass
class TeamResult:
    spec: str
    brief: str        # Lead's breakdown
    backend: str      # Backend Engineer's design
    frontend: str     # Frontend Engineer's design
    final: str        # Lead's integration + review


def run(spec: str, team: dict[str, Agent] | None = None, model: str | None = None,
        chat_fn=chat) -> TeamResult:
    """Run the full team on a project ``spec`` and return everyone's contributions."""
    team = team or build_team()
    lead, backend_eng, frontend_eng = team["lead"], team["backend"], team["frontend"]

    brief = lead.respond(BRIEF_TASK.format(spec=spec), chat_fn=chat_fn, model=model)
    backend = backend_eng.respond(
        BACKEND_TASK.format(spec=spec, brief=brief), chat_fn=chat_fn, model=model)
    frontend = frontend_eng.respond(
        FRONTEND_TASK.format(spec=spec, brief=brief, backend=backend),
        chat_fn=chat_fn, model=model)
    final = lead.respond(
        INTEGRATE_TASK.format(spec=spec, brief=brief, backend=backend, frontend=frontend),
        chat_fn=chat_fn, model=model)

    return TeamResult(spec=spec, brief=brief, backend=backend, frontend=frontend, final=final)


__all__ = ["TeamResult", "run"]
