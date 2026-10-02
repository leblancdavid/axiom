# Phase 5C R5.2 — prospective state-relative composition amendment

**Version:** `PHASE5C-R5-STATE-RELATIVE/1`. **Status:** frozen prospective
composer protocol before B16 case/fragment freeze, prediction, implementation,
or classification on either track. Authorized after the R5.1 B16 fragment halt.
Additive to R5/R5.1; no R5.1 artifact is changed. The preceding audit and
design decision is `R5_2-STATE-RELATIVE-DECISION.md` (pinned below).

## Semantics, inputs and deterministic realization

One request has one frozen functional meaning (`requirements/B16.md`),
independent of a track's implementation language and prior representation.
`target semantics = compose(valid prior achieved semantics, frozen request
semantics)`. `ensure_fields` is a declarative, reusable state-relative schema
realization for a new request fragment, not a second request or a patch to an
application. Each field rule fixes one target type/default and an explicit
finite list of permitted *existing* defaults of that type. If absent from the
prior composed schema, append the field and install that type/default. If
present, require a known identical type and a permitted current default; retain
its position and set the target default. Reject unknown priors, mixed field
operations, duplicates, implicit type changes and malformed fragments. Increment
schema version only by the fragment's frozen `schema_increment`, regardless of
branch. Preserve all unrelated fields, defaults and supersessions. The branch
is based solely on the independently established achieved profile, never on a
track label, source code, generated output, prediction, tests or classification.

The original composer is still authoritative for every history without a new
state-relative fragment, including both B15 checkpoints. The separate R5.2
composer delegates such histories to it and starts state-relative processing
only at the first prospectively frozen fragment using the new operation.
Fragments remain shared and hashed. Later fragments can use this same rule
without introducing a per-track template. Only SUCCESS adds a request to an
achieved set; a failed/blocked attempt cannot activate its profile or grant
implementation capabilities. The B16 oracle may specify required ownership
and users, but each track must independently implement and validate them.

R5/R5.1's exact B16 replacement map, B11/R4 supersessions, origin gating,
and per-achieved-set conditional activation remain unchanged. A successful B16
may replace only applicable historical methods, retaining unaffected checks;
an unsuccessful B16 leaves that track's original B15 acceptance active.
Before any B16 prediction, freeze the *single* requirement, one B16 fragment,
acceptance case and exact derived target profile/hash per B15 achieved history.
Record the relevant prior B15 checkpoint hash and the selected presence rule.
Do not treat the different field positions/schema versions inherited from
prior achieved histories as a difference in B16's required observable behavior.

## Immutable inventory (raw SHA-256)

| Artifact | SHA-256 |
| --- | --- |
| Prior design decision `R5_2-STATE-RELATIVE-DECISION.md` | `24de4ba0b067299f3d0bceefbbc704c39349bab116b34ba9cf52b285a05e0ed3` |
| New composer `benchmark/harness/capability_profile_r5_2.py` | `eb5172eab4287cad80a67e47820e8039a0ac678252a36ed40adf735c4f048f97` |
| New fixture `benchmark/harness/test_phase5c_r5_2.py` | `b76550ccfbb209ca4b734341286a1a99ffdd8ce0e7c1b4bb5add10d08224f124` |
| Original composer (unchanged) | `cd0d318f5e7dd3dc2cdac7c93a0cd8c822c35cf53d83c365093a6c5e6971fb50` |
| Corrected R5.1 runner (unchanged) | `419a5feb9c09643adfa7c48ac9cf5123e255451571ff91345103cd7aa83e28c0` |
| R5 replacements (unchanged) | `9310e8f19557c8e9dfee4a1c4527524ec38c5de238d5b11d3ef9f5e08aa72d74` |
| Conventional B15 checkpoint / snapshot | `b679b53012630ce4e2c29c6c4c1c8ebcb3c1e143b6d7323527350e8e572c0cf3` / `8f06f0f62a224139895b7fae48d14160a60e25ebd97a091679b05b3db3f048bc` |
| Lykoi B15 checkpoint / snapshot | `c5110e4331bf24c2ac6f5889e1ba2a00ba93f9f354f7e9d1c4bd689d7c2b61a0` / `36e34184bd3d9cd9c65287d49d813838ca31197de6467b387defb1e1147c4ff5` |

The R5.1 runner continues to validate **B15 only**. It is not authorized for
B16 profile/checkpoint composition; B16 execution needs a separately pinned
acceptance and checkpoint integration using the R5.2 composer. Neither track
may be exposed to B16 until that integration, B16 case/fragment freeze and
the independent derived-target freeze have been validated prospectively.
