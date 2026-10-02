# Phase 5C R4 — classified B11 continuation

The audited effective environment and fresh B10 revalidation are recorded in
`R4-EXECUTION-PIN.md`. The R3 B11 streams remain halted and unscored. The
fresh R4 prediction and implementation streams for each track are the four
`B11-*-r4.jsonl` files; none reused an R3 B11 workspace.

| Track | B11 classification | B11 acceptance | R4 applicable external | Internal | Achieved |
| --- | --- | --- | --- | --- | --- |
| Conventional | `SUCCESS` | 2/2 | 22 passed, 4 explicit skips, 0 failures (26 methods) | 29/29 | B01–B11 |
| Lykoi | `BLOCKED_BY_GAP` (`depends_on`: B08) | inapplicable | 7 passed, 2 B02 skips, 0 failures (9 methods) | 33/33 | B01, B04 |

The R4 runner applied the two frozen B11 baseline/B01 supersessions and exactly
the two R4 B04/B07 method supersessions on Conventional; their replacements
ran successfully. No B11 supersession or replacement applied on Lykoi, where
the original B04 method ran. Lykoi's complete 27-file B10 implementation
inventory was unchanged. The applicable external tests and internal tests ran
with read-only workspace inventory checks. The acceptance/repair oracle hashes
are `61830ce905deff3565180b3767e933f50e5c17bfeef25ca4bcac41f9c4a706cb9`
and `8a8bfad8451e747e31429f1bd87055689d3115ef851861ec48810fbe4678ca60`.

| Track | Validated checkpoint SHA-256 | Snapshot SHA-256 | Files |
| --- | --- | --- | ---: |
| Conventional | `3ac533ed4857aa39cac6575e330c8d7c172d0a381f85223b47dea0c6361671ca` | `e8a8cc7f4c5cac24791cdbde254d04a06c0902d1f650c9e1805785a093119326` | 2 |
| Lykoi | `f8e1b3ee12a194279bb40d3043f3de6b50f698630926655c73db94e06c129597` | `36e34184bd3d9cd9c65287d49d813838ca31197de6467b387defb1e1147c4ff5` | 27 |

Both snapshots independently restored to new verification workspaces with
matching complete inventories. R4 Conventional's composed B11 expectation
hash is `8aa84b25b295db122e53e4921a1f46413cf1eecdd1fdfbf2081b10c80bf2d93d`;
Lykoi's remains `9c7a4ad3103c62d13de808d01ec3af847c296b0f7f0ccbeb78ca6c4d25f46c13`.
No B12 prediction or implementation may start before its prospective case and
capability fragment are frozen and both B11 states pass B12 preflight.
