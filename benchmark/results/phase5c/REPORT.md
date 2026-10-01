# Phase 5C — execution halted at B03

**Status: PHASE_5C_HALTED.** No B04–B20 request was executed. There is no
comparative analysis or overall result.

**Naming:** Lykoi is the project's name. Historical `axiom` file paths,
checkpoint track IDs, serialized keys, and the frozen
`AXIOM_CAPABILITY_GAP` classification are retained verbatim so their pinned
hashes and restorable evidence remain valid.

## B03 raw results

The B03 requirement, external case and unchanged-schema profile were pinned
before either track received the request; see [B03-FREEZE.md](B03-FREEZE.md).
Both B02 snapshots restored successfully; both B03 preflights passed. Before
the requests, the Conventional accumulated external suite passed 7/7 and its
internal suite 6/6. Lykoi passed 5/5 applicable external methods (two B02
methods skipped), and 31/31 internal tests. Both agents used OpenCode 1.18.32
and `openai/gpt-6-sol` in independent workspace/session pairs. Predictions
were recorded in JSONL before implementation sessions resumed.

| Track | Observed result | Post-run external regression | Internal | Achieved state | Evidence |
| --- | --- | --- | --- | --- | --- |
| Conventional | `SUCCESS`; B03 achieved | 9/9 pass, 0 skip, 0 failure | 8/8 pass | B01, B02, B03 | `B03-conventional-*.jsonl`, `B03-conventional-attempts.json`, `checkpoint-conventional-B03.json`, `snapshot-conventional-B03.tar` |
| Lykoi | Agent reported `BLOCKED_BY_GAP` (`depends_on: ["B02"]`); **run/checkpoint affected by `INFRASTRUCTURE_PROTOCOL_FAILURE`** | 5/5 applicable pass, 2 B02 skips, 0 failure; B03 not applicable | 31/31 pass | Last trustworthy achieved state B01 at Phase 5B B02 checkpoint | `B03-axiom-*.jsonl`, `B03-axiom-attempts.json`, `checkpoint-axiom-B03.json`, `snapshot-axiom-B03.tar` (quarantined evidence; not a valid continuation checkpoint) |

The B03 Lykoi requirement is hard-dependent on the absent B02 persisted tags
field. The agent documented this dependency and read-only model validation.
There is no B03 source/model edit in the Lykoi track. The classification of
the **execution record** is nevertheless protocol failure because the
purported blocked checkpoint violates the unchanged-bytes rule.

## Protocol defect and stopping point

`phase5b/FROZEN.md` rule 5 states: *"A gap leaves that track's achieved bytes
unchanged."* The Lykoi B02 checkpoint has 27 files. The B03 Lykoi checkpoint
has 35: its 27 original files have identical hashes, but eight
`src/air_compiler/__pycache__/*.cpython-314.pyc` files were added by normal
validation/imports in the isolated workspace. The frozen `workspace.py`
inventories and snapshots **every** file, including these runtime artifacts;
it does not enforce the gap unchanged-bytes invariant when checkpointing.
The B03 snapshot and its independent restoration both passed the harness's
hash checks, demonstrating that these checks alone cannot establish the
required checkpoint semantics. Do not use this Lykoi B03 checkpoint to start
B04. The extra files were neither deleted nor hidden, and the harness was not
modified. The affected Lykoi B03 run is preserved as protocol-failure evidence.
The last valid Lykoi checkpoint is Phase 5B B02 (B01 achieved; B02 gap). The
Conventional B03 checkpoint restored successfully and has 9/9 external
regression passing; it is the last valid Conventional checkpoint. Execution
stopped before preparing B04. Review and a new protocol version are required
before resuming the comparison.

## Session telemetry

Raw OpenCode JSONL events are in this directory. Spans are first-to-last event
timestamps (not full wall-clock duration); token counts sum provider-reported
step fields. Tool errors count failed tool-use events.

| Track / stage | Events | Tool calls (errors) | Span seconds | Input / output / cache-read tokens |
| --- | ---: | ---: | ---: | ---: |
| Conventional prediction | 12 | 5 (0) | 20.68 | 40992 / 392 / 72064 |
| Conventional implementation | 13 | 3 (0) | 61.80 | 2261 / 1239 / 165120 |
| Lykoi prediction | 24 | 13 (0) | 33.05 | 73371 / 977 / 205312 |
| Lykoi dependency assessment | 7 | 1 (0) | 11.79 | 1002 / 213 / 145536 |

Conventional changed two source files (`task_manager.py`,
`test_task_manager.py`), created two bytecode files, and reported no repair
attempts. Lykoi changed no application source or model and created eight
bytecode files. The agents reported no regeneration or retries. End-to-end
wall time, blinded review, and a complete separate raw stdout/stderr capture
for coordinator-run regression commands are **N/A / not captured**; the
reported pass/skip counts and commands are preserved here rather than
inventing missing telemetry. The application and bytecode file hashes are in
the B03 checkpoint manifests.

## Raw classification matrix

| Request | Conventional | Lykoi |
| --- | --- | --- |
| B01 | `SUCCESS` (validated Phase 5B, not rerun as a new request) | `SUCCESS` (validated Phase 5B) |
| B02 | `SUCCESS` (validated Phase 5B) | `AXIOM_CAPABILITY_GAP` (validated Phase 5B) |
| B03 | `SUCCESS`; 9/9 applicable regression | `INFRASTRUCTURE_PROTOCOL_FAILURE` on checkpoint; agent's observed `BLOCKED_BY_GAP` depends on B02; 5/5 applicable regression |
| B04–B20 | NOT RUN | NOT RUN |

## Frozen-input integrity

Rechecked SHA-256 against `phase5b/FROZEN.md`: baseline archive and manifest,
`workspace.py`, `regression.py`, Phase 5B validation JSON and both Phase 5B B02
checkpoint/snapshot pairs all matched. The preflights also verified all 20
requirement hashes and the accumulated frozen profile hashes. No frozen
benchmark artifact was modified. B03 prospective hashes and partial-run
evidence hashes are recorded in [FROZEN.md](FROZEN.md).
