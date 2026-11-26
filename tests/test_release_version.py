"""Keep the framework version consistent across config, hook and changelog.

Run: python3 -m unittest discover -s tests -p test_release_version.py -v
"""
import pathlib
import re
import unittest

import yaml

ROOT = pathlib.Path(__file__).resolve().parents[1]


class ReleaseVersionTests(unittest.TestCase):
    def test_config_hook_and_changelog_agree(self):
        config = yaml.safe_load((ROOT / 'project.yaml').read_text())
        configured = str(config['framework']['version'])

        hook = (ROOT / '.claude/hooks/update-check.sh').read_text()
        match = re.search(r'^UPDATE_CHECK_VERSION="([^"]+)"', hook, re.MULTILINE)
        self.assertIsNotNone(match, 'UPDATE_CHECK_VERSION is missing')
        checked = match.group(1)

        changelog = (ROOT / 'CHANGELOG.md').read_text()
        released = re.search(r'^## \[([0-9]+\.[0-9]+\.[0-9]+)\]', changelog, re.MULTILINE)
        self.assertIsNotNone(released, 'no release heading in CHANGELOG.md')

        self.assertEqual(configured, checked, 'update-check reports a stale version')
        self.assertEqual(configured, released.group(1),
                         'the latest changelog release is not the framework version')

    def test_release_date_is_present(self):
        changelog = (ROOT / 'CHANGELOG.md').read_text()
        match = re.search(r'^## \[[0-9.]+\] — (\d{4}-\d{2}-\d{2})',
                          changelog, re.MULTILINE)
        self.assertIsNotNone(match, 'latest release has no date')


if __name__ == '__main__':
    unittest.main()
