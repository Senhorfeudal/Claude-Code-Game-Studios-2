"""Guardrails for the question-watchdog OpenCode plugin.

Run: python3 -m unittest discover -s tests -p test_question_watchdog.py -v
"""
import pathlib
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]
PLUGIN = ROOT / 'plugins/question-watchdog/index.ts'
README = ROOT / 'plugins/question-watchdog/README.md'
RUNTIME_CONFIG = pathlib.Path('/root/.oc-opencode2/config/opencode/opencode.jsonc')


class QuestionWatchdogTests(unittest.TestCase):
    def test_plugin_registers_delivery_hooks(self):
        text = PLUGIN.read_text(encoding='utf-8')
        self.assertIn("id: 'question-watchdog'", text)
        self.assertIn("ctx.session.hook('context'", text)
        self.assertIn("ctx.tool.hook('execute.before'", text)
        self.assertIn("ctx.tool.hook('execute.after'", text)
        self.assertIn('ctx.event.subscribe', text)
        self.assertIn("types: ['form.created']", text)
        self.assertIn('ctx.session.synthetic', text)

    def test_fallback_is_visible_and_answerable(self):
        text = PLUGIN.read_text(encoding='utf-8')
        self.assertIn('Responda com o número da opção', text)
        self.assertIn('wait for the answer before writing or committing anything', text)
        self.assertIn("event?.tool !== 'question'", text)
        self.assertIn('lastPublished', text, 'duplicate fallbacks must be suppressed')
        self.assertIn('clearSession(sessionID)', text)

    def test_readme_documents_load_and_verification(self):
        text = README.read_text(encoding='utf-8')
        self.assertIn('opencode.jsonc', text)
        self.assertIn('waitMs', text)
        self.assertIn('verification', text.lower())

    @unittest.skipUnless(RUNTIME_CONFIG.is_file(), 'runtime config not present on this machine')
    def test_runtime_registers_the_plugin(self):
        text = RUNTIME_CONFIG.read_text(encoding='utf-8')
        self.assertIn('plugins/question-watchdog', text)


if __name__ == '__main__':
    unittest.main()
