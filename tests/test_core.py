"""The team pipeline with a scripted model (offline).

Asserts the professional process: plan -> build -> peer review -> revise -> sign-off,
that each agent answers through its own role prompt, and that context flows forward
(frontend sees backend; reviewer sees both; revisions see the review; sign-off sees all).
"""

import unittest

from dev_team.core import run


def make_team_fake():
    """Routes by role system prompt + task marker; records every prompt."""
    seen = []

    def fake(prompt, model=None, temperature=0.4, **kw):
        seen.append(prompt)
        lead = "lead developer / engineering manager" in prompt
        backend = "senior backend engineer" in prompt
        frontend = "senior frontend engineer" in prompt
        reviewer = "staff engineer doing a design/code review" in prompt
        if lead and "write a short brief" in prompt:
            return "BRIEF + ACCEPTANCE CRITERIA"
        if backend and "Revise your backend design" in prompt:
            return "BACKEND v2 (addressed review)"
        if frontend and "Revise your frontend design" in prompt:
            return "FRONTEND v2 (addressed review)"
        if backend:
            return "BACKEND v1: GET /items"
        if frontend:
            return "FRONTEND v1: ItemList"
        if reviewer:
            return "BLOCKERS: none. IMPROVEMENTS: add pagination. TESTS: list endpoint."
        if lead and "sign off" in prompt:
            return "SIGN-OFF: meets criteria. Ship."
        return "?"

    return fake, seen


class ProfessionalPipelineTests(unittest.TestCase):
    def test_full_process_with_revision(self):
        fake, seen = make_team_fake()
        res = run("Build a to-do app.", chat_fn=fake)  # revise defaults True
        self.assertIn("BRIEF", res.brief)
        self.assertIn("BLOCKERS", res.review)
        self.assertIn("SIGN-OFF", res.final)
        self.assertTrue(res.revised)
        self.assertIn("v2", res.backend)   # post-revision design returned
        self.assertIn("v2", res.frontend)
        # plan, backend, frontend, review, revise-backend, revise-frontend, sign-off = 7
        self.assertEqual(len(seen), 7)

    def test_reviewer_sees_both_designs(self):
        fake, seen = make_team_fake()
        run("Build a to-do app.", chat_fn=fake)
        review_prompt = next(p for p in seen if "design/code review" in p)
        self.assertIn("BACKEND v1: GET /items", review_prompt)
        self.assertIn("FRONTEND v1: ItemList", review_prompt)

    def test_revisions_receive_the_review(self):
        fake, seen = make_team_fake()
        run("Build a to-do app.", chat_fn=fake)
        revise_prompts = [p for p in seen if "Revise your" in p]
        self.assertEqual(len(revise_prompts), 2)
        self.assertTrue(all("add pagination" in p for p in revise_prompts))  # review fed in

    def test_signoff_sees_review_and_revised_work(self):
        fake, seen = make_team_fake()
        run("Build a to-do app.", chat_fn=fake)
        signoff = next(p for p in seen if "sign off" in p)
        self.assertIn("BACKEND v2", signoff)
        self.assertIn("add pagination", signoff)  # the review that was addressed

    def test_quick_mode_skips_revision(self):
        fake, seen = make_team_fake()
        res = run("Build a to-do app.", revise=False, chat_fn=fake)
        self.assertFalse(res.revised)
        self.assertIn("v1", res.backend)  # not revised
        # plan, backend, frontend, review, sign-off = 5 (no revise calls)
        self.assertEqual(len(seen), 5)
        self.assertFalse(any("Revise your" in p for p in seen))

    def test_spec_threaded_through(self):
        fake, seen = make_team_fake()
        run("Build a UNIQUE-SPEC-MARKER app.", chat_fn=fake)
        self.assertTrue(all("UNIQUE-SPEC-MARKER" in p for p in seen))

    def test_to_markdown_renders_all_sections(self):
        fake, _ = make_team_fake()
        md = run("Build a to-do app.", chat_fn=fake).to_markdown()
        for heading in ("# Build a to-do app.", "## Brief & acceptance criteria",
                        "## Backend engineer (revised)", "## Frontend engineer (revised)",
                        "## Reviewer", "## Lead — sign-off"):
            self.assertIn(heading, md)
        self.assertIn("SIGN-OFF", md)  # field bodies are included


if __name__ == "__main__":
    unittest.main()
