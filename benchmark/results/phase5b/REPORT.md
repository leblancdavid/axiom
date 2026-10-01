# Phase 5B — protocol hardening and validation

**Verdict: BENCHMARK_READY (protocol only).** This is neither a comparison of
the implementations nor a rerun of independent benchmark agents. B01/B02
validation replays the archived Phase 5A changes in *new* verified workspaces;
no B03 request has been executed. See `validation.json` for command-level
evidence and `FROZEN.md` for pinned bytes and execution rules.

## Diagnosis and corrections

The first pilot Axiom workspace came from a selective copy that omitted
`experiments/`; `tests/test_compiler.py::test_index_and_diff` reads
`experiments/task_manager-v0.2-before-priority.json`. The resulting failure
and test repair were infrastructure artifacts, not Axiom defects. The corrected
pilot workspace and the restorable archive retained the fixture. Phase 5B
constructs workspaces from that SHA-256-checked archive, enumerates and hashes
**all 56 archive files**, and verifies the declared track projections (27 Axiom
files including the historical fixture; one conventional source file). It
rejects missing, altered, extra, or symlinked files, wrong track contents, and
stale Axiom generated artifacts. Snapshots and checkpoints are verified against
each other on restore, and preflight refuses a non-pinned checkpoint hash.
Neither track can read the other track's application from its working tree.
Requirements and regression tooling are held outside both trees.

The original shared oracle's exact seven-key result assertions and seven-key
migration expectations are valid at schema 3, but not after B02 legitimately
adds `tags: []` and moves Conventional to schema 4. Likewise, loading a raw
schema-3 fixture without migration is not a legitimate post-B02 read. The new
external oracle preserves **all three** baseline scenarios: lifecycle,
filtering, failure/no-write behavior; explicit version-1/version-2 migration
and corruption; and the overdue boundary fixture. It also preserves the two
B01 and two B02 cases. The selected schema profile specifies the *full*
current task shape, current storage version, and only explicitly permitted
migration defaults. Historical records remain at their original version:
the oracle checks `migration_required` with unchanged bytes, calls `migrate`,
then checks every historical value plus specified defaults. A separate
current-version copy exercises the original overdue semantics. Consequently
an expanded schema cannot generate an exact-shape false failure, while
dropping a field, changing an old value, omitting a required new field,
breaking migration, or changing behavior still fails. The same cases and
profiles apply to both tracks; the oracle imports neither application.

The stable runner accepts future append-only, frozen `profiles/Bnn.json`
schema profiles and `cases/Bnn.py` external case modules (the latter must
expose `cases(app, profile, achieved)` returning a `unittest.TestSuite`).
These are created and hashed *before* either track receives that request.
Preflight requires the prospective module's pinned hash from B03 onward and
checks the hashes of all previously achieved modules. A module may declare
dependencies in its own cases. A request-specific schema profile must be
frozen even when the schema is unchanged; its contents then repeat the last
profile. B01 and B02 cases are part of the frozen runner. No B03 profile or
case module has been created here.

## Validation (pilot artifact replay)

Each stage started from a new archive projection or from a verified checkpoint.
The baseline preflight ran **before** B01 replay. At B01, Conventional's exact
priority edit and internal test were recovered from its preserved transcript;
Axiom's pilot model was checked to differ only in `type_priority` and
`inv_priority`, copied as canonical input, then validated and regenerated using
the frozen compiler. Conventional B02 source and tests came from the preserved
pilot output; its source hash was checked. Axiom B02 left the B01 workspace
unchanged: the frozen model and runtime cannot represent a string-array field,
repeat-collect flags, or trim/deduplicate and migrate `[]` through model-only
changes. This is still `AXIOM_CAPABILITY_GAP`. Its attempted B02 features were
probed separately; their failure is not counted as a regression of B01.

| Checkpoint | Applicable external cases passed | Internal tests | Result |
| --- | ---: | ---: | --- |
| Conventional baseline | 3/3 | No baseline internal suite | Baseline valid |
| Axiom baseline | 3/3 | 31/31 | Baseline valid |
| Conventional B01 | 5/5 | 3/3 | SUCCESS |
| Axiom B01 | 5/5 | 31/31 | SUCCESS; model validated and generated |
| Conventional B02 | 7/7 | 6/6 | SUCCESS; baseline + B01 + B02 retained |
| Axiom B02 attempt | 5/5 applicable | 31/31 | AXIOM_CAPABILITY_GAP; baseline + B01 retained |

All six snapshots were independently restored and checked against their
checkpoint manifests. Axiom B01 and B02 snapshots have the same hash. A forced
B02-as-achieved probe against Axiom fails as expected (eight failure events,
including subtests); the normal Axiom run correctly reports the two B02 case
methods as not achieved. An injected change to Conventional's exact-HIGH
filter causes three oracle failure events, establishing that semantic
regressions are detected. Fourteen negative preflight probes (seven per
track) reject missing or modified fixtures/source, unexpected files, stale
generated output, wrong track, wrong request, and wrong checkpoint hash.
The original repository's frozen three-case baseline oracle also passed.

## Outcome and continuation rules

`SUCCESS`: all new and previously achieved applicable external cases pass and
the step is checkpointed. `IMPLEMENTATION_FAILURE`: the requested new behavior
is unmet without demonstrated language-level impossibility. `REGRESSION`:
previously achieved applicable behavior fails (takes precedence over a new
feature failure). `AXIOM_CAPABILITY_GAP`: evidence shows the frozen permitted
Axiom model/validator/compiler/runtime cannot express or produce the request
without an out-of-scope capability change; do not patch generated Python.
`INFRASTRUCTURE_PROTOCOL_FAILURE`: invalid archive, fixture, harness,
requirement, oracle/profile hash, workspace, or preflight; **abort before the
agent request** and do not score implementation. `INVALID_RUN`: missing or
untrustworthy execution evidence, or a violation of track permissions; do not
score implementation. An earlier protocol failure makes its associated run
invalid, not an implementation failure. `BLOCKED_BY_GAP` records a request
whose explicitly named prerequisites are prior gaps, rather than a fresh
failure; its checkpoint must list those gap IDs. A gap alone never stops the
sequence: advance from the bytes actually achieved, not an imagined repaired
state. Record both case-level results and a single primary classification.

## Remaining boundaries

This validation **replays** Phase 5A artifacts; it does not claim new blinded
agent attempts or that future B03–B20 cases have already been written. Their
acceptance modules and schema profiles must be frozen for *both* tracks before
each request; new requirements may explicitly supersede old behavior, and
such applicability must be recorded rather than retroactively changing old
cases. Versioned schema profiles and case modules are external protocol data,
not permission to change this runner or earlier cases. The absolute temporary
paths and timing in `validation.json` are incidental; source/snapshot hashes,
command exit codes and results are the reproducible evidence. The source
repository contains uncommitted benchmark inputs, so the pinned archive—not
the Phase 4 Git commit by itself—is the canonical starting state.
