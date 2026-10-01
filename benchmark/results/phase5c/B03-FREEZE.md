# B03 prospective oracle freeze

Frozen before either track received B03:

- Requirement: `benchmark/requirements/B03.md`, SHA-256 `56c6ac4c187962c71d5866b27f9568c8b6de055a0bab074896ef41b61a554630`.
- External case: `benchmark/harness/cases/B03.py`, SHA-256 `dd99843e8ff79c0f9c3d174671b9a54e9becf64ce8bca19e9ff8e47fa14ae9df`.
- Schema profile: `benchmark/harness/profiles/B03.json`, SHA-256 `46ff02e3ff6ea48a7990c2f522fb9fa7bbefcab3c88550be007e0c2c1b75972f`.

The schema profile repeats B02 because B03 adds no task field. The case uses
only external CLI subprocesses and isolated temporary storage. It checks exact
case-sensitive selection, ordinary list order, completed inclusion, absence,
untrimmed query input, blank rejection, and no-write behavior.
