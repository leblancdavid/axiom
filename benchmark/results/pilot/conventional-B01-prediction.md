# Conventional B01 — pre-change prediction

Agent session `ses_f072e4e64ffemgqWUPYyxiuNC1`. Saved before implementation;
raw event transcript: `C:\Users\lblan\AppData\Local\Temp\opencode\axiom-phase5a\logs\conventional-B01-prediction.jsonl`.

- **Expected source file:** `task_manager.py`. The shared `PRIORITIES` tuple is the likely change point: adding `CRITICAL` after `HIGH` should make it available to both CLI argument choices and stored-record validation.
- **Components affected:** `Task.from_record` should accept persisted `CRITICAL` values; `TaskService.create` should save the selected value. `TaskService.list` should continue to return all tasks, while its `list-high` filter should remain exactly `HIGH`.
- **CLI interface:** `create --priority CRITICAL` should be accepted and returned in the JSON result. `list` should include that task. Omitting `--priority` should still produce `NORMAL`; no new command is expected.
- **Expected tests:** Cover create-and-reload of `CRITICAL`, inclusion in `list`, exclusion from `list-high`, the missing-priority default, and migration preserving existing `LOW`, `NORMAL`, and `HIGH` values.
- **Persistence concerns:** The current schema is version 3, with priority stored as a string. This appears to need expanded value validation rather than a schema-version change. Version 1 migration supplies `NORMAL`; version 2 migration retains each existing priority. Both paths should keep working without rewriting existing priority values.
