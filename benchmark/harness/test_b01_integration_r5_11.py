"""Actual new candidate subprocess cases; no test-authored internal execution events."""

import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

from benchmark.semantic import b01_integration_r5_11 as integration


class Integration(unittest.TestCase):
    def invoke(self, app, cwd, operation, *arguments):
        captured = integration.capture(app, cwd, operation, arguments)
        verdict = integration.challenge(app, captured)
        return captured, verdict

    def test_real_b01_cases(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            app = integration.build(root)
            cwd = root / 'case'
            cwd.mkdir()
            cases = []
            def call(op, *args):
                captured, verdict = self.invoke(app, cwd, op, *args)
                cases.append((op, verdict))
                self.assertEqual(verdict['grounding'], 'GROUNDED')
                self.assertEqual(verdict['conformance'], 'CONFORMANT', (op, verdict))
                return json.loads(captured[1]['stdout'])
            self.assertEqual(call('list'), [])
            normal = call('create', '--title', 'Normal', '--description', 'x')
            high = call('create', '--title', 'High', '--description', 'x', '--priority', 'HIGH')
            critical = call('create', '--title', 'Critical', '--description', 'x', '--priority', 'CRITICAL')
            self.assertEqual(critical['priority'], 'CRITICAL')
            self.assertEqual(call('list-high'), [high])
            self.assertEqual(call('complete', '--id', high['id']), {**high, 'status': 'completed'})
            self.assertEqual(call('list-high'), [{**high, 'status': 'completed'}])
            self.assertEqual(call('list'), sorted([normal, {**high, 'status': 'completed'}, critical],
                                                  key=lambda r: (r['created_at'], r['id'])))
            self.assertEqual(call('complete', '--id', critical['id']), {**critical, 'status': 'completed'})
            self.assertEqual(call('list-high'), [{**high, 'status': 'completed'}])
            failed, verdict = self.invoke(app, cwd, 'complete', '--id', critical['id'])
            self.assertEqual(failed[1]['exit'], 1)
            self.assertEqual(verdict['conformance'], 'CONFORMANT')
            self.assertEqual(verdict['grounding'], 'GROUNDED')
            failed, verdict = self.invoke(app, cwd, 'complete', '--id', 'missing')
            self.assertEqual(json.loads(failed[1]['stderr']), {'error': 'task_not_found'})
            self.assertEqual(verdict['conformance'], 'CONFORMANT')
            self.assertEqual(call('delete', '--id', critical['id'])['priority'], 'CRITICAL')
            self.assertEqual({op for op, _ in cases}, {'list', 'create', 'list-high', 'complete', 'delete'})

    def test_migration_all_legacy_rows_count(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            app = integration.build(root)
            cwd = root / 'migration'
            cwd.mkdir()
            empty, empty_verdict = self.invoke(app, cwd, 'migrate')
            self.assertEqual(json.loads(empty[1]['stdout']), {'migrated': 0})
            self.assertEqual(empty_verdict['conformance'], 'CONFORMANT')
            rows = [{'id': p.lower(), 'title': p, 'description': 'x', 'status': 'pending',
                     'priority': p, 'created_at': '2026-01-01T00:00:00Z'}
                    for p in ('HIGH', 'LOW', 'NORMAL')]
            (cwd / 'tasks.json').write_text(json.dumps({'schema_version': 2, 'records': rows}), encoding='utf-8')
            captured, verdict = self.invoke(app, cwd, 'migrate')
            self.assertEqual(verdict['grounding'], 'GROUNDED')
            self.assertEqual(verdict['conformance'], 'CONFORMANT')
            self.assertEqual(json.loads(captured[1]['stdout']), {'migrated': 3})
            self.assertEqual(captured[3]['value']['schema_version'], 3)
            self.assertEqual(captured[3]['value']['records'], [{**r, 'due_date': None} for r in rows])
            _, verdict = self.invoke(app, cwd, 'migrate')
            self.assertEqual(verdict['conformance'], 'CONFORMANT')
            old = [{k: v for k, v in rows[0].items() if k != 'priority'}]
            (cwd / 'tasks.json').write_text(json.dumps(old), encoding='utf-8')
            _, verdict = self.invoke(app, cwd, 'migrate')
            self.assertEqual(verdict['conformance'], 'CONFORMANT')

    def test_faults_separate_grounding_and_semantics(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            row = {'id': 'old', 'title': 'Old', 'description': 'x', 'status': 'pending',
                   'priority': 'HIGH', 'created_at': '2026-01-01T00:00:00Z'}
            for variant, expected in (('wrong_count', ('GROUNDED', 'NON_CONFORMANT')),
                                      ('false_post', ('GROUNDING_FAILED', None))):
                with self.subTest(variant=variant):
                    build = root / variant
                    build.mkdir()
                    app = integration.build(build, variant)
                    cwd = build / 'case'
                    cwd.mkdir()
                    (cwd / 'tasks.json').write_text(json.dumps({'schema_version': 2, 'records': [row]}), encoding='utf-8')
                    _, verdict = self.invoke(app, cwd, 'migrate')
                    self.assertEqual((verdict['grounding'], verdict['conformance']), expected)
            app = root / 'wrong_count' / 'task_manager.py'
            app.write_text(app.read_text(encoding='utf-8') + '\n# drift\n', encoding='utf-8')
            _, verdict = self.invoke(app, root / 'wrong_count' / 'case', 'list')
            self.assertFalse(verdict['provenance_valid'])
            self.assertIsNone(verdict['conformance'])

    def test_original_frozen_b01_acceptance(self):
        with tempfile.TemporaryDirectory() as folder:
            app = integration.build(Path(folder))
            root = Path(__file__).resolve().parents[1]
            result = subprocess.run([sys.executable, str(root / 'harness' / 'regression.py'),
                                     '--app', str(app), '--achieved', 'B01'],
                                    capture_output=True, text=True, check=False)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(json.loads(result.stdout)['failure_events'], 0)


if __name__ == '__main__':
    unittest.main()
