# Corrected Axiom workspace B01 — pre-change prediction

Fresh session `ses_f0722ffafffeMkFb1UcVhZziW3`; verbatim prediction is in
`C:\Users\lblan\AppData\Local\Temp\opencode\axiom-phase5a\logs\axiom-corrected-B01-prediction.jsonl`.
Saved before implementation in the corrected full Axiom workspace.

The agent predicted edits to `type_priority` and `inv_priority` in
`air/task_manager.json`, plus documentation and application/compiler tests;
generated Python and manifest would be regenerated. It identified
`field_priority` and `arg_priority` as type dependents, `fn_create` and its
priority/persistence contracts, the exact HIGH-only filter in `fn_list_high`,
and conservative impact paths through commands and stored state. The CLI
should accept CRITICAL without a new command; old schema-version-3 state and
the two existing migrations should not require a new version. It predicted
tests for creation, listing, exclusion from `list-high`, default NORMAL,
migration preservation, invariant consistency and deterministic generation.
