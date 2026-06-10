"""The Agent abstraction and the default team."""

import unittest

from dev_team.agents import Agent, build_team


class AgentTests(unittest.TestCase):
    def test_respond_prepends_system_prompt(self):
        seen = {}

        def fake(prompt, model=None, temperature=0.4, **kw):
            seen["prompt"] = prompt
            seen["temperature"] = temperature
            return "  done  "

        agent = Agent("Ben", "Backend Engineer", "You are a senior backend engineer.")
        out = agent.respond("Design an API.", chat_fn=fake)
        self.assertEqual(out, "done")  # stripped
        self.assertTrue(seen["prompt"].startswith("You are a senior backend engineer."))
        self.assertIn("Design an API.", seen["prompt"])


class TeamTests(unittest.TestCase):
    def test_default_team_roles(self):
        team = build_team()
        self.assertEqual(set(team), {"lead", "backend", "frontend", "reviewer"})
        self.assertEqual(team["backend"].title, "Backend Engineer")
        self.assertEqual(team["frontend"].title, "Frontend Engineer")
        self.assertEqual(team["lead"].title, "Lead Developer")
        self.assertIn("Reviewer", team["reviewer"].title)
        # each role carries a distinct system prompt
        systems = {a.system for a in team.values()}
        self.assertEqual(len(systems), 4)


if __name__ == "__main__":
    unittest.main()
