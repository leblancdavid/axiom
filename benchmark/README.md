# Phase 5: comparative maintenance benchmark

Two task CLIs start from equivalent observable behavior. `conventional/task_manager.py`
is maintained as Python source. Track B's source of truth is the repository's
`air/task_manager.json`; `generated/task_manager.py` is its disposable executable.
Historical `experiments/` files are not benchmark working copies.

Run the external baseline oracle from the repository root:

```powershell
python -m unittest discover -s benchmark/harness -v
$env:PYTHONPATH='src'
python -m unittest discover -s tests -v
```

Read `baseline.md` for the external behavioral contract, `requirements/README.md`
for the ordered frozen requests, `harness/README.md` for the oracle protocol, and
`results/BASELINE.md` for provenance and evidence. B01–B20 have **not** been run.
The test harness treats both applications as subprocesses; it never imports
their internal modules or uses their internal test suites as the shared oracle.

## Execution protocol

Use the same AI model/configuration, requirement text, tool limits and time
budget for both tracks. Give Track A only its conventional working tree and
Track B only its model, compiler, generated output, and normal Axiom tools;
keep each track's experiment branch/working copy isolated. Do not reveal the
other track's solution to an agent. Preserve prompts, model/version, transcripts,
tool calls, elapsed wall time, token usage when available, git diff, test results,
and hashes at each step. Run B01, then B02, ... B20; accepted changes accumulate.

Track A instruction: "Implement the requested requirement in the conventional
Python application. Inspect the repository as needed. Python source is
canonical. Preserve prior accepted behavior and verify with the provided
external acceptance tests and relevant internal tests."

Track B instruction: "Implement the requested requirement in the Axiom task
application. The semantic model is canonical. Do not edit generated Python or
the frozen compiler/runtime/schema. Validate and regenerate normally. If the
frozen Axiom language cannot express the requirement, report
AXIOM_CAPABILITY_GAP with the missing concept and supporting validator or
generation evidence. Preserve prior accepted behavior."

Before each change, construct *backend-neutral* external acceptance cases from
that request and freeze them before either agent starts. Run all accumulated
cases on both tracks in fresh isolated directories and run their applicable
internal tests. Never rewrite an earlier baseline/requirement/oracle to make a
track pass. A compiler change during the primary run invalidates that Track B
step; separately studied extensions must be labeled as a different experiment.

If Track B reports a genuine gap, record it, leave B unchanged, and advance.
Where a later request needs a missing prerequisite, report BLOCKED_BY_GAP with
its ID; do not score that dependent request as a new failure or change the
requirement. Track A continues sequentially. Compare outcomes only on shared
achievable behavior; also report cumulative coverage lost to gaps.

For each step record: correctness against external oracle, old-case regressions,
attempts/rework, gap or blocked status, elapsed time and tokens/tool calls when
measurable, and separately a blinded reviewer judgment of change explanation
and inspectability (1–5 rubric: 1 cannot trace behavior; 3 traceable with
significant inference; 5 behavior, constraints, and impact readily traceable).
Mark missing telemetry N/A. Report raw evidence and denominators, not just an
aggregate score. A green validator or safety report is not a behavioral proof.
