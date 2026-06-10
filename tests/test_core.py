"""The team pipeline with a scripted model (offline).

Asserts the collaboration order and that context flows forward: the Lead briefs, the
Backend designs, the Frontend designs *against the backend*, and the Lead integrates
seeing both — each agent answering through its own role system prompt.
"""

import unittest

from dev_team.core import run


def make_team_fake():
    """Routes by role system prompt + task marker; records every prompt."""
    seen = []

    def fake(prompt, model=None, temperature=0.4, **kw):
        seen.append(prompt)
        backend = "senior backend engineer" in prompt
        frontend = "senior frontend engineer" in prompt
        lead = "lead developer of a small engineering team" in prompt
        if lead and "Break this down into a short brief" in prompt:
            return "BRIEF: backend=[/items API], frontend=[list screen]"
        if backend:
            return "BACKEND: GET /items, POST /items"
        if frontend:
            return "FRONTEND: ItemList screen calling GET /items"
        if lead and "Integrate and review" in prompt:
            return "FINAL: backend and frontend line up. Ship it."
        return "?"

    return fake, seen


class PipelineTests(unittest.TestCase):
    def test_collects_all_contributions(self):
        fake, _ = make_team_fake()
        res = run("Build a to-do app.", chat_fn=fake)
        self.assertIn("BRIEF", res.brief)
        self.assertIn("BACKEND", res.backend)
        self.assertIn("FRONTEND", res.frontend)
        self.assertIn("FINAL", res.final)

    def test_four_calls_one_per_phase(self):
        fake, seen = make_team_fake()
        run("Build a to-do app.", chat_fn=fake)
        self.assertEqual(len(seen), 4)  # brief, backend, frontend, integrate

    def test_frontend_sees_the_backend(self):
        fake, seen = make_team_fake()
        run("Build a to-do app.", chat_fn=fake)
        frontend_prompt = next(p for p in seen if "senior frontend engineer" in p)
        self.assertIn("BACKEND: GET /items", frontend_prompt)  # backend design fed forward

    def test_integration_sees_both(self):
        fake, seen = make_team_fake()
        run("Build a to-do app.", chat_fn=fake)
        integrate_prompt = next(p for p in seen if "Integrate and review" in p)
        self.assertIn("BACKEND: GET /items", integrate_prompt)
        self.assertIn("FRONTEND: ItemList", integrate_prompt)

    def test_spec_threaded_through(self):
        fake, seen = make_team_fake()
        run("Build a UNIQUE-SPEC-MARKER app.", chat_fn=fake)
        self.assertTrue(all("UNIQUE-SPEC-MARKER" in p for p in seen))


if __name__ == "__main__":
    unittest.main()
