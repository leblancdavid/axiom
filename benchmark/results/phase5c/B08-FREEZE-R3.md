# Lykoi Phase 5C B08 prospective acceptance freeze

Frozen before either B08 preflight, prediction, or implementation.

| Artifact | SHA-256 (raw bytes) |
| --- | --- |
| `benchmark/requirements/B08.md` | `dbe9d062092c4fc00c2d32210b8e493dbe0f05d0f2ee2e462c44588988335109` |
| `benchmark/harness/cases/B08.py` | `afc07957ca3bdc33ce8ca63bc0fb3ef78d9ada30f20f251c95863b31c6e31c06` |
| `benchmark/harness/capabilities/B08.json` | `d00aab0d1e94b2d778d3525933f161c7d7ed228b094464987d46cea765e19f56` |

The case tests pending and completed archival, independent status, repeat
transition failure without writes, visibility in core lists, normal-order
`list-archived`, and explicit migration. The additional list-tag, list-status,
and list-category visibility checks run only when their earlier capabilities
were actually achieved. The added boolean/default composes independently of
B02/B03/B05/B06/B07, and no earlier case is superseded.
