import json
import importlib.util
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
APP = ROOT / "generated" / "task_manager.py"


class ApplicationTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.cwd = Path(self.tmp.name)

    def run_app(self, *args, error=None):
        result = subprocess.run([sys.executable, str(APP), *args], cwd=self.cwd, capture_output=True, text=True)
        if error is not None:
            self.assertEqual(result.returncode, 1, result.stderr)
            self.assertEqual(json.loads(result.stderr), {"error": error})
            return None
        self.assertEqual(result.returncode, 0, result.stderr)
        return json.loads(result.stdout)

    def test_lifecycle_and_persistence(self):
        self.assertEqual(self.run_app("list"), [])
        task = self.run_app("create", "--title", "First", "--description", "Details")
        self.assertEqual(task["status"], "pending")
        self.assertEqual(task["priority"], "NORMAL")
        self.assertEqual(task["description"], "Details")
        self.assertTrue(task["created_at"].endswith("Z"))
        self.assertEqual(self.run_app("list"), [task])
        completed = self.run_app("complete", "--id", task["id"])
        self.assertEqual(completed["status"], "completed")
        self.run_app("complete", "--id", task["id"], error="invalid_transition")
        self.assertEqual(self.run_app("delete", "--id", task["id"]), completed)
        self.assertEqual(self.run_app("list"), [])
        self.run_app("delete", "--id", task["id"], error="task_not_found")

    def test_failures_leave_state_intact(self):
        self.run_app("create", "--title", "  ", "--description", "x", error="invalid_title")
        self.assertFalse((self.cwd / "tasks.json").exists())
        task = self.run_app("create", "--title", "Valid", "--description", "x")
        before = (self.cwd / "tasks.json").read_bytes()
        self.run_app("complete", "--id", "missing", error="task_not_found")
        self.assertEqual((self.cwd / "tasks.json").read_bytes(), before)
        (self.cwd / "tasks.json").write_text("{broken", encoding="utf-8")
        self.run_app("list", error="invalid_state")
        self.run_app("complete", "--id", task["id"], error="invalid_state")

    def test_invariants_on_load(self):
        task = self.run_app("create", "--title", "Valid", "--description", "x")
        (self.cwd / "tasks.json").write_text(json.dumps({"schema_version": 3, "records": [task, task]}), encoding="utf-8")
        self.run_app("list", error="invalid_state")
        task["id"] = ""
        (self.cwd / "tasks.json").write_text(json.dumps({"schema_version": 3, "records": [task]}), encoding="utf-8")
        self.run_app("list", error="invalid_state")

    def test_high_priority_filter_and_default(self):
        normal = self.run_app("create", "--title", "ordinary", "--description", "x")
        high = self.run_app("create", "--title", "urgent", "--description", "x", "--priority", "HIGH")
        low = self.run_app("create", "--title", "later", "--description", "x", "--priority", "LOW")
        self.assertEqual([normal["priority"], high["priority"], low["priority"]], ["NORMAL", "HIGH", "LOW"])
        self.assertEqual(self.run_app("list-high"), [high])
        self.assertEqual({r["id"] for r in self.run_app("list")}, {normal["id"], high["id"], low["id"]})

    def test_explicit_legacy_migration(self):
        old = {"id": "old", "title": "Previous", "description": "x", "status": "pending", "created_at": "2026-01-01T00:00:00Z"}
        path = self.cwd / "tasks.json"
        path.write_text(json.dumps([old]), encoding="utf-8")
        previous = path.read_bytes()
        self.run_app("list", error="migration_required")
        self.assertEqual(path.read_bytes(), previous)
        self.assertEqual(self.run_app("migrate"), {"migrated": 1})
        self.assertEqual(self.run_app("list"), [{**old, "priority": "NORMAL", "due_date": None}])
        self.assertEqual(self.run_app("migrate"), {"migrated": 0})

    def test_overdue_and_optional_due_date(self):
        past = self.run_app("create", "--title", "past", "--description", "x", "--due-date", "2020-01-01T00:00:00Z")
        future = self.run_app("create", "--title", "future", "--description", "x", "--due-date", "2999-01-01T00:00:00Z")
        undated = self.run_app("create", "--title", "undated", "--description", "x")
        completed = self.run_app("create", "--title", "completed", "--description", "x", "--due-date", "2020-01-01T00:00:00Z")
        self.run_app("complete", "--id", completed["id"])
        self.assertIsNone(undated["due_date"])
        self.assertEqual([r["id"] for r in self.run_app("list-overdue")], [past["id"]])
        self.assertEqual(future["due_date"], "2999-01-01T00:00:00Z")
        self.run_app("create", "--title", "bad", "--description", "x", "--due-date", "yesterday", error="invalid_due_date")

    def test_semantic_scenario_with_fixed_clock(self):
        spec = importlib.util.spec_from_file_location("generated_tasks", APP)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        for scenario in module.SPEC.get("scenarios", []):
            with self.subTest(scenario=scenario["id"]):
                state = module.by_id("state", module.by_id("behaviors", scenario["behavior"])["state"])
                record_type, _ = module.state_layout(state)
                records = [{module.field_name(record_type, fid): value for fid, value in row.items()} for row in scenario["records"]]
                (self.cwd / "tasks.json").write_text(json.dumps({"schema_version": state["schema_version"], "records": records}), encoding="utf-8")
                storage = module.by_id("capabilities", state["storage"])
                original = storage["path"]
                storage["path"] = str(self.cwd / "tasks.json")
                calls = []
                def clock():
                    calls.append(1)
                    return scenario["clock"]
                try:
                    result = module.execute(module.by_id("behaviors", scenario["behavior"]), {}, clock=clock)
                finally:
                    storage["path"] = original
                self.assertEqual([row["id"] for row in result], scenario["expected_ids"])
                self.assertEqual(len(calls), 1)

    def test_version_two_migration(self):
        task = self.run_app("create", "--title", "old", "--description", "x")
        task.pop("due_date")
        (self.cwd / "tasks.json").write_text(json.dumps({"schema_version": 2, "records": [task]}), encoding="utf-8")
        self.run_app("list", error="migration_required")
        self.assertEqual(self.run_app("migrate"), {"migrated": 1})
        self.assertEqual(self.run_app("list")[0]["due_date"], None)


if __name__ == "__main__":
    unittest.main()
