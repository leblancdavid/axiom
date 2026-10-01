# Lykoi Phase 5E — capability-aware oracle repair

**Status: PHASE_5C_RESUME_READY (protocol repair only).** B04 has not been
executed; explicit authorization to resume Phase 5C is still required.

## Root cause and audit

The original Phase 5B runner (`benchmark/harness/regression.py:237-244`)
selected `profiles/<highest achieved ID>.json`. Its `fields()`/
`check_task()` asserted exact keys, `with_defaults()` supplied migration
defaults, and the overdue fixture and B01 historical fixture assumed that
profile's singular `schema_version`. This worked for the prefix-shaped
baseline, B01, B02, B03 validation runs. B02's Lykoi capability gap and B03's
dependency block broke that prefix assumption. Independently achieving B04
would give both tracks highest achieved B04 while leaving B02 `tags` present
only on Conventional; one exact profile cannot protect both legitimate states.

The Phase 5D workspace harness (`workspace.py:236-246,264-270`) also bound a
checkpoint and preflight to the *last* achieved profile. The frozen case
selection in `regression.py:250-259`, by contrast, already uses the full
achieved set and thus correctly omits unachieved B03. Its B02 methods also
explicitly skip when B02 is absent. `validate_attempts()` checks contiguous
**attempts**, not contiguous achievements; both Phase 5D B03 checkpoints
already store achieved and attempted histories separately. `phase5d.py`
bridge is B03-specific and not a general later-request resume path. The
baseline manifest hashes requirement text, not schema profiles; snapshot and
implementation inventory do not infer achieved status. The B03 prediction
records and partial-run measurements are raw transcripts; no profile selection
is encoded in their telemetry. Historical B03 reporting lists attempted and
achieved separately. No past evidence is rewritten.

The later frozen requests include explicitly changed behavior, such as B11's
completed-delete rule and B16/B17's creation authorization. Earlier cases
cannot simply be treated as an always-valid numeric prefix at those stages:
any supersession must be reviewed and recorded before its request, preserving
the old case and evidence. This repair neither guesses later implementation
outcomes nor silently turns off old cases.

## Repair and boundary

New, separate harness entry points compose a pinned baseline with per-achieved
capability contributions, bind the result and fragment hashes into format-3
checkpoints, and run the frozen external cases through the composed contract.
The Phase 5D clean-workspace rule remains in force. `PROTOCOL.md` describes
the exact continuation and prospective-case freeze rules. Separate Phase 5E
bridge checkpoints carry B03 history with unchanged implementation inventories
and reuse the pinned Phase 5D snapshots.

Seven Phase 5E integrity tests passed: they exercise two valid achieved sets
ending in B04 with different task fields and storage versions, reject missing
dependencies/conflicting additions and default changes, verify fragment hashes
change when a contribution changes, check history-preserving metadata bridges,
enforce unchanged bytes on a dependency block, verify explicit case
supersession skips only the named method, and run both historical B03
states through read-only external and internal suites. The six Phase 5D
integrity tests also passed. The Lykoi continuation passed 5/5 applicable
external methods (two B02 methods skipped) and 31/31 internal tests; the
Conventional continuation passed 9/9 external and 8/8 internal tests. Both
workspaces retained their exact pre-observation file inventories. The two
new metadata checkpoints independently restored their Phase 5D snapshots:
Lykoi 27 files, Conventional 2 files. `FROZEN.md` pins all new bytes.

No B04 prediction, implementation, acceptance case, raw agent transcript,
measurement, or B04 checkpoint has been created. B04 preflight is deliberately
unavailable until its external case is frozen. The original Phase 5C halt
records and the Phase 5D continuation checkpoints/snapshots were not changed.
