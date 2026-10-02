# R5.3 candidate inventory and B16 revalidation — STOP, NOT FROZEN

Status: prospective evidence only. Neither B17 exposure nor an R5.3 or B17
freeze is authorized by these results. The historical R4/R5/R5.1/R5.2 files,
implementation states and B16 evidence remain unchanged.

## Pinned loaded-method / syntactic assertion inventory

`benchmark/harness/acceptance_inventory_r5_3.py` enumerates the *actual loaded*
unittest methods, including originals, R4 methods and selected R5 replacements.
It records the full source-file hash and function-body hash, the exact source
locations and expression hashes of assertion calls, and task-mutation and
user-result call locations. R5 wrappers that execute an original function are
identified as such; the two rewritten R5 owner methods are inventoried from
their executable replacement bodies. IDs and hashes are deterministic and
duplicate method/assertion IDs and changed frozen sources fail validation.

| Achieved history | Loaded methods | Syntactic assertion call sites | Inventory SHA-256 | Reconstructed disposition SHA-256 |
| --- | ---: | ---: | --- | --- |
| B01–B16 | 61 | 405 | `6706171247d40a725142ded41cf357fd1d7e5bf30f34875153cc2746c661652a` | `15604f0ac259d52c163e785b6637a989f51ba901fb2074772ee0648e3f6c3cd4` |
| {B01,B04} | 9 | 52 | `07a5e464e994369fbc000b52bbe4cd037c292a4ff736b3b943db793e17472d0c` | `cb8729263f7ba94a6853c06976ddb0e66c9eca1b6e4f8833e0ca5ccf8ca1cddf` |

Complete machine-readable inventories are `R5_3-{conventional,lykoi}-assertion-inventory.json`.
`R5_3-{conventional,lykoi}-method-diff.json` includes the reconstructed and
observed method dispositions and the machine-readable difference: `{}` in
both histories. The reconstruction consumes the achieved history, frozen B11
fragment, frozen R4 supersession metadata and frozen R5 source/replacement map;
it does not read the runner's `select_supersessions` result to decide a skip.
It selects 28 prior supersessions and 33 applicable methods for B01–B16, and
two prerequisite skips and seven applicable methods for {B01,B04}. No track
identity is used to choose a disposition.

**STOP: this is not yet an exhaustive semantic assertion-state proof.** The
inventory is of syntactic call sites, not individually normalized behavioral
assertions: shared assertion helpers (including `check_task` and `upgraded`),
implicit CLI return-code/error checks and conditional branches require
semantic expansion. R4 and the two rewritten R5 methods need verified
assertion-by-assertion lineage, including where an original assertion was
changed or intentionally removed; a method-level equality of dispositions
does not establish that equivalence. The provisional `acceptance_state_r5_3.py`
still has no verified bridge from this inventory to its assertion roots and
chains. Hence the field `assertion_equivalence_proven` in each machine diff is
`false`; no unexplained *method* difference is present, but absence of an
unexplained *semantic* difference has not been demonstrated. The acceptance
proof gate is not satisfied. Do not use the hashes above as a protocol freeze.

## Independent checkpoint restores and unchanged B16 suites

The validator in `benchmark/harness/revalidate_b16_r5_3.py` verifies the two
frozen R5.2 checkpoint and archive SHA-256 values, full versioned checkpoint
pins, fresh-restored implementation inventories and achieved profiles. It
runs the applicable unchanged R5/R5.2 external suite and internal suite in
each independent temporary restore, then checks no implementation files
changed. The candidate method reconstruction was also run against each
restored achieved history; it made no change to the existing runner.

| Checkpoint | Checkpoint SHA-256 | Snapshot SHA-256 | External | Internal |
| --- | --- | --- | --- | --- |
| Conventional | `c2602584521bcacaaf68ac1394531f835fe9578765a1eb5b31aa943c5f728c8a` | `383f9fa7e6d2eb8cbd794370254f90993743c8b9e6a1bf2a863e1e3e3915da3e` | 33 pass, 28 supersession skips, 0 failures | 39 pass |
| Lykoi | `7318a230fb2a89bce5722b02a0899f72122e5bde5679c0fba4d0a896c55edf95` | `36e34184bd3d9cd9c65287d49d813838ca31197de6467b387defb1e1147c4ff5` | 7 pass, 2 prerequisite skips, 0 failures | 33 pass |

Machine-readable restore results:
`R5_3-{conventional,lykoi}-b16-revalidation.json`. The repository harness
passed **39/39**, including the eight original R5.3 fixture methods and two
new pinned real-inventory tests. The previous 37-test count referred to the
earlier prototype.

## Remaining gate before any R5.3 freeze

Expand and reconcile every real behavioral assertion and its carrier under
the prior amendments, and validate the complete assertion-level state against
the effective runner (including R4/R5 overlay, helpers, replacements and
prerequisite skips). Only after **zero unexplained semantic differences** can
the B17 affected-method audit be mapped to active assertion chains and its
candidate executable replacements be built and checked for unrelated-assertion
preservation. Revalidate the finished candidate against independent fresh B16
restores and the harness again. The present run cannot be described as an
R5.3 acceptance-state freeze or as B17 exposure; neither track has seen B17.
