"""The role-specialized agents.

An ``Agent`` is just a name, a title, and a role *system prompt*. ``respond`` prepends
that system prompt to a task and makes one model call — so each agent answers *in
character* (a backend engineer reasons about APIs, a frontend engineer about screens).
"""

from __future__ import annotations

from dataclasses import dataclass

from .llm import chat
from .prompts import BACKEND_SYSTEM, FRONTEND_SYSTEM, LEAD_SYSTEM, REVIEWER_SYSTEM


@dataclass
class Agent:
    name: str
    title: str
    system: str

    def respond(self, task: str, chat_fn=chat, model: str | None = None,
                temperature: float = 0.4) -> str:
        prompt = f"{self.system}\n\n{task}"
        return chat_fn(prompt, model=model, temperature=temperature).strip()


def build_team() -> dict[str, Agent]:
    """The default team: a lead, a backend and frontend engineer, and a reviewer."""
    return {
        "lead": Agent("Dana", "Lead Developer", LEAD_SYSTEM),
        "backend": Agent("Ben", "Backend Engineer", BACKEND_SYSTEM),
        "frontend": Agent("Fiona", "Frontend Engineer", FRONTEND_SYSTEM),
        "reviewer": Agent("Riya", "Reviewer (Staff Engineer)", REVIEWER_SYSTEM),
    }


__all__ = ["Agent", "build_team"]
