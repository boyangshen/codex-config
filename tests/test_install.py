import importlib.util
import json
import os
from pathlib import Path
import subprocess
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('manage', ROOT / 'scripts/manage.py')
manage = importlib.util.module_from_spec(spec)
spec.loader.exec_module(manage)


class InstallTests(unittest.TestCase):
    def test_merge_preserves_host_settings_and_comments(self):
        text = '# host settings\nmodel="old"\n[projects."/server/project"]\ntrust_level="trusted"\n[tui]\ntheme="old"\n'
        merged = manage.merge_text(text, {'model': 'new', 'tui': {'theme': 'new', 'fullscreen_transcript': True}})
        parsed = manage.tomllib.loads(merged)
        self.assertEqual(parsed['projects']['/server/project']['trust_level'], 'trusted')
        self.assertEqual(parsed['model'], 'new')
        self.assertTrue(parsed['tui']['fullscreen_transcript'])
        self.assertIn('# host settings', merged)

    def test_new_config_and_repeated_merge(self):
        shared = {'model': 'gpt-6.1-sol', 'tui': {'theme': 'catppuccin-frappe'}}
        text = manage.merge_text('', shared)
        self.assertEqual(manage.merge_text(text, shared), text)
        self.assertEqual(manage.tomllib.loads(text), shared)

    def test_presets_roundtrip_and_existing_nested_section(self):
        shared = {'tui': {'presets': {'1': {'text': '使用 skill\n规划任务', 'name': '规划'}}}}
        text = '[tui]\ntheme="local"\n[tui.presets.1]\ntext="old"\nname="old"\n'
        merged = manage.merge_text(text, shared)
        parsed = manage.tomllib.loads(merged)
        self.assertEqual(parsed['tui']['presets'], shared['tui']['presets'])
        self.assertEqual(parsed['tui']['theme'], 'local')

    def test_capture_allowlist_excludes_credentials_and_paths(self):
        data = {'model': 'new', 'api_key': 'DO_NOT_EXPORT', 'projects': {'/private': {'trust_level': 'trusted'}},
                'mcp_servers': {'secret': {'token': 'DO_NOT_EXPORT'}}, 'tui': {'theme': 'dark', 'model_availability_nux': {'a': 1}}}
        selected = manage.select_portable(data)
        self.assertEqual(selected, {'model': 'new', 'tui': {'theme': 'dark'}})
        self.assertNotIn('DO_NOT_EXPORT', manage.render(selected))
        self.assertEqual(manage.tomllib.loads(manage.render(selected)), selected)

    def test_unsupported_multiline_layout_does_not_silently_corrupt(self):
        text = 'model = """old\nmodel = \\"embedded\\"\n"""\n'
        with self.assertRaises((ValueError, manage.tomllib.TOMLDecodeError)):
            manage.merge_text(text, {'model': 'new'})

    def test_install_backs_up_existing_files_and_is_repeatable(self):
        with tempfile.TemporaryDirectory() as directory:
            home = Path(directory)
            original = '# local\n[projects."/host/project"]\ntrust_level="trusted"\n'
            (home / '.codex/skills/plan-implement-review').mkdir(parents=True)
            (home / '.codex/skills/plan-implement-review/SKILL.md').write_text('old skill')
            (home / '.agents/skills').mkdir(parents=True)
            (home / '.agents/skills/plan-implement-review').symlink_to(home / '.codex/skills/plan-implement-review')
            (home / '.codex/config.toml').write_text(original)
            manage.install(home, dry_run=True)
            self.assertEqual((home / '.codex/config.toml').read_text(), original)
            self.assertFalse((home / '.codex/backups').exists())
            manage.install(home)
            backup_files = list((home / '.codex/backups').rglob('config.toml'))
            self.assertEqual(len(backup_files), 1)
            self.assertEqual(backup_files[0].read_text(), original)
            self.assertEqual(len(list((home / '.codex/backups').rglob('SKILL.md'))), 1)
            for base in ('.codex/skills', '.agents/skills'):
                self.assertEqual((home / base / 'plan-implement-review').resolve(), (ROOT / 'skills/plan-implement-review').resolve())
            self.assertTrue((home / '.local/bin/codex-personal').is_symlink())
            before_backups = list((home / '.codex/backups').iterdir())
            manage.install(home)
            self.assertEqual(before_backups, list((home / '.codex/backups').iterdir()))
            self.assertEqual(manage.tomllib.loads((home / '.codex/config.toml').read_text())['projects']['/host/project']['trust_level'], 'trusted')

    def test_wrapper_forwards_arguments_when_sync_is_disabled(self):
        with tempfile.TemporaryDirectory() as directory:
            fake = Path(directory) / 'codex'
            fake.write_text('#!/bin/sh\nprintf "%s\\n" "$@"\n')
            fake.chmod(0o755)
            env = dict(os.environ, PATH=directory + os.pathsep + os.environ['PATH'], CODEX_CONFIG_AUTO_SYNC='0')
            result = subprocess.run([str(ROOT / 'bin/codex-personal'), '-m', 'test-model', 'file with spaces'],
                                    env=env, capture_output=True, text=True, timeout=10)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(result.stdout.splitlines(), ['-m', 'test-model', 'file with spaces'])

    def test_dirty_repository_refuses_sync(self):
        # A disposable clone has a tracked local change and no network dependency.
        with tempfile.TemporaryDirectory() as directory:
            clone = Path(directory) / 'repo'
            subprocess.run(['git', 'clone', '--quiet', str(ROOT), str(clone)], check=True)
            (clone / 'README.md').write_text('local uncommitted change')
            result = subprocess.run([str(clone / 'sync.sh')], capture_output=True, text=True, timeout=10)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn('未提交改动', result.stderr)
            self.assertEqual((clone / 'README.md').read_text(), 'local uncommitted change')


if __name__ == '__main__':
    unittest.main()
