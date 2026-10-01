"""Capability divergence and pinned Phase 5D continuation checks for Phase 5E."""

import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

import capability_profile as cap
import phase5d
import regression_phase5e
import workspace as w
import workspace_phase5e as new


class CapabilityProfileTests(unittest.TestCase):
    def test_same_last_achieved_id_distinct_contracts(self):
        conventional = cap.compose(["B01", "B02", "B03", "B04"])
        lykoi = cap.compose(["B01", "B04"])
        self.assertEqual(conventional["schema_version"], 5)
        self.assertEqual(lykoi["schema_version"], 4)
        self.assertEqual(set(conventional["fields"]) - set(lykoi["fields"]), {"tags"})
        self.assertEqual(conventional["migration_defaults"]["tags"], [])
        self.assertEqual(conventional["migration_defaults"]["source"], "")
        self.assertNotIn("tags", lykoi["migration_defaults"])
        self.assertEqual(lykoi["migration_defaults"]["source"], "")
        self.assertEqual(cap.compose(["B01"])["schema_version"], 3)
        self.assertEqual(cap.compose(["B01", "B02", "B03"])["schema_version"], 4)

    def test_dependency_and_order_are_explicit(self):
        for invalid in (["B03"], ["B01", "B03"], ["B04", "B01"], ["B01", "B01"]):
            with self.subTest(invalid=invalid), self.assertRaises(w.ProtocolError):
                cap.compose(invalid)
        self.assertNotEqual(cap.identity(["B01", "B04"])["expectation_sha256"],
                            cap.identity(["B01", "B02", "B03", "B04"])["expectation_sha256"])

    def test_conflicting_fragment_fails_closed_and_changes_are_pinned(self):
        pinned = cap.identity(["B01", "B04"])
        with tempfile.TemporaryDirectory(prefix="lykoi-capability-") as folder:
            target = Path(folder)
            for name in ("B01", "B02", "B03", "B04"):
                (target / f"{name}.json").write_bytes((cap.FRAGMENTS / f"{name}.json").read_bytes())
            with patch.object(cap, "FRAGMENTS", target):
                source = target / "B04.json"
                fragment = json.loads(source.read_text(encoding="utf-8"))
                fragment["add_fields"] = {"tags": {"default": [], "type": "list"}}
                source.write_text(json.dumps(fragment), encoding="utf-8")
                with self.assertRaisesRegex(w.ProtocolError, "conflicting"):
                    cap.compose(["B01", "B02", "B04"])
                fragment["add_fields"] = {"source": {"default": "", "type": "str"}}
                fragment["change_defaults"] = {"tags": {"from": ["wrong"], "to": []}}
                source.write_text(json.dumps(fragment), encoding="utf-8")
                with self.assertRaisesRegex(w.ProtocolError, "conflicting"):
                    cap.compose(["B01", "B02", "B04"])
                fragment.pop("change_defaults")
                fragment["add_fields"]["source"]["default"] = "changed"
                source.write_text(json.dumps(fragment), encoding="utf-8")
                self.assertNotEqual(pinned["expectation_sha256"],
                                    cap.identity(["B01", "B04"])["expectation_sha256"])
                self.assertNotEqual(pinned["capability_hashes"]["B04"],
                                    cap.fragment_hashes(["B01", "B04"])["B04"])

    def test_bridge_is_pure_and_retains_actual_history(self):
        for track in new.BRIDGE:
            with self.subTest(track=track):
                name, expected, snapshot, snapshot_hash = new.BRIDGE[track]
                before = w.file_hash(new.PHASE5D / name)
                result = new.bridge(track)
                self.assertEqual(before, expected)
                self.assertEqual(w.file_hash(new.PHASE5D / snapshot), snapshot_hash)
                self.assertEqual(result["previous_checkpoint_sha256"], expected)
                self.assertEqual(result["achieved"], ["B01"] if track == "axiom"
                                 else ["B01", "B02", "B03"])
                self.assertEqual(result["attempted"][-1]["outcome"],
                                 "BLOCKED_BY_GAP" if track == "axiom" else "SUCCESS")
                self.assertEqual(new.validate_record(result), result)
                tampered = {**result, "achieved": ["B01", "B02", "B03"]}
                if track == "axiom":
                    with self.assertRaises(w.ProtocolError):
                        new.validate_record(tampered)
                self.assertEqual(w.file_hash(new.PHASE5D / name), before)

    def test_explicit_supersession_skips_only_named_old_method(self):
        class Historical(unittest.TestCase):
            def test_superseded(self):
                self.fail("old requirement assertion")

            def test_still_applicable(self):
                self.assertTrue(True)

        suite = unittest.defaultTestLoader.loadTestsFromTestCase(Historical)
        case_id = next(test.id() for test in suite if test._testMethodName == "test_superseded")
        with self.assertRaises(w.ProtocolError):
            regression_phase5e.mark_superseded(suite, {"absent.case": {
                "reason": "replaced", "replacement": "B11", "origin": "baseline"}})
        regression_phase5e.mark_superseded(suite, {case_id: {
            "reason": "completed delete changed", "replacement": "B11", "origin": "baseline"}})
        result = unittest.TestResult()
        suite.run(result)
        self.assertEqual(result.testsRun, 2)
        self.assertEqual(len(result.skipped), 1)
        self.assertIn("B11", result.skipped[0][1])
        self.assertFalse(result.failures or result.errors)
        profile = {"superseded_cases": {
            case_id: {"reason": "changed", "replacement": "B16", "origin": "B03"}}}
        self.assertEqual(regression_phase5e.active_supersessions(profile, ["B01", "B16"]), {})
        self.assertEqual(regression_phase5e.active_supersessions(profile, ["B01", "B03", "B16"]),
                         profile["superseded_cases"])

    def test_read_only_validation_of_both_continuation_states(self):
        with tempfile.TemporaryDirectory(prefix="lykoi-phase5e-") as folder:
            parent = Path(folder)
            for track in new.BRIDGE:
                with self.subTest(track=track):
                    name, _, snapshot, snapshot_hash = new.BRIDGE[track]
                    result = new.bridge(track)
                    work = parent / track
                    w.restore(track, work, result, new.PHASE5D / snapshot, snapshot_hash)
                    checkpoint = parent / f"{track}.json"
                    checkpoint.write_bytes(w.encoded(result))
                    before = w.workspace_files(work)
                    app = (work / "generated/task_manager.py" if track == "axiom"
                           else work / "benchmark/conventional/task_manager.py")
                    self.assertEqual(phase5d.run(work, [sys.executable, "-B",
                        str(Path(new.__file__).with_name("regression_phase5e.py")),
                        "--app", str(app), "--achieved", ",".join(result["achieved"]),
                        "--expectation-hash", result["expectation_sha256"],
                        "--checkpoint", str(checkpoint), "--expected-hash", w.file_hash(checkpoint)], True), 0)
                    if track == "axiom":
                        command = [sys.executable, "-B", "-m", "unittest", "discover", "-s", "tests", "-v"]
                    else:
                        command = [sys.executable, "-B", "-m", "unittest", "discover",
                                   "-s", "benchmark/conventional", "-v"]
                    self.assertEqual(phase5d.run(work, command, True), 0)
                    self.assertEqual(w.workspace_files(work), before)

    def test_new_checkpoint_requires_pinned_predecessor_and_gap_is_unchanged(self):
        with tempfile.TemporaryDirectory(prefix="lykoi-phase5e-") as folder:
            parent = Path(folder)
            prior = new.bridge("axiom")
            pinned = parent / "prior.json"
            pinned.write_bytes(w.encoded(prior))
            source = new.PHASE5D / new.BRIDGE["axiom"][2]
            work = parent / "work"
            w.restore("axiom", work, prior, source, new.BRIDGE["axiom"][3])
            attempted = [*prior["attempted"], {"request": "B04", "outcome": "BLOCKED_BY_GAP",
                                                  "depends_on": ["B02"]}]
            cases = parent / "disposable-cases"
            cases.mkdir()
            (cases / "B03.py").write_bytes((w.CASES / "B03.py").read_bytes())
            (cases / "B04.py").write_text("# disposable checkpoint-test fixture\n", encoding="utf-8")
            with patch.object(w, "CASES", cases):
                result = new.checkpoint(work, "axiom", attempted, pinned, w.file_hash(pinned))
                self.assertEqual(result["files"], prior["files"])
                self.assertEqual(result["achieved"], ["B01"])
                with self.assertRaises(w.ProtocolError):
                    new.checkpoint(work, "axiom", attempted, pinned, "0" * 64)
                (work / "unexplained.log").write_text("unexpected", encoding="utf-8")
                with self.assertRaises(w.ProtocolError):
                    new.checkpoint(work, "axiom", attempted, pinned, w.file_hash(pinned))


if __name__ == "__main__":
    unittest.main()
