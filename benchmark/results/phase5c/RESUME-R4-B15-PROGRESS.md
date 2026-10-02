# Phase 5C R4 — classified B15 continuation

`B15-FREEZE-R4.md` pinned the request/case/fragment before either preflight or
agent exposure. Both B14 restores passed B15 preflight. Predictions and
isolated implementation transcripts are the four `B15-*-r4.jsonl` files.

| Track | B15 outcome | B15 acceptance | Applicable R4 external | Internal |
| --- | --- | --- | --- | --- |
| Conventional | `SUCCESS` | 2/2 | 30 passed, 4 explicit B11 skips (34 methods), 0 failures | 39/39 |
| Lykoi | `BLOCKED_BY_GAP` (B14 dependencies, B08 archival) | inapplicable | 7 passed, 2 B02 skips, 0 failures | 33/33 |

Lykoi's complete 27-file implementation inventory remains unchanged from
B10. Both snapshots independently restored into new verification workspaces
and matched their full checkpoint inventories.

| Track | Checkpoint SHA-256 | Snapshot SHA-256 | Files |
| --- | --- | --- | ---: |
| Conventional | `b679b53012630ce4e2c29c6c4c1c8ebcb3c1e143b6d7323527350e8e572c0cf3` | `8f06f0f62a224139895b7fae48d14160a60e25ebd97a091679b05b3db3f048bc` | 2 |
| Lykoi | `c5110e4331bf24c2ac6f5889e1ba2a00ba93f9f354f7e9d1c4bd689d7c2b61a0` | `36e34184bd3d9cd9c65287d49d813838ca31197de6467b387defb1e1147c4ff5` | 27 |

Conventional composed expectation SHA-256:
`27f67747e9a5b059fb5c3e4f0ecf4686c4e61782517f509ef1a359c77e7b61d8`.
R4 oracle/replacement hashes remain those pinned in `R4-EXECUTION-PIN.md`.
B16 has not yet been frozen, predicted, or attempted.
