"""The collaboration pipeline — a real engineering process, not a single pass.

A small multi-agent software team, inspired by role-based agent frameworks like
MetaGPT and ChatDev, but run the way professionals actually work:

    Lead      -> brief + acceptance criteria
    Backend   -> API contract / data model / errors / security / trade-offs
    Frontend  -> components + states, built to that backend's API
    Reviewer  -> blockers / improvements / tests, and a frontend<->backend mismatch check
    Backend & Frontend -> REVISE to address the review   (when revise=True)
    Lead      -> sign off against the acceptance criteria

Context flows forward at every step, and the work is peer-reviewed and revised before
sign-off. Only the model calls touch the network (injectable ``chat_fn``).
"""

from __future__ import annotations

from dataclasses import dataclass

from .agents import Agent, build_team
from .llm import chat
from .prompts import (BACKEND_TASK, BRIEF_TASK, FRONTEND_TASK, INTEGRATE_TASK,
                      REVIEW_TASK, REVISE_BACKEND_TASK, REVISE_FRONTEND_TASK)


@dataclass
class TeamResult:
    spec: str
    brief: str        # Lead's breakdown + acceptance criteria
    backend: str      # Backend Engineer's design (post-revision if revise=True)
    frontend: str     # Frontend Engineer's design (post-revision if revise=True)
    review: str       # Reviewer's blockers / improvements / tests
    final: str        # Lead's sign-off against the acceptance criteria
    revised: bool = False

    def to_markdown(self) -> str:
        """Render the whole deliverable as one Markdown document (e.g. to save/share)."""
        tag = " (revised)" if self.revised else ""
        return "\n\n".join([
            f"# {self.spec}",
            "## Brief & acceptance criteria\n\n" + self.brief,
            f"## Backend engineer{tag}\n\n" + self.backend,
            f"## Frontend engineer{tag}\n\n" + self.frontend,
            "## Reviewer — blockers / improvements / tests\n\n" + self.review,
            "## Lead — sign-off\n\n" + self.final,
        ]) + "\n"


def run(spec: str, team: dict[str, Agent] | None = None, model: str | None = None,
        revise: bool = True, chat_fn=chat) -> TeamResult:
    """Run the full team on a project ``spec``.

    With ``revise=True`` (default) the engineers address the reviewer's feedback before
    the lead signs off — the professional path. Set ``revise=False`` for a quick,
    single-pass design (plan -> build -> review -> sign off, no revision round).
    """
    team = team or build_team()
    lead, backend_eng = team["lead"], team["backend"]
    frontend_eng, reviewer = team["frontend"], team["reviewer"]

    brief = lead.respond(BRIEF_TASK.format(spec=spec), chat_fn=chat_fn, model=model)
    backend = backend_eng.respond(
        BACKEND_TASK.format(spec=spec, brief=brief), chat_fn=chat_fn, model=model)
    frontend = frontend_eng.respond(
        FRONTEND_TASK.format(spec=spec, brief=brief, backend=backend),
        chat_fn=chat_fn, model=model)

    review = reviewer.respond(
        REVIEW_TASK.format(spec=spec, brief=brief, backend=backend, frontend=frontend),
        chat_fn=chat_fn, model=model)

    if revise:
        backend = backend_eng.respond(
            REVISE_BACKEND_TASK.format(spec=spec, backend=backend, review=review),
            chat_fn=chat_fn, model=model)
        frontend = frontend_eng.respond(
            REVISE_FRONTEND_TASK.format(spec=spec, frontend=frontend, review=review),
            chat_fn=chat_fn, model=model)

    final = lead.respond(
        INTEGRATE_TASK.format(spec=spec, brief=brief, backend=backend,
                              frontend=frontend, review=review),
        chat_fn=chat_fn, model=model)

    return TeamResult(spec=spec, brief=brief, backend=backend, frontend=frontend,
                      review=review, final=final, revised=revise)


__all__ = ["TeamResult", "run"]
