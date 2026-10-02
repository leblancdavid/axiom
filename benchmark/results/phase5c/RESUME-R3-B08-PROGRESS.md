# Lykoi Phase 5C resumed execution — immutable interim evidence through B08

**Status: IN PROGRESS.** B08 was frozen in `B08-FREEZE-R3.md` and both tracks
passed independent preflight on restored B07 snapshots. The earlier R2 and
B07 progress records are preserved.

| Track | B08 attempted | B08 achieved | Raw classification | Applicable external regression | Internal | Resulting achieved set |
| --- | --- | --- | --- | --- | --- | --- |
| Conventional | yes | yes | `SUCCESS` | 18/18 | 22/22 | B01–B08 |
| Lykoi | yes | no | `AXIOM_CAPABILITY_GAP` | 7/7 (2 skipped) | 33/33 | B01, B04 |

The Lykoi implementation call timed out while inspecting its workspace; its
partial event stream is retained as `B08-lykoi-implementation.jsonl`. The
same session resumed in `B08-lykoi-implementation-resume.jsonl` and completed
in-memory validator probes: `prim:boolean` is unavailable, JSON boolean enum
values are rejected, and a string field cannot receive JSON boolean literals
on creation or migration. B08 independently requires a boolean, so its primary
classification is an intrinsic Lykoi capability gap. The separately
unavailable B03/B05/B06 filtered lists are recorded in that transcript, not
reclassified as new gaps. No Lykoi implementation bytes changed.

| Track | Format-3 checkpoint SHA-256 | Snapshot SHA-256 | Files |
| --- | --- | --- | ---: |
| Conventional B08 | `bda4823dbd64ea8d0ef89c8579a918d65f3a558dc270663c44b5e9543b6e5709` | `41d22ff75a5db8df2f984642911410fe7070aa39c122c4bfd6cf66445fa10f28` | 2 |
| Lykoi B08 | `731937160851d8061d896af2f955569cdaad4800200bdb828580ea5e94b74d23` | `36e34184bd3d9cd9c65287d49d813838ca31197de6467b387defb1e1147c4ff5` | 27 |

Both snapshots restored independently against complete file inventories.
Prediction, implementation (including timeout continuation), acceptance,
regression, internal test and attempt history evidence is in the `B08-` files.
No B08 regression or implementation failure was classified. Tool/timing/token
measurements reside in the raw streams where supplied; unavailable telemetry
is N/A. The timeout was recoverable and did not mutate implementation state.

**Next boundary:** freeze B09 acceptance and capability metadata before either
B09 preflight or agent exposure.
