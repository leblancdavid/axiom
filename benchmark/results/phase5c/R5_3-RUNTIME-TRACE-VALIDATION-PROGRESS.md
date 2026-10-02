# R5.3 runtime semantic-trace validation — open, not frozen

R5.2.2 remains the frozen authority. R5.3 is unfrozen; B17 is unexposed.
This is an independent **observer** of the authoritative executable suites,
not a new oracle, protocol revision or amendment to any frozen case.

## Instrument and evidence

`benchmark/harness/runtime_trace_r5_3.py` restores each pinned B16 checkpoint
into an isolated temporary workspace, builds the applicable frozen R5.2.2
composition using its achieved set and expectation hash, and runs the suite.
The observer wraps process-local `unittest` assertions, CLI subprocess calls
and helper entries/exits, and records Python branch/assert-path locations.
Events retain execution order, method, source, helper invocation, concrete
commands and values, success/error channels and assertion operands. The
restored implementation is a separate, uninstrumented process. Original
unittest methods are restored after each construction (the frozen skip marker
mutates their class), permitting repeated in-process runs. No frozen file or
restored workspace file was changed.

| Achieved history | External result | Normalized events | Event SHA-256 |
| --- | --- | ---: | --- |
| B01–B16 | 35 pass, 28 supersession skips | 3398 | `5392fc2522b4f59eb02d880c18351e2226519b2b72821ee4165aca426f7180bc` |
| {B01,B04} | 7 pass, 2 prerequisite skips | 573 | `1d177b10df8f150a8c0d91edc7c6cf8a5fef16a976bdc5651b904361d6943c7e` |

Both hashes repeated in independent fresh processes and twice in-process.
The full event records are `R5_3-{full,early}-runtime-trace.json`. Normalization
replaces **generated** UUIDs and creation instants by first-observation aliases
reused in later assertions, commands and persisted values; fixed historical
fixture values remain literal. Temporary workspace paths are aliases. The
one source-derived wall-clock value at `cases/B12.py:60–62` is represented as
`<B12:now+2days>` at the frozen `_call` boundary and reused on subsequent
observations. This retains the input's two-day relative-time relationship,
its reuse, and ordering; other due dates remain concrete.

The observation of `cases/B04.py:59` (file bytes unchanged after rejected
`list`) and `regression.py:91` (no file on initial list) confirms that the
previously identified gaps execute. The source-only `regression.py:191` branch
remains statically excluded under both achieved profiles. These facts do not
create R5.3 roots by themselves.

## Conservative reconciliation and remaining gate

`runtime_reconcile_r5_3.py` joins the restarted static inventories to recorded
events using method/source/channel only as **provisional site correlations**.
It deliberately does not label a source candidate represented merely because
it executed near another root. `R5_3-{full,early}-runtime-reconciliation.json`
retains each candidate, its execution witnesses, and provisional root/event
indices for review; the explicit semantic root/event maps remain empty until
operation, arguments, state, expectation, binding and lineage have been checked.

| Achieved history | Static candidates with runtime reachability witnesses | Provisional site-correlated roots | Semantic events without provisional site roots | Unexplained candidates |
| --- | ---: | ---: | ---: | ---: |
| B01–B16 | 233 / 233 | 390 | 1304 | 233 |
| {B01,B04} | 28 / 28 | 121 | 249 | 28 |

All 261 source candidates have runtime *reachability* witnesses under their
respective profiles; some may be repeated across the two histories. This is
not proof that each site is an independently rejectable semantic path. These
are **not** counts of missing independent semantic requirements. A
provisional correlation does not establish equivalence; lack of one does not
establish a new root. Direct Python assertion paths and branch locations are
recorded but branch outcomes and all file-write provenance are not yet fully
normalized into independently compared transition/rejection semantics.
Concrete-path reconciliation, candidate dispositions, bidirectional semantic
root mapping, rejection-path completeness and the full assertion-level diff
remain open. In particular **NO KNOWN UNMAPPED SEMANTIC REJECTION PATHS** and
**ZERO UNEXPLAINED SEMANTIC DIFFERENCES** are not established. No final gates,
pre-freeze proof, freeze or B17 exposure follow from this trace.

Verification: `python -m unittest discover -s benchmark/harness -p 'test_*.py'`
passed 73 tests, including observer alias/identity and fail-closed
reconciliation checks. The external suites above were run in clean restored
states; internal restored suites/final certification gates were not rerun as
part of this open reconstruction step.
