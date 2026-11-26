"""Guardrails for /next-step action selection and crew routing.

The skill must stay read-only: it reports state, asks which action to take,
maps that action to at most three agents, asks again, and only then delegates.
Run: python3 -m unittest discover -s tests -p test_next_step_routing.py -v
"""
import pathlib
import re
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]
SKILL = ROOT / '.claude/skills/next-step/SKILL.md'
ROUTES = ROOT / '.claude/skills/next-step/references/agent-routing.md'
SPEC = ROOT / 'studio-tests/skills/utility/next-step.md'
AGENTS = ROOT / '.claude/agents'


def route_rows(text):
    """Yield (action, command, crew, rationale) from the markdown table."""
    for line in text.splitlines():
        if not line.startswith('| ') or line.startswith('| Step id'):
            continue
        cells = [cell.strip() for cell in line.strip('|').split('|')]
        if len(cells) != 4 or set(cells[0].replace('-', '').replace(' ', '')) == set():
            continue
        strip = lambda value: re.sub(r'^`(.*)`$', r'\1', value)
        crew = re.findall(r'`([a-z0-9-]+)`', cells[2])
        yield strip(cells[0]), strip(cells[1]), crew, cells[3]


class NextStepSkillTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.text = SKILL.read_text(encoding='utf-8')
        cls.flat = re.sub(r'\s+', ' ', cls.text)
        cls.frontmatter = cls.text.split('---', 2)[1]

    def test_skill_has_both_tools_but_remains_read_only(self):
        tools = self.frontmatter.split('allowed-tools:', 1)[1].split('\n', 1)[0]
        self.assertIn('AskUserQuestion', tools)
        self.assertIn('Agent', tools)
        self.assertNotIn('Write', tools)
        self.assertNotIn('Edit', tools)

    def test_selection_happens_after_the_state_report(self):
        report = self.text.index('## Step 7: Present Output')
        choice = self.text.index('## Step 7b: Choose the Action and Its Crew')
        gate = self.text.index('## Step 8: Gate Warning')
        self.assertLess(report, choice)
        self.assertLess(choice, gate)
        self.assertIn('Call the question tool directly, with no reasoning', self.text)
        self.assertIn('Nothing right now', self.text)
        self.assertIn('plain-text fallback', self.text)

    def test_two_confirmations_before_delegation(self):
        self.assertIn('Do not spawn an agent yet', self.text)
        self.assertIn('A skipped or dismissed question is not an answer', self.flat)
        self.assertIn('second time', self.text)
        self.assertIn('Start this crew', self.text)
        self.assertIn('Change the agents', self.text)
        self.assertIn('Do it myself', self.text)
        self.assertIn('Only "Start this crew" authorises `Agent` calls', self.text)
        self.assertIn('Never claim a file was written by this skill', self.flat)

    def test_rule_against_auto_running(self):
        self.assertIn('Never auto-run the next skill or spawn a crew unasked', self.text)


class AgentRoutingTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.text = ROUTES.read_text(encoding='utf-8')
        cls.rows = list(route_rows(cls.text))

    def test_routing_file_exists_with_real_rows(self):
        self.assertTrue(ROUTES.is_file(), 'agent routing reference missing')
        self.assertGreaterEqual(len(self.rows), 20, 'routing table lost most entries')

    def test_every_route_has_a_valid_crew(self):
        known = {path.stem for path in AGENTS.glob('*.md')}
        for action, command, crew, rationale in self.rows:
            with self.subTest(action=action):
                self.assertTrue(action and command and rationale)
                self.assertTrue(crew, f'{action} has no owner')
                self.assertLessEqual(len(crew), 3, f'{action} exceeds the three-agent limit')
                self.assertLessEqual(len(set(crew)), len(crew), f'{action} repeats an agent')
                for agent in crew:
                    self.assertIn(agent, known, f'{action} routes to unknown agent {agent}')

    def test_read_only_agents_are_scoped_to_research_routes(self):
        gaming = [action for action, _, crew, _ in self.rows if 'gamer' in crew]
        self.assertEqual(set(gaming), {'game-brief', 'external research'},
                         'gamer must only advise on concept and external research')
        self.assertTrue(all('question-widget-specialist' not in crew
                            for _, _, crew, _ in self.rows),
                        'the question auditor has no action to implement')

    def test_engine_and_approval_rules_are_documented(self):
        for phrase in (
            'Engine override',
            'godot-specialist',
            'unity-specialist',
            'unreal-specialist',
            'read-only',
            'ask-first protocol',
            'NOT ASSESSED — NO ROUTE',
        ):
            self.assertIn(phrase, self.text)

    def test_skill_points_to_the_routing_reference(self):
        text = SKILL.read_text(encoding='utf-8')
        flat = re.sub(r'\s+', ' ', text)
        self.assertIn('.claude/skills/next-step/references/agent-routing.md', text)
        self.assertIn('Read `.claude/skills/next-step/references/agent-routing.md`', text)
        self.assertIn('find the row in **Routes**', flat)


class NextStepSpecTests(unittest.TestCase):
    def test_spec_covers_the_choice_and_approval_case(self):
        text = SPEC.read_text(encoding='utf-8')
        self.assertIn('### Case 11: The user picks an action from the widget', text)
        self.assertIn('Two question-tool calls', text)
        self.assertIn('No `Agent` call before the second question', text)
        self.assertIn('`gamer` is marked read-only', text)
        self.assertIn('allowed-tools` includes `AskUserQuestion` and `Agent`', text)

class QuestionDeliveryGuardTests(unittest.TestCase):
    """A question drafted in reasoning is not a question; subagents cannot ask."""

    @classmethod
    def setUpClass(cls):
        cls.skill = SKILL.read_text(encoding='utf-8')
        cls.flat = re.sub(r'\s+', ' ', cls.skill)
        cls.routes = ROUTES.read_text(encoding='utf-8')
        cls.modes = (ROOT / '.claude/docs/automation-modes.md').read_text(encoding='utf-8')

    def test_next_step_delegation_does_not_ask_from_the_subagent(self):
        self.assertIn(
            'delegated subagent must return its questions to this conversation',
            self.flat,
        )

    def test_next_step_no_longer_routes_to_teams(self):
        self.assertNotIn('Team routes', self.routes)
        self.assertNotIn('/team-', self.routes)
        self.assertNotIn('team route', self.flat)
        spec = SPEC.read_text(encoding='utf-8')
        self.assertNotIn('team route', spec)

    def test_shared_mode_says_reasoning_is_not_delivery(self):
        flat = re.sub(r'\s+', ' ', self.modes)
        self.assertIn('is **not a question**', flat)
        self.assertIn('return the pending decision to the orchestrating conversation', flat)

    def test_all_team_skills_handle_a_missing_question_tool(self):
        skills = {
            'team-combat', 'team-narrative', 'team-ui', 'team-audio',
            'team-level', 'team-live-ops', 'team-qa', 'team-polish', 'team-release',
        }
        for skill in skills:
            with self.subTest(skill=skill):
                text = (ROOT / '.claude/skills' / skill / 'SKILL.md').read_text(encoding='utf-8')
                flat = re.sub(r'\s+', ' ', text)
                for phrase in (
                    '**No question tool:**',
                    'never write the question or its options in chat or in reasoning',
                    'Return the pending decision to the orchestrating conversation',
                    'A question drafted in reasoning is not a question',
                ):
                    self.assertIn(phrase, flat, f'{skill} is missing: {phrase}')


if __name__ == '__main__':
    unittest.main()
