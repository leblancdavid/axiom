# R5.16 — Framed insertion and durable migration lowering (prospective, 2026-10-02)

**Decision:** both targeted general-lowering capabilities have bounded constructive
witnesses. This is an independent non-task compiler experiment, not a frozen
benchmark continuation or a universal correctness claim. The candidate semantic
inventory remains **30 core / 46 historical raw numbered entries**. No #31.

## 1–2. Insertion reconstruction and constructive interpretation

For a full typed input-derived record `R`, a finite uniquely keyed pre-collection
`S`, and post-collection `S'`, R5.9's #10–12/#43/#6/#21–23/#45 decomposition
requires: `select(S, key == R.key) = []` (freshness),
`select(S', key == R.key) = [R]` (exact full record, one occurrence), and
`multiset(select(S', key != R.key)) = multiset(S)` (every other complete record
and its multiplicity survive). The post identity is unique. These jointly
exclude replacement, deletion and extras; checking only target membership
would not. The complete-record comparison includes unrelated fields. This
relation does **not** specify storage order: #43 ordering is a separate rule
when an operation contract calls for it. No normal-order rule is present in
the specimen contract. Generated code chooses a deterministic append witness;
the case verifier accepts any post ordering satisfying the exact frame.

`relations: [{exact_frame: {collection, identity, record}}]` is a checked
**lowering representation of that existing conjunction**, not a candidate core
insertion operator. The compiler checks record shape and string identity against
the projected typed collection, emits freshness/unique-key checks and a
constructive collection containing all old rows plus the constructed record.
It does not dispatch on operation ID or domain. A repeated-key input takes a
typed unchanged branch. The verifier independently tests exact full-record
selection and outside-target multiset equality; it does not require append.

## 3–6. Independent domain, framing, mutation and composition

`test_framed_migration_r5_16.py` declares a specimen registry with typed
`code,label,origin,notes` input/state and a record-valued success. Empty and
two-record durable populations return and persist the constructed specimen;
the existing unrelated rows and notes survive exactly. Duplicate code is an
unchanged, typed alternative. A semantic-only projection mutation changes the
persisted origin from `input.origin` to `input.notes` after regeneration;
changing the independent result mapping likewise changes the public outcome.
No compiler/runtime edit is needed. A second contract composes #13 `trim` on
the label with full-record construction, exact framing and record-valued
outcome, again without composition-specific code. Direct verifier checks also
accept the new record at the *front*, showing that append is not a semantic
postcondition.

Four disposable target faults replace an unrelated record, delete one, insert
an extra identity or persist the wrong new record. They regenerate a matching
disposable provenance manifest so their independently captured public/file
observations and internal event remain **grounded**; each fails **semantic
conformance**. An overlapping collection-relation combination is explicitly
rejected as `UNSUPPORTED_LOWERING_CAPABILITY`, rather than executed with a
silently omitted frame.

## 7–13. Migration reconstruction, versioned domain and durability

Existing #21–23/#45 bind a conditional operation to its pre-state, outcome and
post-state; #44 requires a unique string identity and a bijective keyed
population, filling only missing optional fields, preserving every existing
field and excluding added/dropped identities. #30 relates the exact candidate
population to a typed integer. Version labels and their durable projections
are evolution/binding metadata, not #31: a typed `pre.format == V1` guard
selects the transition; `post.format == V2` is an independently checked
post-state equality. The #44 population source and #30 count source are both
the durable `pre.entries` projection in the *same* branch. No field-absence
count is substituted for population cardinality. The `V2` and unsupported
version branches return distinct typed outcomes with unchanged bytes and no
write. The contract's own `version` string is provenance, **not** the durable
format field.

The independent archive registry has a durable envelope containing `format`,
`entries`, and unrelated `owner`. Each entry has `seal,title,category` and
optional `aisle`. A V1 population of zero, one or two entries is converted to
V2 with absent aisles defaulted to `cold-storage`; an existing `north` aisle,
every seal/title/category, and `owner` survive. The typed outcome is
`{migrated: cardinality(pre.entries)}` (0, 1, 2 observed). Reopened durable
bytes show the version and population after each invocation. V2 is idempotent
and unsupported V0 is unchanged with an `unsupported` outcome. A semantic-only
default change to `vault` changes only the missing aisle in regenerated
durable output. #44's unordered keyed semantics permit reordering of records
in conformance; no migration storage-order rule was invented.

The compiler's `relations` lowering recognizes the general categories
`default_missing` on a typed collection projection and `post_equals` on a
typed state field. It rejects overlapping updates to one collection, rather
than treating the list as an unchecked imperative sequence. The emitted
transition updates only the declared collection and scalar projection; the
generic runtime type-checks the whole state and outcome before persistence.
This is a *checked durable transition*, not R5.15's invocation-edition guard.

## 14–18. Grounding, conformance, purity and composition pressure

The R5.13 observer opens the pre-file bytes, invokes the generated executable
as a subprocess, reads stdout/exit and the post-file independently, and
challenges the internal invocation/pre/post/outcome/write event and generation
digest before invoking the case verifier. Successful insertion, migration,
current/unsupported version and both compositions are grounded and conformant
in the cases above. Disposable migration faults (wrong default, wrong durable
version, wrong numeric count, dropped record, altered unrelated envelope field,
altered existing record field) are faithfully grounded and nonconformant.
Unchallenged intermediate writes and all-input correctness remain unproved.

Migration composes with an already-generative typed record-valued outcome,
#30 cardinality and #13 trim on a receipt string in one operation without
lowerer changes. This is a natural version-transition receipt, not an artificial
insertion during schema conversion. A valid but unsupported overlapping
collection transform rejects explicitly. In particular multiple defaults on
the same collection and arbitrary mixed ordering/update relations are **not**
silently lowered; no claim of full #45 coverage follows.

| Capability | SEMANTICALLY REPRESENTED | VALIDATING LOWERING | GENERATIVE LOWERING | GROUNDED EXECUTION | FAULT-TESTED |
| --- | --- | --- | --- | --- | --- |
| Exact framed insertion | yes, #10–12/#43/#45 conjunction | yes, bounded typed frame and full-row multiset | yes, domain-neutral fresh-key witness | yes, specimen file/call | yes, four target faults |
| Checked durable V1→V2 migration | yes, #21–23/#44/#30/#45 plus declared version binding | yes, bounded typed version/collection/outcome | yes, typed branch + keyed default + version update | yes, archive envelope/call | yes, six target faults |

Implementation purity audit: `generative_r5_13.py` checks typed relation
categories, identity/field names supplied by semantic data, guard expressions
and state projection shape; `generative_evidence_r5_13.py` checks the same
contract from public/durable observations. Runtime only handles typed file,
transport and event boundaries. No task priority/tag constants, B01/B02 command,
synthetic domain name, benchmark version number, fixture value or expected
frozen output enters the new lowerer. `exact_frame` is a checked compiler
recognition of the prior relational composition, not a new numbered semantic
construct. The verifier and emitter share AST/type logic, so common-mode
mistakes remain possible.

## 19–22. Coverage, accounting and next action

| R5.15 coverage row | R5.16 status |
| --- | --- |
| #13–17 ordered normalization | retained; composed into specimen insertion and migration receipt |
| #45 record-valued outcome | retained; used on both success paths |
| #44 one-field default | retained and now tied to checked durable version/post-version on a typed envelope |
| #30 numeric count | now tied to actual durable pre-population, fault-tested |
| #10–12/#43 insertion/frame | bounded constructive exact frame, independently grounded and fault-tested |

**Construct accounting:** 30 candidate core, 46 historical categorized raw
entries; 0 new core constructs. Unnumbered compiler changes: one typed relation
conjunction checker, two constructive collection/scalar relation categories,
record-envelope acceptance, and generated transition emission. Runtime changes:
**0**. Evidence/verifier changes: one relational conformance path and four new
focused tests with disposable faults. The syntactic relation category
`exact_frame` is an internal compiler encoding of existing selection/equality,
not an addition to the candidate vocabulary.

**Contamination audit:** implementation fixtures are specimen and archive
records only. The new generator/verifier contain no B02 command names, B02
field constants, task-specific logic, frozen fixture values, B02 version
constants, or benchmark-branching code. Historical harness suites may replay
their own pinned B02-stage checkpoints; this experiment did **not** generate,
execute acceptance for, ground or evaluate conformance of a B02 candidate.

**Next:** keep Phase 5C paused; independently challenge additional relation
shapes (multi-default evolution, explicitly ordered insertion and nontrivial
candidate selection) and checked interface bindings before deciding a separately
authorized frozen-request retry. R5.2.2 remains historical authority, B17
unexposed/unclassified, the semantic-first format globally unfrozen. Universal
implementation correctness is not claimed.

Verification: benchmark harness **159 OK** (includes architecture, grounding,
semantic prototypes, R5.10–R5.15 focused suites and four R5.16 tests);
application/compiler suite **31 OK**. Focused R5.16 **4 OK** after the final
reordering assertion. `git diff --check` succeeded on tracked changes; Git
separately emitted LF→CRLF working-copy warnings, not whitespace failures.

R5_16_LOWERING_GAPS_CLOSED
