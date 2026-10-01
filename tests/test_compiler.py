import copy
import hashlib
import json
from pathlib import Path
import sys
import unittest


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from air_compiler.generator import HEADER, VERSION, generate
from air_compiler.model import Program
from air_compiler.parser import AirError, load, parse
from air_compiler.semantics import diff, inspect
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
        manifest = json.loads((ROOT / "generated" / "task_manager.manifest.json").read_text(encoding="utf-8"))
        self.assertEqual(manifest["compiler_version"], VERSION)
        self.assertEqual(manifest["model_version"], "0.2")
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


if __name__ == "__main__":
    unittest.main()
