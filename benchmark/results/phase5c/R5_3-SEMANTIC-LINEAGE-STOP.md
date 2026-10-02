# R5.3 assertion lineage: preservation discrepancy — STOP

R5.3 is **unfrozen**; B17 is **unexposed**. This is a targeted finding, not an
exhaustive semantic inventory, assertion-level diff or equivalence certificate.
`R5_3-SEMANTIC-LINEAGE-DISCREPANCY.json` records the machine-readable findings.

## Active helper and replacement audit

The frozen baseline `regression.check_task` contributes more than one assertion
per invocation: exact profile fields, nonblank string ID, UTC timestamp and,
when B02 is achieved, tags-list type. The R5 runner wraps that helper with
one field-type assertion **per profile field per invocation** (seven on the
B01–B16 history, one on {B01,B04}). `upgraded` additionally asserts read-only
migration-required failure, unchanged bytes, migration count, sorted migrated
rows, each migrated task's expanded `check_task` invariants and migration
idempotence; its `count`, `payload` and `expected` arguments matter. Every
`call`/`self.call` contributes return-code/stderr/error-shape requirements,
including calls whose results are not explicitly asserted by their caller.

R4's B04 and B07 replacement bodies retain the source and notes value checks
respectively, while changing completed deletion to require an archive and
adding failed-delete/no-write checks. R5's ordinary replacement methods replay
their original code objects with `create --owner system` adaptation; its B10
owner and migration replacements instead have rewritten bodies, changing
unowned `""` expectations to `"system"`, adding user registration, and
retaining the explicit owner filtering and migration assertions. These
observations do **not** constitute a complete source-to-assertion map.

The B11 lifecycle replacement, however, omits four distinct baseline
assertion groups from `regression.py:99-104`: distinct IDs for the three created
tasks, `check_task` on each task, pending status for each task, and a null
default due date. The replacement at `cases/B11.py:24-72` has priority,
filtering, completion, archive-before-delete, error and no-write checks, but
none of those four groups. The B11 frozen amendment says it covers the
remaining lifecycle behavior. R5's `DeletionLifecycle` replays the B11 body,
so it does not restore those lost assertions. An assertion in another active
test would require a separately evidenced semantic-identity and precondition
comparison; a passing suite or a similarly named check is not proof of that.

There is also a reproducibility hazard for an assertion inventory produced in
one Python process: every invocation of `regression_phase5c_r5_1.build_suite`
wraps the *current* `regression.check_task` in another closure. A subsequent
suite may execute assertions for earlier profiles as well as its own profile.
The new focused fixture confirms this nesting and restores the global helper
after its probe. Any future authoritative comparison must isolate process
state or account for every wrapper invocation explicitly.

The preservation discrepancy remains unreconciled against the amendment's
stated intent, so the required **zero unexplained semantic differences** has
not been established. Stop here: no R5.3 freeze, B17 replacement construction,
B17 exposure or B17 execution. The final fresh B16 restores and full semantic
inventory/hash/diff are pending a completed reconciliation, rather than
misrepresented as a successful gate.
