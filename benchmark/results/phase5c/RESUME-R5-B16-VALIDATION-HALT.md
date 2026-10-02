# Phase 5C R5 — halt during pre-B16 validation

**Status: HALTED BEFORE B16-READY BOUNDARY AND BEFORE B16 EXPOSURE.**
Neither Conventional nor Lykoi has received, predicted, attempted, implemented,
classified or checkpointed B16. B17–B20 remain unprocessed. B01–B15/R4
historical results and evidence remain unchanged. Do not treat the prospective
R5 amendment as a validated executable continuation boundary.

## Completed checks

The frozen-case audit was reconfirmed: 24 active affected Conventional methods
(23 successful ownerless task creation; one B10 empty-owner migration) and five
active affected Lykoi methods. The two previously achieved B11/R4 dispositions
for baseline/B01 and two R4 B04/B07 dispositions remain in place on
Conventional. Composition-only fixture tests passed 3/3, including conditional
B16 selection (24 Conventional, five Lykoi) and independent track applicability.
The repository harness discovery suite passed 20/20 under Python `-B`.

Both B15 checkpoints/snapshots independently restored into fresh, separate
workspaces using `workspace_phase5e.py restore`; complete inventories and
generated artifacts checked: Conventional 2 files, Lykoi 27 files. Source
hashes match the B15 authoritative boundary:

| Track | Checkpoint SHA-256 | Snapshot SHA-256 |
| --- | --- | --- |
| Conventional | `b679b53012630ce4e2c29c6c4c1c8ebcb3c1e143b6d7323527350e8e572c0cf3` | `8f06f0f62a224139895b7fae48d14160a60e25ebd97a091679b05b3db3f048bc` |
| Lykoi | `c5110e4331bf24c2ac6f5889e1ba2a00ba93f9f354f7e9d1c4bd689d7c2b61a0` | `36e34184bd3d9cd9c65287d49d813838ca31197de6467b387defb1e1147c4ff5` |

At validation the repository HEAD was
`7833065ed702192ddd498a2e4fb4179741ad4b38`, Python 3.14.3,
OpenCode 1.18.32. R4 runner, R4 replacement, composer and checkpoint
validator match the effective R4 pin. The new R5 audit, runner, replacement,
fixture and amendment bytes are those recorded in `PROTOCOL_AMENDMENT_R5_B16.md`.

## Blocking protocol defect

Before executing either B15 accumulated external suite, R5 aborted with
`regression_phase5c_r5.py: error: R4 oracle changed`. The **actual** raw SHA-256
of `benchmark/harness/regression_phase5c_r4.py` is
`61830ce905deff3565180b3767e933f50e5c17bfef25ca4bcac41f9c4a706cb9`.
R5's frozen `R4_SHA256` constant inadvertently spells it
`61830ce905deff3565180b3767e933f50e5c17bfeef25ca4bcac41f9c4a706cb9`
(an extra `e`). The first is the value in the existing R4 execution pin;
the new amendment's R4 hash table repeats the erroneous second value. This
is an R5 transcription defect, not
evidence of R4 infrastructure drift or a B15 implementation failure. The
fail-closed check worked as intended; no external acceptance test executed.
The two restored B15 internal suites were not run because validation halted.
No B16-ready record has been issued.

## Required next decision

Correcting this constant changes the R5 runner bytes already declared frozen,
and therefore the amendment's pinned hash. A **new, explicit prospective R5
repair/re-freeze decision** is required before changing either; then restart
independent B15 validation on both tracks and record a fresh ready boundary
only after external/internal and harness tests all pass. Do not weaken the
hash check, relabel this as a B16 result, or proceed with B16–B20 from this
halted boundary.
