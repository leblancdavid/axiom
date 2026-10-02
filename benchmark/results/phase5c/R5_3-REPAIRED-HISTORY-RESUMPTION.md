# R5.3 repaired-history semantic gate — resumed, NOT FROZEN

Predecessor: `R5_2_1-POST-B16-REPAIRED-CONTINUATION.md`. R5.3 now imports the independently frozen R5.2.1 transition through `benchmark/harness/acceptance_repaired_r5_3.py`. That bridge pins the repair implementation SHA-256, obtains the five assertion roots and original-carrier/B11-omission/restoration chains from the repair revision itself, checks the frozen per-history inventory hashes, and compares selected executable repair methods with the loaded parent suite. It does not assign any restored root a new R5.3 or B17 origin. Repeated construction and drift fixtures pass; the full repository harness passed **49/49**.

| Achieved history | Parent method/AST assertion inventory SHA-256 | Restored semantic inventory SHA-256 | Selected repair methods |
| --- | --- | --- | ---: |
| B01–B16 | `6706171247d40a725142ded41cf357fd1d7e5bf30f34875153cc2746c661652a` | `64a522850a1c8a3c698aac1d7be53bb813144e1e3375daeddb5513ab3d12b2e8` | 2 |
| {B01,B04} | `07a5e464e994369fbc000b52bbe4cd037c292a4ff736b3b943db793e17472d0c` | `ca3d163bab055381827226140568f3bef7eaac187cebd76878e0b63e9e442356` | 0 |

**Gate remains open:** the parent inventories contain 405/52 *syntactic* assertion-call sites; not every frozen helper call, CLI envelope, R4 rewritten body and R5 rewritten B10 method has been mapped to an exhaustive normalized semantic root with verified replacement lineage. Consequently a zero-unexplained-difference *assertion-level* proof is not yet established. The bridge explicitly reports `full_prior_assertion_equivalence_proven: false`. No R5.3 freeze is asserted and B17 remains unexposed. Further R5.3 semantic-equivalence work must complete this proof before a freeze may be considered.
