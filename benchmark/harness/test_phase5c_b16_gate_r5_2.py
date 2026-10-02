"""Independent, read-only B16 preflight from each authoritative B15 snapshot."""

import json
from pathlib import Path
import tempfile
import unittest

import regression_phase5c_r5_2 as oracle
import workspace as w
import workspace_phase5c_r5_2 as checkpoint
import workspace_phase5e as legacy
from test_phase5c_checkpoint_r5_2 import SNAPSHOTS, TEMP


class B16Gate(unittest.TestCase):
    def test_independent_b15_restores_and_frozen_target_preflights(self):
        for track in checkpoint.PREDECESSORS:
            with self.subTest(track=track), tempfile.TemporaryDirectory(
                    prefix=f"phase5c-b16-preflight-{track}-", dir=TEMP) as folder:
                prior = checkpoint.predecessor(track)
                work = Path(folder) / "b15"
                snapshot, digest = SNAPSHOTS[track]
                w.restore(track, work, prior, checkpoint.RESULTS / snapshot, digest)
                before = w.workspace_files(work)
                self.assertEqual(before, prior["files"])
                result = legacy.preflight(work, track, "B16", prior,
                                          oracle.CASE_SHA256, oracle.FRAGMENT_SHA256)
                self.assertEqual(result["result"], "PASS")
                app = work / ("generated/task_manager.py" if track == "axiom" else
                              "benchmark/conventional/task_manager.py")
                suite, target, active, dispositions = oracle.prospective(
                    prior, [*prior["achieved"], "B16"], app, mark_skips=False)
                self.assertEqual(target["expectation_sha256"], checkpoint.TARGETS[track])
                self.assertEqual(len([name for name in dispositions
                                      if name.startswith("regression_B16.")]), 3)
                self.assertEqual(len([item for item in active.values()
                                      if item["replacement"] == "B16-R5"]),
                                 5 if track == "axiom" else 24)
                self.assertEqual(suite.countTestCases(), len(dispositions))
                self.assertEqual(w.workspace_files(work), before)
                self.assertNotIn("B16", prior["achieved"])
                self.assertEqual(json.loads((checkpoint.RESULTS /
                                 f"checkpoint-{'lykoi' if track == 'axiom' else track}-B15-r4.json")
                                 .read_text(encoding="utf-8")), prior)


if __name__ == "__main__":
    unittest.main()
