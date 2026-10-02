# R5.3 bulk reconciliation worksheet — incomplete, unfrozen

R5.2.2 remains authoritative and unchanged; B17 remains unexposed. This
prospective worksheet consumes the saved 233/28 candidate inventories and
3,398/573-event traces. It does not replace their historical JSON. The new
`R5_3-{full,early}-bulk-worksheet.json` records every original candidate,
its runtime event indices, checked source-derived root IDs where available,
and *provisional* runtime witnesses where semantic equivalence is not yet
established. Provisional witnesses are **not** canonical roots.

| History | Candidates | Semantic roots | Components | Duplicates | Harness/control | Unexplained |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| B01–B16 | 233 | 46 | 0 | 0 | 0 | 187 |
| {B01,B04} | 28 | 7 | 0 | 0 | 0 | 21 |

The confirmed subset consists of source-derived persisted-state assertions:
file existence, byte equality against an earlier captured snapshot, and the
newly reconstructed persisted JSON field equality on `schema_version`. The
profile-specific expected value is derived from the frozen assertion's right
operand; runtime operands and assertion site are independently checked. The
46/7 source-derived canonical roots each have a checked runtime assertion
witness, and both mapping directions are retained in the worksheet. **These
counts apply only to the confirmed subset**; the global canonical root
inventory and its bidirectional coverage have not been certified. No
unmapped roots occur *within that subset*.

The other sites were examined in bulk, not silently marked as duplicates or
mechanics. Direct assertions have source expressions and runtime operands;
single-command CLI sites have the concrete command, error/exit outcome and
enclosing helper invocation. They remain `UNEXPLAINED` until their complete
source-derived preconditions (including fixture writes, branch context and
replacement lineage), observation phases and expected results are matched to
canonical roots. A CLI call's successful exit alone cannot stand in for a
later returned-value, helper, or persisted-state assertion. The worksheet
still reports **1,416 full / 275 early semantic runtime events** without a
checked root in this pass; that diagnostic includes events potentially
covered by existing roots outside the verified persisted-state subset, and
is not itself a count of independently missing requirements.

**Rejection-path completeness: NOT ESTABLISHED. Semantic diff: BLOCKED.**
`UNEXPLAINED = 0` has not been reached, so no final inventory/trace rerun,
assertion-level comparison, fresh final restores or freeze has been claimed.
No frozen-oracle discrepancy, semantic ambiguity, protocol-change need or
historical-classification implication has been established by this subset.
The next reconciliation step is to join the remaining returned-value and
CLI/helper paths to their source-derived roots and independently check all
assertions executed inside the helpers, including repeated invocations.

Verification of the prospective tooling: repository harness passed 76 tests
after the final test correction. Frozen R5.2.2 files and applications were
not edited.
