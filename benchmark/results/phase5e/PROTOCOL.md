# Lykoi Phase 5E — capability-aware oracle protocol repair

This document repairs the B04 pre-execution profile defect recorded in
`benchmark/results/phase5c/RESUME-HALT.md`. It does not authorize a B04 agent
attempt. Phase 5B historical inputs, Phase 5C halt records and Phase 5D
continuations remain immutable. Existing `axiom` identifiers in checkpoint
serialization remain historical track keys.

## State and composition

A format-3 checkpoint stores the ordered `attempted` entries (including gap
evidence and `depends_on`), the ordered `achieved` capability IDs, complete
implementation file inventory, every attempted case/fragment hash, and an
`expectation` with its SHA-256. The
achieved IDs must equal precisely the `SUCCESS` entries of the attempted
history. A capability gap and its dependent blocks add no achieved capability.

The expectation is built from the unchanged Phase 5B baseline profile and
individual JSON contributions in `benchmark/harness/capabilities/`, applied in
numeric request order **only if achieved**. A contribution declares added
fields, exact JSON-typed migration defaults, explicit schema-version increment,
and prerequisite capabilities. It may explicitly change an earlier default
using its expected old value; conflicts, missing prerequisites, duplicate
fields, missing fragments and unexpected keys fail closed. Neither track name
nor highest achieved request determines the composed result. For example:

| Achieved set | Exact task fields added | Expected storage schema |
| --- | --- | --- |
| B01 | none | 3 |
| B01, B02, B03 | `tags` | 4 |
| B01, B04 | `source` | 4 |
| B01, B02, B03, B04 | `tags`, `source` | 5 |

The B04 contribution is a prospective contract for its independent field,
**not** evidence that either track implemented B04. The B04 case is not yet
frozen. Later requests must add their own reviewed contribution and external
case before either agent receives them. A fragment is protocol data, not
permission to extend the Lykoi compiler or change an implementation. A
legitimate supersession of an earlier external case must be documented and
frozen before that request, retaining historical case/evidence; the capability
schema alone cannot silently disable an earlier test.

`regression_phase5e.py` executes the unchanged Phase 5B baseline/B01/B02
methods and unchanged frozen B03 case against an explicit, hashed expectation.
It selects extra frozen external cases from the **achieved set**, never from a
prefix or maximum. Exact task field assertions, migration defaults, current
storage-version fixtures, and added-field types follow the composed contract.
The runner requires the pinned format-3 checkpoint and matching application
hash, achieved list and expectation hash. Failed prospective-feature probes
are reported separately; only achieved behavior is regression-protected.

## Version and observer bridge

The original Phase 5D `workspace.py`, `regression.py`, `phase5d.py` and
continuation pairs are left byte-for-byte intact. `workspace_phase5e.py bridge`
verifies hard-pinned Phase 5D checkpoint/snapshot hashes and carries the B03
attempted, achieved and implementation bytes into a new format-3 metadata
checkpoint. Its `previous_checkpoint_sha256` pins the Phase 5D record; the
existing Phase 5D snapshot is reused without changing its bytes. Independently
restore the snapshot and compare its complete inventory against the new record
before use. Future format-3 checkpoints require exact attempt-history extension
and the pinned predecessor; a gap or block requires identical implementation
bytes. Case, fragment, oracle, composer, baseline manifest, historical tooling
and all frozen requirement hashes are checked again at preflight. The next
request's case and contribution hashes must also be pinned before preflight.

For every observation use `benchmark/harness/phase5d.py run --read-only` with
`PYTHONDONTWRITEBYTECODE=1` and disposable temp storage outside the workspace.
Run the new regression entry point with `--app`, `--achieved`,
`--expectation-hash`, `--checkpoint`, and `--expected-hash` matching the same
record. Reject unexpected files and Python caches as in amendment 001. Keep
historical measurement definitions, prediction ordering, workflow permissions,
track isolation and capability-gap semantics unchanged.

An expressly superseding future requirement may declare individual frozen
test-method IDs in its capability fragment, each with a nonblank reason, an
origin (`baseline` or an earlier request ID), and a replacement case ID equal
to that request. Supersessions for unachieved origins are inactive. The old case remains intact and
the runner reports an explicit skip with the reason; the request's replacement
case is selected from achieved capabilities. Unknown test IDs, duplicate
supersessions and missing replacement cases abort. This allows a frozen case
containing obsolete assertions to be superseded without silently disabling
other cases. The replacement must cover the still-applicable behaviors during
the prospective-case review; this cannot be inferred from schema metadata.

Do not run a B04 preflight until the B04 external case and its SHA-256 are
frozen. Do not begin B04 prediction or implementation without explicit Phase
5C resume authorization following review of this protocol repair.
