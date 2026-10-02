"""Exact B01 intermediate-state and state-relative carrier fixtures."""

import ast
import copy
import inspect
import textwrap
import unittest
from unittest.mock import patch

import acceptance_inventory_r5_3 as isolated
import assertion_preservation_r5_2_1 as prior
import assertion_preservation_r5_2_2 as correction
import capability_profile_r5_2 as profiles
import regression as original
import regression_phase5c_r5_1 as parent
import workspace as w


EARLY = ["B01", "B04"]
LATE = [f"B{i:02}" for i in range(1, 17)]


def composed(achieved):
    with isolated.isolated_construction():
        replacements = parent.load_module("regression_B16_R5", parent.CASE)
        suite, _, dispositions, inventory = correction.build_suite(
            w.ROOT / "benchmark/conventional/task_manager.py", profiles.compose(achieved),
            achieved, replacements, mark_skips=False)
        return suite, dispositions, inventory


class ExactPrecondition(unittest.TestCase):
    def test_active_carriers_and_lineage_follow_acceptance_state(self):
        for achieved, expected in ((EARLY, False), (LATE, True)):
            with self.subTest(achieved=achieved):
                suite, dispositions, inventory = composed(achieved)
                ids = [test.id() for test in isolated.instances(suite)]
                self.assertEqual(sum(name == correction.OLD_ID for name in ids), 0)
                self.assertEqual(sum(name.endswith("Correction." + correction.METHOD)
                                     for name in ids), int(expected))
                self.assertEqual(correction.selection(dispositions),
                                 [correction.METHOD] if expected else [])
                self.assertEqual(set(inventory), set(prior.ORIGINS) if expected else set())
                if expected:
                    row = inventory[correction.ROOT]
                    self.assertEqual(row["original_carrier"], prior.PRIORITY)
                    self.assertEqual(row["original_source"], prior.ORIGINS[correction.ROOT][1])
                    self.assertEqual(row["chain"], [prior.PRIORITY, "B11:omitted",
                                                    correction.OLD_ID, ids[-1]])
                    self.assertEqual(row["incomplete_carrier"], correction.OLD_ID)
                    self.assertEqual({key: value for key, value in inventory.items()
                                      if key != correction.ROOT},
                                     {key: value for key, value in prior.inventory(
                                         dispositions, profiles.compose(achieved)).items()
                                      if key != correction.ROOT})
                else:
                    self.assertIn("regression.Regression.test_b01_priority_and_regression", ids)
                for label in ("conventional", "lykoi", "arbitrary"):
                    self.assertEqual(correction.selection(copy.deepcopy(
                        {"track": label, "history": dispositions})["history"]),
                        correction.selection(dispositions))

    def test_original_setup_and_observation_match_canonical_root(self):
        original_body = ast.parse(textwrap.dedent(inspect.getsource(
            original.Regression.test_b01_priority_and_regression))).body[0]
        suite, _, inventory = composed(LATE)
        corrected = next(test for test in isolated.instances(suite)
                         if test._testMethodName == correction.METHOD)
        corrected_body = ast.parse(textwrap.dedent(inspect.getsource(
            getattr(type(corrected), correction.METHOD)))).body[0]
        def semantic_calls(body):
            return [(node.func.attr if isinstance(node.func, ast.Attribute) else node.func.id,
                     [ast.unparse(arg) for arg in node.args])
                    for node in ast.walk(body) if isinstance(node, ast.Call)
                    and ((isinstance(node.func, ast.Attribute) and node.func.attr in ("create", "call"))
                         or isinstance(node.func, ast.Name) and node.func.id == "call")]
        source = semantic_calls(original_body)
        target = semantic_calls(corrected_body)
        # Original uses global call for create; compare the exact command
        # arguments for the three creates and both observations in source order.
        source_creates = [args[2:] for _, args in source if len(args) > 1 and args[1] == "'create'"]
        target_creates = [args[1:] for name, args in target if name == "create"]
        self.assertEqual(source_creates, target_creates)
        self.assertEqual(inventory[correction.ROOT]["precondition"], {
            "create_order": ["NORMAL", "HIGH", "CRITICAL"],
            "at_list_high": {"NORMAL": "pending", "HIGH": "pending", "CRITICAL": "completed"}})

    def test_observation_sees_pending_normal_and_high_completed_critical(self):
        suite, _, _ = composed(LATE)
        test = next(item for item in isolated.instances(suite)
                    if item._testMethodName == correction.METHOD)
        state = {}
        observations = []

        def call(self, cwd, command, *args):
            if command == "create":
                title = args[args.index("--title") + 1]
                priority = args[args.index("--priority") + 1] if "--priority" in args else "NORMAL"
                row = {"id": title, "title": title, "priority": priority,
                       "status": "pending", "created_at": f"2020-01-0{len(state) + 1}T00:00:00Z"}
                state[title] = row
                return row.copy()
            if command == "complete":
                state[args[args.index("--id") + 1]]["status"] = "completed"
                return state["Critical"].copy()
            if command == "list":
                return [row.copy() for row in state.values()]
            if command == "list-high":
                observations.append({key: value["status"] for key, value in state.items()})
                return [row.copy() for row in state.values()
                        if row["priority"] == "HIGH" and row["status"] == "pending"]
            self.fail(command)

        with patch.object(type(test), "call", call):
            getattr(test, correction.METHOD)()
        self.assertEqual(observations[-1], {"Default": "pending", "High": "pending",
                                            "Critical": "completed"})
        self.assertEqual(len(observations), 2)

    def test_unknown_supersession_fails_closed(self):
        _, states, _ = composed(EARLY)
        states[prior.PRIORITY] = {"state": "superseded", "replacement": "unknown",
                                  "origin": "B01"}
        with self.assertRaises(w.ProtocolError):
            correction.selection(states)


if __name__ == "__main__":
    unittest.main()
