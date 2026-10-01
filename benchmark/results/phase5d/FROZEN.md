# Lykoi Phase 5D freeze — PROTOCOL_AMENDMENT_001

**Status: PHASE_5C_RESUME_READY.** This is an amendment freeze, not a rewrite
of Phase 5B or the halted Phase 5C evidence. No B04 requirement was executed.
SHA-256 values below are raw file bytes. Historical `axiom` in pinned paths
and serialized track identifiers remains a literal archival identifier.

## Amended protocol and evidence

| File (repository-relative) | SHA-256 |
| --- | --- |
| `benchmark/harness/workspace.py` | `beac945e0102e7e78b15fe7f6e3d8c88bae512f32bfcbf1cbbde9d5fae883e50` |
| `benchmark/harness/regression.py` | `8fa1ff4e8b627cc3c334a099151b97647219abac41949a3a3d32c5e9da2fc596` |
| `benchmark/harness/phase5d.py` (safe execution, pinned bridge) | `cfc209ab50c01e67b739bbbc9c6fc7854e77fcd2913b1fe57cbef03ee6a98900` |
| `benchmark/harness/test_phase5d.py` (validation/negative tests) | `dab90c98bb33832ac6ac2eedbb5de6206b789db4df324206d9ca4a9e4bde5eb5` |
| `benchmark/results/phase5d/PROTOCOL.md` (cleanliness rule) | `00d992c6c12888ff64086e4dd18d78f89340f78da138a4c91a2ca26bcf96b2bf` |
| `benchmark/results/phase5d/REPRODUCTION.json` | `3226734cdb0b1770e45219282f468e4f0fbc4f34b706cb830183c37404b7c4ed` |
| `benchmark/results/phase5d/REPORT.md` | `7266d83c38cb171071f67d3ce0ebbc7f416bc26975f0b12173cae711ab5ed575` |
| `benchmark/results/phase5d/checkpoint-lykoi-B03.json` | `0648016ced11120e57668fb5c9bf824694a450e2463f0ffb68934d962a59a107` |
| `benchmark/results/phase5d/snapshot-lykoi-B03.tar` | `b340a563189d55b71c10d3513b6c740bf9ecb01fdd31711d6faae9df0c1473a7` |
| `benchmark/results/phase5d/checkpoint-conventional-B03.json` | `cf46300fb7fd904a6f42629a049e85bf4af64a7283d42729dd19875156b65999` |
| `benchmark/results/phase5d/snapshot-conventional-B03.tar` | `1945902e524fc6e3b30d76230ea4c4c1b96a232dc0b60724ea82c2cdd9bf171c` |

The Lykoi continuation snapshot is byte-identical to the valid Phase 5B B02
snapshot, as required for a dependency block. Its checkpoint is different
because it records B03 attempted and its predecessor/version metadata.
Conventional B03 contains precisely the historical B03 implementation's
two source/test files; its new archive omits only the separately verified
historical Python import caches. Neither original B03 archive was modified.

## Frozen predecessor and oracle references

Phase 5B `FROZEN.md` itself: `21614bdcf521d74ca2032e57ba45a80697b5a6eaf5fa792b6903e6929a7c664d`.
Its original hashes remain the authoritative frozen-protocol references:

| Historical file | SHA-256 |
| --- | --- |
| `benchmark/results/pilot/baseline-snapshot.tar` | `71bd1692adb5b34de2e99fca40da657b20b2e838e9816bdb0d801cbdca44eb13` |
| `benchmark/results/phase5b/baseline-manifest.json` | `0c4488cf3bdff9dbe6e62baa1124f91222bedc1e94f96121a18d83f9abd1feca` |
| `benchmark/harness/validate_phase5b.py` (historical replay script; unchanged) | `e7b3bf24194a632d1b961ed7b6547f80ca9d845b66deb071b39b784379ba00a4` |
| `benchmark/results/phase5b/validation.json` | `722bba7eeb99e8d5728a716e2f21791276d362ea4e9229db5d8b2f89adb17b25` |
| `benchmark/results/phase5b/checkpoint-axiom-B02.json` | `31dd8302529cdfabd0609ca7b3dddd64ca48764f1ae0255dfcb79d91a400ba90` |
| `benchmark/results/phase5b/snapshot-axiom-B02.tar` | `b340a563189d55b71c10d3513b6c740bf9ecb01fdd31711d6faae9df0c1473a7` |
| `benchmark/results/phase5b/checkpoint-conventional-B02.json` | `a57c38e0681a0fce5e43b09cdf32ea3a348217b6f5ab6ae03e918b3482fc5e7a` |
| `benchmark/results/phase5b/snapshot-conventional-B02.tar` | `0a125c94bcc364f50040c3299ebba254a2f68c9c465e04de0168749fec542bad` |
| `benchmark/requirements/B03.md` | `56c6ac4c187962c71d5866b27f9568c8b6de055a0bab074896ef41b61a554630` |
| `benchmark/harness/cases/B03.py` | `dd99843e8ff79c0f9c3d174671b9a54e9becf64ce8bca19e9ff8e47fa14ae9df` |
| `benchmark/harness/profiles/B03.json` | `46ff02e3ff6ea48a7990c2f522fb9fa7bbefcab3c88550be007e0c2c1b75972f` |

The original Phase 5C `FROZEN.md` remains at
`98610edc07bb0990d74583b64b4e23d9d52d89512ed744530015f6dc15e999c6`;
its `REPORT.md` remains at
`e92536507ecd114d55f042f2d40bb93e0c6c56c374410e29468d3d66293046c5`.
Its original quarantined Lykoi B03 checkpoint/snapshot hashes remain
`c81c5187ac14aee7052a07b370e1678d75e7fc0ac8eac1490ba052f80c8beb80`
and `e89b703b4a8f45aff553241ac2ae09bd08eef671d45b1aa23862f109510f8df1`.
The old Conventional B03 checkpoint/snapshot remain
`727950c4e89b295333ab819eb23e76937b05775d5557e4d287f4fd0041686d19`
and `58e7f75af2a4b57327a2ca0cce3f91ddb778a824a97b3b5765ffc5119e3f8f82`.

## Continuation boundary

The amended continuation checkpoints have format 2 and pin the amended
`workspace.py`, amended `regression.py`, original baseline manifest,
requirements, achieved case hashes, predecessor checkpoint and every
implementation file. Restore by passing the appropriate pair above to
`python -B benchmark/harness/workspace.py restore` with its separately pinned
checkpoint and snapshot hashes. Both pairs were independently restored and
checked. Next-request preflight and prospective case/profile pinning occur
**only after** an explicit Phase 5C resume authorization. Use the symmetric
observer-safe launch rule in `PROTOCOL.md`. Do not restore the quarantined
Lykoi B03 pair as a continuation state.

Provenance: **Phase 5B frozen protocol → Phase 5C B03 halt → Phase 5D
PROTOCOL_AMENDMENT_001 → Phase 5C resume (pending authorization).**
