"""Shared black-box regression oracle, version 5B. Run against either track.

Historical storage is *never* silently rewritten by the oracle: migration is
asserted at the public CLI boundary. New fields are asserted at their stage.
"""

import argparse
from datetime import datetime
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


APP = None
ACHIEVED = set()
PROFILE = None
ROOT = Path(__file__).resolve().parent


class CountedResult(unittest.TextTestResult):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.successes = 0

    def addSuccess(self, test):
        super().addSuccess(test)
        self.successes += 1


def call(cwd, *args, error=None):
    result = subprocess.run([sys.executable, str(APP), *args], cwd=cwd, capture_output=True, text=True)
    if error is not None:
        assert result.returncode == 1 and not result.stdout, (args, result)
        assert json.loads(result.stderr) == {"error": error}, (args, result)
        return None
    assert result.returncode == 0 and not result.stderr, (args, result)
    return json.loads(result.stdout)


def row(identifier="old", priority="HIGH", due=None, status="pending"):
    return {"id": identifier, "title": identifier, "description": "x", "status": status,
            "priority": priority, "created_at": "2026-01-01T00:00:00Z", "due_date": due}


def fields():
    return set(PROFILE["fields"])


def with_defaults(record):
    """Only add defaults specified by the active schema contract, never drop fields."""
    return {**record, **{k: v for k, v in PROFILE["migration_defaults"].items() if k not in record}}


def check_task(test, task):
    test.assertEqual(set(task), fields())
    test.assertIsInstance(task["id"], str)
    test.assertTrue(task["id"].strip())
    test.assertIsInstance(task["created_at"], str)
    test.assertTrue(task["created_at"].endswith("Z"))
    test.assertEqual(datetime.fromisoformat(task["created_at"].replace("Z", "+00:00")).utcoffset().total_seconds(), 0)
    if "B02" in ACHIEVED:
        test.assertIsInstance(task["tags"], list)


def upgraded(test, cwd, payload, expected, count=1):
    path = cwd / "tasks.json"
    path.write_text(json.dumps(payload), encoding="utf-8")
    before = path.read_bytes()
    test.assertIsNone(call(cwd, "list", error="migration_required"))
    test.assertEqual(path.read_bytes(), before)
    test.assertEqual(call(cwd, "migrate"), {"migrated": count})
    rows = call(cwd, "list")
    test.assertEqual(rows, sorted(expected, key=lambda item: (item["created_at"], item["id"])))
    for task in rows:
        check_task(test, task)
    test.assertEqual(call(cwd, "migrate"), {"migrated": 0})
    return rows


class Regression(unittest.TestCase):
    def test_baseline_lifecycle_filters_failures(self):
        with tempfile.TemporaryDirectory() as folder:
            cwd = Path(folder)
            self.assertEqual(call(cwd, "list"), [])
            self.assertFalse((cwd / "tasks.json").exists())
            call(cwd, "create", "--title", "  ", "--description", "x", error="invalid_title")
            self.assertFalse((cwd / "tasks.json").exists())
            normal = call(cwd, "create", "--title", "normal", "--description", "details")
            high = call(cwd, "create", "--title", "high", "--description", "x", "--priority", "HIGH",
                        "--due-date", "2020-01-01T00:00:00Z")
            low = call(cwd, "create", "--title", "low", "--description", "x", "--priority", "LOW",
                       "--due-date", "2999-01-01T00:00:00Z")
            self.assertEqual(len({r["id"] for r in (normal, high, low)}), 3)
            for task in (normal, high, low):
                check_task(self, task)
                self.assertEqual(task["status"], "pending")
            self.assertEqual([normal["priority"], high["priority"], low["priority"]], ["NORMAL", "HIGH", "LOW"])
            self.assertIsNone(normal["due_date"])
            self.assertEqual(call(cwd, "list"), sorted((normal, high, low), key=lambda r: (r["created_at"], r["id"])))
            self.assertEqual(call(cwd, "list-high"), [high])
            self.assertEqual(call(cwd, "list-overdue"), [high])
            before = (cwd / "tasks.json").read_bytes()
            call(cwd, "create", "--title", "bad", "--description", "x", "--due-date", "yesterday", error="invalid_due_date")
            call(cwd, "complete", "--id", "missing", error="task_not_found")
            self.assertEqual((cwd / "tasks.json").read_bytes(), before)
            done = {**high, "status": "completed"}
            self.assertEqual(call(cwd, "complete", "--id", high["id"]), done)
            self.assertEqual(call(cwd, "list-overdue"), [])
            before = (cwd / "tasks.json").read_bytes()
            call(cwd, "complete", "--id", high["id"], error="invalid_transition")
            self.assertEqual((cwd / "tasks.json").read_bytes(), before)
            self.assertEqual(call(cwd, "delete", "--id", high["id"]), done)
            call(cwd, "delete", "--id", high["id"], error="task_not_found")
            self.assertEqual({r["id"] for r in call(cwd, "list")}, {normal["id"], low["id"]})

    def test_baseline_migration_corruption(self):
        for version in (1, 2):
            with self.subTest(version=version), tempfile.TemporaryDirectory() as folder:
                cwd = Path(folder)
                old = row("legacy")
                if version == 1:
                    old = {k: v for k, v in old.items() if k not in ("priority", "due_date")}
                    payload = [old]
                    expected = {**old, "priority": "NORMAL", "due_date": None}
                else:
                    old.pop("due_date")
                    payload = {"schema_version": 2, "records": [old]}
                    expected = {**old, "due_date": None}
                upgraded(self, cwd, payload, [with_defaults(expected)])
        with tempfile.TemporaryDirectory() as folder:
            cwd = Path(folder)
            valid = call(cwd, "create", "--title", "valid", "--description", "x")
            path = cwd / "tasks.json"
            version = json.loads(path.read_text(encoding="utf-8"))["schema_version"]
            for rows in ([valid, valid], [{**valid, "id": ""}]):
                path.write_text(json.dumps({"schema_version": version, "records": rows}), encoding="utf-8")
                call(cwd, "list", error="invalid_state")
            path.write_text("{broken", encoding="utf-8")
            call(cwd, "list", error="invalid_state")

    def test_baseline_overdue_fixture(self):
        with tempfile.TemporaryDirectory() as folder:
            cwd = Path(folder)
            rows = [row("past", "NORMAL", "2020-01-01T00:00:00Z"),
                    row("future", "NORMAL", "2999-01-01T00:00:00Z"), row("none", "NORMAL"),
                    row("done", "NORMAL", "2020-01-01T00:00:00Z", "completed")]
            rows = [with_defaults(r) for r in rows]
            # This is a current-schema fixture of the historical semantic scenario.
            with tempfile.TemporaryDirectory() as seed:
                probe = call(Path(seed), "create", "--title", "probe", "--description", "x")
                self.assertEqual(set(probe), fields())
                schema = json.loads((Path(seed) / "tasks.json").read_text(encoding="utf-8"))["schema_version"]
                self.assertEqual(schema, PROFILE["schema_version"])
            (cwd / "tasks.json").write_text(json.dumps({"schema_version": schema, "records": rows}), encoding="utf-8")
            self.assertEqual(call(cwd, "list-overdue"), [rows[0]])

    def test_b01_priority_and_regression(self):
        if "B01" not in ACHIEVED:
            self.skipTest("B01 not achieved")
        with tempfile.TemporaryDirectory() as folder:
            cwd = Path(folder)
            default = call(cwd, "create", "--title", "Default", "--description", "x")
            high = call(cwd, "create", "--title", "High", "--description", "x", "--priority", "HIGH")
            critical = call(cwd, "create", "--title", "Critical", "--description", "x", "--priority", "CRITICAL")
            self.assertEqual([default["priority"], high["priority"], critical["priority"]],
                             ["NORMAL", "HIGH", "CRITICAL"])
            self.assertEqual(call(cwd, "list-high"), [high])
            self.assertEqual(call(cwd, "list"), sorted((default, high, critical), key=lambda r: (r["created_at"], r["id"])))
            self.assertEqual(call(cwd, "complete", "--id", critical["id"])["status"], "completed")
            self.assertEqual(call(cwd, "list-high"), [high])
            self.assertEqual(call(cwd, "delete", "--id", critical["id"])["priority"], "CRITICAL")
            self.assertEqual(call(cwd, "list-overdue"), [])

    def test_b01_historical_priorities(self):
        if "B01" not in ACHIEVED:
            self.skipTest("B01 not achieved")
        with tempfile.TemporaryDirectory() as folder:
            cwd = Path(folder)
            rows = [row(p.lower(), p) for p in ("HIGH", "LOW", "NORMAL")]
            if PROFILE["schema_version"] > 3:
                upgraded(self, cwd, {"schema_version": 3, "records": rows},
                         [with_defaults(r) for r in rows], count=3)
            else:
                (cwd / "tasks.json").write_text(json.dumps({"schema_version": 3, "records": rows}), encoding="utf-8")
                self.assertEqual(call(cwd, "list"), sorted(rows, key=lambda r: (r["created_at"], r["id"])))
        with tempfile.TemporaryDirectory() as folder:
            rows = [row(p.lower(), p) for p in ("HIGH", "LOW", "NORMAL")]
            older = [{k: v for k, v in r.items() if k != "due_date"} for r in rows]
            upgraded(self, Path(folder), {"schema_version": 2, "records": older},
                     [with_defaults(r) for r in rows], count=3)

    def test_b02_tags_and_failure(self):
        if "B02" not in ACHIEVED:
            self.skipTest("B02 not achieved")
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
        if "B02" not in ACHIEVED:
            self.skipTest("B02 not achieved")
        for payload, expected in (({"schema_version": 3, "records": [row("critical", "CRITICAL")]},
                                   {**row("critical", "CRITICAL"), "tags": []}),
                                  ([{k: v for k, v in row().items() if k not in ("priority", "due_date")}],
                                   {**row(), "priority": "NORMAL", "tags": []})):
            with self.subTest(payload=type(payload).__name__), tempfile.TemporaryDirectory() as folder:
                upgraded(self, Path(folder), payload, [with_defaults(expected)])


def main():
    global APP, ACHIEVED, PROFILE
    parser = argparse.ArgumentParser()
    parser.add_argument("--app", type=Path, required=True)
    parser.add_argument("--achieved", default="", help="comma-separated successfully achieved request IDs")
    args = parser.parse_args()
    APP = args.app.resolve()
    ACHIEVED = set(filter(None, args.achieved.split(",")))
    ids = sorted(ACHIEVED)
    if not APP.is_file() or any(not item.startswith("B") or not item[1:].isdigit() for item in ids):
        parser.error("invalid app or achieved request set")
    profile_name = ids[-1] if ids else "baseline"
    profile_file = ROOT / "profiles" / f"{profile_name}.json"
    if not profile_file.is_file():
        parser.error("frozen schema profile missing")
    PROFILE = json.loads(profile_file.read_text(encoding="utf-8"))
    if "B02" in ACHIEVED and "B01" not in ACHIEVED:
        parser.error("B02 requires B01")
    suite = unittest.defaultTestLoader.loadTestsFromTestCase(Regression)
    # Future requests supply a frozen backend-neutral external case module and
    # schema profile before either agent sees the requirement. No runner edits.
    for item in ids:
        if int(item[1:]) <= 2:
            continue
        path = ROOT / "cases" / f"{item}.py"
        if not path.is_file():
            parser.error(f"frozen external case missing for {item}")
        spec = importlib.util.spec_from_file_location(f"regression_{item}", path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        suite.addTests(module.cases(APP, PROFILE, frozenset(ACHIEVED)))
    result = unittest.TextTestRunner(verbosity=2, resultclass=CountedResult).run(suite)
    print(json.dumps({"passed": result.successes, "failure_events": len(result.failures) + len(result.errors),
                      "skipped": len(result.skipped), "case_methods": result.testsRun,
                      "achieved": sorted(ACHIEVED)}, sort_keys=True))
    return 0 if result.wasSuccessful() else 1


if __name__ == "__main__":
    sys.exit(main())
