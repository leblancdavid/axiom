"""Runtime observer must keep acceptance distinctions and discard only incidental values."""

import unittest
from pathlib import Path

import runtime_trace_r5_3 as trace
import runtime_reconcile_r5_3 as reconcile
import workspace as w


class TraceEvidence(unittest.TestCase):
    def test_dynamic_aliases_preserve_identity_and_order(self):
        uuid = "777348e0-c786-4a61-b1ce-52176ddcf8eb"
        created = "2026-10-02T15:22:26.158769Z"
        recorder = trace.Recorder(Path("C:/restore-123"))
        recorder.raw = [
            {"kind": "cli", "method": "test", "cwd": Path("C:/temporary-9"),
             "command": ["create", "--title", "high"], "returncode": 0,
             "observed": {"id": uuid, "created_at": created, "priority": "HIGH"}},
            {"kind": "assertion", "method": "test", "source": "case.py:3",
             "arguments": [{uuid: "HIGH"}, {uuid: "HIGH"}], "passed": True},
            {"kind": "cli", "method": "test", "cwd": Path("C:/temporary-9"),
             "command": ["complete", "--id", uuid], "returncode": 0,
             "observed": {"id": uuid, "created_at": created, "status": "completed"}},
        ]
        events = recorder.normalize()
        self.assertEqual(events[0]["observed"]["id"], "<id:1>")
        self.assertEqual(events[1]["arguments"][0], {"<id:1>": "HIGH"})
        self.assertEqual(events[2]["command"], ["complete", "--id", "<id:1>"])
        self.assertEqual(events[0]["observed"]["created_at"], "<created_at:1>")
        self.assertEqual(events[2]["observed"]["status"], "completed")

    def test_unproven_source_site_remains_unexplained(self):
        site = {"channel": "direct_assertion", "method": "a.test", "source": "case.py:3",
                "column": 4, "expression": "self.assertEqual(x, 1)", "roots": []}
        static = {"achieved": ["B01"], "unmapped_source_channels": [site],
                  "direct_assertions": [], "cli_sites": []}
        events = [{"kind": "assertion", "method": "a.test", "source": "case.py:3",
                   "assertion": "assertEqual", "arguments": [1, 1], "passed": True}]
        result = reconcile.reconcile(static, {"achieved": ["B01"], "events_sha256":
                                     w.digest(w.encoded(events)), "events": events})
        self.assertEqual(result["candidate_counts"]["UNEXPLAINED"], 1)
        self.assertEqual(result["semantic_event_to_roots"], {})
        self.assertEqual(result["rejection_path_completeness"], "NOT ESTABLISHED")


if __name__ == "__main__":
    unittest.main()
