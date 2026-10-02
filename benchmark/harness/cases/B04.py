"""B04 black-box acceptance: source is verbatim, persistent and migrated."""

import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


def cases(app, profile, achieved):
    class SourceLabel(unittest.TestCase):
        def call(self, cwd, *args, error=None):
            result = subprocess.run([sys.executable, str(app), *args], cwd=cwd,
                                    capture_output=True, text=True)
            if error is not None:
                self.assertEqual(result.returncode, 1, result)
                self.assertEqual(result.stdout, "")
                self.assertEqual(json.loads(result.stderr), {"error": error})
                return None
            self.assertEqual(result.returncode, 0, result)
            self.assertEqual(result.stderr, "")
            return json.loads(result.stdout)

        def test_verbatim_default_and_mutations(self):
            with tempfile.TemporaryDirectory() as folder:
                cwd = Path(folder)
                labelled = self.call(cwd, "create", "--title", "labelled", "--description", "x",
                                     "--priority", "HIGH", "--source", "  API\tfeed  ")
                omitted = self.call(cwd, "create", "--title", "omitted", "--description", "x")
                empty = self.call(cwd, "create", "--title", "empty", "--description", "x",
                                  "--source", "")
                self.assertEqual(labelled["source"], "  API\tfeed  ")
                self.assertEqual(omitted["source"], "")
                self.assertEqual(empty["source"], "")
                self.assertEqual({task["id"]: task["source"] for task in self.call(cwd, "list")},
                                 {labelled["id"]: "  API\tfeed  ", omitted["id"]: "", empty["id"]: ""})
                self.assertEqual(self.call(cwd, "list-high")[0]["source"], "  API\tfeed  ")
                completed = self.call(cwd, "complete", "--id", labelled["id"])
                self.assertEqual(completed["source"], "  API\tfeed  ")
                self.assertEqual(next(task for task in self.call(cwd, "list")
                                      if task["id"] == labelled["id"])["source"], "  API\tfeed  ")
                self.assertEqual(self.call(cwd, "delete", "--id", labelled["id"])["source"],
                                 "  API\tfeed  ")

        def test_explicit_migration_of_prior_storage(self):
            with tempfile.TemporaryDirectory() as folder:
                cwd = Path(folder)
                previous = {"id": "prior", "title": "prior", "description": "x",
                            "status": "pending", "priority": "NORMAL",
                            "created_at": "2026-01-01T00:00:00Z", "due_date": None}
                # Version 3 predates source on both tracks. The achieved set
                # determines whether an additional tags field is applicable.
                payload = {"schema_version": 3, "records": [previous]}
                path = cwd / "tasks.json"
                path.write_text(json.dumps(payload), encoding="utf-8")
                before = path.read_bytes()
                self.call(cwd, "list", error="migration_required")
                self.assertEqual(path.read_bytes(), before)
                self.assertEqual(self.call(cwd, "migrate"), {"migrated": 1})
                expected = {**previous, **profile["migration_defaults"]}
                self.assertEqual(self.call(cwd, "list"), [expected])
                self.assertEqual(json.loads(path.read_text(encoding="utf-8"))["schema_version"],
                                 profile["schema_version"])
                unchanged = path.read_bytes()
                self.assertEqual(self.call(cwd, "migrate"), {"migrated": 0})
                self.assertEqual(path.read_bytes(), unchanged)

    return unittest.defaultTestLoader.loadTestsFromTestCase(SourceLabel)
