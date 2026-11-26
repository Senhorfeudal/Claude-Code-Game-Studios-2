"""Guardrails for the Senhorfeudal Game Studios rebrand.

The upstream project stays credited in LICENSE and CHANGELOG.md, but active
docs and configuration must not point back to its owners, donation pages or
release feed. Run: python3 -m unittest discover -s tests -p test_branding.py -v
"""
import pathlib
import subprocess
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]
NEW_REPO = 'Senhorfeudal/Claude-Code-Game-Studios-2'
UPSTREAM_REPO = 'Donchitos/Claude-Code-Game-Studios'
FORBIDDEN = ('Claude Code Game Studios', UPSTREAM_REPO, '@Donchitos', 'donchitos3')
HISTORICAL = {'CHANGELOG.md', 'LICENSE', 'README.md'}


def tracked_text_files():
    names = subprocess.check_output(['git', 'ls-files'], cwd=ROOT, text=True).splitlines()
    for name in names:
        if name.startswith('tests/') or name in HISTORICAL:
            continue
        path = ROOT / name
        try:
            yield path, path.read_text()
        except (UnicodeDecodeError, OSError):
            continue


class BrandingTests(unittest.TestCase):
    def test_readme_identity_credit_and_links(self):
        text = (ROOT / 'README.md').read_text()
        self.assertIn('<h1 align="center">Senhorfeudal Game Studios</h1>', text)
        self.assertIn(f'https://github.com/{NEW_REPO}.git', text)
        self.assertIn(f'https://github.com/{NEW_REPO}/issues', text)
        self.assertIn(f'https://github.com/{NEW_REPO}/discussions', text)
        self.assertIn(f'[Claude Code Game Studios](https://github.com/{UPSTREAM_REPO})', text)
        self.assertNotIn('buymeacoffee.com/donchitos3', text)
        self.assertNotIn('github.com/sponsors/Donchitos', text)

    def test_license_preserves_upstream_copyright_and_adds_modifications(self):
        text = (ROOT / 'LICENSE').read_text()
        self.assertIn('MIT License', text)
        self.assertIn('Copyright (c) 2026 Donchitos', text)
        self.assertIn('Modifications Copyright (c) 2026 Senhorfeudal', text)

    def test_active_files_do_not_reference_the_upstream_identity(self):
        offenders = {}
        for path, text in tracked_text_files():
            for token in FORBIDDEN:
                if token in text:
                    offenders.setdefault(str(path.relative_to(ROOT)), []).append(token)
        self.assertEqual(offenders, {}, 'upstream identity leaked into active files')

    def test_release_checks_use_the_new_repository(self):
        hook = (ROOT / '.claude/hooks/update-check.sh').read_text()
        self.assertIn(f'UPDATE_CHECK_REPO="{NEW_REPO}"', hook)
        self.assertIn('senhorfeudal-game-studios', hook)
        effects = (ROOT / '.claude/docs/effects-map.md').read_text()
        self.assertIn(f'api.github.com/repos/{NEW_REPO}/releases/latest', effects)

    def test_owners_and_funding(self):
        owners = (ROOT / '.github/CODEOWNERS').read_text()
        self.assertIn('@Senhorfeudal', owners)
        self.assertNotIn('@Donchitos', owners)
        self.assertFalse((ROOT / '.github/FUNDING.yml').exists(),
                         'donation config still points at a third party')


if __name__ == '__main__':
    unittest.main()
