# Axiom B02 — pre-change prediction

Agent session `ses_f072c4b7cffehP7aLM3Qp4dznV`; raw event transcript:
`C:\Users\lblan\AppData\Local\Temp\opencode\axiom-phase5a\logs\axiom-B02-prediction.jsonl`.
Saved before any B02 implementation attempt.

Predicted entities if expressible: `field_tags` on `type_task`, a `fn_create`
input and assignment, a `cmd_create` repeated flag, `err_invalid_tag`, a
precondition and guarantee/invariant, `state_tasks` version-4 migration with
`[]` default, `cmd_migrate` rebinding and scenario fixture changes. B01's
`type_priority`, exact HIGH filter and historical migrations must remain.
Impact paths predicted: `type_task → type_task_list → state_tasks` and
task-returning behaviors, `field_tags → fn_create → cmd_create`, and
`state_tasks → migration → cmd_migrate`; artifact provenance is wide.

**Predicted capability gap:** the frozen record/input algebra supports
primitive or enum fields, but the only list type is a list of records, not
strings. CLI flags do not collect repeated values; assignments do not trim
or deduplicate arrays; migration defaults cannot be array literals. Declaring
`invalid_tag` alone cannot implement the required observable behavior.
Expected canonical model, application/compiler tests and regenerated
artifact would require extending the forbidden compiler/runtime/schema.
This was an inspection prediction, not an implementation result.
