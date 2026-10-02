# B14 prospective acceptance freeze — Phase 5C R4

Frozen before B14 preflight or agent exposure on either track.

| Artifact | SHA-256 (raw bytes) |
| --- | --- |
| `benchmark/requirements/B14.md` | `c267a859afff26708f17feea0c88bd77ec53f5768a0087dd8345ada3fd3bd31c` |
| `benchmark/harness/cases/B14.py` | `6d17945700606cbab38fb933d281e5880c2becc8bdefd638201dc635c106a729` |
| `benchmark/harness/capabilities/B14.json` | `adbc836a999ca34b3770851397eba14b74da41fbf0d78862887bd899fe361dce` |

The independent capability contribution adds an ordered task-ID array and a
schema migration. The external case checks append order, duplicate/self/missing
ID and direct/transitive cycle failures without writes, deletion protection
including an archived referenced task, and explicit migration of an older
version. No historical method is superseded. A missing earlier note-array
capability may inform Lykoi's feasibility but is not assumed to be a formal
dependency of the B14 task-ID array.
