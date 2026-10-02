"""B14: ordered dependency IDs, cycle prevention, and deletion integrity."""

import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


def cases(app, profile, achieved):
    class Dependencies(unittest.TestCase):
        def call(self, cwd, *args, error=None):
            result = subprocess.run([sys.executable, str(app), *args], cwd=cwd,
                                    capture_output=True, text=True)
            self.assertEqual(result.returncode, 1 if error else 0, result)
            if error:
                self.assertEqual(result.stdout, "")
                self.assertEqual(json.loads(result.stderr), {"error": error})
                return None
            self.assertEqual(result.stderr, "")
            return json.loads(result.stdout)

        def test_order_cycles_and_no_write_failures(self):
            with tempfile.TemporaryDirectory() as folder:
                cwd = Path(folder)
                tasks = [self.call(cwd, "create", "--title", name, "--description", "x")
                         for name in ("a", "b", "c", "d")]
                a, b, c, d = tasks
                self.assertEqual([task["dependencies"] for task in tasks], [[], [], [], []])
                a = self.call(cwd, "add-dependency", "--id", a["id"], "--depends-on", b["id"])
                a = self.call(cwd, "add-dependency", "--id", a["id"], "--depends-on", c["id"])
                self.assertEqual(a["dependencies"], [b["id"], c["id"]])
                b = self.call(cwd, "add-dependency", "--id", b["id"], "--depends-on", d["id"])
                self.assertEqual(b["dependencies"], [d["id"]])
                before = (cwd / "tasks.json").read_bytes()
                for target, other, error in ((a, a, "invalid_dependency"),
                                             (a, b, "invalid_dependency"),
                                             (a, {"id": "missing"}, "task_not_found"),
                                             (d, a, "invalid_dependency"),
                                             (c, a, "invalid_dependency"),
                                             ({"id": "missing"}, a, "task_not_found")):
                    self.call(cwd, "add-dependency", "--id", target["id"],
                              "--depends-on", other["id"], error=error)
                    self.assertEqual((cwd / "tasks.json").read_bytes(), before)
                self.assertEqual(next(t for t in self.call(cwd, "list") if t["id"] == a["id"]), a)
                self.call(cwd, "delete", "--id", d["id"], error="dependency_in_use")
                self.call(cwd, "delete", "--id", b["id"], error="dependency_in_use")
                self.assertEqual((cwd / "tasks.json").read_bytes(), before)
                self.assertEqual(self.call(cwd, "delete", "--id", a["id"]), a)
                self.assertEqual(self.call(cwd, "delete", "--id", b["id"]), b)
                self.assertEqual(self.call(cwd, "delete", "--id", d["id"]), d)

        def test_archived_reference_and_explicit_migration(self):
            with tempfile.TemporaryDirectory() as folder:
                cwd = Path(folder)
                source = self.call(cwd, "create", "--title", "source", "--description", "x")
                parent = self.call(cwd, "create", "--title", "parent", "--description", "x")
                source = self.call(cwd, "archive", "--id", source["id"])
                parent = self.call(cwd, "add-dependency", "--id", parent["id"],
                                   "--depends-on", source["id"])
                before = (cwd / "tasks.json").read_bytes()
                self.call(cwd, "delete", "--id", source["id"], error="dependency_in_use")
                self.assertEqual((cwd / "tasks.json").read_bytes(), before)
                self.assertEqual(self.call(cwd, "delete", "--id", parent["id"]), parent)
                self.assertEqual(self.call(cwd, "delete", "--id", source["id"]), source)

            with tempfile.TemporaryDirectory() as folder:
                cwd = Path(folder)
                old = self.call(cwd, "create", "--title", "old", "--description", "x")
                store = cwd / "tasks.json"
                payload = json.loads(store.read_text(encoding="utf-8"))
                self.assertGreater(payload["schema_version"], 9)
                payload["schema_version"] = 9
                for record in payload["records"]:
                    record.pop("dependencies")
                store.write_text(json.dumps(payload), encoding="utf-8")
                before = store.read_bytes()
                self.call(cwd, "list", error="migration_required")
                self.assertEqual(store.read_bytes(), before)
                self.assertEqual(self.call(cwd, "migrate"), {"migrated": 1})
                self.assertEqual(self.call(cwd, "list")[0], {**old, "dependencies": []})
                self.assertEqual(self.call(cwd, "migrate"), {"migrated": 0})

    return unittest.defaultTestLoader.loadTestsFromTestCase(Dependencies)
