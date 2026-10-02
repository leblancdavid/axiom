# R5.3 restarted coverage: returned-priority assertion missing

**R5.3 UNFROZEN; R5.2.2 authoritative and unchanged; B17 UNEXPOSED.** Machine-readable witness: `R5_3-PRIORITY-PRECONDITION-COVERAGE-STOP.json`.

The corrected B01 carrier at `benchmark/harness/assertion_preservation_r5_2_2.py:70-75` creates DEFAULT, HIGH and CRITICAL tasks and independently checks that their **returned** priority fields equal `["NORMAL", "HIGH", "CRITICAL"]`. This checks the actual CLI results; deriving an entity's intended priority from create arguments is not equivalent. The source site is applicable to the full achieved history and currently has no direct assertion root. The later post-completion `list-high` observation is mapped, but its state binding does not replace this independent returned-field assertion. Classification: **R5.3 reconstruction incompleteness**, not an oracle discrepancy.

The earlier distinct-ID and default-due-date restoration assertions now have prospective direct assertion roots. The restarted site inventory still has unmapped candidates, and branch-qualified CLI path completeness has not been demonstrated. `NO KNOWN UNMAPPED SEMANTIC REJECTION PATHS` and `ZERO UNEXPLAINED SEMANTIC DIFFERENCES` remain unestablished. Determinism certification, fresh B16 restores, freeze and B17 exposure remain blocked.

The repository harness passes 65 tests with the prospective reconstruction changes.
