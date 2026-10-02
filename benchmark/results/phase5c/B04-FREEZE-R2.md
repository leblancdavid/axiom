# Lykoi Phase 5C B04 prospective acceptance freeze

Frozen before either B04 preflight, prediction, or implementation attempt.

| Artifact | SHA-256 (raw bytes) |
| --- | --- |
| `benchmark/requirements/B04.md` | `2c2e9e3787d53eb45df7b4b48362db2217e62c165dedda38222f5561cd859221` |
| `benchmark/harness/cases/B04.py` | `85be09e650943ac296fea889577d21657a31a6e9993e32603e9604e2b7b89c03` |
| `benchmark/harness/capabilities/B04.json` | `597a702c6f860330938ecbe982c0bb8adc5f6d2640c0924e9c4619bc60b5b982` |

The external subprocess case checks omitted, empty, and verbatim whitespace-bearing
`source` values; persistence through listing and mutations; and explicit migration
of pre-source version-3 storage with no mutation on legacy reads. It derives the
expected storage version and migration fields from the composed achieved-capability
profile. It does not invoke tags or list-tag, and applies unchanged to both tracks
if B04 is achieved without B02/B03. B04 does not supersede an earlier case.

These bytes are frozen for the duration of B04 execution. Historical halt and
continuation evidence is unaffected.
