"""B16 shared black-box users and required task ownership acceptance."""

import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


def cases(app, profile, achieved):
    class RequiredOwnership(unittest.TestCase):
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

        def test_users_required_owner_and_existing_filter(self):
            with tempfile.TemporaryDirectory() as folder:
                cwd = Path(folder)
                self.assertEqual(self.call(cwd, "list-users"), [{"id": "system"}])
                for user in ("", " \t "):
                    self.call(cwd, "create-user", "--id", user, error="invalid_user")
                self.assertEqual(self.call(cwd, "create-user", "--id", "Alex"), {"id": "Alex"})
                self.assertEqual(self.call(cwd, "create-user", "--id", "alex"), {"id": "alex"})
                for user in ("Alex", "system"):
                    self.call(cwd, "create-user", "--id", user, error="user_exists")
                self.assertEqual(self.call(cwd, "list-users"),
                                 [{"id": "Alex"}, {"id": "alex"}, {"id": "system"}])
                path = cwd / "tasks.json"
                before = path.read_bytes() if path.exists() else None
                self.call(cwd, "create", "--title", "missing", "--description", "x",
                          error="invalid_owner")
                self.call(cwd, "create", "--title", "unknown", "--description", "x",
                          "--owner", "other", error="invalid_owner")
                self.call(cwd, "create", "--title", "blank", "--description", "x",
                          "--owner", "", error="invalid_owner")
                self.assertEqual(path.read_bytes() if path.exists() else None, before)
                first = self.call(cwd, "create", "--title", "first", "--description", "x",
                                  "--owner", "Alex")
                second = self.call(cwd, "create", "--title", "second", "--description", "x",
                                   "--owner", "system")
                self.assertEqual([first["owner"], second["owner"]], ["Alex", "system"])
                self.assertEqual(set(first), set(profile["fields"]))
                self.assertEqual(self.call(cwd, "list"),
                                 sorted((first, second), key=lambda item: (item["created_at"], item["id"])))
                if "B10" in achieved:
                    self.assertEqual(self.call(cwd, "list-owner", "--owner", "Alex"), [first])
                    self.assertEqual(self.call(cwd, "list-owner", "--owner", "system"), [second])
                    self.assertEqual(self.call(cwd, "list-owner", "--owner", ""), [])

        def test_unowned_migration_defaults_to_system(self):
            with tempfile.TemporaryDirectory() as folder:
                cwd = Path(folder)
                old = {"id": "old", "title": "old", "description": "x", "status": "pending",
                       "priority": "NORMAL", "created_at": "2026-01-01T00:00:00Z", "due_date": None}
                path = cwd / "tasks.json"
                path.write_text(json.dumps({"schema_version": 3, "records": [old]}), encoding="utf-8")
                before = path.read_bytes()
                self.call(cwd, "list", error="migration_required")
                self.assertEqual(path.read_bytes(), before)
                self.assertEqual(self.call(cwd, "migrate"), {"migrated": 1})
                expected = {**old, **profile["migration_defaults"]}
                self.assertEqual(expected["owner"], "system")
                self.assertEqual(self.call(cwd, "list"), [expected])
                self.assertEqual(json.loads(path.read_text(encoding="utf-8"))["schema_version"],
                                 profile["schema_version"])
                self.assertEqual(self.call(cwd, "list-users"), [{"id": "system"}])

        def test_unresolved_nonempty_owner_migration_is_atomic_and_retryable(self):
            if "B10" not in achieved:
                self.skipTest("no previously achieved owner field to migrate")
            with tempfile.TemporaryDirectory() as folder:
                cwd = Path(folder)
                self.call(cwd, "create-user", "--id", "known")
                task = self.call(cwd, "create", "--title", "prior", "--description", "x",
                                 "--owner", "known")
                path = cwd / "tasks.json"
                payload = json.loads(path.read_text(encoding="utf-8"))
                payload["schema_version"] = profile["schema_version"] - 1
                payload["records"][0]["owner"] = "missing-user"
                path.write_text(json.dumps(payload), encoding="utf-8")
                before = path.read_bytes()
                self.call(cwd, "migrate", error="invalid_owner")
                self.assertEqual(path.read_bytes(), before)
                self.assertEqual(self.call(cwd, "create-user", "--id", "missing-user"),
                                 {"id": "missing-user"})
                self.assertEqual(self.call(cwd, "migrate"), {"migrated": 1})
                self.assertEqual(self.call(cwd, "list")[0]["owner"], "missing-user")
                self.assertEqual(self.call(cwd, "list")[0]["id"], task["id"])

    return unittest.defaultTestLoader.loadTestsFromTestCase(RequiredOwnership)
