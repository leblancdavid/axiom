# Lykoi Phase 5C B10 prospective acceptance freeze

Frozen before either B10 preflight, prediction, or implementation.

| Artifact | SHA-256 (raw bytes) |
| --- | --- |
| `benchmark/requirements/B10.md` | `3bf536185111466f225ccc8a1fc8ae10a99cfa6da8e85d3a04fca533306febe5` |
| `benchmark/harness/cases/B10.py` | `5753a963f1f23932f66be7619cf7232bf3b605b803b6673cb070506777f24851` |
| `benchmark/harness/capabilities/B10.json` | `cb9d76741775e4edb2f72c4ee710d2d92ab15c51249a0d5fcf09f4fc0ed14ea8` |

The public subprocess case checks trimmed and rejected supplied owner IDs,
default unowned tasks, exact case-sensitive list-owner matching including the
empty owner, preservation on status changes and deletion, no-write queries,
and explicit migration. The composed migration expectation follows actual
achieved sets. B10 does not require B02/B03/B05/B06/B07/B08/B09 or supersede
any frozen case. No archived task is used in this case, since B10 does not
specify how its newly introduced list-owner interacts with earlier archival.
