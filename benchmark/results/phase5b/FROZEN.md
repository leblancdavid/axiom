# Phase 5B frozen protocol — full-run starting point

**Canonical baseline:** the 56-file archive
`benchmark/results/pilot/baseline-snapshot.tar`, SHA-256
`71bd1692adb5b34de2e99fca40da657b20b2e838e9816bdb0d801cbdca44eb13`.
It includes the uncommitted conventional baseline and benchmark inputs as well
as the Phase 4 tree. Parent commit `7e1d5eb` alone is **not** a restoration
source. `benchmark/results/BASELINE.md` pins individual original application
and B01–B20 requirement hashes; the independently checked baseline is also
specified byte-for-byte by `baseline-manifest.json` (SHA-256
`0c4488cf3bdff9dbe6e62baa1124f91222bedc1e94f96121a18d83f9abd1feca`).
All hashes in this document are SHA-256 of raw bytes, not Git object IDs.

## Frozen harness and oracle

| Component | SHA-256 |
| --- | --- |
| `benchmark/harness/workspace.py` (builder, snapshots, checkpoints, preflight, restore) | `f4ec699692b7b51fe98518856281d53d626b337028aab98b3235374f0749160b` |
| `benchmark/harness/regression.py` (shared external oracle) | `16d55bac4dc1efa3debc6764ddde9dc27c16b7538de476a0fae9cf7db7519596` |
| `benchmark/harness/validate_phase5b.py` (pilot artifact replay) | `e7b3bf24194a632d1b961ed7b6547f80ca9d845b66deb071b39b784379ba00a4` |
| Original `benchmark/harness/test_baseline.py` | `93ac14d9a5ccd8d1034d5ec314edfbbcb4604de5865ca19a0cf1de709a0890e6` |
| Original `benchmark/harness/pilot_oracle.py` | `329e693dbb7103c8556883b39624be5e65aeaf0e12c5d94e6369ae6744984281` |
| `benchmark/harness/profiles/baseline.json` | `56890855fc2161c06693657e11534349c4ebfef71316e866ebcd3f1cbc6dd808` |
| `benchmark/harness/profiles/B01.json` | `56890855fc2161c06693657e11534349c4ebfef71316e866ebcd3f1cbc6dd808` |
| `benchmark/harness/profiles/B02.json` | `46ff02e3ff6ea48a7990c2f522fb9fa7bbefcab3c88550be007e0c2c1b75972f` |
| `benchmark/results/phase5b/validation.json` (full captured evidence) | `722bba7eeb99e8d5728a716e2f21791276d362ea4e9229db5d8b2f89adb17b25` |

Requirements B01 and B02 retain hashes
`b7b2d714db5cee566e9e55982dd4c4d95d3d57f0c341e04ba1e15c24e9a8e94d`
and `8a76e276240fa840c473be60a8e7ed0e10bd0c165426b1bfc84741e69872032b`.
The **full B01–B20 hash table** remains in `benchmark/results/BASELINE.md`
and is machine-checked in `baseline-manifest.json`; neither file is to be
changed to repair a benchmark outcome. The original pilot evidence under
`benchmark/results/pilot/` remains immutable.

## Verified starting checkpoints

Each JSON checkpoint is the complete file-hash inventory and accumulated
attempt/achieved/oracle/profile state; each tar is a deterministic restorable
byte snapshot. They are external to the track workspaces.

| Track-stage (file prefix `checkpoint-` / `snapshot-`) | Checkpoint SHA-256 | Snapshot SHA-256 |
| --- | --- | --- |
| conventional-baseline | `df2be38baf07358bb4c8aa67f9c6f908cd33878eb26da80bd08f3fbd3863dc09` | `5404af03ba0d680db772c4bb2dada81c00cb53e86f7badf9efd4c7419a45daf7` |
| axiom-baseline | `355bb52af56837641695fff062a8c383a8feb85f9b63b88e4465f1aedb6032de` | `7163eb9320f043e48137c10c2216e50cc3c78d498210114fe27ae20e32170357` |
| conventional-B01 | `8e60de8af96ba1f4d0f06b7d986be53693ce8a94dca00f3b738ebd47d0c41887` | `a8f1ad637bfee7996044f97da052816ed586a14caa6a79a6771425ed8815c705` |
| axiom-B01 | `e4a62afa2b49ce5d28c6b8e3e317d4adce253f5b157baa0701dd107114cf909f` | `b340a563189d55b71c10d3513b6c740bf9ecb01fdd31711d6faae9df0c1473a7` |
| conventional-B02 | `a57c38e0681a0fce5e43b09cdf32ea3a348217b6f5ab6ae03e918b3482fc5e7a` | `0a125c94bcc364f50040c3299ebba254a2f68c9c465e04de0168749fec542bad` |
| axiom-B02 | `31dd8302529cdfabd0609ca7b3dddd64ca48764f1ae0255dfcb79d91a400ba90` | `b340a563189d55b71c10d3513b6c740bf9ecb01fdd31711d6faae9df0c1473a7` |

The Axiom B02 checkpoint records an attempt and its evidence-backed gap, but
its `achieved` list is only B01; its snapshot equals its B01 snapshot. The
Conventional B02 checkpoint records B01 and B02 achieved.

## Reproduction and preflight (PowerShell, repository root)

To rebuild an empty baseline directory: `python -B benchmark/harness/workspace.py
build --track axiom --workspace "<new-empty-path>"` (or `conventional`).
`<new-empty-path>` must **not** exist; its parent must exist. The archive and
all file/requirement/profile hashes are checked before construction completes.

To restore the last achieved **Axiom** state into an absent workspace path:

```powershell
python -B benchmark/harness/workspace.py restore --track axiom --workspace "<absent-path>" --checkpoint benchmark/results/phase5b/checkpoint-axiom-B02.json --expected-hash 31dd8302529cdfabd0609ca7b3dddd64ca48764f1ae0255dfcb79d91a400ba90 --snapshot benchmark/results/phase5b/snapshot-axiom-B02.tar --snapshot-hash b340a563189d55b71c10d3513b6c740bf9ecb01fdd31711d6faae9df0c1473a7
```

For **Conventional**, use `--track conventional`, its own B02 checkpoint/hash,
and its own B02 snapshot/hash from the table. Verify identity *before any
agent prediction or mutation* with `workspace.py preflight --workspace
"<restored-path>" --track <track> --request <next-ID> --checkpoint
<checkpoint-path> --expected-hash <pinned-checkpoint-hash>`; B03+ additionally
requires `--case-hash <frozen-Bnn-case-SHA256> --profile-hash
<frozen-Bnn-profile-SHA256>`. The prospective case/profile must be written,
reviewed and pinned **before** either agent is shown that request. An abort
with exit code 2 and `INFRASTRUCTURE_PROTOCOL_FAILURE` is not an agent result.
Do not run the shown next-request command as part of Phase 5B.

After a valid run, run the same external oracle on each track with the IDs
actually achieved: `python -B benchmark/harness/regression.py --app
"<absolute-app-path>" --achieved B01,B02` (Axiom after its B02 gap: `B01`).
Run applicable internal tests; capture raw stdout/stderr, exit status, command,
attempts, and hashes. Use `workspace.py checkpoint --track <track> --workspace
"<path>" --attempts-file <JSON-attempt-list> --output <new-checkpoint>` to
capture gap evidence/dependencies. Then `workspace.py snapshot --track
<track> --workspace "<path>" --checkpoint <new-checkpoint> --expected-hash
<new-checkpoint-hash> --output <new-snapshot.tar>` writes the deterministic
archive only if the workspace matches that checkpoint.
Hash and pin both checkpoint and snapshot **outside** the workspace, restore
once and compare before trusting the next step. Only a successful external
case set may enter `achieved`; a gap or blocked request enters `attempted`.

## Unchangeable methodology during full execution

1. Use the pinned archive, manifest, track projections, compiler/runtime,
   requirement texts/hashes, and shared external oracle. Do not alter an
   earlier case, profile, requirement, checkpoint, or pilot record.
2. Freeze each new backend-neutral Bnn external case module and current schema
   profile *before* either track receives Bnn; record their hashes once for
   both tracks. Extensions are data through the frozen runner interface, not
   edits to `regression.py`. Historical fixtures keep their original versions;
   only the explicit profile defaults/migration path adapt them. If an old
   behavior is expressly superseded, document its applicability and retain
   the old case/evidence rather than silently rewriting it.
3. Restore the actual achieved track-specific checkpoint, run preflight and
   baseline/accumulated applicable regressions before handing out a request.
   Abort on any failed preflight; record it as protocol failure. Neither track
   receives the other's application, solution, or generated edits.
4. Use the same frozen request text, comparable agent model/configuration and
   run conditions. Conventional source is canonical for its track; Axiom
   model is canonical for its track and must regenerate via its frozen tools.
   Do not edit Axiom generated output or extend compiler/schema/runtime during
   a primary benchmark step.
5. Record pass/fail/skip applicability with denominators, internal tests,
   transcript and tool/error evidence; apply REPORT.md's classifications.
   A gap leaves that track's achieved bytes unchanged. A later request proceeds
   unless explicitly dependent on a named missing capability; a dependent
   request records `BLOCKED_BY_GAP` and its `depends_on` gap IDs.
6. Any necessary change to a frozen methodological rule invalidates the
   affected run and requires review and a new protocol version before a
   resumed comparative run; never silently repair a result.

**STOP:** Phase 5B has not run B03 or the full comparison. Review and explicit
authorization are required before another request is shown to agents.
