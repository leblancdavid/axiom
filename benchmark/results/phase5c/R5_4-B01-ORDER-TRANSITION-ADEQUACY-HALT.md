# R5.4 B01 order/transition adequacy restart — prospective halt

**STOP at B01.** R5.2.2 remains authoritative. This semantic prototype is
UNFROZEN; no Phase 5C execution, B17 exposure/classification, clause bridge or
schema freeze follows. Sources: `benchmark/requirements/B01.md:3-6`, the
pre-existing `benchmark/baseline.md:9-32`, original
`benchmark/harness/regression.py:163-196` and its corrected R5.2.2
intermediate-state carrier. The acceptance cases supply observable witnesses,
not implementation instructions or a license to generalize finite examples.

## Clause-by-clause frozen-text reconstruction

| Obligation | Status after this prototype | Reason |
| --- | --- | --- |
| B01:3 CRITICAL accepted as a priority, above HIGH | **Uncertain** for “above”: frozen text gives a domain extension and priority rank, not a requirement to sort task lists by priority. No typed priority-domain/rank relation or universally bound create input exists. Finite `invoke`/`observe` can witness acceptance. |
| B01:3–4 `create --priority CRITICAL` returns CRITICAL | **Expressible by existing scenario vocabulary** for a concrete call; **not currently expressible** for every valid create input as a typed command contract. |
| B01:4 CRITICAL persists and appears in `list` | **Expressible by existing scenarios** for a call/read sequence; **not currently expressible** as a general create-to-state-to-list relation for arbitrary states. |
| B01:4 `list` includes tasks in the baseline normal order | **Expressible by #43 for a given complete collection**: ascending `(created_at instant, id string)` with exact record multiset. The binding of that collection to every public list call is **not currently expressible**. |
| B01:4–5 `list-high` means exactly HIGH, including after CRITICAL is completed | **Expressible by new selection prototype** for any ordered source, exact predicate equality and all occurrences. Composition with #43 can fix source order, but universal binding to the application's state and call result is **not currently expressible**. R5.2.2 corrects the witness precondition: NORMAL and HIGH pending, CRITICAL completed. |
| B01:5–6 existing LOW/NORMAL/HIGH retain priorities through migration | **Expressible by #44 over a given valid before/after collection**; preservation applies to all present fields, including priority, matched by arbitrary unique identity, not fixture IDs. Universal CLI/storage binding remains **not currently expressible**. |
| B01:6 missing priority defaults to NORMAL | **Expressible by #44 for a given migration transition**, including mixed present/absent records; existing baseline create default is witnessable by existing scenarios. A general create omission/default contract and migration invocation binding are **not currently expressible**. |
| Baseline retained: migration is explicit; legacy read fails without write, migration count/idempotence, current-schema behavior, complete/delete retain priority | **Existing finite scenario vocabulary** can witness these; the new relations do not universally quantify over command traces, outcomes or persistent storage. These are inherited baseline obligations, not new B01-only operators. |

## Order decision

The normal result order is lexicographic ascending **created_at then id**, not
priority rank. The first key is a typed UTC instant, so representations of the
same instant compare as instants; the second is the unique task identifier.
For valid task collections, `(created_at, id)` ties cannot occur: no stable
sort/source-relative tie-break or deterministic fallback for invalid duplicate
IDs is required. The exact-result relation preserves full record multiplicity
and rejects omissions/extras. Applying exact HIGH selection to an already
ordered source retains the order without adding sorting to `selection`.
`state_relations.py` is an independent relation: it states permitted observable
results, not the implementation algorithm. It does not establish that the
prototype's partial three-field record schema represents every later task
field; a full declared schema is needed for each applicable state shape.

## Migration decision

`default_missing` relates arbitrary finite collections with unique string
identities. For each before record it requires exactly one after record with
the same identity, every existing field unchanged, and the declared default
only when that field was absent. No removed or added identities, changed
titles, overwritten priorities or missing updates pass. Result collection
order is deliberately independent of storage order; #43 constrains public
ordered query results. This reuses the finite transition and record concepts
without conflating B02's `stable_unique(map(trim(...))` or B14's acyclic graph
postcondition with record migration. A generic frame/default relation is
justified provisionally; its vocabulary/validator integration is unresolved.

`state-relation-fixtures.json` has three ordering witnesses (one positive,
two negative) and six migration witnesses (one positive mixed population,
five negatives: changed existing, wrong default, omitted, unintended, extra).
They distinguish these cases; they are not a proof over arbitrary inputs.

**Adequacy answer: NO.** The next precise gap is a typed, universally scoped
**command/state observation binding**: relate arbitrary valid create arguments,
persisted state before/after, returned task and subsequent exact `list` and
`list-high` results, and bind migration's old/new record collections to the
explicit public migration operation. Without it, #43/#44 constrain supplied
collections only, while scenarios enumerate fixed traces. A checked
priority-domain/rank meaning for “above HIGH” also needs adjudication without
inventing priority-based list ordering. Halt the B01 screen here. The
[updated ledger](R5_4-SELECTION-VOCABULARY-LEDGER.md) counts 44 provisional
constructs; reuse count alone does not justify either addition.
