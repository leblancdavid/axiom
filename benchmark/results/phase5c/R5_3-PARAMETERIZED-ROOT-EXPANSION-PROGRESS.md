# R5.3 finite parameterized-root reconstruction — prospective progress, NOT FROZEN

Parent: `R5_3-B10-PARAMETERIZED-CLI-ROOT-COVERAGE-STOP.md`. The discrepancy is **R5.3 reconstruction-coverage incompleteness**, not an oracle or implementation defect. The authoritative boundary is unchanged R5.2.2. B17 remains unexposed.

`benchmark/harness/parameterized_roots_r5_3.py` now interprets finite loops in loaded executable methods, retaining source-site and per-iteration IDs, arguments, result expressions, source-derived entity bindings, prior steps, branch context, expected CLI envelope and post-loop byte-equality locations. It does not execute an implementation to derive expectations. `semantic_channels_r5_3.collect` includes these roots for *all* loaded dispositions and separately reports unresolved method and helper loops. This is an additive reconstruction of the prospective inventory, not an amendment to frozen acceptance.

## B10 witness: effective B16 carrier

Source: `benchmark/harness/cases/B10.py:44-47`; preserved assertion `:45` → B16 replacement `benchmark/harness/cases/B16_R5_replacements.py:112-115`, assertion and CLI invocation at `:113`. The carrier creates users `Alex` and `alex` after two invalid-owner create rejections and a no-file check. It creates `first` (padded Alex trimmed to Alex), `second` (Alex), `other` (alex), `formerly_unowned` (system), completes `first`, captures `normal = list` and the task-store bytes, then issues the following six calls **in order**. Each must exit 0, have empty stderr and JSON stdout; the entire returned list must equal `[task for task in normal if task["owner"] == owner]` (including full task-row shape). The assertion at `:115` checks bytes unchanged after the full sequence. Entity IDs/timestamps remain the corresponding dynamically created task values, not fabricated constants.

| Query argument | Exact returned task bindings from `normal` | Canonical executable call-root ID |
| --- | --- | --- |
| `Alex` | `first` (completed), `second` (pending) | `c7f198235cd7a62920f8f21a4c2a6f955d833653359917cc7b9d2ce743572924` |
| `alex` | `other` (pending) | `a34254f7cd599b14868a9e6a5f7cd9d06b69f353d81c8de1e274b4e5fcfc2593` |
| `""` | `[]` | `99fb394aa7ed63f3a275e44d8c35f4f998fbdc8a232ed231af66e1251967fa30` |
| ` Alex ` | `[]` | `1cac7b765b4f3cd518b6b63cb1a75e14438db1ebe045413f1f3ec3fc2b3a2eb6` |
| `missing` | `[]` | `a7c7485a4f20143a62e5ef311a7b52d499cf5ae12bf58398544c95432935d16d` |
| `system` | `formerly_unowned` (pending) | `c0e4442ceab7b2d650e2c4ea58d908110b0809b58c5aba4f3455c8daacc745a8` |

All six are independently addressable by ID, have their concrete command/owner argument and a snapshot of preceding observations/state, and carry common source-site/original-lineage and applicable replacement disposition. Their CLI rejection paths no longer collapse to one AST call site. This witness applies to B01–B16, not {B01,B04}. The pre-B16 B10 five-case source is also retained as superseded provenance; it is not mistaken for six additional active observations.

## Finite method-loop audit (B01–B16 live carrier)

| Executable method loop | Per-site executed cardinality |
| --- | --- |
| B03 blank-tag rejection and no-file assertion | 2 each |
| B06 category filtering and equality assertion, replayed by B16 | 5 each |
| B09 invalid due-date start and end, replayed by B16 | 3 each (6 CLI paths) |
| B10 B16 invalid-owner create | 2 |
| B10 B16 owner filter and equality | 6 each |
| B13 archived pending/completed mutation failures, replayed by B16 | 2 per CLI operation and byte assertion |
| B14 dependency failures, replayed by B16 | 6 per CLI operation and byte assertion |
| B16 invalid/duplicate user registration | 2 per CLI source site |
| Baseline migration corruption, replayed by B16 | 2 per helper/invalid-state call site |
| B02 explicit migration | 2 helper calls |
| R5.2.1 restored baseline creation | 3 check-created calls and 3 pending assertions |

Finite method-loop iterator resolution reports **no unresolved iterator** for either achieved history. Expanded roots preserve repeated commands when the task binding or the prior state differs. Helper-side loops are also explicitly discovered: `regression.py:80` iterates `rows` and invokes `check_task` per migrated task; `assertion_preservation_r5_2_1.py:105` iterates profile field types per `check_created` invocation. The existing source-channel expansion records seven R5 field assertions on the full history and one on {B01,B04}, but those helper-mediated executions have **not yet been assigned complete canonical invocation-specific precondition/result roots**. Other non-loop direct/CLI sites also remain source channels rather than fully normalized semantic roots.

## Gate position

The six known B10 executable rejection paths map to the six IDs above. This is **not** an exhaustive rejection-path completeness certificate: helper iterations, branch-specific CLI outcomes, all direct assertions, restoration/replacement carrier equivalence and the full assertion-level semantic diff still require normalization and independent coverage verification. `ZERO UNEXPLAINED SEMANTIC DIFFERENCES` is **not established**. In particular, the existing `semantic_equivalence_proven` and `full_prior_assertion_equivalence_proven` flags remain false. This is remaining R5.3 reconstruction work, not an identified frozen-oracle difference. The freeze prerequisites have not been met; final fresh B16 restores and freeze are deferred under the existing gate. No historical carrier, implementation, classification or acceptance boundary was changed.
