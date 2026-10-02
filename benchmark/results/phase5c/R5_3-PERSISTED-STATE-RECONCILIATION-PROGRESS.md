# R5.3 persisted-state reconciliation — partial, unfrozen

R5.2.2 remains the frozen authority; B17 remains unexposed. The 233/28
candidate inventories and 3,398/573-event traces in
`R5_3-RUNTIME-TRACE-VALIDATION-PROGRESS.md` are the baseline for this step.
Their saved reconciliation JSON predates the roots below and still reports all
candidates as `UNEXPLAINED`; it must not be presented as an updated proof.

## Mechanism and independent rejectability

Two executed assertion mechanisms inspect **persisted state**, separately from
the CLI result: `assertFalse(path.exists())` checks the absence of the storage
file, while `assertEqual(path.read_bytes(), snapshot)` compares the entire file
against bytes captured *before* the intervening operation. Either assertion
can fail with all preceding CLI/return assertions still passing. The byte
snapshot is a relational expectation, not an implementation-derived literal.
These checks are independent even when their expected values match at multiple
sites: their preceding operations and state phases differ.

`parameterized_roots_r5_3.expand` now constructs canonical direct-assertion
roots for these source-derived mechanisms. Each root has an assertion-site
identity, method, phase `persisted_state`, expected observation, preceding
steps, entities, context and lineage. Byte-equality roots require an earlier
captured byte snapshot in the executable source; unsupported shapes remain
unmapped. CLI success/failure and later queries retain distinct roots/phases.

| Frozen assertion | Runtime witness (zero-based event index) | Persisted-state rejection record |
| --- | --- | --- |
| `regression.py:91`, early | 211 | After successful initial `list` returns `[]`, `tasks.json` does **not** exist. Root `file-existence`, expected `false`. |
| `regression.py:93`, early | 218 | After rejected blank-title `create`, `tasks.json` still does **not** exist. Separate `file-existence` root, expected `false`. |
| `regression.py:111`, early | 316 | After rejected invalid-due-date `create` and missing-ID `complete`, stored bytes equal the snapshot at line 108. Root `file-bytes-equality`. |
| `regression.py:117`, early | 335 | After rejected repeat `complete`, stored bytes equal the later snapshot at line 115. Separate `file-bytes-equality` root. |
| `cases/B04.py:59`, full / early | 355 / 493 | With a version-3 fixture written at line 56 and captured at line 57, rejected `list` (`migration_required`) does not change file bytes. Separate from the rejection channel; root `file-bytes-equality`. |
| `cases/B04.py:67`, full / early | 378 / 516 | After successful first migration and a later `migrate` returning `{"migrated": 0}`, file bytes equal the *post-migration* snapshot at line 65. Separate root and precondition from line 59. |

The root generator is tested against both real frozen carriers and a synthetic
sequence with two different persistence phases. `python -m unittest discover
-s benchmark/harness -p 'test_*.py'` passed **75 tests**. This establishes a
source-and-trace-supported mapping for these listed observations only; the
remaining direct assertions, CLI invocation contexts and helper/loop paths
have not been dispositioned or bidirectionally compared. The baseline 233/28
candidate report has **not** been reduced by assertion proximity or assumed
duplicates. Quantitative convergence, `UNEXPLAINED = 0`, rejection-path
completeness, semantic diff, final restores and freeze remain open.
