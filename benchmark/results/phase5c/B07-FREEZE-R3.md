# Lykoi Phase 5C B07 prospective acceptance freeze

Frozen before either B07 preflight, prediction, or implementation.

| Artifact | SHA-256 (raw bytes) |
| --- | --- |
| `benchmark/requirements/B07.md` | `588e21f734cf75003dfd96a414a4f7352aded8c4146daab5e1e2b4f74164f1f8` |
| `benchmark/harness/cases/B07.py` | `d02a0d9ea314a4fcf65eb12ad2ec4ae41cf18cec6a5a7d6aa69e26114b576c5d` |
| `benchmark/harness/capabilities/B07.json` | `53dd70d998aac4309c3d35b68f438a6c77b822aa2422d76b86326d660c206c91` |

The public subprocess case checks initially empty notes, ordered trimmed appends,
blank-note rejection without changing storage, persistence through reads and
mutations, and explicit migration from schema 3. The composed profile supplies
the actual achieved-set migration defaults and target schema independently for
each track. The case invokes none of B02/B03/B05/B06's new commands or fields;
its trimming assertion comes directly from B07's own requirement. There are no
capability prerequisites or superseded earlier cases.

These bytes are frozen for the duration of B07 execution.
