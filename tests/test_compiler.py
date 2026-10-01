import copy
from pathlib import Path
import sys
import unittest


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from air_compiler.generator import HEADER, generate
from air_compiler.model import Program
from air_compiler.parser import AirError, load, parse
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
        self.doc["behaviors"][2]["assignments"][0]["field"] = "field_id"
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

    def test_parser_rejects_duplicate_keys(self):
        with self.assertRaisesRegex(AirError, "duplicate JSON key"):
            parse('{"air_version": "0.1", "air_version": "0.2"}')


if __name__ == "__main__":
    unittest.main()
