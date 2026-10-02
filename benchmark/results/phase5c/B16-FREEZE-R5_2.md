# B16 prospective semantic and derived-target freeze — R5.2

**Frozen before either track's B16 preflight, prediction, implementation,
classification or exposure.** One track-neutral semantic requirement governs
both tracks: the existing `benchmark/requirements/B16.md`. No B16 capability
is deemed achieved by this freeze. Validated protocol predecessor:
`R5_2-B15-REVALIDATION.md`; immutable versioned protocol amendment:
`PROTOCOL_AMENDMENT_R5_2_STATE_RELATIVE.md` SHA-256
`ecdf7b72e79a0756c628a998e6ed7654b02c26e4de20191317edc64ca237d828`.

## Frozen common semantic request, case and selection rule

| Raw artifact | SHA-256 |
| --- | --- |
| `benchmark/requirements/B16.md` | `cf9ede733a5b305677dc954a50a9146d9766a7943e0a2f70099b9db4c4fdc1be` |
| `benchmark/harness/capabilities/B16.json` | `2e50f5ff3fc35ae3adfbed5c263b192f887b5d476da8af943262c87421e5411d` |
| `benchmark/harness/cases/B16.py` | `b4e3bf5eaa3286d3f9569a0f48a3a8974fbc0d4defaf97f8f64958d64b24f49b` |
| `benchmark/harness/regression_phase5c_r5_2.py` (prospective B16 oracle) | `ef0aa0b99b7c9f398d5096bb4c90268e48b7f0116427df1bab7bf5e1b4f7a2c2` |
| `benchmark/harness/test_phase5c_b16_prospective.py` | `1129d2595e769f23d7eec23e4e71e7835661812bc5b3c8e5ee6edc358ab34c65` |
| State-relative composer | `eb5172eab4287cad80a67e47820e8039a0ac678252a36ed40adf735c4f048f97` |

The B16 fragment defines one `ensure_fields.owner` target: string with
`system` migration default; if the achieved prior contract already contains
it, its existing default must be exactly `""`. No B10 prerequisite is
declared. The three methods in the common B16 case cover user creation and
ordering; built-in system; ownership required and existing-user validation;
system migration of unowned tasks; migration failure/no-write and retry of an
unresolved nonempty owner when a prior owner field exists; and continuing
owner filters where previously achieved. The last conditional test is
inapplicable only when the prior achieved contract has no owner to migrate.
This is a prior-state applicability condition, not a track condition.

R5's exact 27-method replacement inventory remains pinned unchanged. The
prospective runner validates the B15 predecessor and pinned artifact hashes,
derives the B16 target, composes that frozen case plus conditional R5
replacements and prior applicable cases, and requires an exact target hash.
The earlier corrected R5.1 runner remains reserved for the B15 boundary.

## Independently derived targets (before predictions)

| Achieved B15 predecessor | Predecessor checkpoint SHA-256 | Structural realization selected solely from prior state | B16 target expectation SHA-256 | Conditional R5 methods |
| --- | --- | --- | --- | ---: |
| Conventional B01–B15 | `b679b53012630ce4e2c29c6c4c1c8ebcb3c1e143b6d7323527350e8e572c0cf3` | `owner` exists as string/default `""`; refine default to `"system"`, do not append | `272f3cbef481b47b6ac91d85b7dc708e64b8e5263a9bdcc63840687f825922c8` | 24 |
| Lykoi B01,B04 | `c5110e4331bf24c2ac6f5889e1ba2a00ba93f9f354f7e9d1c4bd689d7c2b61a0` | `owner` absent; append string field/default `"system"` | `0c61e3be245c0b0e2870ed872c71ea62a6423b59c90575ac720e41f608040f98` | 5 |

Both use the *same* new requirement, case and fragment. Their complete
expectation hashes differ because their independently validated earlier
achievements and inherited field sets, version numbers and B11 supersessions
already differ. In both B16 targets `owner` is a string whose migration
default is `system`. The prior profiles and B15 implementation bytes remain
unchanged. The new prospective fixture built both oracles without executing
B16 against either B15 app. Complete harness discovery passed 26/26 after
this freeze preparation; both complete B15 external/internal suites and the
original 20 harness cases passed in `R5_2-B15-REVALIDATION.md`.

**Execution gate:** a versioned checkpoint writer/validator for the R5.2
composed profile and B16 result, plus track-local preflight and prediction
freeze, must be prepared before any track receives B16. A prospective oracle
target is not an implemented capability. Neither track has yet received B16.
