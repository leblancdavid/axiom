# Frozen baseline evidence (2026-10-01)

Phase 4 parent commit: `7e1d5eb` on `main`. Benchmark preparation is uncommitted
at this record's creation; use the hashes below, not the parent commit alone,
to identify the conventional implementation and the new oracle. No B01–B20
change has been executed. Python: `3.14.3`; compiler version: `0.3.0`;
model version: `0.3`; no third-party runtime dependencies.

Verification from the repository root:

* `python -m unittest discover -s benchmark/harness -v`: **3 tests passed**,
  each runs against both tracks as separate CLI subprocesses.
* `$env:PYTHONPATH='src'; python -m unittest discover -s tests -v`:
  **31 tests passed**.
* Generated artifact manifest's SHA-256 of `task_manager.py` agrees with the
  actual artifact hash below.

All hashes below are lowercase **SHA-256 of file bytes**, not Git object IDs.
The parent commit pins the remainder of the unchanged compiler and test tree.

| File | SHA-256 |
| --- | --- |
| `benchmark/conventional/task_manager.py` | `0c2b0411b5b88b9604915e3c34dfa97d44e154695cd388b03c274914688ad581` |
| `air/task_manager.json` | `971b8ec4079d45101ff8fd7877b6ccd86e7c931124621cf4b5394e93e9dd2f14` |
| `src/air_compiler/generator.py` | `20ca127d8c8eaba1578c470eb091cb662151f17fb224e519815775908a93a27f` |
| `src/air_compiler/runtime_template.py` | `123377385c864a0e3e7913686315e69b706b6cfa919994d911f2f910352ae4b9` |
| `src/air_compiler/validator.py` | `b9943552b286ee9692871742ef2ee1426d6a607d141e39e26debb5e965be2cd0` |
| `generated/task_manager.py` | `8ca83a7a0a11b91aff864bdefd6a861a4dc09e2003c5bbed1988e1ca626df6c6` |
| `generated/task_manager.manifest.json` | `58b7c24089d290db7e2acd6d49372ee148819e6839fce1da79ee91b4e44f88fd` |
| `benchmark/baseline.md` | `d69de8d4da44c74aff1ac9c6361995ad8dc881f454271cfaedff61d3e98651e5` |
| `benchmark/harness/test_baseline.py` | `93ac14d9a5ccd8d1034d5ec314edfbbcb4604de5865ca19a0cf1de709a0890e6` |
| `benchmark/README.md` | `2033035c0f8fe48da63737059ce8b05bccce310a82465107e1e9425d9c72d1fa` |
| `benchmark/harness/README.md` | `55990199d403d5c5e7197d0d3d1b612e5a23d6982bc82a0421f5ecb8de5d495c` |
| `benchmark/requirements/README.md` | `152efdaf2ddaac79ae7e87bcc0dc31327a6ff6d9ba7a45e17711f097353d1e8b` |

## Frozen requirement hashes

| Request | SHA-256 |
| --- | --- |
| B01 | `b7b2d714db5cee566e9e55982dd4c4d95d3d57f0c341e04ba1e15c24e9a8e94d` |
| B02 | `8a76e276240fa840c473be60a8e7ed0e10bd0c165426b1bfc84741e69872032b` |
| B03 | `56c6ac4c187962c71d5866b27f9568c8b6de055a0bab074896ef41b61a554630` |
| B04 | `2c2e9e3787d53eb45df7b4b48362db2217e62c165dedda38222f5561cd859221` |
| B05 | `fc06265789c2781c913e14dfc22a8c37a0ed627b1e1839d43ebaec31373372ff` |
| B06 | `b2be288e4e5a58ac348169860f3e4123b1560c9a9d787787005ff94b46c04b61` |
| B07 | `588e21f734cf75003dfd96a414a4f7352aded8c4146daab5e1e2b4f74164f1f8` |
| B08 | `dbe9d062092c4fc00c2d32210b8e493dbe0f05d0f2ee2e462c44588988335109` |
| B09 | `dd44a353c5d26c099e7cee3fc7e0d3fe6361f70b139a11e85b61473631b3c121` |
| B10 | `3bf536185111466f225ccc8a1fc8ae10a99cfa6da8e85d3a04fca533306febe5` |
| B11 | `7ab1ea7ac3cf963993a30135ae9cf4f3de1a05b64ab294bc86940bc5ecf66c92` |
| B12 | `d60ee7901f4735fb9903cc24e5abb61a6483b9a884970f029be3ddd7567ab942` |
| B13 | `6a93ed0a15f3869fb6e35f6ddfa34f200a0e1620d1b3e0dc2505711d450e00f5` |
| B14 | `c267a859afff26708f17feea0c88bd77ec53f5768a0087dd8345ada3fd3bd31c` |
| B15 | `fe38279c15d7ed6b3282390539f0bd8a8e2e8e6026e3dface0e1774a2c0ae9ff` |
| B16 | `cf9ede733a5b305677dc954a50a9146d9766a7943e0a2f70099b9db4c4fdc1be` |
| B17 | `2a4cf402ded60283086ff321e614b0fac542410fd9c6ce6b4a89af696b090fe0` |
| B18 | `dc0394bdbfbb0460298a86f9be25c2d6dfcf3340b83b4a423d106907d02e57ae` |
| B19 | `854b9441eb2637dc025fc4e050d7e6bd892b6c27e347d0132c59ca851866abcd` |
| B20 | `94a030660b74bafd44513204e3d3e36c5cca16f24f0fd39101b67eea8d4eaefb` |

Baseline preparation only; subsequent experiment results should go into new
step-specific files, never overwrite this record or earlier requirements.
