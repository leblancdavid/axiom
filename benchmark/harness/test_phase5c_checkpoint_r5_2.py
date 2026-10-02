"""Disposable B16 checkpoint writer/restore exercises; no actual B16 exposure."""

import json
from pathlib import Path
import tempfile
import unittest

import workspace as w
import workspace_phase5c_r5_2 as versioned


TEMP = Path("C:/Users/lblan/AppData/Local/Temp/opencode")
SNAPSHOTS = {
    "conventional": ("snapshot-conventional-B15-r4.tar",
                     "8f06f0f62a224139895b7fae48d14160a60e25ebd97a091679b05b3db3f048bc"),
    "axiom": ("snapshot-lykoi-B15-r4.tar",
              "36e34184bd3d9cd9c65287d49d813838ca31197de6467b387defb1e1147c4ff5"),
}


class CheckpointRoundTrip(unittest.TestCase):
    def test_disposable_write_restore_and_independent_semantics(self):
        for track in versioned.PREDECESSORS:
            with self.subTest(track=track), tempfile.TemporaryDirectory(
                    prefix=f"phase5c-r5-2-{track}-", dir=TEMP) as folder:
                parent = Path(folder)
                prior = versioned.predecessor(track)
                name, snapshot_hash = SNAPSHOTS[track]
                workspace = parent / "source"
                w.restore(track, workspace, prior, versioned.RESULTS / name, snapshot_hash)
                before = w.workspace_files(workspace)
                # A non-success exercise must keep the actual B15 semantics byte-identical.
                gap = ({"request": "B16", "outcome": "AXIOM_CAPABILITY_GAP",
                        "evidence": "disposable writer fixture"} if track == "axiom" else
                       {"request": "B16", "outcome": "IMPLEMENTATION_FAILURE"})
                for suffix, last in (("unchanged", gap), ("synthetic-target", {"request": "B16", "outcome": "SUCCESS"})):
                    with self.subTest(outcome=suffix):
                        attempts = [*prior["attempted"], last]
                        record = versioned.checkpoint(workspace, track, attempts)
                        self.assertEqual(record["protocol_version"], versioned.PROTOCOL)
                        self.assertEqual(record["composer_sha256"], versioned.pins()["composer_sha256"])
                        self.assertEqual(record["achieved"], [a["request"] for a in attempts if a["outcome"] == "SUCCESS"])
                        self.assertEqual(record["applicable_oracle_sha256"],
                                         record["oracle_sha256"] if suffix == "synthetic-target" else
                                         record["legacy_oracle_sha256"])
                        self.assertEqual(record["expectation_sha256"],
                                         versioned.TARGETS[track] if suffix == "synthetic-target" else
                                         prior["expectation_sha256"])
                        self.assertEqual(record["files"], before)
                        checkpoint = parent / f"{suffix}.json"
                        checkpoint.write_bytes(w.encoded(record))
                        archive = parent / f"{suffix}.tar"
                        archive_hash = w.snapshot(workspace, archive)
                        loaded = json.loads(checkpoint.read_text(encoding="utf-8"))
                        self.assertEqual(versioned.validate_record(loaded), record)
                        restored = parent / f"{suffix}-restored"
                        w.restore(track, restored, loaded, archive, archive_hash)
                        self.assertEqual(w.workspace_files(restored), before)
                        self.assertEqual(versioned.checkpoint(restored, track, attempts), record)
                        self.assertEqual(w.file_hash(checkpoint), w.digest(w.encoded(loaded)))
                self.assertEqual(w.workspace_files(workspace), before)

    def test_cross_track_and_tampering_fail_closed(self):
        conventional = versioned.predecessor("conventional")
        lykoi = versioned.predecessor("axiom")
        with self.assertRaises(w.ProtocolError):
            versioned.record("axiom", [*conventional["attempted"],
                                       {"request": "B16", "outcome": "SUCCESS"}], lykoi["files"])
        record = versioned.record("conventional", [*conventional["attempted"],
                                                   {"request": "B16", "outcome": "SUCCESS"}],
                                  conventional["files"])
        for key, value in (("applicable_oracle_sha256", "0" * 64),
                           ("files", lykoi["files"]), ("protocol_version", "wrong"),
                           ("b16_case_sha256", "0" * 64)):
            with self.subTest(key=key), self.assertRaises(w.ProtocolError):
                versioned.validate_record({**record, key: value})


if __name__ == "__main__":
    unittest.main()
