# External oracle

`test_baseline.py` launches both programs by absolute path in independent
temporary working directories. It imports neither application's code. The
cases cover the lifecycle, sorting, filtered reads, failures and no-write
guarantee, two legacy migrations, corrupt state, and overdue selection using
fixed past/future records. Tests assert the contract in `../baseline.md` for
each track; a normalized trace additionally compares both tracks. New
requirement acceptance tests belong here and are frozen before agents see them.

Run with `python -m unittest discover -s benchmark/harness -v` from the root.
For time-boundary requirements, inject fixtures or use externally observable
instants robust to elapsed execution time; never import backend internals as a
substitute for black-box verification.
