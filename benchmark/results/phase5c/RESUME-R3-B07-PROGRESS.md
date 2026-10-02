# Lykoi Phase 5C resumed execution — immutable interim evidence through B07

**Status: IN PROGRESS.** B07 was frozen and executed after the verified B06
continuation. B08–B20 have not been executed. Historical evidence and
`RESUME-R2-PROGRESS.md` are preserved.

The B07 prospective requirement, acceptance case and capability contribution
were frozen in `B07-FREEZE-R3.md` before either preflight or prediction.
Independent B06 restores and B07 preflights passed; prior applicable external
regressions passed (Conventional 14/14; Lykoi 7/7, two skipped). Prediction
JSONL preceded implementation JSONL for each track. Both agents used
`openai/gpt-6-sol` in isolated OpenCode sessions with bytecode disabled and
temporary storage outside their workspaces.

| Track | B07 attempted | B07 achieved | Raw classification | Applicable external regression | Internal | Resulting achieved set |
| --- | --- | --- | --- | --- | --- | --- |
| Conventional | yes | yes | `SUCCESS` | 16/16 | 18/18 | B01–B07 |
| Lykoi | yes | no | `AXIOM_CAPABILITY_GAP` | 7/7 (2 skipped) | 33/33 | B01, B04 |

The Lykoi model-only in-memory probes in `B07-lykoi-implementation.jsonl`
show the validator rejects a list-valued record field, an array migration
default for a string field and an append assignment. B07 independently demands
an ordered array and append semantics; this is an intrinsic Lykoi capability
gap, not a new dependency block on B02/B03/B05/B06. The historical raw
classification label remains serialized as shown. Lykoi implementation bytes
were unchanged. No B07 regression or implementation failure was classified.

| Track | Format-3 checkpoint SHA-256 | Snapshot SHA-256 | Files |
| --- | --- | --- | ---: |
| Conventional B07 | `7a61e32b3237507d0e69ad4bea2234aebf08e4b3e08afad7977ae84148dcf957` | `291a7f26aceb8b5968d3e87f3a99f4d07effecc2d831ef9dd0921e1fd67ea526` | 2 |
| Lykoi B07 | `2ac278ea3e726d972fe6a733040d47fefdc3678940ec96749c1bb3419a4ea676` | `36e34184bd3d9cd9c65287d49d813838ca31197de6467b387defb1e1147c4ff5` | 27 |

Both snapshots independently restored against their complete inventories.
Raw prediction and implementation event streams, attempt histories, external
regression output and internal-test output are in this directory under `B07-`.
Conventional prospective acceptance output is `B07-conventional-acceptance.log`.
Tool/timing/token measurements are preserved in event streams where provided;
other unavailable telemetry is N/A. A first Conventional internal-test invocation
used the wrong relative harness path and was rerun successfully with the
read-only wrapper; an initial Conventional regression probe supplied an
incorrect expectation hash and was rejected before running tests, then rerun
with the checkpoint's correct hash. Neither changed workspace bytes or the
reported verified outcomes.

**Next boundary:** construct and freeze B08's external case and capability
fragment before either B08 preflight, prediction or implementation. Do not
report Phase 5C complete before B20 and final read-only validation.
