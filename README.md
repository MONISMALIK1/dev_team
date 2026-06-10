# dev_team

[![tests](https://github.com/MONISMALIK1/dev_team/actions/workflows/test.yml/badge.svg)](https://github.com/MONISMALIK1/dev_team/actions/workflows/test.yml)

A from-scratch, dependency-free **multi-agent software engineering team**. Give it a
one-line spec and three role-specialized LLM agents collaborate to design it:

- **Lead Developer** — breaks the spec into a brief, then integrates & reviews.
- **Backend Engineer** — designs the data model and API against the brief.
- **Frontend Engineer** — designs the UI/components **against that backend's API**.

Inspired by role-based agent frameworks like **MetaGPT** and **ChatDev**, built from
scratch over any OpenAI-compatible backend.

## How they collaborate

```
spec ─► Lead: brief ─► Backend: API design ─► Frontend: UI (built to that API) ─► Lead: integrate & review
                 └──────────── context flows forward at every step ─────────────┘
```

Each agent answers **in character** (its role system prompt + the work so far), so the
frontend is designed for the backend it will actually call, and the Lead's review can
check that every screen has its endpoints and every endpoint is used.

## Quickstart

```bash
git clone https://github.com/MONISMALIK1/dev_team.git
cd dev_team
pip install -e .                       # installs the `dev_team` command

export OPENROUTER_API_KEY=sk-or-...    # or a local model (see below)
dev_team "Build a URL shortener with click analytics." --show-work
```

No key? Point it at a local model — no cloud:

```bash
export DEVTEAM_BASE_URL=http://localhost:11434/v1/chat/completions   # Ollama
export DEVTEAM_MODEL=qwen2.5:7b
```

(You can also run without installing: `python -m dev_team "..."` from the repo root.)

## Library use

```python
from dev_team import run, build_team

res = run("Build a to-do app with user accounts.")
print(res.brief)      # Lead's breakdown
print(res.backend)    # Backend Engineer's API design
print(res.frontend)   # Frontend Engineer's UI design
print(res.final)      # Lead's integration & review

# customize the team (e.g. swap in your own role prompts)
team = build_team()
team["backend"].system += " Always use PostgreSQL and REST."
res = run("...", team=team)
```

## Design

| Module | Responsibility |
| --- | --- |
| `agents.py` | the `Agent` (name + title + role system prompt) and the default team |
| `prompts.py` | the three role prompts + the brief/backend/frontend/integrate task templates |
| `core.py` | the collaboration pipeline → `TeamResult` |
| `llm.py` | backend-agnostic OpenAI-compatible client (OpenRouter or local) |

The orchestration is pure stdlib and unit-tested offline; only the agents' calls touch
the network (via the injectable `chat_fn`).

## Test

```bash
make test        # or: python -m unittest discover -s tests -t . -v
```

10 offline tests with a scripted model: the collaboration order (brief → backend →
frontend → integrate), that each agent answers through its own role prompt, and that
context flows forward (the frontend sees the backend; the review sees both).

## Limitations

- **Design, not deployment.** It produces designs/plans and code sketches, not a
  guaranteed-runnable, tested application. Treat the output as a strong first draft.
- **No execution or critique loop.** It's a single forward pass; it doesn't run code or
  iterate. (A reviewer/test loop is a natural extension.)
- **Quality is the base model's.** The agents are only as good as the model behind them.

## License

MIT
