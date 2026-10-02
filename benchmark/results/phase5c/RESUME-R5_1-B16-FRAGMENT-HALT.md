# Phase 5C R5.1 — halt before B16 case/fragment freeze

**Status: HALTED AFTER VALID B16-READY BOUNDARY, BEFORE B16 FREEZE OR EXPOSURE.**
`B16-READY-R5_1.md` remains the validated B15 continuation boundary. Neither
Conventional nor Lykoi has received, predicted, attempted or classified B16;
no B16 case/fragment, prediction, implementation or checkpoint exists. No
B17–B20 request has been exposed. B01–B15 and both R5 freezes, including the
defective R5 pin and R5.1 correction, remain preserved.

## Additional protocol/composer contradiction discovered at B16 freeze planning

The unchanged frozen `capability_profile.py` accepts **one** track-neutral
`capabilities/B16.json` for all achieved histories and rejects adding any field
already present in the achieved schema (`add_fields` collision). Its
`change_defaults` requires the field already to be in the migration defaults.
There is no conditional contribution based on prior achieved capabilities.

* Conventional's B15 achieved set is B01–B15, including B10; its `owner` field
  and empty-string migration default already exist. To express B16's migration
  of unowned tasks to `system`, a B16 fragment must use `change_defaults` for
  `owner` from `""` to `"system"`, and **must not** use `add_fields.owner`.
* Lykoi's B15 achieved set is only B01 and B04. Its composed schema has no
  `owner` field. If Lykoi independently achieves B16 by introducing required
  ownership and users, a B16 fragment must contribute an `owner` field with
  `system` migration default. The same unconditional `change_defaults.owner`
  proposed for Conventional is rejected on Lykoi because that field is absent.
  Conversely unconditional `add_fields.owner` is rejected on Conventional
  because B10 already contributed it.

Selecting `requires: ["B10"]` for B16 would make Lykoi's B16 a preordained
blocked-by-B10 case, even though B16's new required-owner semantics might be
expressible independently and the protocol requires determining capability
through the normal experiment. The B16 requirement says existing owner
filters continue, but does not explicitly make achieved B10 a prerequisite
to expressing B16's new user/ownership semantics. Assuming that dependency
would prejudge the track-specific result. There is no valid single fragment
in the current composer that both represents a successful B16 on Conventional
and leaves an independent Lykoi B16 achievement representable. The
`B16-ACCEPTANCE-COMPOSITION-AUDIT.md` already noted both contribution cases;
the incompatibility of the frozen composer with a shared fragment became
decisive during prospective B16 freeze planning.

The authorized R5.1 repair was **only** the mistyped R4 integrity hash plus
necessary revision metadata; it did not authorize changing the frozen
composer, creating separate track-specific B16 fragments, redefining B10
dependency, or making another acceptance-composition amendment. Do not
silently choose one of these to continue. This is a protocol expressiveness
gap, **not** a Lykoi capability gap or any B16 classification.

## Next decision needed

Obtain a new explicit prospective decision on representing B16's `owner`
field/default across histories with and without achieved B10. Any authorized
solution must retain the frozen B01–B15 meanings, R5.1 track-conditional
acceptance mapping and independent B16 classification. Freeze the selected
solution and revalidate as required **before** either track's B16 preflight,
prediction or implementation. Do not rewrite this halt or the B16-ready
boundary, and do not report `PHASE_5C_COMPLETE`.
