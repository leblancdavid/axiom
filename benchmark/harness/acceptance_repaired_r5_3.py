"""Prospective R5.3 bridge: import the frozen R5.2.2 corrected transition.

This does not claim equivalence for all earlier rewritten R4/R5 bodies. It
fails closed on drift and proves the new carriers match the composed suite.
"""

from pathlib import Path

import acceptance_inventory_r5_3 as prior
import assertion_preservation_r5_2_1 as frozen_parent
import assertion_preservation_r5_2_2 as repair
import capability_profile_r5_2 as profiles
import regression_phase5c_r5_1 as parent
import workspace as w


REPAIR_SHA256 = "f258414bd585f8f1aff5cc3ef7ba4514172b0c0d86febb2e2571eabaf6b30e8c"
PARENT_SHA256 = "b1748609f0a1f9d24013a3b5626f96be5a0faa1f77c5d3406f7eb3f549df3db0"
FREEZE = prior.RESULTS / "PROTOCOL_AMENDMENT_R5_2_2_B01_PRECONDITION.md"
BOUNDARY = prior.RESULTS / "R5_2_2-POST-B16-CORRECTED-CONTINUATION.md"
EXPECTED = {
    tuple(f"B{i:02}" for i in range(1, 17)):
        "dbccec9d10889aee7e04f160a7fbfd070d99aaa758c5db333b4e22be8b1362fe",
    ("B01", "B04"):
        "ca3d163bab055381827226140568f3bef7eaac187cebd76878e0b63e9e442356",
}


def collect(achieved):
    """Load the repair's own root inventory, with no R5.3-local root definitions."""
    w.require(FREEZE.is_file() and BOUNDARY.is_file() and
              w.file_hash(Path(frozen_parent.__file__)) == PARENT_SHA256 and
              w.file_hash(Path(repair.__file__)) == REPAIR_SHA256,
              "frozen assertion-preservation transition drift")
    profile = profiles.compose(achieved)
    methods, _, observed = prior.collect(achieved)
    prior.validate_sources(methods)
    root_inventory = repair.inventory(observed, profile)
    digest = w.digest(w.encoded(root_inventory))
    w.require(digest == EXPECTED[tuple(achieved)], "frozen repair semantic inventory drift")
    with prior.isolated_construction():
        replacements = parent.load_module("regression_B16_R5", parent.CASE)
        suite, _, disposition, actual = repair.build_suite(
            w.ROOT / "benchmark/conventional/task_manager.py", profile, achieved,
            replacements, mark_skips=False)
        w.require(actual == root_inventory and disposition == observed,
                  "repair carrier selection differs from parent composition")
        repair_ids = {test.id() for test in prior.instances(suite)
                      if test.id().startswith(("assertion_preservation_r5_2_1.",
                                               "assertion_preservation_r5_2_2."))}
        parent_names = set(frozen_parent.selection(observed)) - {
            frozen_parent.CARRIERS[frozen_parent.PRIORITY]}
        expected_ids = {f"assertion_preservation_r5_2_1.cases.<locals>.Preservation.{name}"
                        for name in parent_names}
        expected_ids.update(f"assertion_preservation_r5_2_2.cases.<locals>.Correction.{name}"
                            for name in repair.selection(observed))
        w.require(repair_ids == expected_ids, "executable repair/inventory mismatch")
    return {"achieved": list(achieved), "parent_methods": methods,
            "restored_roots": root_inventory, "repair_inventory_sha256": digest,
            "repair_carrier_ids": sorted(repair_ids),
            "parent_inventory_sha256": w.digest(w.encoded(
                {"achieved": list(achieved), "methods": methods})),
            "full_prior_assertion_equivalence_proven": False}
