"""Frozen Phase 5A external cases. Run separately with --app PATH --through B01|B02."""

import argparse
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


APP = None
THROUGH = None


def call(cwd, *args, error=None):
    response = subprocess.run([sys.executable, str(APP), *args], cwd=cwd, capture_output=True, text=True)
    if error is None:
        assert response.returncode == 0 and not response.stderr, (args, response)
        return json.loads(response.stdout)
    assert response.returncode == 1 and not response.stdout, (args, response)
    assert json.loads(response.stderr) == {"error": error}, (args, response)


def fixture(identifier="old", priority="HIGH"):
    return {"id": identifier, "title": "Prior", "description": "x", "status": "pending",
            "priority": priority, "created_at": "2026-01-01T00:00:00Z", "due_date": None}


class PilotOracle(unittest.TestCase):
    def test_b01_priority_and_regression(self):
        with tempfile.TemporaryDirectory() as folder:
            cwd = Path(folder)
            default = call(cwd, "create", "--title", "Default", "--description", "x")
            high = call(cwd, "create", "--title", "High", "--description", "x", "--priority", "HIGH")
            critical = call(cwd, "create", "--title", "Critical", "--description", "x", "--priority", "CRITICAL")
            self.assertEqual(default["priority"], "NORMAL")
            self.assertEqual(high["priority"], "HIGH")
            self.assertEqual(critical["priority"], "CRITICAL")
            self.assertEqual(call(cwd, "list-high"), [high])
            listed = call(cwd, "list")
            self.assertEqual([r["id"] for r in listed],
                             [r["id"] for r in sorted((default, high, critical), key=lambda r: (r["created_at"], r["id"]))])
            self.assertEqual(call(cwd, "complete", "--id", critical["id"])["status"], "completed")
            self.assertEqual(call(cwd, "list-high"), [high])
            self.assertEqual(call(cwd, "delete", "--id", critical["id"])["priority"], "CRITICAL")
            self.assertEqual(call(cwd, "list-overdue"), [])

    def test_b01_existing_priorities(self):
        with tempfile.TemporaryDirectory() as folder:
            cwd = Path(folder)
            rows = [fixture("high", "HIGH"), fixture("low", "LOW"), fixture("normal", "NORMAL")]
            (cwd / "tasks.json").write_text(json.dumps({"schema_version": 3, "records": rows}), encoding="utf-8")
            if THROUGH == "B01":
                self.assertEqual(call(cwd, "list"), rows)
            else:
                self.assertEqual(call(cwd, "list", error="migration_required"), None)
                self.assertEqual(call(cwd, "migrate"), {"migrated": 3})
                self.assertEqual([r["priority"] for r in call(cwd, "list")], ["HIGH", "LOW", "NORMAL"])

    def test_b02_tags_and_failure(self):
        if THROUGH != "B02":
            self.skipTest("B02 not yet due")
        with tempfile.TemporaryDirectory() as folder:
            cwd = Path(folder)
            plain = call(cwd, "create", "--title", "Plain", "--description", "x")
            self.assertEqual(plain["tags"], [])
            tagged = call(cwd, "create", "--title", "Tagged", "--description", "x", "--priority", "CRITICAL",
                          "--tag", "  work  ", "--tag", "Work", "--tag", "work", "--tag", "home")
            self.assertEqual(tagged["tags"], ["work", "Work", "home"])
            self.assertEqual(call(cwd, "list-high"), [])
            self.assertEqual({r["id"] for r in call(cwd, "list")}, {plain["id"], tagged["id"]})
            before = (cwd / "tasks.json").read_bytes()
            call(cwd, "create", "--title", "Invalid", "--description", "x", "--tag", "  ", error="invalid_tag")
            self.assertEqual((cwd / "tasks.json").read_bytes(), before)
            self.assertEqual(call(cwd, "complete", "--id", tagged["id"])["tags"], ["work", "Work", "home"])

    def test_b02_explicit_migration(self):
        if THROUGH != "B02":
            self.skipTest("B02 not yet due")
        for payload in ({"schema_version": 3, "records": [fixture(priority="CRITICAL")]},
                        [{k: v for k, v in fixture().items() if k not in ("priority", "due_date")}]):
            with self.subTest(payload=type(payload).__name__), tempfile.TemporaryDirectory() as folder:
                cwd = Path(folder)
                path = cwd / "tasks.json"
                path.write_text(json.dumps(payload), encoding="utf-8")
                before = path.read_bytes()
                call(cwd, "list", error="migration_required")
                self.assertEqual(path.read_bytes(), before)
                self.assertEqual(call(cwd, "migrate"), {"migrated": 1})
                self.assertEqual(call(cwd, "list")[0]["tags"], [])
                self.assertEqual(call(cwd, "list")[0]["priority"],
                                 "CRITICAL" if isinstance(payload, dict) else "NORMAL")
                self.assertEqual(call(cwd, "migrate"), {"migrated": 0})


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--app", type=Path, required=True)
    parser.add_argument("--through", choices=("B01", "B02"), required=True)
    options = parser.parse_args()
    APP = options.app.resolve()
    THROUGH = options.through
    unittest.main(argv=[sys.argv[0]], verbosity=2)
