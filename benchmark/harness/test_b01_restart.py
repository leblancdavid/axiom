"""Prospective B01 adapter checks; not additions to frozen acceptance."""

import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

from benchmark.semantic import b01_restart as restart


class B01Restart(unittest.TestCase):
    def test_snapshot_provenance_and_real_public_root(self):
        self.assertEqual(restart.sha(restart.deployed_bytes()),
                         json.loads(restart.CHECKPOINT.read_text())['files'][restart.MEMBER])
        result = restart.run_selected()
        self.assertEqual(result['calls'], 7)
        self.assertTrue(result['public_root_observation'])
        self.assertTrue(result['independent_public_and_durable_endpoints'])
        self.assertEqual(result['grounding'], 'GROUNDING_FAILURE')
        self.assertIsNone(result['contract_conformant'])

    def test_binding_rejects_unmapped_or_missing_arguments(self):
        for operation, args in (('list-high', {'--priority': 'HIGH'}),
                                ('create', {'--title': 'x'}),
                                ('complete', {}), ('unknown', {})):
            with self.subTest(operation=operation), self.assertRaises(ValueError):
                restart.validate_binding(operation, args)

    def test_failure_observes_unchanged_durable_bytes_without_claiming_internal_trace(self):
        with tempfile.TemporaryDirectory() as temp:
            cwd = Path(temp)
            app = cwd / 'task_manager.py'
            app.write_bytes(restart.deployed_bytes())
            created = restart.capture(app, cwd, 'create',
                                      {'--title': 'x', '--description': 'y'})
            identifier = json.loads(created['stdout'])['id']
            restart.capture(app, cwd, 'complete', {'--id': identifier})
            event = restart.capture(app, cwd, 'complete', {'--id': identifier})
            self.assertEqual((event['exit'], json.loads(event['stderr'])),
                             (1, {'error': 'invalid_transition'}))
            self.assertEqual(event['before_sha256'], event['after_sha256'])
            self.assertIsNone(event['internal_event'])

    def test_frozen_b01_acceptance_on_pinned_snapshot(self):
        with tempfile.TemporaryDirectory() as temp:
            app = Path(temp) / 'task_manager.py'
            app.write_bytes(restart.deployed_bytes())
            process = subprocess.run(
                [sys.executable, str(restart.ROOT / 'benchmark/harness/regression.py'),
                 '--app', str(app), '--achieved', 'B01'],
                capture_output=True, text=True, check=False, timeout=90)
            self.assertEqual(process.returncode, 0, process.stderr)
            summary = json.loads(process.stdout)
            self.assertEqual(summary['achieved'], ['B01'])
            self.assertEqual(summary['failure_events'], 0)
            self.assertEqual(summary['passed'], 5)

    def test_migration_public_count_and_independent_durable_readback(self):
        with tempfile.TemporaryDirectory() as temp:
            cwd = Path(temp)
            app = cwd / 'task_manager.py'
            app.write_bytes(restart.deployed_bytes())
            old = {'id': 'legacy', 'title': 'Legacy', 'description': 'x',
                   'status': 'pending', 'created_at': '2026-01-01T00:00:00Z'}
            (cwd / 'tasks.json').write_text(json.dumps([old]), encoding='utf-8')
            event = restart.capture(app, cwd, 'migrate')
            self.assertEqual(json.loads(event['stdout']), {'migrated': 1})
            self.assertEqual(event['before'], [old])
            self.assertEqual(event['after']['schema_version'], 3)
            self.assertEqual(event['after']['records'],
                             [{**old, 'priority': 'NORMAL', 'due_date': None}])
            self.assertNotEqual(event['before_sha256'], event['after_sha256'])
            self.assertIsNone(event['internal_event'])


if __name__ == '__main__':
    unittest.main()
