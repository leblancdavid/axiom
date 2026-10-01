# Phase 5A pilot inputs (frozen before either agent ran)

Pilot requirements are the verbatim content of:

* `benchmark/requirements/B01.md`: SHA-256 `b7b2d714db5cee566e9e55982dd4c4d95d3d57f0c341e04ba1e15c24e9a8e94d`
* `benchmark/requirements/B02.md`: SHA-256 `8a76e276240fa840c473be60a8e7ed0e10bd0c165426b1bfc84741e69872032b`

The backend-neutral pilot acceptance runner is
`benchmark/harness/pilot_oracle.py`: SHA-256
`329e693dbb7103c8556883b39624be5e65aeaf0e12c5d94e6369ae6744984281`.
It runs each CLI as a subprocess with independent temporary persisted state.
Call with `--app PATH --through B01` or `--through B02` (the latter includes
B01 regression cases). This runner lives outside both agent working copies.

Restorable application baseline snapshot:
`C:\Users\lblan\AppData\Local\Temp\opencode\axiom-phase5a\snapshot`.
Isolated conventional and Axiom application workspaces are its siblings. Prior to B01,
SHA-256 of the copied conventional application, Axiom model and Axiom generated
artifact matched the snapshot; a disposable copy of the Python source and a
disposable copy of the Axiom model were each deliberately perturbed and
restored from the snapshot with hashes matching again. The original repository
and frozen snapshot were not perturbed.

**Setup correction:** this snapshot omitted `experiments/`, which the Axiom
internal tests reference. The first Axiom run from that incomplete workspace
is retained as a method failure. A corrected Axiom workspace was built from
the same unmodified application snapshot plus `experiments/`, `docs/`, and
`README.md` from the baseline repository. It passed all 31 baseline tests
*before* the fresh Axiom B01 run. The corrected run's predictions were saved
anew before its edits. The historical files are available unchanged from
Phase 4 commit `7e1d5eb`.

The Phase 4 parent commit alone is insufficient to recover the full snapshot:
the conventional baseline and benchmark inputs are uncommitted. Recovery uses
the snapshot and the hashes in `benchmark/results/BASELINE.md`.

For durable recovery, after the run the unchanged canonical baseline was also
packed into `benchmark/results/pilot/baseline-snapshot.tar` (SHA-256
`71bd1692adb5b34de2e99fca40da657b20b2e838e9816bdb0d801cbdca44eb13`).
It includes tracked Phase 4 files and uncommitted baseline benchmark files,
but no pilot changes. An independent extraction matched the recorded
application and requirement hashes, passed the 3 baseline oracle tests and
the 31 Phase 4 tests. This later durable archive supplements—not replaces—the
disposable-copy restore rehearsal performed before B01.

Pilot failure categories: PLANNING, PLAN_VALIDATION, MODEL_VALIDATION,
GENERATION, STATIC_CHECK, INTERNAL_TEST, EXTERNAL_ORACLE, MANUAL_DISCOVERY.
An expected failed probe is still recorded with its discovery stage; neither
initial failures nor repairs are discarded when a final check passes.
