# Blocked-request clause diagnostic — prospective record template

Copy to separately versioned evidence beside `benchmark/results/phase5c/` only
after an independently observable clause is probed. A blank template is not an
observation. Follow the
[B17 adjudication](../results/phase5c/R5_4-B17-PARTIAL-DEPENDENCY-ADJUDICATION.md).

| Diagnostic field | Evidence / value |
| --- | --- |
| Request ID and separately recorded request-level classification (source) | |
| Frozen clause semantic ID and requirement text/source span | |
| Exact prerequisite semantic root IDs; missing roots | |
| Track, pinned starting checkpoint hash and complete achieved-request set | |
| Disposable/restored setup, commands/inputs and expected observation | |
| Actual observation and preserved evidence (outputs, snapshots, hashes) | |
| Diagnostic result: `OBSERVED_SUPPORTED`, `OBSERVED_UNSUPPORTED`, or `NOT_OBSERVED_DEPENDENCY` | |
| Confirmation that B16/B17 semantics were not activated by the probe | |
| Proof the authoritative continuation and request-level classification were unchanged | |

Never add clause IDs to an achieved-request set or activate `adds`, `replaces`,
acceptance cases, or later-request dependencies on the strength of this record.
Do not mark an untested clause supported or unsupported. On Conventional's B16
continuation, B17 must still satisfy complete request-level acceptance.
