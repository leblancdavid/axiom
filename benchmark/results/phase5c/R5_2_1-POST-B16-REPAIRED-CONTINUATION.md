# R5.2.1 repaired-oracle continuation boundary — post-B16

The independently frozen `PROTOCOL_AMENDMENT_R5_2_1_ASSERTION_PRESERVATION.md` was applied **prospectively** to each authoritative B16 achieved history. Both B16 checkpoints and snapshots were restored into separate disposable workspaces, their recorded file inventories and derived profiles verified before the suites, and their files verified unchanged after testing. Results are separate from all historical B16 results/classifications.

| State | Original checkpoint SHA-256 | Original snapshot SHA-256 | Repair roots | Repaired external | Internal | Inventory effect |
| --- | --- | --- | ---: | --- | --- | --- |
| Lykoi {B01,B04} | `7318a230fb2a89bce5722b02a0899f72122e5bde5679c0fba4d0a896c55edf95` | `36e34184bd3d9cd9c65287d49d813838ca31197de6467b387defb1e1147c4ff5` | 0 | 7 pass, 2 prerequisite skips, 0 failures (9 methods) | 33 pass | Original baseline/B01 carriers remain active; effective semantic state unchanged |
| Conventional B01–B16 | `c2602584521bcacaaf68ac1394531f835fe9578765a1eb5b31aa943c5f728c8a` | `383f9fa7e6d2eb8cbd794370254f90993743c8b9e6a1bf2a863e1e3e3915da3e` | 5 | 35 pass, 28 supersession skips, 0 failures (63 methods) | 39 pass | B11-superseded original carriers receive two additive methods covering five original semantic roots |

Machine-readable results: `R5_2_1-lykoi-b16-revalidation.json` and `R5_2_1-conventional-b16-revalidation.json`. The pre-repair Conventional external result was 33 pass, 28 skips; the additional two successful methods are the five restoration groups. The current authoritative Conventional B16 continuation state **satisfies** the repaired oracle. No inference is made that every historical implementation passed the omitted checks, and no historical result or classification is rewritten.

**Authoritative prospective acceptance boundary:** original historical results retained; historical oracle coverage defect repaired via R5.2.1; both current authoritative post-B16 states validated; R5.3 may resume semantic-equivalence analysis against this repaired acceptance history while remaining **UNFROZEN**. B17 remains **UNEXPOSED**. Any future R5.3 proof must ingest these five roots through the frozen R5.2.1 transition and establish exhaustive assertion-level equivalence independently before any R5.3 freeze or B17 work.
