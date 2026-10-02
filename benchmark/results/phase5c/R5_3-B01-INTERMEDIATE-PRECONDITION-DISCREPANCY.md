# R5.3 assertion-specific precondition discrepancy — STOP

Status: **R5.3 UNFROZEN; B17 UNEXPOSED.** This is a focused historical-coverage discrepancy discovered while expanding the repaired oracle's assertion-specific preconditions. It is not a complete semantic inventory or an assertion-level zero-difference certificate. No frozen source, implementation, checkpoint, or historical classification is changed.

## Root and lineage

* Semantic root: `B01.high_after_critical` (`benchmark/harness/regression.py:168-176`, especially `:176`). The B01 method is live on the achieved history `{B01,B04}`; B11 supersedes it on the achieved history `B01–B16` (`benchmark/harness/capabilities/B11.json`).
* B11 carrier: `benchmark/harness/cases/B11.py:24-72`, replayed in B16-R5 as `DeletionLifecycle` with the existing-owner create adaptation (`benchmark/harness/cases/B16_R5_replacements.py:35,169-189`). B11 observes `list-high == [high]` at `:44` **before** either HIGH or CRITICAL completes. At `:51-55` it completes HIGH before CRITICAL; therefore it never observes `list-high` with pending HIGH after CRITICAL completion.
* Frozen R5.2.1 restoration: `benchmark/harness/assertion_preservation_r5_2_1.py:122-130`, selected for the B11-superseded B01 source. Its inventory at `:31,58-70` names the original root and its restoration chain.

## Expected state versus executable state

| | Original B01 assertion | Frozen repaired carrier |
| --- | --- | --- |
| Prior successful creates | `default` (omitted priority: NORMAL), `high` (HIGH), `critical` (CRITICAL), in that order (`regression.py:168-170`) | `high` (HIGH), `critical` (CRITICAL), in that order (`assertion_preservation_r5_2_1.py:125-128`); **no NORMAL task exists** |
| Intermediate mutation | Complete CRITICAL while DEFAULT and HIGH remain pending (`regression.py:175`) | Complete CRITICAL while HIGH remains pending (`assertion_preservation_r5_2_1.py:129`) |
| Observation | `list-high == [high]` with **pending NORMAL + pending HIGH + completed CRITICAL** present (`regression.py:176`) | `list-high == [high]` with **pending HIGH + completed CRITICAL** present (`assertion_preservation_r5_2_1.py:130`) |
| CLI semantics | Success and JSON result through the baseline `call` envelope | Success and JSON result through the repair `call` envelope |

Both paths require the HIGH result after CRITICAL completion. Only the original path constrains exclusion of a coexisting pending NORMAL task **at that intermediate state**. That extra task is observable input to `list-high`, not a temporary-directory or local-variable detail. A program could return `[high, default]` only when both a pending NORMAL task and a completed CRITICAL task coexist, while returning `[high]` in the restored two-task scenario and the B11 pre-completion scenario. Neither carrier would reject that behavior at the original observation point. Earlier B11 checks that exclude NORMAL before completion do not rule out this state-dependent failure.

The prior preservation audit (`benchmark/results/phase5c/B11-R4-HISTORICAL-ASSERTION-PRESERVATION-AUDIT.md:182-187`) explicitly proposed a *minimal* two-task restoration. That decision explains the carrier but does not establish assertion-specific precondition equivalence with the original three-task B01 observation. The frozen R5.2.1 carrier must not be edited as part of this R5.3 proof.

## Disposition

Affected achieved history: **B01–B16** (and any B11-achieved history selecting this restoration). The `{B01,B04}` history runs the original B01 method and retains the three-task observation. The exact discrepancy is `B01.high_after_critical`: expected original precondition `pending NORMAL + pending HIGH + completed CRITICAL`; observed repaired precondition `pending HIGH + completed CRITICAL`. Expected outcome in both is `[high]`, but the stronger source-state requirement is not preserved.

**STOP for separate adjudication.** Do not normalize away the NORMAL task, silently strengthen or repair the frozen carrier, claim `ZERO UNEXPLAINED SEMANTIC DIFFERENCES`, perform final fresh B16 restores, freeze R5.3, or expose B17. CLI/loop expansion, independent rejection-path completeness and the full assertion-level diff remain unfinished; this focused discrepancy is not an exhaustive assessment.
