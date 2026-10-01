# Frozen sequential change set

Execute B01–B20 in numeric order; a change is cumulative. Each file states an
observable API and acceptance criteria, not an implementation strategy. New
fields on existing tasks require an explicit `migrate` path; ordinary reads of
old storage must report `migration_required` without mutation. Migration is
atomic, returns the number of migrated tasks, and is idempotent. Missing IDs
return `task_not_found` unless a request explicitly defines another error.
Successful operations output JSON; application errors use the baseline JSON
error envelope and exit 1. New list commands use the baseline `(created_at,
id)` sort unless stated otherwise. Existing commands remain compatible unless
a request expressly changes them. Errors must leave observable state intact.

IDs and test cases are fixed before execution; correcting a faulty requirement
requires a recorded protocol deviation, never a silent retroactive edit.
The authoritative frozen file hashes are in `../results/BASELINE.md`.
