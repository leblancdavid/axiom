# Phase 5C partial-run evidence freeze — halted

This records evidence available at the B03 stop. It is **not** authorization
to resume execution or a completed B01–B20 benchmark.
Lykoi is the project name; `axiom` in the artifact names below is a frozen
historical identifier, not the current project name.

| Artifact | SHA-256 |
| --- | --- |
| `benchmark/requirements/B03.md` | `56c6ac4c187962c71d5866b27f9568c8b6de055a0bab074896ef41b61a554630` |
| `benchmark/harness/cases/B03.py` | `dd99843e8ff79c0f9c3d174671b9a54e9becf64ce8bca19e9ff8e47fa14ae9df` |
| `benchmark/harness/profiles/B03.json` | `46ff02e3ff6ea48a7990c2f522fb9fa7bbefcab3c88550be007e0c2c1b75972f` |
| `B03-conventional-prediction.jsonl` | `1c06e96deaead5f47255ee9cfefb3b74bbc32d3864d7978e90845bd3b5e238e7` |
| `B03-conventional-implementation.jsonl` | `53ac79ba5c0f14a8ee80b63fee531bc092470570733171afbec873a8a66a1eb2` |
| `B03-axiom-prediction.jsonl` | `7af0932bcf9ce42bc74b3f0b26bf751fb948bdc55f9923c500b6e6aa309a5e66` |
| `B03-axiom-implementation.jsonl` | `a859214c2ba9396d4f518afdf44069f6b6e6b80df42a43bc3d61ccddb8fa89b5` |
| `checkpoint-conventional-B03.json` | `727950c4e89b295333ab819eb23e76937b05775d5557e4d287f4fd0041686d19` |
| `snapshot-conventional-B03.tar` | `58e7f75af2a4b57327a2ca0cce3f91ddb778a824a97b3b5765ffc5119e3f8f82` |
| `checkpoint-axiom-B03.json` **quarantined** | `c81c5187ac14aee7052a07b370e1678d75e7fc0ac8eac1490ba052f80c8beb80` |
| `snapshot-axiom-B03.tar` **quarantined** | `e89b703b4a8f45aff553241ac2ae09bd08eef671d45b1aa23862f109510f8df1` |

Last valid starting checkpoints remain the Phase 5B B02 pair for Lykoi and
the independently restored B03 pair above for Conventional. See `REPORT.md`
for the defect, classification and evidence limitations. No B04 case/profile
has been created.
