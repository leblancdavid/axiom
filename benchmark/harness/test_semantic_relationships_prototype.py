"""Prospective fixtures; do not alter the frozen R5.2.2 parent."""

import copy
from datetime import datetime, timezone
import tarfile
import tempfile
from pathlib import Path
import unittest

from benchmark.semantic import format as semantic
from benchmark.semantic import probe, relationships


def record(key, origin, requires, depends=(), replaces=()):
    return {"id": key, "origin": origin,
            "when": {"requires": requires, "forbids": []},
            "depends_on": list(depends), "replaces": list(replaces)}


REGISTRY = [
    record("BASELINE.deletion", "BASELINE", []),
    record("B01.deletion", "B01", ["B01"], replaces=["BASELINE.deletion"]),
    record("B01.priority", "B01", ["B01"]),
    record("B04.other", "B04", ["B04"], depends=["B01.priority"]),
    record("B11.deletion", "B11", ["B11"], replaces=["BASELINE.deletion"]),
    record("B16.users", "B16", ["B16"]),
    record("B17.roles", "B17", ["B16", "B17"], depends=["B16.users"]),
]


def clock_document():
    now = {"clock_ref": "now"}
    def offset(seconds):
        return {"offset": {"from": now, "seconds": seconds}}
    def before(key, actual, result):
        return {"observe": {"id": key, "relation": "before", "actual": actual,
                            "expected": now, "result": result}}
    return {"version": semantic.VERSION, "status": "prototype", "scenarios": [{
        "id": "B12.utc_strict_boundary",
        "origin": {"requirement": "B12", "source": "benchmark/requirements/B12.md",
                   "note": "Typed fixed-clock relation fixture; no application witness."},
        "lineage": {"kind": "adds", "prior": []},
        "variants": [{"id": "controlled", "when": {"requires": ["B12"], "forbids": []},
                      "steps": [
                          {"clock": {"bind": "now", "source": "utc_now"}},
                          before("B12.past", offset(-1), True),
                          before("B12.equal", offset(0), False),
                          before("B12.future", offset(1), False),
                          {"observe": {"id": "B12.same_binding", "relation": "equals",
                                       "actual": now, "expected": now}},
                      ]}]}]}


class ClockVocabulary(unittest.TestCase):
    def test_strict_boundary_and_one_clock_read(self):
        doc = semantic.validate(clock_document())
        calls = []
        def clock():
            calls.append(1)
            return datetime(2026, 1, 1, tzinfo=timezone.utc)
        probe.run_variant(None, semantic.compile_plan(doc, ["B12"])[0], clock=clock)
        self.assertEqual(calls, [1])

    def test_clock_requires_controlled_adapter(self):
        plan = semantic.compile_plan(clock_document(), ["B12"])[0]
        with self.assertRaisesRegex(semantic.FormatError, "controlled clock required"):
            probe.run_variant(None, plan)

    def test_before_requires_instants(self):
        bad = clock_document()
        bad["scenarios"][0]["variants"][0]["steps"][1]["observe"]["actual"] = {
            "literal": "2020-01-01T00:00:00Z"}
        with self.assertRaisesRegex(semantic.FormatError, "two typed instants"):
            semantic.validate(bad)

    def test_undeclared_clock_fails(self):
        bad = clock_document()
        bad["scenarios"][0]["variants"][0]["steps"][1]["observe"]["expected"] = {
            "clock_ref": "missing"}
        with self.assertRaisesRegex(semantic.FormatError, "undeclared clock reference"):
            semantic.validate(bad)

    def test_instant_projection_requires_utc(self):
        bad = clock_document()
        bad["scenarios"][0]["variants"][0]["steps"][1]["observe"]["actual"] = {
            "instant": {"literal": "2020-01-01T00:00:00+01:00"}}
        with self.assertRaisesRegex(semantic.FormatError, "UTC timestamp"):
            semantic.validate(bad)

    def test_b12_entity_due_instants_and_query_plan_share_app_clock(self):
        doc = clock_document()
        steps = doc["scenarios"][0]["variants"][0]["steps"]
        now = {"clock_ref": "now"}
        for title, seconds, binding in (("past", -1, "past_task"),
                                        ("equal", 0, "equal_task"),
                                        ("future", 1, "future_task")):
            steps.append({"invoke": {"command": "create", "args": [
                {"literal": "--title"}, {"literal": title},
                 {"literal": "--description"}, {"literal": "x"},
                 {"literal": "--priority"}, {"literal": "HIGH"},
                 {"literal": "--owner"}, {"literal": "system"},
                 {"literal": "--due-date"},
                {"offset": {"from": now, "seconds": seconds}}], "bind": binding}})
            steps.append({"observe": {"id": f"B12.{title}_due_relation",
                                      "relation": "before",
                                      "actual": {"instant": {"ref": f"{binding}.due_date"}},
                                      "expected": now, "result": seconds < 0}})
        steps.append({"invoke": {"command": "list-urgent", "args": [], "bind": "urgent"}})
        steps.append({"observe": {"id": "B12.strict_urgent_result",
                                  "relation": "equals", "actual": {"ref": "urgent"},
                                  "expected": {"list": [{"ref": "past_task"}]}}})
        steps.append({"observe": {"id": "B12.application_clock_is_semantic_clock",
                                  "relation": "equals",
                                  "actual": {"instant": {"ref": "past_task.created_at"}},
                                  "expected": now}})
        semantic.validate(doc)
        instant = datetime(2026, 1, 1, tzinfo=timezone.utc)
        name, sha, member, _ = probe.SNAPSHOTS["conventional"]
        with tarfile.open(probe.RESULTS / name) as archive, tempfile.TemporaryDirectory() as folder:
            app = Path(folder) / "app.py"
            app.write_bytes(archive.extractfile(member).read())
            plan = semantic.compile_plan(doc, ["B12"])[0]
            for _ in range(2):
                probe.run_variant(app, plan, clock=lambda: instant, application_clock=instant)
            with self.assertRaisesRegex(semantic.FormatError, "controlled clock required"):
                probe.run_variant(app, plan)
            with self.assertRaisesRegex(semantic.FormatError, "mismatched application clock"):
                probe.run_variant(app, plan, clock=lambda: instant,
                                  application_clock=datetime(2026, 1, 2, tzinfo=timezone.utc))


class CheckedRelationships(unittest.TestCase):
    def test_state_relative_root_and_unaffected_clauses(self):
        full = relationships.compose(REGISTRY, ["B01", "B04", "B11", "B16", "B17"])
        self.assertEqual(full["BASELINE.deletion"], "B11.deletion")
        self.assertEqual(full["B04.other"], "B04.other")
        self.assertEqual(full["B17.roles"], "B17.roles")
        early = relationships.compose(REGISTRY, ["B01", "B04"])
        self.assertEqual(early["BASELINE.deletion"], "B01.deletion")
        self.assertNotIn("B17.roles", early.values())

    def test_unknown_and_malformed_targets_fail(self):
        for field in ("depends_on", "replaces"):
            bad = copy.deepcopy(REGISTRY)
            bad[-1][field] = ["B99.unknown"]
            with self.assertRaises(semantic.FormatError):
                relationships.validate(bad)
            bad[-1][field] = ["not a valid ID"]
            with self.assertRaises(semantic.FormatError):
                relationships.validate(bad)

    def test_missing_active_dependency_fails(self):
        with self.assertRaisesRegex(semantic.FormatError, "missing active dependency"):
            relationships.compose(REGISTRY, ["B04"])

    def test_inactive_replacement_fails(self):
        bad = copy.deepcopy(REGISTRY)
        bad.append(record("B15.change", "B15", ["B15"], replaces=["B16.users"]))
        with self.assertRaisesRegex(semantic.FormatError, "prior semantic root"):
            relationships.validate(bad)
        bad[-1] = record("B17.change", "B17", ["B17"], replaces=["B16.users"])
        with self.assertRaisesRegex(semantic.FormatError, "inactive replacement root"):
            relationships.compose(bad, ["B17"])

    def test_duplicate_active_replacement_fails(self):
        bad = copy.deepcopy(REGISTRY)
        bad.append(record("B11.conflict", "B11", ["B11"],
                          replaces=["BASELINE.deletion"]))
        with self.assertRaisesRegex(semantic.FormatError, "duplicate active replacement"):
            relationships.compose(bad, ["B01", "B11"])

    def test_cycle_fails(self):
        bad = copy.deepcopy(REGISTRY)
        bad[-1]["depends_on"] = ["B17.other"]
        bad.append(record("B17.other", "B17", ["B17"], depends=["B17.roles"]))
        with self.assertRaisesRegex(semantic.FormatError, "cyclic semantic dependency"):
            relationships.validate(bad)


if __name__ == "__main__":
    unittest.main()
