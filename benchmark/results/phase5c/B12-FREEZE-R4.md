# B12 prospective acceptance freeze — Phase 5C R4

Frozen before either B12 preflight, prediction, or implementation. The B11
continuation and identities are recorded in `RESUME-R4-B11-PROGRESS.md`.

| Artifact | SHA-256 (raw bytes) |
| --- | --- |
| `benchmark/requirements/B12.md` | `d60ee7901f4735fb9903cc24e5abb61a6483b9a884970f029be3ddd7567ab942` |
| `benchmark/harness/cases/B12.py` | `2a6550d2758dd9f2eee102b89818661380e8fb18516ccc226d6673b1d244eec6` |
| `benchmark/harness/capabilities/B12.json` | `8a89ae7cd314c62573998b841d0cc7d82a0eb5196e489879911f0b786dc9d1c0` |

B12 requires B01 priority and B08 archival, not B11's deletion change. The
external case selects nonarchived pending HIGH/CRITICAL tasks due in the past,
checks normal order, excludes every other priority, status and archive state,
checks unchanged `list-overdue` coverage and read-only behavior, and uses a
two-day future date to avoid clock-boundary flakiness. No previous case is
superseded.
