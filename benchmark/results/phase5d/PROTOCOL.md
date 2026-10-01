# Lykoi Phase 5D — PROTOCOL_AMENDMENT_001

This amendment follows the Phase 5B freeze and Phase 5C B03 halt. It applies
identically to Conventional and Lykoi. The original records remain immutable.
The historical `axiom` track identifier and historical path components are
serialized identifiers, not a project rename.

## Cleanliness and provenance

Implementation state is the byte inventory of **every regular file** in a
track workspace, including source, model, tests, historical fixtures, generated
application and its provenance manifest. Checkpoints and snapshots store these
bytes, and preflight requires an exact inventory match. Only byte differences
count; timestamp-only changes do not. Symlinks are forbidden. No unknown extra
file, log, compiler output, or new metadata is automatically ignored.

Infrastructure state comprises harness/oracle/evidence outside the workspace,
temporary test storage outside the workspace, and incidental interpreter
bytecode/cache created by executing observers. Python import bytecode is not an
achieved implementation artifact in this experiment: the application is run
from pinned `.py` files, and the `.pyc` files are reproducible import caches.
The amended harness **rejects** in-workspace `__pycache__`, `.pyc`, `.pyo`,
`.pytest_cache`, `.mypy_cache`, `.ruff_cache`, `.hypothesis`, and `.coverage*`
instead of omitting them from a manifest. If an implementation explicitly
needs one of these files, the run halts for a separate protocol review: the
name alone cannot confer exemption. Other caches, logs, OS metadata, temporary
files and generated files remain included and will fail an unchanged-state
check; the observer producing them must instead be redirected or repaired.
Generated executable and generated manifest always remain included.

Launch each track agent process with `PYTHONDONTWRITEBYTECODE=1` inherited by
all tool processes, or use the amended `phase5d.py run` wrapper for commands.
The wrapper additionally redirects `TEMP`, `TMP`, `TMPDIR`, and
`PYTHONPYCACHEPREFIX` to a disposable directory beside, never inside, the
workspace. `run --read-only` compares complete byte inventories before and
after an observation. The external regression runner enforces bytecode
suppression for itself and its application children, including frozen case
modules. Use `run --read-only` for validation, preflight, regression and
internal tests; do not use it for an implementation step expected to edit
source/model. Checkpointing always refuses residual caches, whichever track
produced them. Use the same settings for both tracks; a failing or unexpected
observer write is a protocol failure, not an implementation outcome.

## Version bridge and request outcomes

Format 1 checkpoints retain their original harness/oracle hashes. They cannot
be silently accepted by the format 2 preflight, which pins the amended harness
and oracle. `phase5d.py bridge` checks hard-pinned historical checkpoint and
snapshot hashes and every archive member against its original inventory. For
Conventional B03 it omits **only** the two named, verified Python import caches
from a new continuation workspace; it never rewrites the old archive. For
Lykoi it takes the valid B02 snapshot, verifies the preserved B03 attempt and
its `depends_on: ["B02"]`, and creates a *new* blocked B03 checkpoint without
an implementation edit. Both new checkpoints record the pinned predecessor
hash; the bridge is one-time, not a general cache filter.

`attempted` is request history, `achieved` is successful implementation history,
and checkpoint validity is independently established by file inventory,
snapshot/restore, and pinned protocol hashes. The amended checkpoint operation
requires a pinned predecessor for each non-baseline attempt, verifies an exact
attempt-history extension and requires **identical implementation bytes** when
the new outcome is `AXIOM_CAPABILITY_GAP` or `BLOCKED_BY_GAP`. Other failures
retain their actual changed bytes and require their own validity assessment.
A downstream `BLOCKED_BY_GAP` names its
earlier intrinsic gap; it is not another gap. `IMPLEMENTATION_FAILURE` and
`REGRESSION` retain their distinct outcome labels. A protocol failure has no
valid continuation checkpoint. The old Lykoi B03 failure stays quarantined.

Before any later request, independently restore each amended continuation
snapshot, run preflight with that checkpoint's pinned hash and prospective
case/profile hashes, and run accumulated applicable tests. This document does
not authorize B04 or change a requirement, success criterion, case, profile,
regression expectation, or benchmark metric. Agent transcripts and historical
run classifications remain untouched.
