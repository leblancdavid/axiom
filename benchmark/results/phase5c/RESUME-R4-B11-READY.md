# Phase 5C R4 — B11 restart preflight, unclassified

**Status: B11_RESTART_PREFLIGHT_PASSED; PREDICTION PAUSED.** `PROTOCOL_AMENDMENT_R4.md`
versions the B11 acceptance repair after the R3 halt. This record does not
reclassify B11, claim a B11 implementation, or create a B11 checkpoint. B12–B20
remain unattempted. All B01–B10 outcomes and their evidence are unchanged.

| Track | Fresh isolated workspace (outside repository) | B10 checkpoint/snapshot independently restored | B11 preflight | R4 applicable external | Internal |
| --- | --- | --- | --- | --- | --- |
| Conventional | `C:\Users\lblan\AppData\Local\Temp\opencode\phase5c-r4-B10-conventional` | PASS (2 files) | PASS | 22/22, 0 skipped | 28/28 |
| Lykoi (`axiom` checkpoint key) | `C:\Users\lblan\AppData\Local\Temp\opencode\phase5c-r4-B10-lykoi` | PASS (27 files) | PASS | 7/7, 2 skipped (B02) | 33/33 |

Restores used the B10 checkpoint and snapshot hashes pinned in the R4 amendment.
Both preflights required the original B11 case hash
`721fc2fb1c4d9f7d51978721799fd26be12a3186d481667fff5b0060be64201a`
and fragment hash `5dcf7ee0f046515bfdd198feede631c5b767fb17d5e77302d79b662f7e335f7c`.
The achieved-set expectation hashes remain Conventional
`62333bf2e49b640ca5c4348650675ee366b59bb097699f87bebe0051d063cb46`
and Lykoi `9c7a4ad3103c62d13de808d01ec3af847c296b0f7f0ccbeb78ca6c4d25f46c13`.
Tests used `phase5d.py run --read-only` with observer temporary storage outside
each workspace. At B10 the R4 oracle reports no supersessions; both B04 and
B07 methods still run where achieved.

**Concurrent infrastructure change noticed after verification:** the repository
now also has modifications to `benchmark/harness/workspace.py`,
`benchmark/harness/workspace_phase5e.py`, `benchmark/harness/test_phase5e.py`
and `benchmark/README.md` that were not part of this R4 repair and were not
present at the initial clean status check. They have not been overwritten or
adopted into the R4 freeze. Before a fresh agent prediction, review and pin the
effective harness version, repeat both preflights and read-only accumulated
tests against that version, and halt if it changes the checkpoint identity or
protocol. The results above describe the observed preflight, not permission
to bypass that check.

**Next required action:** capture fresh isolated, comparable R4 B11 prediction
streams for both tracks from these verified B10 states, then run new isolated
implementation sessions. The R3 B11 streams and changed R3 workspace remain
quarantined as halted evidence. If B11 is achieved, execute the R4 oracle with
the explicit B04/B07 skips and replacements, all other applicable cases and
internal tests before any outcome/checkpoint; if B11 is blocked on Lykoi, keep
the B10 implementation bytes and B04 original method active. Freeze B12 before
showing either agent B12. No Phase 5C completion or Phase 6 result is claimed.
