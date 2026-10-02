# R5.2.2 corrected-oracle continuation boundary — post-B16

The independently frozen `PROTOCOL_AMENDMENT_R5_2_2_B01_PRECONDITION.md` was applied prospectively to fresh, independent restores of both authoritative B16 checkpoints. Checkpoint and snapshot SHA-256 pins, recorded file inventories before and after testing, achieved profiles and expectation hashes, and parent method inventories were verified. The new results are separate from historical B16 classifications, which remain unchanged.

| Achieved history | Checkpoint / snapshot SHA-256 | Corrected root | External | Internal |
| --- | --- | --- | --- | --- |
| B01–B16 | `c2602584521bcacaaf68ac1394531f835fe9578765a1eb5b31aa943c5f728c8a` / `383f9fa7e6d2eb8cbd794370254f90993743c8b9e6a1bf2a863e1e3e3915da3e` | R5.2.2 exact B01 carrier active; pending NORMAL + HIGH and completed CRITICAL; R5.2.1 B01 carrier absent | 35 pass, 28 supersession skips, 0 failures (63 methods) | 39 pass |
| {B01,B04} | `7318a230fb2a89bce5722b02a0899f72122e5bde5679c0fba4d0a896c55edf95` / `36e34184bd3d9cd9c65287d49d813838ca31197de6467b387defb1e1147c4ff5` | Original B01 carrier active; no duplicate correction or R5.2.1 B01 carrier | 7 pass, 2 prerequisite skips, 0 failures (9 methods) | 33 pass |

Machine-readable evidence: `R5_2_2-conventional-b16-revalidation.json` and `R5_2_2-lykoi-b16-revalidation.json`. The corrected root inventories hash to `dbccec9d10889aee7e04f160a7fbfd070d99aaa758c5db333b4e22be8b1362fe` and `ca3d163bab055381827226140568f3bef7eaac187cebd76878e0b63e9e442356`, respectively. The repository harness passed 57 tests at the independent freeze.

**Authoritative prospective semantic acceptance boundary:** the original B01 root is carried through R5.2.2 where B11 superseded it and remains in the original B01 carrier otherwise. R5.3 must consume this corrected boundary and establish its complete assertion-level semantic-equivalence proof separately. R5.3 remains **UNFROZEN**, B17 **UNEXPOSED**; no phase-completion claim follows.
