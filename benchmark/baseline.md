# External baseline contract (before B01)

The interface is a subprocess CLI run from an isolated working directory.
Commands print exactly one JSON value to stdout on success (exit 0); expected
application failures print `{"error":"CODE"}` to stderr (exit 1). Commands
persist across separate processes in `tasks.json` in that directory. `list`
on missing storage returns `[]` without creating the file.

Each task result has exactly `id`, `title`, `description`, `status`, `priority`,
`created_at`, and `due_date`. IDs are unique nonempty strings; timestamps are
UTC ISO strings ending in `Z`. Lists sort by `(created_at, id)` ascending.

* `create --title T --description D [--priority LOW|NORMAL|HIGH]
  [--due-date UTC_TIMESTAMP]`: nonblank title, verbatim description, new ID,
  status `pending`, priority default `NORMAL`, current creation timestamp,
  due date default `null`. Blank title fails `invalid_title`; malformed or
  non-UTC due date fails `invalid_due_date` without changing storage.
* `list`: return all tasks including completed tasks.
* `list-high`: return only HIGH tasks (including completed ones).
* `list-overdue`: return only pending tasks with a non-null due date **strictly
  earlier** than current UTC time. Undated and completed tasks are excluded.
* `complete --id ID`: pending task becomes completed and is persisted; a
  missing ID fails `task_not_found`, an already completed task fails
  `invalid_transition`, both without altering the stored file.
* `delete --id ID`: remove and return the task (pending or completed); missing
  ID fails `task_not_found` without altering storage.
* `migrate`: explicit conversion of legacy unversioned records to version 3
  (add `priority: NORMAL`, `due_date: null`) and version 2 records to version 3
  (add `due_date: null`); return `{"migrated": N}`. Running on current data or
  absent storage returns `{"migrated": 0}`. Legacy reads fail
  `migration_required` without changing data. New writes use a version-3
  envelope with `schema_version` and `records`.

Malformed JSON and invalid record shape, duplicate IDs, blank IDs/titles,
invalid enums and timestamps fail `invalid_state` on read. Failed operations
must not mutate persisted bytes. An exact-time overdue boundary can be checked
only with a controlled clock; the external CLI oracle checks widely separated
past and future instants instead of relying on timing-sensitive sleeps.

The oracle exercises *both* executable CLIs with fresh subprocesses and
independent temporary directories; it asserts this contract before comparing
normalized outcomes. Random IDs and wall-clock timestamps are checked for
properties, not falsely required to be byte-identical across tracks.
