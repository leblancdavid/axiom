# Phase 5A pilot: methodology report (B01, B02 only)

**This is a method check, not evidence that either maintenance approach is
better.** The canonical Phase 5 baseline (`air/`, `generated/`, and
`benchmark/conventional/`) was not changed by the agents. Results live under
`outputs/`; event-level transcripts for all sessions, including an invalid
first Axiom setup, live under `transcripts/`.

## Inputs and isolation

`FROZEN.md` pins the unmodified B01/B02 SHA-256 values and the pilot oracle
hash. The requirements were read verbatim inside both track workspaces, with
track-specific instructions but no other track's solution. Both tracks used
OpenCode `1.18.32`, model `openai/gpt-6-sol`, in separate sessions and
directories. The conventional workspace contained its Python application,
its own developing tests and the two requirements. The corrected Axiom
workspace contained the full Phase 4 Axiom tree, documentation and the two
requirements; it contained no conventional application. Each B01 and B02
prediction was saved before implementation. B02 followed B01 within each
track's session. No pilot request after B02 was executed.

The uncommitted baseline was first copied to an external, untouched snapshot.
Before B01, a disposable copy of each application was perturbed and recovered
from that snapshot with matching SHA-256; both agent workspaces matched the
snapshot. The initial Axiom copy **omitted `experiments/`** even though its
internal suite reads a historical fixture. That invalid first run was retained
and a new Axiom session started from a corrected workspace which passed all
31 Phase 4 tests before B01. A later durable archive,
`baseline-snapshot.tar`, was independently extracted and passed the original
3-case shared oracle and 31 internal tests (see `FROZEN.md`).

## Four primary runs

| Run | Actual inspected components | Changes | Agent verification | Frozen external cases |
| --- | --- | --- | --- | --- |
| Conventional B01 | `task_manager.py`, B01 | `task_manager.py` priority tuple; new `test_task_manager.py` | 3/3 internal; one test attempt | 2 B01 cases pass; 2 B02 cases not yet due |
| Axiom B01 (corrected) | `type_priority`, `inv_priority`, impact/provenance, model, docs and tests | `air/task_manager.json` (`type_priority`, `inv_priority`), `tests/test_application.py`, `README.md`; compiler-generated Python and manifest | validation 1 pass, generation 1 pass, 31/31 internal; one test attempt | 2 B01 cases pass; 2 B02 cases not yet due |
| Conventional B02 | `task_manager.py`, `test_task_manager.py`, B02 | task `tags`, repeated CLI flag, version-4 migration and tests | 6/6 internal; one test attempt | all 4 cases pass (including B01 regression) |
| Axiom B02 (corrected) | `cmd_create`, `type_task`, `arg_priority`, semantic impact, frozen validator/runtime vocabulary | **No files changed**; `AXIOM_CAPABILITY_GAP` | validation 1 pass, 31/31 B01 internal; one test attempt | B01 functionality passes; B02 cases fail as expected for the documented gap |

Pre-change predicted surfaces are in the four `*-prediction.md` files (the
corrected Axiom pair is authoritative). Axiom B01 touched the predicted enum
and invariant. Conventional B02 touched its predicted model, CLI, validation,
migration and tests. Axiom B02's predicted string-array/repeated-flag gap was
confirmed by inspection: record fields and inputs cannot hold arrays of
strings, CLI arguments do not collect repetitions, and assignments and
migrations cannot trim/deduplicate or supply `[]`. No compiler extension was
made. The B02 oracle reports two failed assertions and two errors against
the unchanged B01 Axiom artifact; these are symptoms of **one** B02 capability
gap, not four unrelated regressions. Its B01 CRITICAL behavior and 31 internal
tests remain intact.

## Failure ledger (no failed attempt discarded)

| Stage | Run and discovery | Cause | Repair/outcome |
| --- | --- | --- | --- |
| INTERNAL_TEST | First Axiom B01 run: its first 32-test suite had one error, `test_index_and_diff` | The *pilot workspace builder* omitted historical `experiments/task_manager-v0.2-before-priority.json`; the file existed in the frozen repository | Agent changed the compiler test to avoid the fixture and its second 32-test run passed. This was an **invalid infrastructure run**, not an Axiom defect. Entire Axiom side was rerun from the corrected baseline and the initial run is excluded from primary outcomes. |
| MANUAL_DISCOVERY | Corrected Axiom B01: four `apply_patch` tool errors before model edit | A combined patch expected README context that did not match its file; edit verification refused the patch | The fifth edit attempt succeeded; validation, generation and the first 31-test run then passed. The four failed tool calls remain counted. |
| PLANNING | Axiom B02, before model mutation | Frozen model, CLI and migration vocabulary cannot represent repeated string-array tags | `AXIOM_CAPABILITY_GAP` recorded with supporting inspection; B01 state unchanged. No failed model validation or generation was manufactured to demonstrate it. |
| EXTERNAL_ORACLE | Axiom B02, four case-level outcomes (two assertion failures, two missing-tag errors) | B02 is absent due to the recorded gap | Unrepaired within frozen language; B01 regression cases run separately and pass. Do not treat passing internal tests as B02 success. |

No PLAN_VALIDATION, MODEL_VALIDATION, GENERATION, or STATIC_CHECK failure was
observed in the corrected primary runs. `plan`/`apply` were not invoked;
"zero plan-validation failures" must not be reported as evidence of coverage.

## Recorded telemetry

Event spans are from the first to last timestamp in each OpenCode JSON stream,
**not** end-to-end wall-clock cost; CLI startup, external checks and setup are
excluded. Tool calls count `tool_use` events, including errors. Usage numbers
are sums of the provider-reported per-step `input`/`output`/`cache.read`
fields, not estimates of total unique text or a monetary cost.

| Session stage | Event span (s) | Tool calls (errors) | Input / output / cache-read tokens reported |
| --- | ---: | ---: | ---: |
| Conventional B01 prediction | 19.90 | 4 (0) | 39048 / 436 / 72064 |
| Conventional B01 implementation | 34.99 | 3 (0) | 2326 / 1154 / 157696 |
| Axiom B01 corrected prediction | 64.59 | 23 (0) | 81122 / 1937 / 252416 |
| Axiom B01 corrected implementation | 129.64 | 17 (4) | 13754 / 2596 / 1405440 |
| Conventional B02 prediction | 10.84 | 3 (0) | 4094 / 456 / 81408 |
| Conventional B02 implementation | 47.05 | 3 (0) | 3168 / 1837 / 181632 |
| Axiom B02 corrected prediction | 42.04 | 13 (0) | 26025 / 1561 / 289792 |
| Axiom B02 corrected gap verification | 34.87 | 5 (0) | 3863 / 520 / 475392 |

The invalid first Axiom run is retained in `transcripts/axiom-B01-*` and
`transcripts/axiom-B02-*`, with corresponding predictions; its B01 agent
needed an INTERNAL_TEST repair. Do not aggregate these extra sessions into
either track's primary timing or usage.

## What the pilot says about the protocol

1. **Check complete workspace dependencies before running agents.** The
   missing fixture created a spurious repair and changed tests. Preflight the
   full baseline suite in *each* isolated workspace before starting predictions.
2. **Separate gap from incorrect implementation and inherited regression.**
   The B02 test runner assumes a successful B02 schema migration, so running
   it unchanged against the frozen B01 Axiom state produces multiple failures.
   Report the gap once, with case-level details and B01 checks separately.
3. **The frozen baseline oracle assumes exactly seven fields.** It cannot be
   rerun verbatim on a legitimately expanded B02 task; the pilot runner tests
   selected baseline behavior but does not replicate all three baseline
   scenarios after B02. Before any full benchmark, define accumulated,
   version-aware external regression cases and explicit coverage accounting.
4. **Preserve an artifact at every step.** B01 conventional source was not
   archived before B02 overwrote it; the precise B01 patch and test addition
   remain in the B01 transcript, but a dedicated checkpoint is preferable.
5. **Clarify measurable priority ordering.** B01 says CRITICAL is “above” HIGH,
   but the baseline exposes no ranking operation; the frozen oracle checks
   acceptance, persistence, and exact HIGH-only filtering, not relative rank.
   Do not silently add a ranking assertion or rewrite the frozen requirement.
6. The Axiom README in the corrected workspace mentions a comparative
   benchmark even though the agent prompt made no comparative claim. Avoid
   giving track agents experiment-context documentation in a future blinded
   run, or explicitly record it as visible context. No conclusion about
   comparative efficiency or reliability follows from this pilot.

Primary output hashes (SHA-256): conventional B02 source
`e573c719964b197f6a02efde60a9589f465f2e78f7d2efa48d35873f48282106`;
Axiom B01/B02 model `b2a937bb752053f26a53826112defe28e3f0edada27914bb6821cd7a55ddc4cb`;
generated Python `07ae9da906cd40b4aca8e23046eb389a303e070409fae498cd470e3d1828031f`
(matches its manifest). Baseline input hashes are in `../BASELINE.md`.
