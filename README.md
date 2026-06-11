# dev_team

[![tests](https://github.com/MONISMALIK1/dev_team/actions/workflows/test.yml/badge.svg)](https://github.com/MONISMALIK1/dev_team/actions/workflows/test.yml)

A from-scratch, dependency-free **multi-agent software engineering team** that works the
way professionals do — plan, build, **peer-review, revise**, then sign off. Give it a
one-line spec and four role-specialized LLM agents collaborate:

- **Lead Developer** — writes a brief with **acceptance criteria**, then signs off against them.
- **Backend Engineer** — designs the data model + an explicit **API contract**, with errors, auth, and trade-offs.
- **Frontend Engineer** — designs the UI/components and states **against that backend's API**.
- **Reviewer (Staff Engineer)** — a rigorous design review: **blockers / improvements / tests**, and a frontend↔backend mismatch check.

Inspired by role-based agent frameworks like **MetaGPT** and **ChatDev**, built from
scratch over any OpenAI-compatible backend.

## How they collaborate

```
spec
 └► Lead: brief + acceptance criteria
     └► Backend: API contract, data model, errors, security, trade-offs
         └► Frontend: components + loading/empty/error states, built to that API
             └► Reviewer: BLOCKERS / IMPROVEMENTS / TESTS + mismatch check
                 └► Backend & Frontend: revise to address the review
                     └► Lead: sign off against each acceptance criterion
       └──────────────── context flows forward at every step ────────────────┘
```

Each agent answers **in character** (its role system prompt + the work so far), so the
frontend is built to the backend it will actually call, the reviewer holds the work to
the acceptance criteria, and the engineers **revise against the review before sign-off**.
Pass `revise=False` (CLI `--quick`) to skip the revision round.

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

## Example output

[`examples/task_manager_api.md`](examples/task_manager_api.md) is a real, unedited run on
a task-manager REST API spec — watch the **Reviewer flag six concrete blockers** and the
engineers **revise to fix each** before the Lead signs off. Generate your own as a single
document with `--markdown`:

```bash
dev_team "Build a URL shortener with click analytics." --markdown > shortener.md
```

## Library use

```python
from dev_team import run, build_team

res = run("Build a to-do app with user accounts.")   # revise=True by default
print(res.brief)      # Lead's breakdown + acceptance criteria
print(res.backend)    # Backend Engineer's API design (revised against the review)
print(res.frontend)   # Frontend Engineer's UI design (revised against the review)
print(res.review)     # Reviewer's blockers / improvements / tests
print(res.final)      # Lead's sign-off against the acceptance criteria

# customize the team (e.g. swap in your own role prompts)
team = build_team()
team["backend"].system += " Always use PostgreSQL and REST."
res = run("...", team=team)
```

## Design

| Module | Responsibility |
| --- | --- |
| `agents.py` | the `Agent` (name + title + role system prompt) and the default 4-role team |
| `prompts.py` | the role prompts + brief/backend/frontend/**review**/**revise**/sign-off tasks |
| `core.py` | the plan→build→review→revise→sign-off pipeline → `TeamResult` |
| `llm.py` | backend-agnostic OpenAI-compatible client (OpenRouter or local) |

The orchestration is pure stdlib and unit-tested offline; only the agents' calls touch
the network (via the injectable `chat_fn`).

## Test

```bash
make test        # or: python -m unittest discover -s tests -t . -v
```

11 offline tests with a scripted model: the full professional order (brief → backend →
frontend → review → revise → sign-off), that each agent answers through its own role
prompt, that context flows forward (frontend sees the backend, reviewer sees both,
revisions receive the review, sign-off sees the revised work), and that `--quick` skips
the revision round.

## Limitations

- **Design, not deployment.** It produces designs/plans and code sketches, not a
  guaranteed-runnable, tested application. Treat the output as a strong first draft.
- **It reviews, but doesn't execute.** There's a peer review + one revision round, but the
  agents don't actually run code or tests. (Wiring in a real test/execute step is the
  next extension.) Use `revise=False`/`--quick` if you just want a fast single pass.
- **Quality is the base model's.** The agents are only as good as the model behind them.

## Part of a series

From-scratch, dependency-free agent & LLM-reasoning projects:
[mixture_of_agents](https://github.com/MONISMALIK1/mixture_of_agents) ·
[rewoo](https://github.com/MONISMALIK1/rewoo) ·
[react_agent](https://github.com/MONISMALIK1/react_agent) ·
[reflexion](https://github.com/MONISMALIK1/reflexion) ·
[chain_of_verification](https://github.com/MONISMALIK1/chain_of_verification) ·
**dev_team** (this repo).

## License

MIT
