# R5.22 — Known general lowering-coverage completion (prospective, 2026-10-03)

A compiler-coverage completion phase over the **known** lowering-coverage backlog
identified at the R5.21 lock. It closes that set on independent non-task domains.
R5.22 performs **no fourth B02 retry**: it generates no complete B02 candidate, runs
no frozen B02 acceptance, and performs no B02 grounding or B02 semantic conformance.
R5.2.2 remains historical benchmark authority. Phase 5C does not advance to B03;
B17 remains unexposed and unclassified; the semantic-first format remains globally
unfrozen; universal implementation correctness is not claimed. Candidate core
semantic constructs remain **30**; no #31 was added; no existing semantic definition
was changed to simplify a compiler implementation.

Every relation/composition below is realized inside the existing prospective
**generative** lowering channel (`benchmark/semantic/typed_lowering_r5_12.py`,
`generative_r5_13.py`, `generative_runtime_r5_13.py`, `generative_evidence_r5_13.py`)
plus one new checked module (`capability_boundary_r5_22.py`) and one disposable
suite (`benchmark/harness/test_lowering_coverage_r5_22.py`). The canonical application
model and `src/air_compiler/` were not touched.

## 1. Starting lowering-coverage matrix (from the R5.21 §9 evidence, R5.22 Part 1)

Columns: representation exists / validating lowering / generative lowering /
synthetic (non-task) generative evidence / B02-shaped executed transfer /
grounded / fault-tested / known limitation.

| Relation or composition | repr | valid | generative | synthetic | B02-transfer | grounded | fault | starting classification |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Exact selection (#10–12) | yes | yes | yes | yes (R5.13) | yes (R5.21) | yes | yes | GENERATIVE |
| Read-only state preserve (#21–23) | yes | yes | yes | yes (R5.13) | yes (R5.21) | yes | yes | GENERATIVE |
| Ordered normalization (#13–17) | yes | yes | yes | yes (R5.15) | yes (R5.21) | yes | yes | GENERATIVE |
| Typed record-valued outcome (#45) | yes | yes | yes | yes (R5.15) | yes (R5.21) | yes | yes | GENERATIVE |
| Keyed missing-field default (#44) | yes | yes | yes | yes (R5.15) | yes (R5.21) | yes | yes | GENERATIVE |
| Framed insertion (#21–23) | yes | yes | yes | yes (R5.16) | no (create gate) | yes | yes | GENERATIVE (synthetic-only at R5.21) |
| Durable version transition | yes | yes | yes | yes (R5.16) | yes (R5.21) | yes | yes | GENERATIVE |
| Cardinality (#30) | yes | yes | yes | yes (R5.16) | yes (R5.21) | yes | yes | GENERATIVE |
| Overlapping compatible defaults (#44) | yes | yes | yes | yes (R5.18) | yes (R5.21) | yes | yes | GENERATIVE |
| Typed lexicographic ordering (#43) | yes | yes | yes | yes (R5.20) | yes (R5.21) | yes | yes | GENERATIVE |
| **External values (#24 clock, #25 instant, fresh-ID)** | yes | no | **no** | no | no | no | no | **UNSUPPORTED (create gate)** |
| **Omitted-input fallback** | yes | no | **no** | no | no | no | no | **UNSUPPORTED (create gate)** |
| **Before comparison (#27)** | yes | yes | **no** | no | no | no | no | **VALIDATING_ONLY (R5.4)** |
| **Projection: matched-row / post-state outcome (#45 post/outcome)** | yes | yes | **no** | no | no | no | no | **VALIDATING_ONLY (R5.12)** |
| **Remove transition (delete)** | yes | no | **no** | no | no | no | no | **UNSUPPORTED** |
| **`replace_field` over envelope state (#44/#45)** | yes | yes | partial | plain-seq only | no (envelope) | partial | partial | **UNSUPPORTED (envelope)** |
| **Integrated AST / CLI binding** | yes | yes | partial | no | no | no | no | **INCOMPLETE / NOT_REACHED** |

The eight bold rows are the R5.22 known backlog. R5.22 turns each into independent
generative evidence.

## 2. External semantic reconstruction (§2)

`external` was reconstructed, not invented. In the candidate vocabulary the
generation of a fresh identity and the reading of the UTC creation instant are
**inherited binding/adapter obligations** (R5.14 §2; #24 clock `utc_now → Instant`,
#25 instant). They are not a first-class core relation and are not a #31. The
R5.21 create gate carried them as frontier nodes `{'external': {'source':
'fresh_unique_id' | 'utc_clock'}}`; the existing representation keys an external
reference by a named **source** and types it by that source (identity → string,
clock → typed instant). R5.22 interprets exactly that node shape. No new semantic
was introduced; only a constructive target meaning was added.

## 3. External capability boundary (§3/§4)

`capability_boundary_r5_22.py` is the checked side of a typed capability boundary:
a registry `{'fresh_unique_id': 'string', 'utc_clock': 'instant'}`, provider
descriptors (real and controlled), and independent re-validation of the value the
runtime actually supplied. Conceptual path (all generative, no ad-hoc target calls
embedded in application behavior):

```
semantic {'external': {'source': <capability>}}
    → typed generated request   EXTERNAL['<capability>']   (expression emission)
    → runtime capability provider (Capabilities in generative_runtime_r5_13.py)
    → concrete value of the declared type, resolved once per invocation and logged
```

Typing is preserved end to end: a capability's declared type flows into the record
shape, and incompatible use rejects — a `utc_clock` (instant) value demanded where a
plain string outcome is declared raises a type mismatch; an unknown capability raises;
a controlled value violating its capability type is refused by the boundary and by the
runtime. The two independent type checkers (`_type`, runtime `valid`) both understand
the existing typed `instant` form (UTC `Z`, aware-UTC parse), matching `format.py`,
`state_relations.py` and the R5.4 controlled clock. Target-language dynamic typing is
never allowed to silently define semantics.

## 4. External grounding and fault results (§5/§6)

Executions ran the generated program as a real subprocess and passed the
provenance/integrity challenge (R5.7 model): internal trace matched independently
captured stdout and durable file readback; the event records `externals`, the **actual**
supplied values. Semantic conformance judges the *relation actually specified*, not an
unknowable future value: under a controlled provider the supplied identity/instant are
fixed and compared; under the real provider conformance checks type, freshness
(identity absent from pre, present in post) and that the persisted row's identity and
clock equal the logged supplied values. Observed evidence:

- register (controlled, `gen-7`/clock) → GROUNDED + CONFORMANT; `externals` recorded.
- register (real provider) → GROUNDED + CONFORMANT; `validate_logged(externals)` true;
  persisted identity/clock equal the actually supplied values.
- **faithful lowering fault** (returned identity replaced while persistence uses the
  actual value) → PROVENANCE VALID + GROUNDED, **NON-CONFORMANT** (returned record
  differs from the persisted external value).
- **stale reused identity** (controlled value collides with pre) → the exact-frame
  structural freshness guard refuses to insert a duplicate; the run does not ground and
  nothing was written — freshness is enforced, not fabricated.
- **wrong capability source / wrong type** → rejected at the typed boundary.
- **controlled provider missing a capability** → provider cannot supply; run fails, so
  grounding faithfully reports failure (no silent substitution).

## 5. Fallback lowering (§7/§8)

`fallback` was reconstructed as a distinct input-side obligation:
`fallback(value: optional T, default: T) → T` — the explicitly present input wins, the
absent optionally-present field takes the default. It is **not** conflated with the
migration state relation `default_missing` (#44, keyed over a population): `fallback`
operates on a single optionally-present input reference and appears inside record/insert
expressions. A fallback source must be a field reference whose leaf is optional, and the
default must be the unwrapped type; incompatible defaults reject. Generative evidence on
the sensor domain: explicit `unit='kelvin'` preserved; omitted `unit` → semantic default
`'celsius'`; changing only the fallback default (`'celsius'`→`'kelvin'`) changed the
generated behavior with no lowerer edit; a fallback lowering fault (returned value ignores
the present input) grounded faithfully but failed conformance.

## 6. Before comparison lowering (§9)

The existing #27 strict instant comparison was promoted from validating-only to
generative. Operands must be typed instants (`instant` shape, UTC `Z`); comparison uses
the semantic instant parse (aware-UTC), not incidental Python string ordering. It lowers
in three roles: a selection predicate (publication `published_at before input.cutoff`),
a branch guard, and a typed boolean outcome. Before / equal / after all observed: equal
and after reject the strict relation. Plain-string operands reject (`before requires two
typed instants`), so no unsupported time form is guessed.

## 7. Projection lowering (§10/§11)

Projection is realized as generative lowering of existing constructs (#2 field
projection, #10–12 selection, #45 post/outcome slots), with target-neutral `sole`
(exactly-one matched record) and `project` (typed field-subset record) helpers and a
`post` slot added to the value channel so an outcome can reference the post-transition
state. No result shape is hard-coded: subsets, matched records and post-transition
records are derived from semantic field references. Preservation was grounded for
read-only cases: a subset projection over publications returns the projected record with
`before == after` bytes; a post-transition projection returns the persisted row's
projected fields, and the durable write is the insertion itself, not the projection.

## 8. Remove lowering (§12/§13/§14)

`remove` is lowered as a keyed relation transition inside the relation-set grammar
(`{'remove': {'collection', 'identity', 'match'}}`), relation-driven and independent of
state shape: it works over a plain-sequence state and an envelope collection. Framing is
preserved — the targeted element is absent from post, unrelated records and fields
remain, no extra record appears, and identity matching is typed (string identity). Target
behavior when absent follows the existing contract: a cardinality-1 guard routes an
unmatched removal to a `preserve` no-write branch. Cardinality is derived through the
existing #30 relation (post-state `cardinality`), with no new arithmetic. Faults: a
lowering fault that drops the wrong (first, positional) element grounds faithfully yet
fails semantic conformance. No `delete_task`-style branch exists in the lowerer.

## 9. replace_field lowering and composition (§15/§16)

The "envelope-shaped" `replace_field` was reconstructed: a keyed replacement whose target
collection lives under a named field of a record-shaped state (`{schema_version, records:
Seq<Record>}`), guarded by an envelope-level equality. It is lowered through the relation
conjunction (collection-qualified), matching the existing #44/#45 keyed-replacement
semantics and preserving unrelated envelope fields and record identity. The older
single-transition top-level forms remain for sequence state (unchanged); the envelope form
is reached compositionally, not by widening a top-level convenience into a special case.
Composition without any domain branch: predicate selection (`before` ∩ keyed match)
narrows the transition; a projected post-transition record is returned from `post`. A
replacement lowering fault keeps the old field value — faithful grounding, non-conformance.

## 10. AST integration (§17)

Every R5.22 operation is a **semantic AST** (one contract: `id`, `version`, `input`,
`state`, `branches`) fed to `generate`, which drives
`typed` (validation) → `_relational`/`ordering_plan`/`_compile` (relation planning) →
`render`/`expression` (generative lowering). Lowerer-internal plans are derived from the
AST, not assembled by callers as authoritative input; `sole`/`project`/`before`/`external`/
`fallback` and the new transitions flow through the same validated-expression path as the
previously supported relations. No capability required an external hand-authored plan to
be injected as the application input.

## 11. CLI / public binding integration (§18)

A **generic** CLI adapter `run_cli` (in the self-contained runtime) builds its public
flags from checked input-shape binding metadata (one `--field` per declared input-record
field, required iff not optional, typed by the field), then invokes the *same* generated
`execute`. `observe_cli` reconstructs named flags from that metadata for an independent
public observation. The adapter embeds no domain behavior; the operation's behavior lives
only in the generated `execute`. A sensor register executed through `run_cli` (flags, not
a JSON payload) generated, grounded and conformed identically to the subprocess payload
path, with the runtime carrying no `argparse` for a specific command. This separates the
generic CLI/runtime adapter from generated operation behavior.

## 12. First end-to-end synthetic operation (§19)

**Environmental sensor reading registration** (plain-sequence state) composes: omitted
`unit` → **fallback** → **external** identity and **external** UTC clock → construct a
typed record → **framed insertion** (exact frame) → **cardinality**/**projected record**
result → **durable state**. The complete behavior derives from semantics through general
lowering; nothing copies B02's field names or domain. Executed, grounded and conformed
under both real and controlled providers.

## 13. Second end-to-end synthetic operation (§20)

**Publication archive maintenance** (envelope state) composes a different subset: exact
**selection** → typed instant **before** comparison → keyed **replace_field** over the
envelope (and, in the retire variant, keyed **remove**) → **projected post-transition
record** result → **durable state**, with byte-preserving read-only selection and
guarded no-write branches. No compiler edit was made between the two operations; the same
locked lowerer handled both domains.

## 14. Semantic mutation results (§21)

For both operations, only the semantic source changed and behavior changed correspondingly,
with zero lowerer edits: fallback default `'celsius'→'kelvin'` (registered unit follows);
projected field set `[reading_id, recorded_at] → [station, unit]` (result shape follows);
replacement target value `'archived'→'retired'` (persisted post-state follows). Contract
digests changed and regenerated artifacts changed; grounding and conformance re-verified.

## 15. Grounding results (§22)

Each newly generative capability was grounded through the R5.7-style challenge: internal
per-operation event (input, pre, post, outcome, `attempted_write`, `externals`),
independent public stdout, and independent durable file readback, behind the provenance
digest/integrity check. Read-only relations recorded `attempted_write: false` with
byte-identical storage; mutating relations recorded a real durable change. The actual
external values used are captured in the event for independent evidence.

## 16. Conformance / fault results (§23)

Correct executions evaluated against the same contracts that drove generation were GROUNDED
+ CONFORMANT. Faithfully grounded lowering faults were injected for each major class —
external (returned≠persisted), fallback (ignore present input), replacement (retain old
value), removal (drop wrong element), plus the inherited ordering fault — each producing
PROVENANCE VALID + GROUNDED + **NON-CONFORMANT**. Contracts were never altered to match an
injected fault. `GROUNDING_FAILED: 0` for the faithful faults; rejections (missing provider,
stale identity) fail *grounding*, not conformance, exactly as intended.

## 17. Safe unsupported behavior (§24)

Relations still outside the deliberate lowering grammar reject explicitly and are never
silently ignored, partially implemented, or substituted with authored behavior. Verified
rejecting: an unregistered expression kind (`unsupported relation: …`), a non-`source`
external shape, a fallback over a non-optional / non-reference source, `before` over
non-instant operands, a projection of an optionally-present field, `sole` on a
non-singleton, an unknown capability, and overlapping noncommuting collection transforms
(`overlapping collection relations`). The top-level single-transition `remove`/envelope
`replace_field` forms (not wired into the relation-set path) still reject as
`state relation`, matching the R5.21 observations.

## 18. B02 contamination audit (§25)

`test_changed_modules_contain_no_task_b02_or_benchmark_vocabulary` asserts that none of
the changed lowering modules — `generative_r5_13.py`, `typed_lowering_r5_12.py`,
`generative_runtime_r5_13.py`, `generative_evidence_r5_13.py`,
`capability_boundary_r5_22.py` — contains task/tag/priority/due/status/title tokens, B02
command names (`list-high`, `list-overdue`, `migrate`, `delete_task`, `insert_task`),
B02 fixture/version constants (`schema_version`, `NORMAL`, `HIGH`, `CRITICAL`, `tasks.json`),
`created_at`, or any `B02` identifier. There is **no behavioral dependency on B02**: the
only B02 linkage is the R5.21 coverage matrix that *named which capability was needed*,
never a domain-specific implementation. Every domain value arrives only through a typed
contract; the lowerer dispatches on relation kind, not on any application identifier.

## 19. Final known-coverage matrix (§26)

No B02 was executed to build this; classification uses representation + independent
generative evidence + previously demonstrated transfer.

| Known required relation/composition | R5.22 final classification |
| --- | --- |
| Exact selection | GENERATIVE_INDEPENDENTLY_VALIDATED (+ B02 transfer R5.21) |
| Read-only state preserve | GENERATIVE_INDEPENDENTLY_VALIDATED (+ transfer) |
| Ordered normalization | GENERATIVE_INDEPENDENTLY_VALIDATED (+ transfer) |
| Typed record-valued outcome | GENERATIVE_INDEPENDENTLY_VALIDATED (+ transfer) |
| Keyed missing-field default | GENERATIVE_INDEPENDENTLY_VALIDATED (+ transfer) |
| Framed insertion | GENERATIVE_INDEPENDENTLY_VALIDATED (R5.16 + R5.22 re-grounded) |
| Durable version transition | GENERATIVE_INDEPENDENTLY_VALIDATED (R5.16 + transfer) |
| Cardinality (#30) | GENERATIVE_INDEPENDENTLY_VALIDATED (R5.10/R5.16 + R5.22 composed) |
| Overlapping compatible defaults | GENERATIVE_INDEPENDENTLY_VALIDATED (R5.18 + transfer) |
| Typed lexicographic ordering | GENERATIVE_B02_TRANSFER_PREVIOUSLY_DEMONSTRATED (R5.20/R5.21) |
| **External values** | **GENERATIVE_INDEPENDENTLY_VALIDATED (R5.22)** |
| **Omitted-input fallback** | **GENERATIVE_INDEPENDENTLY_VALIDATED (R5.22)** |
| **Before comparison** | **GENERATIVE_INDEPENDENTLY_VALIDATED (R5.22)** (was VALIDATING_ONLY) |
| **Projection: matched-row / post-state** | **GENERATIVE_INDEPENDENTLY_VALIDATED (R5.22)** (was VALIDATING_ONLY) |
| **Remove transition** | **GENERATIVE_INDEPENDENTLY_VALIDATED (R5.22)** |
| **replace_field over envelope** | **GENERATIVE_INDEPENDENTLY_VALIDATED (R5.22)** |
| **Integrated AST / CLI binding** | **GENERATIVE_INDEPENDENTLY_VALIDATED (R5.22)** |

**Gate condition.** Within the known lowering-coverage backlog (the relations/compositions
R5.21 enumerated and Part 1 lists), **no known required capability remains VALIDATING_ONLY,
UNSUPPORTED or UNKNOWN**. Each is generative with independent non-task evidence or a
previously demonstrated benchmark transfer.

**Out of the lowering-coverage backlog (kept distinct, not claimed closed).** These are
interface/transport or specification items, not semantic relations in the backlog: the full
multi-operation integrated command document (which is B02 assembly, prohibited here);
error-envelope / exit-code transport; missing-file→`[]`; one shared store across commands;
`invalid_state` corruption mapping; and failure-branch precedence / stored malformed-tag
taxonomy (`BENCHMARK_UNDERSPECIFIED` as in R5.14). Completing the lowering set does not
assert that a complete B02 operation has been generated, grounded or accepted.

## 20. Construct accounting (§27)

Candidate core semantic constructs remain **30** (historical raw inventory 46; no #31). The
frontier nodes R5.21 recorded as placeholders — `external`, `fallback`, `before`, `remove`,
projection, envelope `replace_field` — each map to an existing candidate construct or an
inherited binding obligation (#24 clock, #25 instant, #27 before, #2 field projection,
#10–12 selection, #21–23 transition, #30 cardinality, #44 keyed default, #45 post/outcome
slots). R5.22 added **lowering/typing/binding/runtime/testing machinery only** (a new typed
`instant` value form and target-neutral `sole`/`project` helpers, the capability boundary,
relation-set `remove`/collection-qualified `replace_field`, and a generic CLI adapter) — never
a new core semantic construct. No capability revealed a true semantic deficiency, so no
`SEMANTIC_LOWERING_MISMATCH` halt occurred.

## 21. Exact next-step recommendation

The known general lowering coverage set is closed on independent domains. The next step is a
**single** separately locked B02 retry that regenerates the complete B02 contract through
this closed lowerer — create-success (external/fallback), matched-row and post-state
projection, strict-past selection, removal, envelope lifecycle replacement, and the integrated
multi-operation AST with CLI/clock/ID binding — and only then reassesses frozen acceptance
under its own protocol. Do not resume further serial one-capability discovery; do not advance
Phase 5C to B03; do not expose B17. If that comprehensive retry reveals a *genuine* semantic
gap (not a lowering gap), halt and classify it distinctly. Longer term, complete the ordered
benchmark with honest gap/dependency/regression accounting; repeated B02 success still cannot
establish generality, which requires new unseen domains.

## Verification record

Green **pre-work** (locked from R5.21 working copy): harness 197/197; application/compiler
31/31; validate ok; safety 0 capability violations / 0 invalid transitions; `git diff
--check` exit 0.

Post-work (this phase): full benchmark harness **224 run, 224 passed, 0 failed** (197 prior
+ 27 new R5.22; the 14 R5.21 retry tests remain 14 after retiring four frontier-rejection
expectations that R5.22 superseded, following the R5.19/R5.20 lifecycle precedent, and adding
no B02 execution); application/compiler **31 passed**; validate ok; safety 0/0. Focused
R5.10–R5.21 suites all pass: R5.13 5, R5.12 3, R5.15 6, R5.16 4, R5.18 4, R5.20 18, R5.17 1,
R5.19 1, R5.21 14, R5.10 4, R5.11 4, R5.7 grounding 10, R5.5 architecture 6, R5.8 3; new R5.22
suite 27. `git diff --check` exit 0; the new files produced no whitespace diagnostics
(`--no-index --check` against `NUL` empty).

**Line-ending notices (reported separately, not failures):** Git emitted LF→CRLF working-copy
conversion warnings for the touched files (`test_b02_retry_r5_21.py`,
`generative_evidence_r5_13.py`, `generative_r5_13.py`, `generative_runtime_r5_13.py`,
`typed_lowering_r5_12.py`). These are conversion notices, distinct from any actual whitespace
or test failure.

Regardless of the gate: candidate core count remains **30**; B02 was **not** retried; Phase 5C
remains paused; B03 is not advanced; B17 remains unexposed and unclassified; the semantic-first
format remains globally unfrozen; R5.2.2 remains historical benchmark authority; universal
implementation correctness is not claimed.

    R5_22_KNOWN_LOWERING_COVERAGE_COMPLETE
