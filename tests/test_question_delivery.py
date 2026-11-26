"""Guardrails for the question-delivery protocol (widget first, no raw reasoning).

Run: python3 -m unittest discover -s tests -p test_question_delivery.py -v
"""
import json
import pathlib
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]

# Instructions that made an agent print a question as raw text next to, or
# instead of, the rendered question widget.
LEAK_PHRASES = (
    'plain text, not a widget',
    'plain text, never with',
    'ask in plain text:',
    'ask (plain text)',
    'In plain text: "',
    'Then, in plain text:',
)


class QuestionDeliveryTests(unittest.TestCase):
    def test_central_rule_is_present(self):
        claude = (ROOT / 'CLAUDE.md').read_text(encoding='utf-8')
        modes = (ROOT / '.claude/docs/automation-modes.md').read_text(encoding='utf-8')
        self.assertIn("Questions go through the runtime's question widget", claude)
        self.assertIn('Question delivery — widget first, no raw reasoning', modes)
        self.assertIn('Do not emit reasoning, a draft', modes)
        # The shared "ask again in plain text" fallback line stays covered.
        self.assertIn('"ask again in plain text"', modes)
        # The root protocol must not contradict the widget-first rule.
        self.assertNotIn('re-ask in\n  plain text and wait', claude)

    def test_no_skill_instructs_a_raw_text_question(self):
        offenders = []
        for path in sorted((ROOT / '.claude/skills').rglob('*.md')):
            text = path.read_text(encoding='utf-8')
            for phrase in LEAK_PHRASES:
                if phrase in text:
                    offenders.append(f'{path.relative_to(ROOT)}: {phrase}')
        self.assertEqual(offenders, [], '\n'.join(offenders))

    def test_failed_widget_fallback_is_specified(self):
        modes = (ROOT / '.claude/docs/automation-modes.md').read_text(encoding='utf-8')
        claude = (ROOT / 'CLAUDE.md').read_text(encoding='utf-8')
        agent = (ROOT / '.claude/agents/question-widget-specialist.md').read_text(encoding='utf-8')
        spec = (ROOT / 'studio-tests/agents/specialists/question-widget-specialist.md').read_text(encoding='utf-8')
        self.assertIn('Widget failure or abort', modes)
        self.assertIn('failed delivery', modes)
        self.assertIn('restate the question as plain numbered', modes)
        self.assertIn('never renders', modes)
        self.assertIn('never renders', claude)
        self.assertIn('a widget call errors, is interrupted, or never renders', agent)
        self.assertIn('Widget failure or abort', agent)
        self.assertIn('Case 7: Question widget call aborted', spec)


class QuestionWidgetAgentTests(unittest.TestCase):
    def test_agent_is_registered(self):
        agent = ROOT / '.claude/agents/question-widget-specialist.md'
        spec = ROOT / 'studio-tests/agents/specialists/question-widget-specialist.md'
        self.assertTrue(agent.is_file(), 'agent definition missing')
        self.assertTrue(spec.is_file(), 'agent test spec missing')
        catalog = (ROOT / 'studio-tests/catalog.yaml').read_text(encoding='utf-8')
        self.assertIn('name: question-widget-specialist', catalog)
        self.assertIn('spec: studio-tests/agents/specialists/question-widget-specialist.md', catalog)

    def test_agent_is_read_only_and_count_is_consistent(self):
        text = (ROOT / '.claude/agents/question-widget-specialist.md').read_text(encoding='utf-8')
        self.assertIn('tools: Read, Glob, Grep', text)
        self.assertNotIn('Write', text.split('\n## ')[0])
        count = len(list((ROOT / '.claude/agents').glob('*.md')))
        self.assertEqual(count, 51, 'agent count drifted from the docs')
        claude = (ROOT / 'CLAUDE.md').read_text(encoding='utf-8')
        self.assertIn('51 coordinated Claude Code subagents', claude)


class SubagentQuestionBoundaryTests(unittest.TestCase):
    CANON_HEADING = '### Question Delivery (all runtimes)'
    CANON_MARKERS = (
        'Never use the runtime question tool (`question` / `AskUserQuestion`): it belongs',
        'own window waiting for an answer',
        '2-4',
        'independent options',
        '"(Recommended)"',
        'This section overrides any softer wording',
    )
    SPEC_BULLET = (
        '- [ ] Returns every pending question to the orchestrator with 2-4 options '
        'and a recommendation; never calls the question tool or asks in its own window'
    )

    def test_every_agent_declares_the_unified_question_clause(self):
        paths = sorted((ROOT / '.claude/agents').glob('*.md'))
        self.assertEqual(len(paths), 51, 'agent count drifted from the docs')
        offenders = []
        for path in paths:
            text = path.read_text(encoding='utf-8')
            if self.CANON_HEADING not in text:
                offenders.append(f'{path.name}: missing canonical heading')
                continue
            for marker in self.CANON_MARKERS:
                if marker not in text:
                    offenders.append(f'{path.name}: missing {marker!r}')
        self.assertEqual(offenders, [], '\n'.join(offenders))

    def test_every_agent_spec_requires_the_subagent_boundary(self):
        paths = sorted((ROOT / 'studio-tests/agents').rglob('*.md'))
        self.assertEqual(len(paths), 51, 'agent spec count drifted from the catalog')
        offenders = []
        for path in paths:
            text = path.read_text(encoding='utf-8')
            if self.SPEC_BULLET not in text:
                offenders.append(str(path.relative_to(ROOT)))
        self.assertEqual(offenders, [], '\n'.join(offenders))


class RuntimeAgentConfigTests(unittest.TestCase):
    CONFIG = pathlib.Path('/root/.oc-opencode2/config/opencode/opencode.jsonc')
    MARKER = '### Question Delivery (all runtimes)'

    @unittest.skipUnless(CONFIG.is_file(), 'runtime config not present on this machine')
    def test_registered_studio_agents_deny_question(self):
        data = json.loads(self.CONFIG.read_text(encoding='utf-8'))
        agents = data.get('agents', {})
        offenders = []
        for name, agent in agents.items():
            system = agent.get('system', '')
            if isinstance(system, list):
                system = '\n'.join(
                    part if isinstance(part, str) else str(part.get('text', ''))
                    for part in system
                )
            if self.MARKER not in system:
                continue
            rules = agent.get('permissions', [])
            if not any(rule.get('action') == 'question' and rule.get('effect') == 'deny'
                       for rule in rules):
                offenders.append(name)
        self.assertEqual(offenders, [], 'studio agents without question deny: ' + ', '.join(offenders))
