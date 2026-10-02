# Phase 5C R5.1 — prospective R4 oracle-pin correction

**Frozen revision:** `PHASE5C-R5-PIN-FIX-1`. Authorized by the user after
`RESUME-R5-B16-VALIDATION-HALT.md`. This additive correction supersedes ONLY
the defective R4 integrity hash in the original R5 freeze. All acceptance
semantics, 27 mapped replacement IDs/methods, original cases, B11/R4 overlay,
achieved-capability gating and track independence remain as stated in
`PROTOCOL_AMENDMENT_R5_B16.md`. The original frozen runner and amendment at
their original paths and original hashes remain historical evidence of the
halted attempt, not runnable continuation artifacts. Neither track has seen
B16. This revision is frozen before repeating the B15 readiness validation.

## Verified provenance and minimal-difference review

The authoritative complete SHA-256 in `R4-EXECUTION-PIN.md` line 32 matches
the raw bytes of `benchmark/harness/regression_phase5c_r4.py`:

`61830ce905deff3565180b3767e933f50e5c17bfef25ca4bcac41f9c4a706cb9`

The defective `regression_phase5c_r5.py` contains this *different* value for
its `R4_SHA256` field (also copied erroneously into the old amendment's R4
hash table):

`61830ce905deff3565180b3767e933f50e5c17bfeef25ca4bcac41f9c4a706cb9`

The corrected `regression_phase5c_r5_1.py` was compared against the defective
runner with `git diff --no-index --` before this freeze. The complete diff is
the **single line** changing `R4_SHA256` from the defective second value to
the authoritative first value. No other source line, case, behavior, or
dependency changed. A separate path identifies the revised runner; the
unmodified R5 original is retained. The new addendum supplies revised version
and hash metadata without rewriting the frozen original amendment.

## Immutable inventory (raw SHA-256)

| Artifact | SHA-256 |
| --- | --- |
| Defective R5 runner `benchmark/harness/regression_phase5c_r5.py` | `26c24272474a4a814d2adf016a174bfc243f93be23f6f7da126635133a6c9444` |
| Defective R5 amendment `PROTOCOL_AMENDMENT_R5_B16.md` | `54ff1293e3a52976e48423ce8c8ace83adea7fc78571aac50bfe8e0764b0387e` |
| Corrected R5.1 runner `benchmark/harness/regression_phase5c_r5_1.py` | `419a5feb9c09643adfa7c48ac9cf5123e255451571ff91345103cd7aa83e28c0` |
| Existing R5 replacement `benchmark/harness/cases/B16_R5_replacements.py` (27 exact methods) | `9310e8f19557c8e9dfee4a1c4527524ec38c5de238d5b11d3ef9f5e08aa72d74` |
| Existing R5 fixture `benchmark/harness/test_phase5c_r5.py` | `6e01d242a18119253feb58323bfb8c6099b2ecf2dfbedc1f5bf504f473ee8229` |
| Halt `RESUME-R5-B16-VALIDATION-HALT.md` | `6cdb599c39b8062de4503a12b757cf06e4e0aa3cacc11ba1a41a60ce11db2c66` |
| Authoritative R4 runner | `61830ce905deff3565180b3767e933f50e5c17bfef25ca4bcac41f9c4a706cb9` |

The affected method inventory and exact replacement mapping are the unchanged
pinned 27-entry `METHODS` table and the unchanged audited 27-row table named
by `PROTOCOL_AMENDMENT_R5_B16.md`. No historical evidence was rewritten.
For B15 revalidation and subsequent B16 continuation use only the corrected
`regression_phase5c_r5_1.py`, keeping all other R5 components unchanged.
Repeat fresh independent B15 restores, external/internal suites and harness
validation from the beginning. Stop on any new discrepancy; this pin repair
does not authorize any other protocol alteration.
