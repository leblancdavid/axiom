# PHASE5C-R5.2.2-B01-PRECONDITION/1 — independent corrective freeze

Parent: `PHASE5C-R5.2.1-ASSERTION-PRESERVATION/1`. Status: **frozen independently**. R5.3 remains **UNFROZEN**; B17 remains **UNEXPOSED**. The authoritative semantic root is the original `B01.high_after_critical`, `benchmark/harness/regression.py:168-176` (assertion at `:176`). The original frozen B01/B11 methods, R5.2.1, implementation, historical checkpoints and classifications are unchanged.

The original B01 carrier creates Default (omitted priority = NORMAL), High (HIGH), Critical (CRITICAL), in that order; checks priorities, initial `list-high`, and `list`; completes Critical and checks its completed status; then expects `list-high == [high]` while Default and High remain pending. B11 supersession unintentionally removed this exact observation. R5.2.1's `assertion_preservation_r5_2_1.cases.<locals>.Preservation.test_b01_intermediate_high_restored` restored the result without the pending NORMAL task. The corrected carrier `assertion_preservation_r5_2_2.cases.<locals>.Correction.test_b01_intermediate_high_exact_precondition` reproduces the original setup and observation, with only the existing achieved-profile owner create adaptation. This corrects the **carrier**, not the root; no inference about implementation failure follows from the earlier incomplete oracle.

Lineage: `original B01 semantic root` → `B11:omitted` → `R5.2.1 incomplete carrier` → `R5.2.2 corrected carrier`. The other four R5.2.1 restoration inventory entries remain byte-identical when composed.

## Pinned source inventory (raw SHA-256)

| Source | SHA-256 |
| --- | --- |
| `benchmark/harness/assertion_preservation_r5_2_2.py` | `f258414bd585f8f1aff5cc3ef7ba4514172b0c0d86febb2e2571eabaf6b30e8c` |
| `benchmark/harness/test_assertion_preservation_r5_2_2.py` | `79791eba5c9c122db514d99fd8db0fef66843717e7160b94edafeaa6e263ff30` |
| `benchmark/harness/revalidate_preservation_r5_2_2.py` | `1b1f12a443301d1d85cb5f53c0ee8e2dcfc5c8b398a93d741dfcfe18474b322c` |
| Frozen parent `benchmark/harness/assertion_preservation_r5_2_1.py` | `b1748609f0a1f9d24013a3b5626f96be5a0faa1f77c5d3406f7eb3f549df3db0` |

## Applicability and fixtures

Selection consumes the composed acceptance dispositions: active/skipped original B01 or verbatim B16-R5 replay keeps its original carrier; B11-superseded original B01 replaces only the selected R5.2.1 B01 method, with exactly one corrected method. Unknown supersession fails closed. No track identity is an input. The machine-readable corrected inventory SHA-256 (`workspace.encoded`) is `dbccec9d10889aee7e04f160a7fbfd070d99aaa758c5db333b4e22be8b1362fe` for B01–B16 (five roots) and `ca3d163bab055381827226140568f3bef7eaac187cebd76878e0b63e9e442356` for {B01,B04} (zero restoration roots). Fixture execution verifies create arguments against original B01, pending NORMAL and HIGH plus completed CRITICAL at the observation, root provenance, carrier replacement, no duplicate and track-independent selection, unrelated restoration identity, and fail-closed behavior.

`python -m unittest discover -s benchmark/harness -p 'test_*.py'`: **57 passed** at correction freeze, including four correction fixtures and existing deterministic helper/inventory protections. Fresh checkpoint restore and validation are separate post-freeze evidence; historical B16 results are not retroactively changed. A failure of the corrected B01 assertion requires a separate historical-behavior adjudication and a stop.
