"""Regression tests for task priority and tag handling."""

import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

from task_manager import TaskStore


SCRIPT = Path(__file__).resolve().with_name("task_manager.py")
CREATED_AT = "2026-01-01T00:00:00Z"


class PriorityTests(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)
        self.store = TaskStore(Path(self.directory.name) / "tasks.json")

    def cli(self, *args):
        result = subprocess.run(
            [sys.executable, str(SCRIPT), *args],
            cwd=self.directory.name,
            capture_output=True,
            text=True,
            check=True,
        )
        return json.loads(result.stdout)

    def test_critical_round_trip_and_high_filter(self):
        critical = self.cli("create", "--title", "Urgent", "--description", "Now",
                            "--priority", "CRITICAL")
        high = self.cli("create", "--title", "Important", "--description", "Soon",
                        "--priority", "HIGH")
        default = self.cli("create", "--title", "Routine", "--description", "Later")

        self.assertEqual(critical["priority"], "CRITICAL")
        self.assertEqual(default["priority"], "NORMAL")
        self.assertEqual(default["tags"], [])
        self.assertEqual({task.id: task.priority for task in self.store.load()}, {
            critical["id"]: "CRITICAL", high["id"]: "HIGH", default["id"]: "NORMAL",
        })
        self.assertEqual({task["id"] for task in self.cli("list")},
                         {critical["id"], high["id"], default["id"]})
        self.assertEqual([task["id"] for task in self.cli("list-high")], [high["id"]])

    def test_migration_preserves_existing_priorities(self):
        rows = [
            {"id": priority.lower(), "title": priority, "description": "",
             "status": "pending", "priority": priority, "created_at": CREATED_AT}
            for priority in ("LOW", "NORMAL", "HIGH")
        ]
        self.store.path.write_text(json.dumps({"schema_version": 2, "records": rows}),
                                   encoding="utf-8")

        self.assertEqual(self.cli("migrate"), {"migrated": 3})
        self.assertEqual({task.id: task.priority for task in self.store.load()},
                         {"low": "LOW", "normal": "NORMAL", "high": "HIGH"})
        self.assertEqual({task.due_date for task in self.store.load()}, {None})
        self.assertEqual([task.tags for task in self.store.load()], [[], [], []])

    def test_legacy_migration_defaults_to_normal(self):
        row = {"id": "legacy", "title": "Old", "description": "",
               "status": "pending", "created_at": CREATED_AT}
        self.store.path.write_text(json.dumps([row]), encoding="utf-8")

        self.assertEqual(self.cli("migrate"), {"migrated": 1})
        self.assertEqual(self.store.load()[0].priority, "NORMAL")
        self.assertEqual(self.store.load()[0].tags, [])

    def test_tags_are_trimmed_ordered_and_case_sensitive(self):
        created = self.cli("create", "--title", "Tagged", "--description", "Test",
                           "--priority", "CRITICAL", "--tag", "  work  ",
                           "--tag", "Work", "--tag", "work", "--tag", "home ")
        expected = ["work", "Work", "home"]
        self.assertEqual(created["tags"], expected)
        self.assertEqual(self.store.load()[0].tags, expected)
        self.assertEqual(self.cli("list")[0]["tags"], expected)
        self.assertEqual(self.cli("complete", "--id", created["id"])["tags"], expected)
        self.assertEqual(self.cli("list")[0]["tags"], expected)

    def test_blank_tag_rejects_create_without_writing(self):
        existing = self.cli("create", "--title", "Existing", "--description", "Keep")
        before = self.store.path.read_bytes()
        result = subprocess.run(
            [sys.executable, str(SCRIPT), "create", "--title", "New", "--description", "No",
             "--tag", "valid", "--tag", " \t "],
            cwd=self.directory.name, capture_output=True, text=True,
        )
        self.assertEqual(result.returncode, 1)
        self.assertEqual(json.loads(result.stderr), {"error": "invalid_tag"})
        self.assertEqual(self.store.path.read_bytes(), before)
        self.assertEqual([task["id"] for task in self.cli("list")], [existing["id"]])

    def test_version_three_migration_adds_tags_without_changing_fields(self):
        row = {"id": "critical", "title": "Old", "description": "Retain",
               "status": "pending", "priority": "CRITICAL", "created_at": CREATED_AT,
               "due_date": "2026-02-01T00:00:00Z"}
        self.store.path.write_text(json.dumps({"schema_version": 3, "records": [row]}),
                                   encoding="utf-8")
        result = subprocess.run([sys.executable, str(SCRIPT), "list"],
                                cwd=self.directory.name, capture_output=True, text=True)
        self.assertEqual(result.returncode, 1)
        self.assertEqual(json.loads(result.stderr), {"error": "migration_required"})
        self.assertEqual(self.cli("migrate"), {"migrated": 1})
        self.assertEqual(self.cli("list"), [{**row, "tags": []}])
        self.assertEqual(json.loads(self.store.path.read_text(encoding="utf-8"))["schema_version"], 4)


if __name__ == "__main__":
    unittest.main()
