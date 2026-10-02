"""R4 protocol repair: preserve B04/B07 behavior under B11 deletion semantics.

The original B04, B07 and B11 cases remain frozen and byte-for-byte unchanged.
These tests replace only the two obsolete methods when B11 is achieved.
"""

import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


class Calls(unittest.TestCase):
    def call(self, cwd, *args, error=None):
        result = subprocess.run([sys.executable, str(self.app), *args], cwd=cwd,
                                capture_output=True, text=True)
        self.assertEqual(result.returncode, 1 if error else 0, result)
        if error:
            self.assertEqual(result.stdout, "")
            self.assertEqual(json.loads(result.stderr), {"error": error})
            return None
        self.assertEqual(result.stderr, "")
        return json.loads(result.stdout)


def cases(app, profile, achieved):
    class Source(Calls):
        def test_verbatim_default_and_mutations_after_b11(self):
            with tempfile.TemporaryDirectory() as folder:
                cwd = Path(folder)
                labelled = self.call(cwd, "create", "--title", "labelled", "--description", "x",
                                     "--priority", "HIGH", "--source", "  API\tfeed  ")
                omitted = self.call(cwd, "create", "--title", "omitted", "--description", "x")
                empty = self.call(cwd, "create", "--title", "empty", "--description", "x",
                                  "--source", "")
                self.assertEqual(labelled["source"], "  API\tfeed  ")
                self.assertEqual(omitted["source"], "")
                self.assertEqual(empty["source"], "")
                self.assertEqual({t["id"]: t["source"] for t in self.call(cwd, "list")},
                                 {labelled["id"]: "  API\tfeed  ", omitted["id"]: "", empty["id"]: ""})
                self.assertEqual(self.call(cwd, "list-high")[0]["source"], "  API\tfeed  ")
                completed = self.call(cwd, "complete", "--id", labelled["id"])
                self.assertEqual(completed["source"], "  API\tfeed  ")
                self.assertEqual(next(t for t in self.call(cwd, "list")
                                      if t["id"] == labelled["id"])["source"], "  API\tfeed  ")
                before = (cwd / "tasks.json").read_bytes()
                self.call(cwd, "delete", "--id", labelled["id"], error="delete_requires_archive")
                self.assertEqual((cwd / "tasks.json").read_bytes(), before)
                archived = self.call(cwd, "archive", "--id", labelled["id"])
                self.assertEqual(archived["source"], "  API\tfeed  ")
                self.assertEqual(self.call(cwd, "delete", "--id", labelled["id"])["source"],
                                 "  API\tfeed  ")

    class Notes(Calls):
        def test_append_order_trim_and_failed_append_after_b11(self):
            with tempfile.TemporaryDirectory() as folder:
                cwd = Path(folder)
                first = self.call(cwd, "create", "--title", "first", "--description", "x")
                second = self.call(cwd, "create", "--title", "second", "--description", "x")
                self.assertEqual(first["notes"], [])
                self.assertEqual(second["notes"], [])
                first = self.call(cwd, "append-note", "--id", first["id"], "--text", "  first note  ")
                self.assertEqual(first["notes"], ["first note"])
                first = self.call(cwd, "append-note", "--id", first["id"], "--text", "second\t")
                self.assertEqual(first["notes"], ["first note", "second"])
                self.assertEqual(next(t for t in self.call(cwd, "list") if t["id"] == first["id"]), first)
                before = (cwd / "tasks.json").read_bytes()
                self.call(cwd, "append-note", "--id", first["id"], "--text", " \t ",
                          error="invalid_note")
                self.assertEqual((cwd / "tasks.json").read_bytes(), before)
                self.assertEqual(next(t for t in self.call(cwd, "list") if t["id"] == first["id"]), first)
                self.assertEqual(next(t for t in self.call(cwd, "list") if t["id"] == second["id"])["notes"], [])
                completed = self.call(cwd, "complete", "--id", first["id"])
                self.assertEqual(completed["notes"], ["first note", "second"])
                before = (cwd / "tasks.json").read_bytes()
                self.call(cwd, "delete", "--id", first["id"], error="delete_requires_archive")
                self.assertEqual((cwd / "tasks.json").read_bytes(), before)
                archived = self.call(cwd, "archive", "--id", first["id"])
                self.assertEqual(archived["notes"], ["first note", "second"])
                self.assertEqual(self.call(cwd, "delete", "--id", first["id"])["notes"],
                                 ["first note", "second"])

    Source.app = app
    Notes.app = app
    suite = unittest.TestSuite()
    if "B04" in achieved:
        suite.addTests(unittest.defaultTestLoader.loadTestsFromTestCase(Source))
    if "B07" in achieved:
        suite.addTests(unittest.defaultTestLoader.loadTestsFromTestCase(Notes))
    return suite
