"""Guardrails for the /filesdelete skill and its scoped deletion helper.

The helper may delete one relative item inside CLAUDE_PROJECT_DIR and nothing
else. The skill must route every question through the widget, require the typed
project name, and never fall back to a raw rm when the helper refuses.
Run: python3 -m unittest discover -s tests -p test_filesdelete.py -v
"""
import os
import pathlib
import re
import subprocess
import tempfile
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]
SCRIPT = ROOT / '.claude/scripts/filesdelete.sh'
SKILL = ROOT / '.claude/skills/filesdelete/SKILL.md'


def run_helper(project, *args):
    env = dict(os.environ, CLAUDE_PROJECT_DIR=str(project))
    return subprocess.run(
        ['bash', str(SCRIPT), *args],
        env=env, capture_output=True, text=True, check=False,
    )


class HelperTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.base = pathlib.Path(self.tmp.name)
        self.project = self.base / 'demo'
        (self.project / 'src').mkdir(parents=True)
        (self.project / 'build').mkdir()
        (self.project / 'README.md').write_text('x' * 4096, encoding='utf-8')
        (self.project / 'src' / 'main.js').write_text('// ok', encoding='utf-8')

    def tearDown(self):
        self.tmp.cleanup()

    def test_lists_root_total_and_top_level_items(self):
        result = run_helper(self.project, 'list')
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn(f'PROJECT_ROOT {self.project}', result.stdout)
        self.assertIn('PROJECT_NAME demo', result.stdout)
        rows = [line.split('\t') for line in result.stdout.splitlines() if '\t' in line]
        names = {row[2] for row in rows}
        self.assertEqual(names, {'src', 'build', 'README.md'})
        bytesizes = [int(row[0]) for row in rows]
        self.assertEqual(bytesizes, sorted(bytesizes, reverse=True))

    def test_deletes_one_selected_item(self):
        result = run_helper(self.project, 'delete', '--target', 'build', '--confirm', 'demo')
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stdout.strip(), 'DELETED build')
        self.assertFalse((self.project / 'build').exists())
        self.assertTrue((self.project / 'src' / 'main.js').exists())
        self.assertTrue((self.project / 'README.md').exists())

    def test_refuses_paths_outside_the_project(self):
        outside = self.base / 'outside'
        outside.mkdir()
        (outside / 'keep.txt').write_text('keep', encoding='utf-8')
        for target in ('/etc', '../outside', './build', 'src/../../outside'):
            with self.subTest(target=target):
                result = run_helper(
                    self.project, 'delete', '--target', target, '--confirm', 'demo'
                )
                self.assertEqual(result.returncode, 3)
                self.assertIn('REFUSED OUTSIDE_PROJECT', result.stderr)
                self.assertTrue((outside / 'keep.txt').exists())
                self.assertTrue((self.project / 'build').exists())

    def test_refuses_wrong_confirmation_name(self):
        result = run_helper(
            self.project, 'delete', '--target', 'build', '--confirm', 'production'
        )
        self.assertEqual(result.returncode, 3)
        self.assertIn('REFUSED CONFIRMATION_MISMATCH', result.stderr)
        self.assertTrue((self.project / 'build').exists())

    def test_refuses_root_symlink_and_missing_target(self):
        outside = self.base / 'outside'
        outside.mkdir()
        (outside / 'keep.txt').write_text('keep', encoding='utf-8')
        (self.project / 'link').symlink_to(outside, target_is_directory=True)
        for target, reason in (
            ('.', 'ROOT_NOT_DELETABLE'),
            ('link', 'SYMLINK_NOT_DELETABLE'),
            ('ghost', 'TARGET_NOT_FOUND'),
        ):
            with self.subTest(target=target):
                result = run_helper(
                    self.project, 'delete', '--target', target, '--confirm', 'demo'
                )
                self.assertEqual(result.returncode, 3)
                self.assertIn(f'REFUSED {reason}', result.stderr)
        self.assertTrue(self.project.exists())
        self.assertTrue((outside / 'keep.txt').exists())

    def test_missing_project_root_is_refused(self):
        result = run_helper(self.base / 'missing', 'delete', '--target', 'x', '--confirm', 'x')
        self.assertNotEqual(result.returncode, 0)
        self.assertIn('REFUSED PROJECT_ROOT_NOT_FOUND', result.stderr)


class SkillTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.text = SKILL.read_text(encoding='utf-8')
        cls.flat = re.sub(r'\s+', ' ', cls.text)
        cls.frontmatter = cls.text.split('---', 2)[1]

    def test_skill_is_interactive_and_cannot_write(self):
        tools = self.frontmatter.split('allowed-tools:', 1)[1].split('\n', 1)[0]
        self.assertIn('AskUserQuestion', tools)
        self.assertNotIn('Write', tools)
        self.assertNotIn('Edit', tools)

    def test_skill_uses_only_the_scoped_helper(self):
        self.assertIn('.claude/scripts/filesdelete.sh list', self.text)
        self.assertIn('.claude/scripts/filesdelete.sh delete --target', self.text)
        self.assertNotIn('rm -rf', self.text)

    def test_confirmation_is_mandatory_and_typed(self):
        for phrase in (
            'mandatory in every `modes.automation` mode',
            'exact project folder name',
            'typed free-text answer must equal `PROJECT_NAME` exactly',
            'A wrong name cancels the deletion',
            'Never fall back to `rm` or another command',
        ):
            self.assertIn(phrase, self.flat, f'missing rule: {phrase}')

    def test_scope_rules_and_verdicts_are_documented(self):
        for phrase in (
            'Absolute paths, `..`, `./…`, the project root itself and symlinks are refused',
            'it never deletes more than the item confirmed in the widget',
            'DELETED — ITEM removed permanently',
            'COMPLETE — nothing deleted',
            'REFUSED — <reason>',
            '`/next-step`',
        ):
            self.assertIn(phrase, self.flat, f'missing rule: {phrase}')


if __name__ == '__main__':
    unittest.main()
