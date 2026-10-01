# Conventional B02 — pre-change prediction

Agent session `ses_f072e4e64ffemgqWUPYyxiuNC1`; raw event transcript:
`C:\Users\lblan\AppData\Local\Temp\opencode\axiom-phase5a\logs\conventional-B02-prediction.jsonl`.
Saved before any B02 modification.

- **Expected files:** `task_manager.py` for implementation and `test_task_manager.py` for regression coverage.
- **Components:** Add a `tags` field to `Task` so every serialized task includes an array. Validate stored tags in `Task.from_record`. In `TaskService.create`, trim each supplied tag, reject blank values with `invalid_tag`, and deduplicate case-sensitively while preserving first occurrence order.
- **CLI:** `create` should accept repeatable `--tag VALUE` flags. With no flags, the created task should have `"tags": []`. The existing task-returning commands should include `tags` through their current serialization path. An invalid tag should return the existing JSON error format and leave the store without a new task.
- **Tests:** Cover repeated flags, trimming, ordered deduplication, case sensitivity, omitted tags, invalid blank input with no write, persistence/reload, and tags on task output. Extend migration tests for older records.
- **Persistence and migration:** Strict record validation requires a migration path for existing version 3 stores and default `tags: []` for version 1 and 2 records. A schema-version increase is likely needed; preserve existing priorities (including CRITICAL) and other fields.
