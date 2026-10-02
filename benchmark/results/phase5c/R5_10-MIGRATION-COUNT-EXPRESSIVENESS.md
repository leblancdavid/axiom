# R5.10 — migration count expressiveness (prospective, 2026-10-02)

**Boundary.** R5.2.2 is authoritative for benchmark execution. This is a
semantic review and synthetic prototype, not a B01 execution, grounding repair,
benchmark amendment, or semantic-first format freeze. Sources read: frozen
`benchmark/baseline.md:27-32`, `benchmark/requirements/B01.md:3-6`, original
`benchmark/harness/regression.py:71-83,122-135,180-196`, B01 profile, and
`PROTOCOL_AMENDMENT_R5_2_2_B01_PRECONDITION.md` / corrected continuation.
R5.9's pinned public observations and its missing internal B01 event stand.

## 1. Frozen count reconstruction

The B01 request adds priority and says existing LOW/NORMAL/HIGH survive
migration; it does **not** itself define the number. The inherited baseline
requires explicit conversion of unversioned v1 and version-2 records to v3,
returning `{"migrated": N}`; current data and absent storage return zero.
Original `upgraded` checks `migrated == count`, then checks all resulting rows,
then a repeat migration returns zero. Its v1 one-row example lacks priority and
due date; its v2 one-row example already has priority but lacks due date. The
B01 v2 three-row example (`HIGH`, `LOW`, `NORMAL`) expects **3**, despite *no*
missing priority fields. The v3 three-row example is read without conversion.
The corrected R5.2.2 B01 carrier restores an intermediate `list-high` state;
it does not alter migration-count expectations.

Thus, for a valid explicit migration from a supported legacy version, `N` is
the number of **legacy records converted in that invocation**, not the number
missing priority, the number inspected during a read, or the number whose
priority changes. V2's three preserved priorities disprove a priority-change
count. No frozen assertion distinguishes a durable-write count from a
per-record conversion count in every imaginable storage implementation;
the baseline describes conversion and a record count, not a number of writes.
An empty legacy envelope is not directly sampled. The most economical
source-relative interpretation is its zero legacy records imply zero, while
the frozen text does not prescribe a separate `migrated` value for an empty
legacy envelope beyond `N`. No mixed-version record population is specified:
version is an envelope-level property. Neither corruption nor a failed
migration is a successful numeric result.

Let `legacy(S)` mean a valid, supported, non-current storage version. For a
successful explicit invocation, `C(S) = exact_select(T(S), legacy(S))` (all
records if legacy; empty if current or absent) and `O.migrated = |C(S)|`.
The defaulting predicate *within* a legacy conversion is different: missing
priority for v1, missing due date for v1/v2. Counting only defaulted fields
would be wrong. `S` includes version/absence and the population; no record
constant is embedded in the rule.

## 2. Decomposition and 3. composition attempts

| Obligation | Existing candidate relation / limit |
| --- | --- |
| Arbitrary finite pre-state and version applicability | #21–23 scope/before-state; version mapping is evolution metadata. A supplied sequence can vary without changing the rule. |
| Predicate and exact candidate selection | #1–8 typed fields/Boolean values plus #10–12 exact source-relative selection; use envelope legacy condition, not missing priority. |
| State transition | #44 keyed `default_missing` preserves present fields and identities; v1/v2 defaults and version evolution are separate, with nullable due date still a domain integration issue. |
| Typed success, numeric field and equality | #1–3 record/projection, #5 literal and #6 typed equality, #45 same-invocation tuple. The current #45 checker only accepts a uniform record-sequence payload; integer is recognized in v0.3 version metadata and prospective #26 integral-seconds offset, **not** as a general #45 result field type. |

Attempts with the 29 candidates: (a) #44 establishes an exact keyed
transformation for each row, but offers no size-to-scalar projection. (b)
#10–12 selects the right sequence exactly, including multiplicity and zero,
but yields another collection, not its integer size. (c) #23 quantifies over
a finite domain and #9 membership predicates each element; neither provides
an indexed domain of precisely N distinct integers or a checked enumeration
of all members. (d) #6 equates two typed values only after both exist; there
is no count-valued term on its collection side. (e) #43 order/multiset equality
and #44 one-to-one key preservation imply equal collection *sizes*, but do not
equate either size to an independently reported integer. (f) #26's integral
seconds offset is typed time arithmetic, not an enumerable finite index
domain or general collection size. (g) a fixture-specific literal `N` and
historical #28–36 scenario length checks constrain only sampled cases, not
arbitrary applicable states. (h) #45 binds four conceptual slots but adds no
cardinality operation. Therefore exact candidate selection and scalar equality
are already expressible **separately**; the smallest missing relation is a
typed finite collection's cardinality to an integer value. This is a semantic
gap, plus distinct type-checker/lowering work, not a migration operator.

## 4–5. Cardinality gap and competing formulations

| Model | Precision, validation, portability, authoring/growth tradeoff |
| --- | --- |
| A — `cardinality(C,n)` | Exact finite multiplicity, including zero. Typed collection and integer reference validate locally; regular node, predictable edits, backend-independent. One orthogonal concept; selected. |
| B — aggregate expression | Count is one instance; sum/min/max need new value domains, empty-set policy and reduction algebra. Larger validator and AI editing surface without evidence B01 needs them. Rejected for now. |
| C — bijection to numeric/index domain | Mathematically sufficient *if* a finite interval of length `n`, successor/order, distinctness, totality and bijection can all be stated and checked. These are not among the 29; building them only to recover size increases core and error surface. |
| D — existing relational composition | Exact selection + preservation + equality cannot synthesize an integer extent. Would require an unmentioned count or index axiom; rejected. |

Unrelated conceptual pressures: `result.count = |selected|`, `|selected|=0`,
`|selected|=1`, `affected = |changed|` (only with a separately defined exact
changed set), `|A|=|B|` via two cardinality relations and #6, and bounds
`min <= |A| <= max` if a future typed comparison is supplied. The first five
use the *same* relation; min/max comparisons are **not** implemented or implied
by cardinality alone. This is generality analysis, not six implementations.
No formal minimality or AI-authoring reliability experiment was conducted.

## 6–7. Numeric domain and one-invocation integration

The current v0.3 schema uses JSON integers for version metadata, and the
prototype time offset validates integral seconds. Neither makes an integer
outcome a checked #45 payload. #30 needs a machine integer field, explicitly
rejecting booleans/floats/strings, with finite nonnegative cardinality and
equality; it does **not** require addition, subtraction, division, arbitrary
precision serialization guarantees, or an unbounded arithmetic language.
For mathematical semantics `n` is a nonnegative integer (a backend must
faithfully represent finite collection sizes); negative well-typed outcomes
simply fail the relation. The experimental checker uses Python `int` and
`len`, with no bounded-machine-overflow proof.

For the *same* abstract #45 `(I,S,O,S')`, constrain `I=migrate`, valid legacy
`S`, `C=exact_select(T(S), legacy(S))`, successful typed `O`, and
`cardinality(C,O.migrated)`; constrain `S'` by keyed defaults and version
transition. Current/absent state selects empty `C`, yields success 0 and the
appropriate unchanged/absent state. Per-row missing-field defaults are not
the candidate-count predicate. The synthetic evaluator composes exact
selection, a priority-only #44 transition, a success tag, and #30 over a
*supplied* tuple; it does not wire those nodes into `contracts.py`'s limited
#45 checker, validate versioned v1/v2/v3 envelopes, implement nullable due
dates, or establish a faithful public outcome mapping. The conceptual
same-invocation contract is now expressible; integrated B01 conformance is not.

## 8–9. Reuse and construct decision

Already-exposed B01–B16 text plausibly benefits from count when describing
filtered list sizes (B03/B05/B06/B09/B12) or batch/migration affected
populations (B02/B04/B10/B16), *if* their own contracts actually require a
numeric outcome or numeric constraint. No adequacy classification was
reopened and none of those clauses has demonstrated reuse of #30 here.
**Demonstrated reuse:** synthetic strings with duplicates and the B01-shaped
supplied record populations; no independent B02–B16 execution. **Plausible
reuse:** the other clause scenarios above, conditional on their frozen text.

**CONSTRUCT_30_JUSTIFIED.** #30 is the general typed relation
`cardinality(finite_collection, integer)`, not a migration primitive or a
fixture length. The additional `integer` typed outcome-field support is
domain/type-checker integration, not another numbered core construct.

## 10. Prototype results and 11. accounting

`benchmark/semantic/cardinality.py` validates a typed finite sequence
(including optionally present record fields) and a typed integer field on an
outcome record; rejects mistyped elements/outcomes, equates sequence length to
the field, and admits empty and duplicate-containing collections. In
`benchmark/harness/test_migration_count_r5_10.py`, synthetic supplied tuple
families of sizes 0, 1, 4, 17 satisfy exact selection, priority defaulting
and reported counts; `n+1` and omitted candidate fail. V2-shaped records
whose priority is already LOW/HIGH count as **2**; the *same two rows* in a
current-version invocation are non-candidates and require **0**, proving
total stored population is not always candidate size. An unrelated three-row
eligible/ineligible selection has two candidates and one non-candidate in the
*same* supplied pre-state: its cardinality is 2, not 3. This is a general
selection/count witness, not a mixed-version B01 envelope. An error tag fails.
These are semantic witnesses, not universal implementation proof; even the
synthetic transition only models priority, not the complete frozen migration.
The existing selection validator accepts the empty type probe, but its record
type checker requires all declared fields on nonempty cases; the synthetic
v1 omitted-priority rows are passed directly to its evaluator. #30 validates
optional fields itself. An integrated checker must explicitly reconcile #10's
record presence typing with #44's optional before-state, rather than claiming
these v1 tuples are already checked end to end.

Historical numbered inventory: 45 raw = 29 core + 16 non-core. New #30 is
**one prospective core relation**, yielding **46 raw categorized = 30 core
(13 domain, 12 collection including #30, 4 state, 1 operation) + 16 non-core**.
R5.7's 12 unnumbered responsibilities and R5.9's two unnumbered B01 adapter/
snapshot responsibilities remain separate: expanded accounting 60 = 46 + 12
+ 2. Witnesses, Python adapter functions and fixtures are not core constructs.
The historical 45-entry numbering (including non-core historical #30) is
unchanged; prospective *core* #30 refers to a different ledger, not a
retroactive renumbering or an amendment to frozen semantics.

## 12–13. Remaining B01 gaps and exact R5.11 recommendation

The checkpoint-pinned B01 executable passed the original frozen B01 methods
and its public-call/durable-file endpoints can be observed independently;
it **does not emit** the internal per-operation event required by R5.7. B01
grounding remains failed/unestablished; no synthetic semantic witness or
acceptance pass converts that into grounded #45 conformance. Other R5.9
obligations remain: integrated typed outcome and exact selection/default
checking on the same #45 tuple, nullable defaults and version mapping,
interface/storage lowering, provenance and durable effect coverage, ordinal
priority ambiguity and universal correctness. **B01 stays inadequate and
halted.** Phase 5C remains paused, B17 unexposed/unclassified, the
semantic-first format unfrozen, R5.2.2 authoritative.

**R5.11 recommendation:** separately review the checked integration of #30
with #10–12/#44 and a heterogeneous integer success payload in #45 on
synthetic versioned tuples (v1/v2/current/absent), including null due date and
invalid typed outcomes. Independently scope the B01 grounding architecture
against R5.7 without altering the pinned executable or claiming a grounded
B01 run. Do not restart benchmark execution, unpause Phase 5C or expose B17.

Verification from repository root: benchmark harness **137 tests OK**;
application/compiler **31 OK**; focused architecture **6 OK**; grounding
**10 OK**; semantic prototype group **41 OK**, conditional semantic **3 OK**;
focused R5.10 **4 OK** (included in 137). `git diff --check` exited 0;
three new files were separately checked via `git diff --no-index --check`
against `NUL` with no whitespace diagnostics (the new-file diff returns 1).
Git emitted LF-to-CRLF working-copy conversion warnings for four tracked and
three new files; these are **not** test or whitespace-check failures.
These counts establish only the executed finite development checks.

R5_10_MIGRATION_COUNT_RESOLVED
