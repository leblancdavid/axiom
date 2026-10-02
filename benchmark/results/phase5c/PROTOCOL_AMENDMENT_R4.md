# Phase 5C R4 — B11 acceptance-composition repair and restart boundary

**Authority:** the B11 protocol defect and halt are recorded in
`RESUME-R3-B11-HALT.md`. This amendment authorizes a fresh B11 attempt from
each independently restored B10 checkpoint. The interrupted R3 B11 prediction
and implementation streams are retained as unclassified historical evidence,
not scored or reused as continuations. This repair applies symmetrically to
both tracks. No B11 checkpoint exists at the time of this freeze.

## Frozen inputs and R4 additions (SHA-256 of raw bytes)

| Artifact | SHA-256 |
| --- | --- |
| Conventional B10 checkpoint | `5bb65e500add4ff348a0004cd216efb44519bc11d3c4815a7ee22f6c7e367688` |
| Conventional B10 snapshot | `f771bbdb709a34bfd2113de70e370ed95812cf9b36123328adf12676973164a7` |
| Lykoi B10 checkpoint | `cb2fb04d04fa80c6af67c7ef6933002995b40fcd5bb84bc7f51599f49f6ee9a6` |
| Lykoi B10 snapshot | `36e34184bd3d9cd9c65287d49d813838ca31197de6467b387defb1e1147c4ff5` |
| Frozen B04 case | `85be09e650943ac296fea889577d21657a31a6e9993e32603e9604e2b7b89c03` |
| Frozen B07 case | `d02a0d9ea314a4fcf65eb12ad2ec4ae41cf18cec6a5a7d6aa69e26114b576c5d` |
| Frozen B11 case | `721fc2fb1c4d9f7d51978721799fd26be12a3186d481667fff5b0060be64201a` |
| Frozen B11 fragment | `5dcf7ee0f046515bfdd198feede631c5b767fb17d5e77302d79b662f7e335f7c` |
| R4 replacement cases `benchmark/harness/cases/B11_R4_replacements.py` | `8a8bfad8451e747e31429f1bd87055689d3115ef851861ec48810fbe4678ca60` |
| R4 runner `benchmark/harness/regression_phase5c_r4.py` | `61830ce905deff3565180b3767e933f50e5c17bfeef25ca4bcac41f9c4a706cb9` |

Before any R4 observation, verify all listed hashes. If any differ, halt for
protocol review; do not silently update the pins. B11 requirement and original
case/fragment remain governed by `B11-FREEZE-R3.md`. B01–B10 classifications,
attempt streams, checkpoint inventories, and expectation hashes are immutable.

## Narrow supersession overlay

The frozen B11 fragment's baseline/B01 supersessions remain active only after
B11 is achieved. Additionally, **only when B11 and the originating capability
are achieved**, R4 explicitly supersedes these entire historical methods:

| Frozen method ID | Origin | Replacement |
| --- | --- | --- |
| `regression_B04.cases.<locals>.SourceLabel.test_verbatim_default_and_mutations` | B04 | R4 B11 source case |
| `regression_B07.cases.<locals>.Notes.test_append_order_trim_and_failed_append` | B07 | R4 B11 notes case |

Reason: each method asserts success when deleting a completed unarchived task,
which B11 forbids. The frozen methods remain byte-identical and run before B11
is achieved (including on Lykoi if B11 is blocked). The versioned R4 runner
uses the existing format-3 checkpoint, composer and frozen-case loader; it
requires the exact selected historical method IDs, emits explicit skip reasons,
and adds the replacement case **only when B11 is achieved**. It aborts on a
missing method, fragment collision, missing replacement, invalid checkpoint,
app hash or achieved/expectation hash. No replacement is run for an unachieved
origin. The B04 migration and B07 migration methods remain active unchanged.

The B04 replacement preserves verbatim source on create, omitted/empty defaults,
list/list-high, completion and deletion; it also checks B11 rejection leaves
storage untouched and that archiving permits deletion with source preserved.
The B07 replacement preserves empty/ordered/trimmed notes on create/append,
list round-trip, blank-append rejection without writes, unaffected second task,
completion and deletion; it checks no-write rejection then archiving and
deletion retain notes. The frozen B11 case separately covers its deletion rule,
baseline lifecycle and B01 priority. No behavior unrelated to obsolete
deletion assertions is waived.

## Restart and future boundary

Restore each B10 snapshot into a **new clean workspace**, independently verify
the complete inventory against its B10 checkpoint, run B11 preflight with the
unchanged frozen B11 case/fragment hashes, and run the R4 external regression
runner and internal tests on both B10 states using read-only observation and
disposable storage outside the workspaces. Capture fresh R4 predictions before
new isolated implementations; do not promote the quarantined R3 workspaces,
reuse R3 B11 predictions for scoring, or call R3 B11 a failure. Continue with
the pre-existing prospective freeze → preflight → prediction → implementation →
applicable regression/internal validation → classification → checkpoint and
independent restore sequence. Checkpoint only a valid classified state. Record
R4 oracle/replacement hashes with every B11+ result, and require an explicit
new prospective freeze before B12 and every later request. No Phase 6 before
B20 and final validation. Any uncovered conflict halts rather than weakening
another historical assertion.
