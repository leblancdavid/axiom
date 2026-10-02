# PHASE5C-R5.2.1-ASSERTION-PRESERVATION/1 — independent additive repair freeze

Parent: `PHASE5C-R5-STATE-RELATIVE/1` (R5.2). Authority: `B11-R4-HISTORICAL-ASSERTION-PRESERVATION-AUDIT.md` SHA-256 `1d099e1502dd96718f45b6082d9b686ec1a67b26f72c22141f2cfa6b3898e699`.

Status: **frozen independently**; R5.3 remains unfrozen and B17 unexposed. This version adds acceptance carriers only. Original cases, R4/R5/R5.1/R5.2, checkpoints, snapshots, results and classifications retain their historical meaning and bytes.

## Frozen source inventory (raw SHA-256)

| Source | SHA-256 |
| --- | --- |
| `benchmark/harness/assertion_preservation_r5_2_1.py` | `b1748609f0a1f9d24013a3b5626f96be5a0faa1f77c5d3406f7eb3f549df3db0` |
| `benchmark/harness/test_assertion_preservation_r5_2_1.py` | `08745f237fb09d2fe270480f7c805ad4a34c031585ec3c6cd030c4c860d0f875` |
| `benchmark/harness/revalidate_preservation_r5_2_1.py` | `d5d945e4e83646d6a501e01b78885502016aaddd7c8aa54f1c51140cf9487e8d` |
| Prospective isolated inventory constructor `benchmark/harness/acceptance_inventory_r5_3.py` | `fdfc898d7895e39f6f26ac4c5bcf9f927c3fdf592bb4cdcccd8d75fee67b2f64` |

The original method bodies remain pinned through R5.1 and the existing B16 freezes. This revision composes **after** the R5.2 achieved-history selection, and reads only the original method's observed disposition: if active or inapplicable/skipped, no new method; if superseded by B16-R5's verbatim owner-adapted replay, no duplicate method; if superseded by B11 with the expected origin, add the matching carrier; otherwise fail closed. No track identity enters selection. B16's owner creation argument follows the composed schema's `owner: system` migration default. A disposable directory per method preserves the original creation/observation preconditions.

## Five restored semantic roots

| Original requirement and assertion | Lost at | Added carrier and observation |
| --- | --- | --- |
| Baseline `regression.py:99`: three normal/HIGH/LOW create-result IDs distinct | B11 baseline lifecycle supersession | `test_baseline_create_assertions_restored`: pairwise ID count is three on the original three create results |
| Baseline `regression.py:100-101`, helper `:60-69`: `check_task` on **each** of those results | B11 baseline lifecycle supersession | same carrier: exact achieved fields, nonblank string ID, parseable UTC `Z` time, conditional B02 tags-list, and exactly one achieved-profile field-type layer per created task |
| Baseline `regression.py:100-102`: initial pending status on each create result | B11 baseline lifecycle supersession | same carrier: each `status == pending` before mutation |
| Baseline `regression.py:104`: omitted normal due date null | B11 baseline lifecycle supersession | same carrier: normal `due_date is None` |
| B01 `regression.py:168-176`, specifically `:176`: after completing CRITICAL, pending HIGH remains selected | B11 B01 priority supersession | `test_b01_intermediate_high_restored`: complete CRITICAL while HIGH remains pending, then `list-high == [high]` |

Each machine inventory entry has the original carrier/source, the audit, the B11 omission edge and the new carrier chain; the root is **not** a new requirement. The B11 archive-before-delete rule and all unrelated frozen assertion bodies remain selected as before. The previously lost completed-unarchived delete success is not restored. R5.1's repeated wrapper accumulation is avoided only in prospective inventory construction; frozen runners are unchanged.

## Deterministic inventory and fixture evidence at freeze

| Achieved history | Active repair roots | Repair inventory SHA-256 (`workspace.encoded`) | Parent loaded assertion inventory SHA-256 |
| --- | ---: | --- | --- |
| B01–B16 | 5 | `64a522850a1c8a3c698aac1d7be53bb813144e1e3375daeddb5513ab3d12b2e8` | `6706171247d40a725142ded41cf357fd1d7e5bf30f34875153cc2746c661652a` |
| {B01,B04} | 0 | `ca3d163bab055381827226140568f3bef7eaac187cebd76878e0b63e9e442356` | `07a5e464e994369fbc000b52bbe4cd037c292a4ff736b3b943db793e17472d0c` |

`python -m unittest discover -s benchmark/harness -p 'test_*.py'`: **47 tests passed** at repair freeze, including five new repair fixtures and repeated helper-construction fixtures. Revalidation of restored B16 checkpoints is a separate *post-freeze* operation; its findings must be recorded separately and must not backdate the B16 classifications. Any failure of a restored assertion triggers a stop and separate adjudication.
