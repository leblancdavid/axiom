# Phase 5C R4 execution pin (B11 restart)

This pin supplements `PROTOCOL_AMENDMENT_R4.md`; it does not replace or
reclassify any B01–B10 evidence. Verify hashes against raw bytes before
continuing, and stop if the effective harness or toolchain changes. The R3 B11
agent streams and modified R3 workspaces are quarantined.

## Audited infrastructure change

At audit time the repository was clean at commit
`cb8ab0a23f865db1367287871592a55655aeafcf` (`5c B11`). This commit
contains the R4 oracle and an independently introduced compatibility edit to
`workspace.py`, `workspace_phase5e.py`, `test_phase5e.py`, `benchmark/README.md`
and `.gitignore`. The compatibility edit accepts both the historical
`AXIOM_CAPABILITY_GAP` and new `LYKOI_CAPABILITY_GAP` labels, and recognizes
the frozen legacy harness identifiers in existing checkpoints. Historical
checkpoint bytes, requirement/case/fragment bytes, composer and prior oracle
are unchanged. Continue to use the historical labels in historical records;
record the exact label chosen for any new attempt. Do not silently switch
labels within a recorded attempt stream.

## Effective executable identity

| Component | SHA-256 of raw bytes |
| --- | --- |
| `benchmark/harness/workspace.py` | `44f7ea2ba483113002f46f63101577550a0fe11fb08a202ecc5735aa711c1c8f` |
| `benchmark/harness/workspace_phase5e.py` | `7299f99459eba21139e275418dd065d973c15ebf97682c543546d05d473b4c85` |
| `benchmark/harness/phase5d.py` | `cfc209ab50c01e67b739bbbc9c6fc7854e77fcd2913b1fe57cbef03ee6a98900` |
| `benchmark/harness/capability_profile.py` | `cd0d318f5e7dd3dc2cdac7c93a0cd8c822c35cf53d83c365093a6c5e6971fb50` |
| `benchmark/harness/regression.py` | `8fa1ff4e8b627cc3c334a099151b97647219abac41949a3a3d32c5e9da2fc596` |
| `benchmark/harness/regression_phase5e.py` | `d59392d4f535800491fd047540292888038996b08a8c039078724879cd4791be` |
| `benchmark/harness/regression_phase5c_r4.py` | `61830ce905deff3565180b3767e933f50e5c17bfeef25ca4bcac41f9c4a706cb9` |
| `benchmark/harness/cases/B11_R4_replacements.py` | `8a8bfad8451e747e31429f1bd87055689d3115ef851861ec48810fbe4678ca60` |

The two last hashes, B04/B07/B11 case and B11 fragment hashes, and both B10
checkpoint/snapshot hashes are also pinned in `PROTOCOL_AMENDMENT_R4.md`.
Checkpoint format remains 3. Existing B10 checkpoint identities are Conventional
`5bb65e500add4ff348a0004cd216efb44519bc11d3c4815a7ee22f6c7e367688`
and Lykoi `cb2fb04d04fa80c6af67c7ef6933002995b40fcd5bb84bc7f51599f49f6ee9a6`.

Execution host at audit: Windows 11 build 26200; Python 3.14.3 at
`C:\Users\lblan\AppData\Local\Python\pythoncore-3.14-64\python.exe`;
OpenCode CLI 1.18.32; model for comparable agent runs `openai/gpt-6-sol`.
Isolate tracks, use the same model/configuration and budgets, disable Python
bytecode, and set TEMP/TMP/TMPDIR/PYTHONPYCACHEPREFIX to disposable locations
outside the implementation workspaces. Record the precise agent prompts,
session configuration and event streams before classifying new work.

The static audit independently matched each B10 snapshot to its complete
checkpoint inventory and matched all 2 Conventional and 27 Lykoi files in the
previously restored R4 B10 workspaces. This byte check alone is not a behavioral
preflight. A fresh restore, B11 preflight and read-only accumulated external
and internal validation on **both** tracks are required before predictions.

## Revalidated B10 → B11 boundary

Fresh restores outside the repository at
`C:\Users\lblan\AppData\Local\Temp\opencode\phase5c-r4-pinned-B10-conventional`
and `...\phase5c-r4-pinned-B10-lykoi` passed complete inventory and generated
artifact checks (2 and 27 files respectively). Both B11 preflights passed with
the original frozen B11 case and fragment hashes. They returned exactly the
unchanged B10 checkpoint and expectation hashes above.

With Python bytecode disabled, `phase5d.py run --read-only` executed the pinned
`regression_phase5c_r4.py` and internal unittest discovery in each fresh
workspace. Results:

| B10 state | R4 external | Internal | Applicable R4 supersessions |
| --- | --- | --- | --- |
| Conventional | 22/22, 0 skipped, 0 failure events | 28/28 | none |
| Lykoi | 7/7, 2 B02 skips, 0 failure events | 33/33 | none |

Each read-only run verified its implementation inventory before and after.
The repository harness discovery suite also passed 17/17 under Python `-B`.
This is a B10 boundary validation, **not** a B11 prediction, implementation,
classification, or checkpoint. B11 and B12–B20 remain unclassified/unattempted
under R4 until fresh isolated agent sessions and subsequent gates complete.
