# B15 prospective acceptance freeze — Phase 5C R4

Frozen before preflight, prediction, or implementation on either track.

| Artifact | SHA-256 (raw bytes) |
| --- | --- |
| `benchmark/requirements/B15.md` | `fe38279c15d7ed6b3282390539f0bd8a8e2e8e6026e3dface0e1774a2c0ae9ff` |
| `benchmark/harness/cases/B15.py` | `536f9b3840ee011700470aa8992834e744a0a1fba1c4aba4f40f3476ac2645db` |
| `benchmark/harness/capabilities/B15.json` | `aae4a6bbdd17e9b012629a88c360e48aff51a900b75e8740df126111deb99345` |

B15 requires achieved B14 dependencies and B13 archived transition behavior.
The external case checks rejection without writes while any dependency is
pending, eventual completion after all are completed, archived completed
dependencies counting as completed, retention of dependency order, and the
pre-existing archived-parent and repeat-complete invalid transitions. No prior
method is superseded.
