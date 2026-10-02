# B13 prospective acceptance freeze — Phase 5C R4

Frozen before either B13 preflight, prediction, or implementation.

| Artifact | SHA-256 (raw bytes) |
| --- | --- |
| `benchmark/requirements/B13.md` | `6a93ed0a15f3869fb6e35f6ddfa34f200a0e1620d1b3e0dc2505711d450e00f5` |
| `benchmark/harness/cases/B13.py` | `137f7d5e6b8fb1fccb711fec33e2072d6cb0fd5dd906dcfe2f34e77a1449951d` |
| `benchmark/harness/capabilities/B13.json` | `14103d35dff5e20b12051a169fc213d4b23d58b06031ff6c8972b34844db514c` |

B13 requires B08 archival and B11 deletion behavior. The case checks both
archived pending and archived completed tasks reject completion and note
append without writes, remain visible until deletion, and retain B11 deletion
semantics. Unarchived mutation behavior remains active. No historical method
is superseded.
