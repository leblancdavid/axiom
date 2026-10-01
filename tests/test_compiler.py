import copy
from contextlib import redirect_stdout
import hashlib
from io import StringIO
import json
from pathlib import Path
import sys
import unittest
import tempfile


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from air_compiler.generator import HEADER, VERSION, generate
from air_compiler.model import Program
from air_compiler.parser import AirError, load, parse
from air_compiler.semantics import diff, inspect, impact, safety
from air_compiler.planning import evaluate, blob_hash
from air_compiler.cli import main
from air_compiler.validator import validate


class CompilerTests(unittest.TestCase):
    def setUp(self):
        self.doc = copy.deepcopy(load(ROOT / "air" / "task_manager.json").document)

    def invalid(self, expected):
        with self.assertRaisesRegex(AirError, expected):
            validate(Program(self.doc))

    def test_valid_and_deterministic(self):
        program = validate(Program(self.doc))
        generated = generate(program)
        self.assertEqual(generated, generate(program))
        self.assertTrue(generated.startswith(HEADER))
        self.assertEqual(generated, (ROOT / "generated" / "task_manager.py").read_text(encoding="utf-8"))

    def test_missing_and_duplicate_ids(self):
        del self.doc["behaviors"][0]["reads"]
        self.invalid("fn_create: missing")
        self.doc = copy.deepcopy(load(ROOT / "air" / "task_manager.json").document)
        self.doc["behaviors"][1]["id"] = "fn_create"
        self.invalid("duplicate or invalid ID")

    def test_dangling_reference(self):
        self.doc["behaviors"][0]["assignments"][1]["id"] = "arg_missing"
        self.invalid("nonexistent reference")

    def test_incompatible_type_and_mutation(self):
        self.doc["behaviors"][0]["assignments"][3]["value"] = "unknown"
        self.invalid("invalid enum literal")
        self.doc = copy.deepcopy(load(ROOT / "air" / "task_manager.json").document)
        self.doc["behaviors"][3]["assignments"][0]["field"] = "field_id"
        self.invalid("invalid state mutation")

    def test_undeclared_effect_and_dependency(self):
        self.doc["behaviors"][0]["effects"].remove("clock_read")
        self.invalid("fn_create.effects")
        self.doc = copy.deepcopy(load(ROOT / "air" / "task_manager.json").document)
        self.doc["behaviors"][0]["dependencies"].remove("cap_ids")
        self.invalid("fn_create.dependencies")

    def test_impossible_contract(self):
        self.doc["behaviors"][0]["guarantees"][0]["value"] = "completed"
        self.invalid("impossible or unproven")

    def test_index_and_diff(self):
        current = validate(Program(self.doc))
        old = validate(load(ROOT / "experiments" / "task_manager-v0.2-before-priority.json"))
        report = diff(old, current)
        self.assertIn("field_priority", [c["entity_id"] for c in report["changes"] if c["change"] == "added"])
        self.assertIn("fn_list_high", report["affected"])
        self.assertIn("field_priority", report["affected"]["fn_list_high"]["via"])
        self.assertIn({"relation": "filters_by", "id": "field_priority"}, inspect(current, "fn_list_high")["dependencies"])

    def test_invalid_filter_migration_and_contract_identity(self):
        self.doc["behaviors"][2]["filter"]["field"] = "field_missing"
        self.invalid("nonexistent reference")
        self.doc = copy.deepcopy(load(ROOT / "air" / "task_manager.json").document)
        self.doc["migrations"][0]["to_version"] = 3
        self.invalid("invalid migration versions")
        self.doc = copy.deepcopy(load(ROOT / "air" / "task_manager.json").document)
        self.doc["behaviors"][0]["guarantees"][0]["id"] = "field_priority"
        self.invalid("duplicate or invalid ID")

    def test_optional_enum_and_effects_are_validated(self):
        self.doc["behaviors"][0]["assignments"][4]["value"] = "URGENT"
        self.invalid("invalid enum literal")
        self.doc = copy.deepcopy(load(ROOT / "air" / "task_manager.json").document)
        self.doc["behaviors"][2]["effects"].remove("state_read")
        self.invalid("fn_list_high.effects")

    def test_manifest_and_schema(self):
        json.loads((ROOT / "schema" / "axiom-v0.2.schema.json").read_text(encoding="utf-8"))
        schema = json.loads((ROOT / "schema" / "axiom-v0.3.schema.json").read_text(encoding="utf-8"))
        self.assertIn("state_machines", schema["required"])
        manifest = json.loads((ROOT / "generated" / "task_manager.manifest.json").read_text(encoding="utf-8"))
        self.assertEqual(manifest["compiler_version"], VERSION)
        self.assertEqual(manifest["model_version"], "0.3")
        self.assertIn("ax:transition:task_complete", manifest["artifacts"][0]["entity_ids"])
        self.assertEqual(manifest["artifacts"][0]["sha256"], hashlib.sha256(generate(Program(self.doc)).encode()).hexdigest())
        self.assertIn("field_priority", manifest["artifacts"][0]["entity_ids"])

    def test_renaming_preserves_identity(self):
        old = validate(Program(copy.deepcopy(self.doc)))
        self.doc["types"][2]["name"] = "WorkItem"
        report = diff(old, validate(Program(self.doc)))
        self.assertEqual([c for c in report["changes"] if c["entity_id"] == "type_task"],
                         [{"entity_id": "type_task", "kind": "type", "change": "modified", "attributes": ["name"]}])

    def test_parser_rejects_duplicate_keys(self):
        with self.assertRaisesRegex(AirError, "duplicate JSON key"):
            parse('{"air_version": "0.1", "air_version": "0.2"}')

    def test_impact_paths_and_clock_validation(self):
        graph = impact(Program(self.doc), "type_task")
        paths = {item["id"]: item["path"] for item in graph["impacts"]}
        self.assertEqual(paths["cmd_list"][0]["relation"], "exposes")
        self.assertEqual(paths["state_tasks"][-1]["to"], "type_task")
        self.assertNotIn("field_title", paths)
        overdue = next(b for b in self.doc["behaviors"] if b["id"] == "fn_list_overdue")
        overdue["effects"].remove("clock_read")
        self.invalid("fn_list_overdue.effects")

    def test_manifest_provenance_is_artifact_wide(self):
        output = StringIO()
        with redirect_stdout(output):
            result = main(["impact", str(ROOT / "air" / "task_manager.json"), "field_due_date",
                           "--manifest", str(ROOT / "generated" / "task_manager.manifest.json")])
        self.assertEqual(result, 0)
        provenance = json.loads(output.getvalue())["artifact_provenance"]
        self.assertEqual(provenance[0]["scope"], "artifact-wide")
        self.assertEqual(provenance[0]["via_entity_id"], "field_due_date")

    def test_plan_fails_without_mutating_model(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "model.json"
            data = json.dumps(self.doc).encode()
            path.write_bytes(data)
            plan = {"id": "bad", "intent": "remove state", "model": str(path), "baseline": blob_hash(data),
                    "operations": [{"op": "remove", "id": "state_tasks"}], "anticipated_impacts": [],
                    "verification": {"preserve": [], "add": []}}
            report, candidate = evaluate(plan)
            self.assertIsNone(candidate)
            self.assertTrue(any(d["severity"] == "ERROR" for d in report["diagnostics"]))
            self.assertEqual(path.read_bytes(), data)

    def test_plan_rejects_duplicate_and_stale_baseline(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "model.json"
            data = json.dumps(self.doc).encode()
            path.write_bytes(data)
            plan = {"id": "bad", "intent": "add duplicate command", "model": str(path), "baseline": blob_hash(data),
                    "operations": [{"op": "add", "group": "commands", "value": {"id": "cmd_create"}}],
                    "anticipated_impacts": [], "verification": {"preserve": ["existing tests"], "add": []}}
            report, candidate = evaluate(plan)
            self.assertIsNone(candidate)
            self.assertTrue(any("duplicate ID" in d["message"] for d in report["diagnostics"]))
            plan["baseline"] = "wrong"
            report, _ = evaluate(plan)
            self.assertTrue(any("baseline" in d["message"] for d in report["diagnostics"]))

    def test_lifecycle_rejects_unmodeled_and_inconsistent_changes(self):
        complete = next(b for b in self.doc["behaviors"] if b["id"] == "fn_complete")
        del complete["performs"]
        self.invalid("does not perform transition")
        complete["performs"] = "ax:transition:task_complete"
        complete["assignments"][0]["value"] = "pending"
        self.invalid("mismatched transition")
        complete["assignments"][0]["value"] = "completed"
        self.doc["transitions"][0]["source"] = "completed"
        self.invalid("unreachable lifecycle states")

    def test_transition_references_and_guard(self):
        self.doc["transitions"][0]["target"] = "MISSING"
        self.invalid("unknown lifecycle state")
        self.doc["transitions"][0]["target"] = "completed"
        self.doc["transitions"][0]["guard"] = "unknown"
        self.invalid("source guard missing")
        self.doc["transitions"][0]["guard"] = "pre_complete_pending"
        self.doc["transitions"][0]["trigger"] = "missing_behavior"
        self.invalid("nonexistent reference")

    def test_least_authority_for_behaviors_and_migrations(self):
        overdue = next(b for b in self.doc["behaviors"] if b["id"] == "fn_list_overdue")
        overdue["requires"].append("cap_task_write")
        self.invalid("capability violation")
        overdue["requires"].remove("cap_task_write")
        overdue["requires"].remove("cap_clock")
        self.invalid("capability violation")
        overdue["requires"].append("cap_clock")
        self.doc["migrations"][0]["requires"].remove("cap_task_write")
        self.invalid("migration_task_priority.requires")

    def test_predicates_safety_and_impact(self):
        report = safety(Program(self.doc))
        self.assertEqual(report["declared_transitions"], 1)
        self.assertEqual(report["capability_violations"], 0)
        self.assertEqual(report["evidence_counts"]["UNVERIFIED"], 0)
        self.assertIn("inv_status", next(m for m in report["mutations"] if m["behavior"] == "fn_complete")["relevant_invariants"])
        self.assertEqual(next(f for f in report["findings"] if f["id"] == "inv_overdue_excludes_completed")["evidence"], "STRUCTURALLY_GUARANTEED")
        graph = impact(Program(self.doc), "ax:transition:task_complete")
        self.assertEqual(next(i for i in graph["impacts"] if i["id"] == "fn_complete")["semantic_classification"], "TRANSITION_IMPACT")
        self.doc["invariants"][-2]["predicate"]["values"] = ["LOW"]
        self.invalid("IN must enumerate")

    def test_safety_cli(self):
        output = StringIO()
        with redirect_stdout(output):
            self.assertEqual(main(["safety", str(ROOT / "air" / "task_manager.json")]), 0)
        report = json.loads(output.getvalue())
        self.assertEqual(report["state_machines"], 1)
        self.assertEqual(report["protected_resources"], 1)
        self.assertEqual(report["evidence_counts"]["SCENARIO_VERIFIED"], 0)

    def test_plan_rejects_unauthorized_change_before_generation(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "model.json"
            data = json.dumps(self.doc).encode()
            path.write_bytes(data)
            plan = {"id": "unauthorized", "intent": "remove write authority", "model": str(path), "baseline": blob_hash(data),
                    "operations": [{"op": "set", "id": "fn_complete", "path": ["requires"], "value": ["cap_task_read"]}],
                    "anticipated_impacts": ["fn_complete"], "verification": {"preserve": ["lifecycle"], "add": []}}
            report, candidate = evaluate(plan)
            self.assertIsNone(candidate)
            self.assertTrue(any("capability violation" in d["message"] for d in report["diagnostics"]))
            self.assertEqual(path.read_bytes(), data)


if __name__ == "__main__":
    unittest.main()
