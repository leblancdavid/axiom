# Lykoi Phase 5C B11 prospective acceptance and supersession freeze

Frozen before either B11 preflight, prediction, or implementation.

| Artifact | SHA-256 (raw bytes) |
| --- | --- |
| `benchmark/requirements/B11.md` | `7ab1ea7ac3cf963993a30135ae9cf4f3de1a05b64ab294bc86940bc5ecf66c92` |
| `benchmark/harness/cases/B11.py` | `721fc2fb1c4d9f7d51978721799fd26be12a3186d481667fff5b0060be64201a` |
| `benchmark/harness/capabilities/B11.json` | `5dcf7ee0f046515bfdd198feede631c5b767fb17d5e77302d79b662f7e335f7c` |

B11 requires B08 archival. The new black-box case checks deletion of completed
unarchived tasks fails without writing, deletion of completed archived tasks
succeeds, and pending deletion in either archive state succeeds. It retains
baseline lifecycle and B01 priority, list, invalid-input, transition, sorting
and no-write coverage. Two prior frozen methods that assert completed
*unarchived* deletion succeeds are expressly superseded only if B11 is achieved:
`regression.Regression.test_baseline_lifecycle_filters_failures` (baseline)
and `regression.Regression.test_b01_priority_and_regression` (B01). They remain
unchanged on disk and active where B11 is not achieved. Their replacement is
the B11 case in this freeze, with explicit reasons in the fragment. No other
earlier case is superseded.
