# Lykoi Phase 5C B09 prospective acceptance freeze

Frozen before either B09 preflight, prediction, or implementation.

| Artifact | SHA-256 (raw bytes) |
| --- | --- |
| `benchmark/requirements/B09.md` | `dd44a353c5d26c099e7cee3fc7e0d3fe6361f70b139a11e85b61473631b3c121` |
| `benchmark/harness/cases/B09.py` | `bd9c6d33eeb7948b1e2da63e19b23358353e758c7d86b09296562ded6beadade` |
| `benchmark/harness/capabilities/B09.json` | `a211e72aed0d468c88ba9a7134ee4acf30027120616be59429922f75e7a18541` |

The public CLI case checks inclusive endpoints, ordinary ordering, exclusion
of completed, undated, and archived tasks, empty results, invalid ranges and
non-UTC timestamps, and no writes by queries. B09 explicitly requires the
B08 archival capability for its nonarchived selection; its fragment declares
that dependency. No earlier case is superseded or weakened.
