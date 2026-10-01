# Lykoi Phase 5E freeze — capability-aware oracle repair

**Status: PHASE_5C_RESUME_READY (preparation only).** B04 has not been
executed. SHA-256 entries are raw file bytes. This new freeze does not alter
the earlier Phase 5C halt or the Phase 5D continuation records.

| New file (repository-relative) | SHA-256 |
| --- | --- |
| `benchmark/harness/capability_profile.py` | `cd0d318f5e7dd3dc2cdac7c93a0cd8c822c35cf53d83c365093a6c5e6971fb50` |
| `benchmark/harness/regression_phase5e.py` | `d59392d4f535800491fd047540292888038996b08a8c039078724879cd4791be` |
| `benchmark/harness/workspace_phase5e.py` | `26b593844adf95e8f21fffddfde57e4ff39c46190117c35a7ca4333e48baf6de` |
| `benchmark/harness/test_phase5e.py` | `e4c1f45ad08108acb40986b583557de0473e84cb8dfddb1c15579e9a376246a2` |
| `benchmark/harness/capabilities/B01.json` | `15118f0c52482f2eb1c31be462f6392ac8b11ef0234883740ef12eefe9a885c1` |
| `benchmark/harness/capabilities/B02.json` | `71aa0309e092ec72d8f6b23bfee6d4f7f8420f8a5d5ae380eb01d5777323d456` |
| `benchmark/harness/capabilities/B03.json` | `11df5bd2f5cc06780ac6c21263b86c3a084aa14fefbe65f3e1c9beb05f62cb5e` |
| `benchmark/harness/capabilities/B04.json` (prospective schema contribution only) | `597a702c6f860330938ecbe982c0bb8adc5f6d2640c0924e9c4619bc60b5b982` |
| `benchmark/results/phase5e/PROTOCOL.md` | `3ffca511e174f371e333faddb589d4fc02c4a75c20c480351b9e35b42b27a89f` |
| `benchmark/results/phase5e/REPORT.md` | `8651ff1689ff144bc612a62294f426656fa7349b13159761d489a0ee3160f1de` |
| `benchmark/results/phase5e/checkpoint-lykoi-B03.json` | `2a0d2d6cc44ba75e8677e9bd419d52ad2dac1af3ab0d5567a435e4716a5b15c0` |
| `benchmark/results/phase5e/checkpoint-conventional-B03.json` | `fec41a9a3e26bfeab1175faa6eab62567abbcd1ef96e4b4e02035adecf3290fe` |

Format-3 B03 checkpoints retain the Phase 5D B03 implementation bytes and
attempt histories. Their snapshot files are the unchanged Phase 5D snapshots
at `b340a563189d55b71c10d3513b6c740bf9ecb01fdd31711d6faae9df0c1473a7`
(Lykoi, 27 files) and
`1945902e524fc6e3b30d76230ea4c4c1b96a232dc0b60724ea82c2cdd9bf171c`
(Conventional, 2 files). Independent restore with format-3 records passed for
both tracks. Their `previous_checkpoint_sha256` references the pinned Phase
5D checkpoints (`0648016ced11120e57668fb5c9bf824694a450e2463f0ffb68934d962a59a107`
and `cf46300fb7fd904a6f42629a049e85bf4af64a7283d42729dd19875156b65999`).

## Verified predecessor integrity

The original Phase 5B `FROZEN.md` matched
`21614bdcf521d74ca2032e57ba45a80697b5a6eaf5fa792b6903e6929a7c664d`;
the original Phase 5C halted `FROZEN.md`/`REPORT.md` matched
`98610edc07bb0990d74583b64b4e23d9d52d89512ed744530015f6dc15e999c6`
and `e92536507ecd114d55f042f2d40bb93e0c6c56c374410e29468d3d66293046c5`.
The new Phase 5C resume-halt record matched
`5c497e0496c58982b40c4b998c86f8a5c4ae8225ac12347fd3daf7541cac5b13`.
Phase 5D `PROTOCOL.md`/`REPORT.md` matched
`00d992c6c12888ff64086e4dd18d78f89340f78da138a4c91a2ca26bcf96b2bf`
and `7266d83c38cb171071f67d3ce0ebbc7f416bc26975f0b12173cae711ab5ed575`.
The Phase 5D harness/oracle/observer hashes matched
`beac945e0102e7e78b15fe7f6e3d8c88bae512f32bfcbf1cbbde9d5fae883e50`,
`8fa1ff4e8b627cc3c334a099151b97647219abac41949a3a3d32c5e9da2fc596`,
and `cfc209ab50c01e67b739bbbc9c6fc7854e77fcd2913b1fe57cbef03ee6a98900`.
The baseline archive/manifest and B03 case/profile retained the hashes pinned
in Phase 5B/5D. No historical file was changed.

## Read-only validation

`python -B -m unittest discover -s benchmark/harness -p 'test_phase5*.py' -v`
passed 13 integration tests (six Phase 5D, seven Phase 5E) with bytecode
suppression and temporary storage outside implementation workspaces. The
Phase 5E replay passed Lykoi 5/5 applicable external cases, 31/31 internal
tests, and Conventional 9/9 external cases, 8/8 internal tests. The observed
implementation inventories were unchanged. The two format-3 B03 checkpoints
were then separately restored with the original snapshots and independently
verified at 27 and 2 files.

**Resume boundary:** freeze and pin the B04 external case before B04
preflight. The B04 schema contribution above is already pinned; no B04
prediction, agent implementation, acceptance case or B04 checkpoint exists.
Do not proceed to B04 without explicit resume authorization.
