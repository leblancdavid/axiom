# Phase 5C resume halt — B04 oracle/profile incompatibility

**Status: PHASE_5C_HALTED.** No B04 implementation or prediction session was
started on either track. No B04 acceptance case or schema profile was frozen,
no B04 workspace was restored, and no B04 checkpoint was created. The original
B03 halt evidence in `REPORT.md` and `FROZEN.md` remains unchanged.

## Protocol failure discovered before B04 preflight

The Phase 5B protocol requires one backend-neutral B04 external case and one
current-schema `profiles/B04.json`, frozen before either track receives B04.
The frozen shared runner (`benchmark/harness/regression.py`) selects the profile
using the *last achieved request ID* and requires its `fields` to match every
returned task **exactly** (`fields()` and `check_task()`); it also requires a
single `schema_version` for the current storage fixture. A schema profile is
not selected or interpreted according to the full achieved-request history.

The valid Phase 5D B03 continuation checkpoints have different achieved
histories:

| Track | Achieved entering B04 | Current task schema |
| --- | --- | --- |
| Conventional | B01, B02, B03 | Version 4, including B02 `tags` |
| Lykoi | B01 | Version 3, without B02 `tags` |

B04 independently requests a new `source` field and its migration default.
If both tracks implement B04 successfully, their achieved lists both end in
`B04`, so the unchanged runner selects the **same** B04 profile for each.
Conventional must preserve its achieved `tags` field and migrate from its
version-4 schema; Lykoi must preserve its actual B01 state without inventing
unachieved B02 `tags` and migrate from its version-3 schema. A single fixed
`fields`, `schema_version`, and migration-default contract cannot describe
both legitimate states. A Conventional-shaped profile would falsely fail a
successful Lykoi B04 run; a Lykoi-shaped profile would falsely fail a
successful Conventional B04 run. The runner also applies the profile to
baseline and previously achieved regression cases, not just to the new case.

This is an **infrastructure/protocol defect**, not a result for either
implementation. It cannot be fixed by choosing one track's profile, declaring
B04 dependent on B02, equalizing the tracks, weakening exact assertions, or
changing the frozen runner while the benchmark is running. The Phase 5D
amendment addresses observer-created caches, not divergent schema profiles.
Further execution needs separate protocol review; no amendment is made here.

## Last valid continuation and affected evidence

- Conventional: `benchmark/results/phase5d/checkpoint-conventional-B03.json`
  (SHA-256 `cf46300fb7fd904a6f42629a049e85bf4af64a7283d42729dd19875156b65999`)
  and `snapshot-conventional-B03.tar`
  (SHA-256 `1945902e524fc6e3b30d76230ea4c4c1b96a232dc0b60724ea82c2cdd9bf171c`).
- Lykoi: `benchmark/results/phase5d/checkpoint-lykoi-B03.json`
  (SHA-256 `0648016ced11120e57668fb5c9bf824694a450e2463f0ffb68934d962a59a107`)
  and `snapshot-lykoi-B03.tar`
  (SHA-256 `b340a563189d55b71c10d3513b6c740bf9ecb01fdd31711d6faae9df0c1473a7`).
- Affected request: B04, both tracks, at prospective oracle/profile freeze;
  `benchmark/requirements/B04.md` is pinned at
  `2c2e9e3787d53eb45df7b4b48362db2217e62c165dedda38222f5561cd859221`.
- Supporting protocol evidence: `benchmark/results/phase5b/FROZEN.md`
  (rules 2–5), `benchmark/results/phase5b/REPORT.md` (profile semantics),
  `benchmark/results/phase5d/PROTOCOL.md`, the two Phase 5D checkpoint JSON
  files, and `benchmark/harness/regression.py` (`fields`, `check_task`,
  `test_baseline_overdue_fixture`, and `main`).

No B04 transcript, prediction, measurement, implementation, regression, or
checkpoint exists. The B01–B03 classifications and the quarantined original
Lykoi B03 checkpoint retain their historical provenance.
