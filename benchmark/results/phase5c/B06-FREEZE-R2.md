# Lykoi Phase 5C B06 prospective freeze

Frozen before either B06 preflight, prediction, or implementation.

| Artifact | SHA-256 (raw bytes) |
| --- | --- |
| `benchmark/requirements/B06.md` | `b2be288e4e5a58ac348169860f3e4123b1560c9a9d787787005ff94b46c04b61` |
| `benchmark/harness/cases/B06.py` | `e558f1c5f0c83fe4e08e9ea2874e51f1ff1e2c9d0863f3806f0706307a45263f` |
| `benchmark/harness/capabilities/B06.json` | `88bcec0fd6d9cda02ef89978d6a4ca840e07d65dc82d6ec9a2ad3b32983b30fb` |

The case checks trimming and rejection on create, exact case-sensitive listing
including uncategorized/completed tasks, unchanged storage on queries and failed
creates, preservation through mutations, and explicit old-storage migration.
The contract composes with each track's achieved set without requiring B02/B03
or B05. No previous case is superseded.
