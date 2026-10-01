# Lykoi Phase 5D — PROTOCOL_AMENDMENT_001

**Verdict: PHASE_5C_RESUME_READY (preparation only).** Phase 5C remains halted
pending explicit authorization. No B04–B20 requirement was executed. This is
not a comparative result.

## Provenance and root cause

Phase 5B froze a byte-complete workspace manifest and the rule that a gap
leaves achieved bytes unchanged. Phase 5C B03 then halted, with the original
Lykoi B03 checkpoint quarantined as `INFRASTRUCTURE_PROTOCOL_FAILURE`.
The Lykoi agent's recorded command was `python -m air_compiler.cli validate
air/task_manager.json` with `PYTHONPATH=src`, without `-B`. Python 3.14 imported
the compiler's `__init__`, `cli`, `generator`, `model`, `parser`, `planning`,
`semantics`, and `validator` modules; it wrote eight
`src/air_compiler/__pycache__/*.cpython-314.pyc` import caches in the agent's
workspace. The validator only read the model. The eight exact paths and hashes
are in the quarantined checkpoint. All 27 valid B02 implementation-file
hashes remained equal. Subsequent regression/internal tests can import the
same modules; the original checkpoint mechanism then captured the caches as
if they were implementation changes. Git ignores them, but the frozen
inventory correctly included every file and exposed the protocol defect.

Before changing the harness, a clean disposable restore of the pinned Lykoi
B02 checkpoint (27 files) ran the same unsuppressed validation command. It
exited 0, produced the **same eight cache paths**, increased the inventory to
35 files, and changed zero of the original 27 hashes. See
[`REPRODUCTION.json`](REPRODUCTION.json) for the original command and every
reproduction file hash. Bytecode bytes differed from the quarantined run
because the restored absolute workspace path differed. Nothing in the
quarantined workspace, snapshot, or checkpoint was changed.

## Observer-effect audit and classification

| Activity / artifact | Classification and treatment |
| --- | --- |
| Track source, Lykoi model/compiler/runtime, tests, historical fixtures | Implementation state: full byte inventory; no omissions. |
| Generated executable and generated provenance manifest | Implementation state even though generated; retain their hashes and Lykoi source/model-to-output check. |
| `__pycache__`, `.pyc`, `.pyo`, Python test/coverage caches caused by executing validation/tests | Infrastructure state only when proven to be interpreter/test side effects. Prevent their creation; reject any observed in a checkpoint rather than silently ignoring them. |
| Oracle fixtures, `tasks.json`, test output and temporary storage | External regression and internal tests use temporary working directories outside the track workspaces; redirect process temporary directories outside as well. Such test data is infrastructure state, not implementation input. |
| Checkpoint JSON/tar, command output, transcript/logs and Phase 5D evidence | Infrastructure state outside track workspaces; capture separately. A log placed inside a workspace remains an unexpected tracked file. |
| Explicit compiler generation, model-plan application, staging and generated metadata | Generated files/model/manifest are implementation state; temporary staging during a deliberate apply is not automatically exempt. The amended observer wrapper is read-only only for observation, not implementation steps. |
| Unknown package-manager/compiler caches, OS metadata, logs, scratch files, `.tmp` files | Ambiguous: no general exclusion. Any added regular file changes the inventory and requires explicit provenance review; redirect observer output outside the workspace. |
| Timestamp-only file changes, empty temporary directories | No change to the byte inventory; timestamps are not implementation decisions. Remaining empty directories contain no checkpointed file bytes. |

Workspace construction and restore write the known pinned projection/snapshot
and check the result. Preflight hashes files and checks Lykoi generation via an
already bytecode-suppressed subprocess. Snapshot hashes and archives files
without importing application code. The Phase 5B replay ran its child Python
commands with `-B` and `PYTHONDONTWRITEBYTECODE=1`; its B01/B02 checkpoint
inventories contain no caches. The frozen baseline oracle runs applications
by path with test storage outside workspaces; running that historical oracle
without suppression can leave cache files in the *repository*, but those are
not track checkpoints. Internal `unittest` discovery **can** write caches in a
track workspace when launched unsuppressed. The shared regression runner and
the frozen B03 case run application subprocesses; the amended runner sets the
inherited bytecode flag without changing any test or assertion. The
Conventional B03 agent ran unsuppressed `python -m unittest` and its checkpoint
includes two caches for `task_manager` and `test_task_manager`. Thus the
observer effect affected both tracks' checkpoint inventories, although only
the Lykoi blocked/checkpoint invariant forced the halt.

## Repair and validation

[`PROTOCOL.md`](PROTOCOL.md) defines track-independent cleanliness. The amended
`workspace.py` rejects recognized in-workspace Python/test caches instead of
excluding them; it retains every other implementation file in checkpoint and
snapshot integrity. It binds each new request checkpoint to its pinned
predecessor and enforces identical implementation bytes for a capability gap
or dependency block. `phase5d.py run` supplies bytecode suppression and
out-of-workspace temporary directories to observation or agent commands;
`--read-only` verifies before/after byte inventories. The amended shared
regression runner propagates suppression to all frozen-case subprocesses.

On a **second**, clean disposable restore of Lykoi B02, the amended read-only
wrapper ran validation (exit 0), the applicable external regression (5/5
passed, 2 B02 skips), and internal tests (31/31 passed). Each command retained
the exact 27-file implementation inventory. On the bridged Conventional B03
workspace, amended external regression passed **9/9**, no skips/failures, and
internal tests passed **8/8**, with unchanged implementation bytes. The new
continuation snapshots restored independently: 27 Lykoi and 2 Conventional
files, with exact hashes and no caches. The six integration/negative tests in
`test_phase5d.py` passed. They detect changes to Conventional application
source, the Lykoi model, generated executable and manifest, and the historical
fixture; an additional meaningful generated file changes the inventory.
They also confirm that injected import caches are rejected, external scratch
activity is harmless, and an altered predecessor hash or a changed blocked
workspace cannot form a valid blocked checkpoint. They also confirm that
amended preflight accepts a clean B02-format continuation for the already
frozen B03 case/profile. Existing external tests and
success criteria were not weakened.

## Asymmetry and B03 disposition

The Phase 5B B01/B02 records for both tracks have cache-free snapshots; their
replay explicitly suppressed bytecode. Both Phase 5C B03 workspaces acquired
incidental Python caches: eight on Lykoi, two on Conventional. They were
**captured**, not ignored or removed, in both old B03 checkpoint/snapshot
pairs. The implementation bytes and regression results were unaffected, but
the gap/checkpoint rule made the Lykoi B03 continuation invalid. The old
Conventional B03 checkpoint captured extra infrastructure bytes; the amended
bridge checked its old hashes and entire archive, then omitted exactly its two
named, verified import caches in a **new** checkpoint. Its two source/test
hashes match the old B03 implementation and 9/9 external cases passed under
the amended observer-safe execution. **Conventional B03 remains `SUCCESS`; no
implementation rerun is necessary.**

The Lykoi agent transcript already establishes the B02 prerequisite and
reports `BLOCKED_BY_GAP` without model or source edits. Rather than supplying
a new implementation attempt or retroactively changing the quarantined B03,
the bridge uses the last valid B02 snapshot and the preserved B03 attempt. It
retains the Phase 5B B02 evidence citation (the halted run abbreviated this
citation), records `depends_on: ["B02"]`, retains only B01 in `achieved`, and
requires its 27 implementation hashes to equal B02 exactly. **The semantic
B03 outcome is a downstream dependency block, not a new intrinsic capability
gap or success.** The original B03 checkpoint remains a historical protocol
failure; the separately pinned Phase 5D checkpoint is the valid continuation.

The repair changes no request, case, schema profile, scoring criterion, or
benchmark metric. No track receives additional feature information or an
implementation edit. It repairs an asymmetric *validity effect* by applying
the same clean-workspace and predecessor rules to both tracks. Historical
runtime overhead and telemetry are not silently normalized.

## Resume point and freeze

The new continuation pair is `checkpoint-conventional-B03.json` plus
`snapshot-conventional-B03.tar`, and `checkpoint-lykoi-B03.json` plus
`snapshot-lykoi-B03.tar`. Both are in this directory and pinned in
[`FROZEN.md`](FROZEN.md), along with the amended harness, rules, validation
test, original Phase 5B/5C references, and reproduction evidence. Preserve the
provenance chain:

**Phase 5B frozen protocol → Phase 5C B03 halt → Phase 5D
PROTOCOL_AMENDMENT_001 → Phase 5C resume (only upon authorization).**

The B03 observer effect is understood and reproduced, the repaired runs do
not contaminate implementation state, real implementation edits remain
detectable, the rule is symmetric, frozen historical evidence is unchanged,
and both continuation checkpoints are independently restorable. Therefore:

**PHASE_5C_RESUME_READY**
