"""Lykoi protocol amendment integration checks on disposable continuation copies."""

import json
from pathlib import Path
import shutil
import sys
import tempfile
import unittest

import phase5d
import workspace as w


class CleanCheckpointTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        root = w.ROOT / "benchmark/results/phase5d"
        cls.lykoi = json.loads((root / "checkpoint-lykoi-B03.json").read_text(encoding="utf-8"))
        cls.conventional = json.loads((root / "checkpoint-conventional-B03.json").read_text(encoding="utf-8"))

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(prefix="lykoi-integrity-")
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.work = self.root / "work"
        source = w.ROOT / "benchmark/results/phase5d/snapshot-lykoi-B03.tar"
        w.restore("axiom", self.work, self.lykoi, source, w.file_hash(source))

    def test_validation_and_external_ephemera_do_not_mutate_work(self):
        before = w.workspace_files(self.work)
        self.assertEqual(phase5d.run(self.work, [sys.executable, "-m", "air_compiler.cli", "validate",
                                                  "air/task_manager.json"], True), 0)
        self.assertEqual(before, w.workspace_files(self.work))
        self.assertEqual(phase5d.run(self.work, [sys.executable, "-c",
            "import os,pathlib; pathlib.Path(os.environ['TMP']).joinpath('tool.log').write_text('scratch')"], True), 0)
        self.assertEqual(before, w.workspace_files(self.work))

    def test_application_model_fixture_and_generated_output_are_detected(self):
        for name in ("air/task_manager.json", "experiments/task_manager-v0.2-before-priority.json",
                     "generated/task_manager.py", "generated/task_manager.manifest.json"):
            with self.subTest(file=name):
                probe = self.root / name.replace("/", "-")
                shutil.copytree(self.work, probe)
                target = probe / name
                target.write_bytes(target.read_bytes() + b"\n")
                self.assertNotEqual(w.workspace_files(probe), self.lykoi["files"])
                with self.assertRaises(w.ProtocolError):
                    w.checkpoint(probe, "axiom", self.lykoi["attempted"],
                                 json.loads((w.ROOT / "benchmark/results/phase5b/checkpoint-axiom-B02.json").read_text()),
                                 phase5d.PINS["axiom"]["prior"][1])

    def test_conventional_source_and_new_generated_file_are_detected(self):
        source = w.ROOT / "benchmark/results/phase5d/snapshot-conventional-B03.tar"
        probe = self.root / "conventional"
        w.restore("conventional", probe, self.conventional, source, w.file_hash(source))
        target = probe / "benchmark/conventional/task_manager.py"
        target.write_bytes(target.read_bytes() + b"\n")
        self.assertNotEqual(w.workspace_files(probe), self.conventional["files"])
        target.write_bytes(target.read_bytes()[:-1])
        generated = probe / "benchmark/conventional/compiled-implementation.bin"
        generated.write_bytes(b"implementation decision")
        self.assertIn("benchmark/conventional/compiled-implementation.bin", w.workspace_files(probe))
        self.assertNotEqual(w.workspace_files(probe), self.conventional["files"])

    def test_import_caches_are_rejected_not_hidden(self):
        directory = self.work / "src/air_compiler/__pycache__"
        directory.mkdir()
        (directory / "validator.cpython-314.pyc").write_bytes(b"cache")
        with self.assertRaisesRegex(w.ProtocolError, "runtime cache"):
            w.workspace_files(self.work)

    def test_blocked_request_requires_unmodified_predecessor(self):
        prior_path, prior_hash = phase5d.pinned(phase5d.PINS["axiom"]["prior"])
        prior = json.loads(prior_path.read_text(encoding="utf-8"))
        record = w.checkpoint(self.work, "axiom", self.lykoi["attempted"], prior, prior_hash)
        self.assertEqual(record["files"], prior["files"])
        self.assertEqual(record["achieved"], ["B01"])
        self.assertEqual(record["attempted"][-1]["depends_on"], ["B02"])
        with self.assertRaises(w.ProtocolError):
            w.checkpoint(self.work, "axiom", self.lykoi["attempted"], prior, "0" * 64)

    def test_repaired_preflight_accepts_clean_b02_for_b03(self):
        source = w.ROOT / "benchmark/results/phase5b/checkpoint-axiom-B01.json"
        prior = json.loads(source.read_text(encoding="utf-8"))
        b02 = w.checkpoint(self.work, "axiom", self.lykoi["attempted"][:2],
                           prior, w.file_hash(source))
        result = w.preflight(self.work, "axiom", "B03", b02,
                             w.file_hash(w.CASES / "B03.py"),
                             w.file_hash(w.PROFILES / "B03.json"))
        self.assertEqual(result["result"], "PASS")
        self.assertEqual(result["files"], 27)


if __name__ == "__main__":
    unittest.main()
