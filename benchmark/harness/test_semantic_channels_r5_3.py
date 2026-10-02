"""Source-channel coverage and repeatable helper expansion (prospective)."""

import unittest

import acceptance_inventory_r5_3 as prior
import acceptance_repaired_r5_3 as repaired
import semantic_channels_r5_3 as channels
import workspace as w


class SemanticChannels(unittest.TestCase):
    def test_construction_is_repeatable_without_wrapper_accumulation(self):
        full = [f"B{i:02}" for i in range(1, 17)]
        early = ["B01", "B04"]
        baseline = prior.r5.original.check_task
        for achieved in (full, early, full):
            first = channels.collect(achieved)
            self.assertEqual(first, channels.collect(achieved))
            self.assertIs(prior.r5.original.check_task, baseline)
            self.assertFalse(first["semantic_equivalence_proven"])
            prior_methods, _, _ = prior.collect(achieved)
            for name, method in first["methods"].items():
                expected = prior_methods[name]["assertions"] if name in prior_methods else None
                if expected is not None:
                    self.assertEqual(
                        sum(c["kind"].startswith("assert") for c in method["channels"]) +
                        sum(c["kind"] in ("check_task", "upgraded") for c in method["channels"]),
                        len(expected), name)
                for site in method["channels"]:
                    if "helper" in site or "local_helper" in site:
                        self.assertTrue(site["expansion"], (name, site))
            self.assertEqual(w.digest(w.encoded(first)), w.digest(w.encoded(channels.collect(achieved))))

    def test_parameterized_helper_and_intermediate_state_are_retained(self):
        full = channels.collect([f"B{i:02}" for i in range(1, 17)])
        early = channels.collect(["B01", "B04"])
        for evidence, fields in ((full, 7), (early, 1)):
            checks = channels.helper_sites(channels.prior.BASE_CHECK_TASK,
                                           channels.profiles.compose(evidence["achieved"]),
                                           evidence["achieved"])
            self.assertEqual(sum(r.get("condition") == "R5 field_types" for r in checks), fields)
        restored = next(m for n, m in full["methods"].items()
                        if n.endswith("test_b01_intermediate_high_exact_precondition"))
        self.assertIn('self.create(cwd, "--title", "Default", "--description", "x")',
                      restored["body"])
        self.assertIn('self.call(cwd, "complete", "--id", critical["id"])', restored["body"])
        self.assertIn('self.assertEqual(self.call(cwd, "list-high"), [high])', restored["body"])
        self.assertEqual(early["repair_inventory_sha256"],
                         repaired.EXPECTED[tuple(early["achieved"])])


if __name__ == "__main__":
    unittest.main()
