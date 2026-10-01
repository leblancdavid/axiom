# Axiom B01 — pre-change prediction

Agent session `ses_f072c4b7cffehP7aLM3Qp4dznV`. Saved before implementation;
raw event transcript: `C:\Users\lblan\AppData\Local\Temp\opencode\axiom-phase5a\logs\axiom-B01-prediction.jsonl`.

Expected canonical edit: `air/task_manager.json` adds CRITICAL to `type_priority`
and the `inv_priority` IN predicate. `field_priority` and `arg_priority` type
references, `fn_create` default assignment, `contract_create_priority`,
`contract_create_persisted`, `fn_list_high` exact HIGH filter and command
bindings remain relevant but need not change. The CLI gains an accepted
`create --priority CRITICAL` value; `list-high` remains exactly HIGH.

State schema version 3 and the existing version-1/2 migrations should remain
valid without a new migration. Reverse impact paths predicted include
`type_priority → field_priority → inv_priority/fn_create/fn_list_high →
cmd_list_high` and `type_priority → arg_priority → fn_create → cmd_create`,
as well as broader paths via `type_task`, `type_task_list`, and `state_tasks`.
The generated artifact and manifest should be regenerated, not edited.
Expected tests: create/reload/default/filter/migration cases in
`tests/test_application.py`, and enum/invariant/generation checks in
`tests/test_compiler.py`. No compiler or generic schema change predicted.

The verbatim agent output is retained in the raw transcript.
