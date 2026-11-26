"""Guardrails for the /gamer skill that exposes the read-only gamer agent.

The skill must be discoverable in the skill list, write nothing, delegate to one
gamer subagent, and ask the agent's returned question through the orchestrator's
widget instead of dumping research into the conversation.

Run: python3 -m unittest discover -s tests -p test_gamer_skill.py -v
"""
import pathlib
import re
import unittest

import yaml

ROOT = pathlib.Path(__file__).resolve().parents[1]
SKILL = ROOT / '.claude/skills/gamer/SKILL.md'
SPEC = ROOT / 'studio-tests/skills/utility/gamer.md'
AGENT = ROOT / '.claude/agents/gamer.md'


class GamerSkillTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.text = SKILL.read_text(encoding='utf-8')
        cls.flat = re.sub(r'\s+', ' ', cls.text)
        cls.frontmatter = cls.text.split('---', 2)[1]
        cls.catalog = yaml.safe_load((ROOT / 'studio-tests/catalog.yaml').read_text())

    def test_skill_is_registered_and_user_invocable(self):
        self.assertTrue(SKILL.is_file(), 'gamer SKILL.md missing')
        self.assertTrue(SPEC.is_file(), 'gamer skill spec missing')
        self.assertIn('user-invocable: true', self.frontmatter)
        names = {entry['name'] for entry in self.catalog['skills']}
        self.assertIn('gamer', names, 'gamer skill missing from the catalog')
        entry = next(e for e in self.catalog['skills'] if e['name'] == 'gamer')
        self.assertEqual(entry['spec'], 'studio-tests/skills/utility/gamer.md')

    def test_skill_is_read_only_but_can_delegate_and_ask(self):
        tools = self.frontmatter.split('allowed-tools:', 1)[1].split('\n', 1)[0]
        self.assertIn('Agent', tools)
        self.assertIn('AskUserQuestion', tools)
        self.assertNotIn('Write', tools)
        self.assertNotIn('Edit', tools)

    def test_delegation_contract(self):
        for phrase in (
            'spawn **one** `gamer` subagent',
            'Never ask a question from the subagent',
            'it has no question widget',
            'verbatim in a single question tool call',
            'Never accept a raw research dump as the final answer',
            'NOT ASSESSED — NO AGENT TOOL',
            'NOT ASSESSED — NO DATA',
        ):
            self.assertIn(phrase, self.flat, f'missing rule: {phrase}')

    def test_verdicts_and_handoff(self):
        for phrase in (
            'COMPLETE — research delivered',
            'COMPLETE — research declined',
            'NOT ASSESSED — <reason>',
            '`/next-step`',
        ):
            self.assertIn(phrase, self.flat, f'missing rule: {phrase}')

    def test_original_agent_still_exists(self):
        self.assertTrue(AGENT.is_file(), 'gamer agent was removed')
        agent_text = AGENT.read_text(encoding='utf-8')
        self.assertIn('no question tool', agent_text)
        self.assertIn('Question for the orchestrator', agent_text)


if __name__ == '__main__':
    unittest.main()
