"""Guardrails for in-chat team orchestration.

Team skills are orchestrators executed in the user's current conversation. They
are never routed through `Agent` / `subagent`, and they never spawn specialists:
each phase is an inline pass with its decisions and write approvals asked here.
Run: python3 -m unittest discover -s tests -p test_in_chat_teams.py -v
"""
import pathlib
import re
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]
GUIDE = ROOT / '.claude/docs/in-chat-teams.md'
TEAM_IDS = (
    'team-audio', 'team-combat', 'team-level', 'team-live-ops',
    'team-narrative', 'team-polish', 'team-qa', 'team-release', 'team-ui',
)
COORDINATION = ROOT / '.claude/docs/coordination-rules.md'
GENERATOR = ROOT / '.opencode/scripts/generate-opencode-layer.py'
NEXT_STEP = ROOT / '.claude/skills/next-step/SKILL.md'


class InChatTeamTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.texts = {
            skill: (ROOT / '.claude/skills' / skill / 'SKILL.md').read_text(encoding='utf-8')
            for skill in TEAM_IDS
        }

    def test_shared_guide_states_the_rule(self):
        text = GUIDE.read_text(encoding='utf-8')
        for phrase in (
            'A team is an **orchestrator that runs in the conversation the user opened**',
            'no team skill may spawn its specialists',
            'Every phase is performed inline',
            'Ask before every write',
            'never an agent',
        ):
            self.assertIn(phrase, text)

    def test_no_team_can_call_agent(self):
        for skill, text in self.texts.items():
            with self.subTest(skill=skill):
                frontmatter = text.split('---', 2)[1]
                tools = frontmatter.split('allowed-tools:', 1)[1].split('\n', 1)[0]
                self.assertNotIn('Agent', tools)
                self.assertNotIn('Task(', tools)

    def test_every_team_declares_in_chat_orchestration(self):
        for skill, text in self.texts.items():
            with self.subTest(skill=skill):
                self.assertIn('**In-chat orchestration:**', text)
                self.assertIn('## How to Run Inline', text)
                self.assertNotIn('**No question tool:**', text)
                self.assertNotIn('## How to Delegate', text)

    def test_decisions_are_asked_in_the_current_chat(self):
        for skill, text in self.texts.items():
            with self.subTest(skill=skill):
                flat = re.sub(r'\s+', ' ', text)
                self.assertIn('never as a subagent and never inside a subagent conversation', flat)
                self.assertIn('nothing is forwarded to a parent', text)
                self.assertIn('If this\nskill is somehow invoked inside a subagent, stop', text)
                self.assertNotIn('Return the pending decision to the orchestrating conversation', text)

    def test_writes_are_ask_first_with_no_subagent_exception(self):
        for skill, text in self.texts.items():
            with self.subTest(skill=skill):
                flat = re.sub(r'\s+', ' ', text)
                self.assertIn('wait for approval', re.sub(r'\s+', ' ', text))
                self.assertIn('ask \"May I write this\nto [path]?\"', text)
                self.assertIn('There is no subagent exception', text)
                self.assertIn('## File Write Protocol', text)

    def test_parallel_phases_became_consecutive_inline_passes(self):
        for skill, text in self.texts.items():
            with self.subTest(skill=skill):
                flat = re.sub(r'\s+', ' ', text)
                self.assertIn('inline', flat)
                self.assertNotIn('Delegate in parallel', text)
                self.assertNotIn('Launch independent agents in parallel', text)
                self.assertNotIn('issue all `Agent` calls', text)


class RoutingAndDocsTests(unittest.TestCase):
    def test_next_step_loads_teams_in_chat(self):
        text = NEXT_STEP.read_text(encoding='utf-8')
        self.assertIn('### Team actions run in this chat', text)
        self.assertIn('.claude/docs/in-chat-teams.md', text)
        self.assertIn('there is **no crew and no\n`Agent` call**', text)
        self.assertIn('Never put a team id in an `Agent` / `subagent` call', text)
        self.assertIn('For every **non-team** action', text)

    def test_coordination_rules_distinguish_in_chat_teams_from_subagents(self):
        text = COORDINATION.read_text(encoding='utf-8')
        self.assertIn('in-chat teams', text)
        self.assertIn('in-chat-teams.md', text)
        self.assertNotIn('Used by all\n`team-*` skills and orchestration skills', text)

    def test_generator_emits_the_in_chat_rule_for_team_wrappers(self):
        text = GENERATOR.read_text(encoding='utf-8')
        self.assertIn('in-chat-teams.md', text)
        self.assertIn('never use the `subagent` tool', text)

    def test_generated_wrappers_carry_the_rule(self):
        for skill in TEAM_IDS:
            with self.subTest(skill=skill):
                wrapper = ROOT / '.opencode/skills' / skill / 'SKILL.md'
                self.assertTrue(wrapper.is_file(), f'{skill} wrapper missing; rerun the generator')
                text = wrapper.read_text(encoding='utf-8')
                self.assertIn('in-chat orchestrator', text)
                self.assertIn('never use the `subagent` tool', text)


if __name__ == '__main__':
    unittest.main()
