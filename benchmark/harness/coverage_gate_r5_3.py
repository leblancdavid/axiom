"""Fail-closed prospective source-to-root inventory for both achieved histories.

UNMAPPED means no invocation root was found; it never implies the frozen oracle
is wrong. Source-site coverage is a necessary, not sufficient, completeness gate.
"""

import argparse
import ast
import json
from pathlib import Path

import audit_direct_observations_r5_3 as direct_audit
import semantic_channels_r5_3 as channels
import parameterized_roots_r5_3 as parameterized
import capability_profile_r5_2 as profiles
import workspace as w


LIVE = ("active", "replacement", "restoration")
CLI = ("call", "create", "upgraded")


def branch_qualifications(entry, achieved, profile):
    """Qualify statically decidable frozen branches, retaining unknowns open."""
    tree = ast.parse(entry["body"])
    bindings = {"PROFILE": profile, "profile": profile}
    result = {}

    def inspect_branch(statements, conditions=()):
        for statement in statements:
            if isinstance(statement, ast.If):
                test = statement.test
                decision = None
                if (isinstance(test, ast.Compare) and isinstance(test.left, ast.Constant)
                        and len(test.ops) == 1 and isinstance(test.ops[0], (ast.In, ast.NotIn))
                        and isinstance(test.comparators[0], ast.Name)
                        and test.comparators[0].id in ("achieved", "ACHIEVED")):
                    decision = (test.left.value in achieved) == isinstance(test.ops[0], ast.In)
                else:
                    try:
                        decision = parameterized.predicate(test, bindings)
                    except (ValueError, KeyError, TypeError, IndexError):
                        pass
                for branch, body in ((True, statement.body), (False, statement.orelse)):
                    condition = {"condition": ast.unparse(test), "branch": "then" if branch else "else",
                                 "reachable": decision is None or decision == branch,
                                 "resolution": "profile/achievement" if decision is not None else "unresolved"}
                    if decision is not None and decision != branch:
                        for item in body:
                            for descendant in ast.walk(item):
                                if isinstance(descendant, ast.Call):
                                    line = entry["first_line"] + descendant.lineno - 1
                                    result[line] = [*conditions, condition]
                    else:
                        inspect_branch(body, (*conditions, condition))
            elif isinstance(statement, (ast.With, ast.AsyncWith, ast.For, ast.While, ast.Try)):
                for attr in ("body", "orelse", "finalbody"):
                    inspect_branch(getattr(statement, attr, []), conditions)
                for handler in getattr(statement, "handlers", []):
                    inspect_branch(handler.body, conditions)

    inspect_branch(tree.body[0].body)
    return result


def collect(achieved):
    inventory = channels.collect(achieved)
    profile = profiles.compose(achieved)
    assertions = []
    cli = []
    for method, entry in inventory["methods"].items():
        if entry["state"] not in LIVE:
            continue
        direct = inventory["direct_observation_roots"].get(method, [])
        direct_assertions = inventory["direct_assertion_roots"].get(method, [])
        loops = inventory["parameterized_roots"].get(method, [])
        helper = inventory["helper_invocation_roots"].get(method, [])
        inactive = branch_qualifications(entry, achieved, profile)
        for site in entry["channels"]:
            location = f"{entry['source']}:{site['line']}"
            unreachable = site["line"] in inactive
            if site["kind"].startswith("assert") or site["kind"] == "python_assert":
                matches = [root["id"] for root in direct if root["assertion"] == location
                           and root["assertion_column"] == site["column"]]
                matches += [root["id"] for root in direct_assertions
                            if root["assertion"] == location and
                            root["assertion_column"] == site["column"]]
                matches += [root["id"] for root in loops if root["site"] == location
                            and root["column"] == site["column"]]
                assertions.append({"method": method, "source": location,
                                   "column": site["column"], "expression": site["expression"],
                                    "disposition": "unreachable" if unreachable else
                                    "mapped" if matches else "UNMAPPED",
                                    "branch": inactive.get(site["line"]),
                                    "roots": matches})
            if site["kind"] in CLI:
                matches = [root["id"] for root in direct if root["call"] == location
                           and root["call_column"] == site["column"]]
                matches += [root["id"] for root in loops if root["site"] == location
                            and root["column"] == site["column"] and root["kind"] == site["kind"]]
                matches += [root["id"] for root in helper if root["caller"] == location
                            and site["kind"] == "upgraded"]
                cli.append({"method": method, "source": location, "column": site["column"],
                            "kind": site["kind"], "expression": site["expression"],
                             "disposition": "unreachable" if unreachable else
                             "mapped" if matches else "UNMAPPED",
                             "branch": inactive.get(site["line"]),
                             "roots": matches})
    pattern = direct_audit.audit(achieved)
    gaps = [*({"channel": "direct_assertion", **row} for row in assertions
              if row["disposition"] == "UNMAPPED"),
            *({"channel": "CLI", **row} for row in cli
              if row["disposition"] == "UNMAPPED")]
    return {"achieved": list(achieved), "direct_assertions": assertions,
            "cli_sites": cli, "same_pattern_audit": pattern,
            "applicability_limit": "Source-site enumeration; conditional branch viability and concrete CLI invocations outside reconstructed loops are not yet fully classified. UNMAPPED rows are coverage candidates, not automatically applicable rejection paths.",
            "root_inventory": {key: {method: [root["id"] for root in roots]
                                     for method, roots in inventory[key].items()}
                               for key in ("direct_observation_roots", "direct_assertion_roots", "parameterized_roots",
                                           "helper_invocation_roots")},
            "root_hashes": {key: w.digest(w.encoded(inventory[key]))
                            for key in ("direct_observation_roots", "direct_assertion_roots", "parameterized_roots",
                                        "helper_invocation_roots")},
            "unmapped_source_channels": gaps,
            "rejection_path_completeness": "NOT ESTABLISHED" if gaps else
            "SOURCE SITES MAPPED; CONCRETE PATH COMPLETENESS UNPROVEN",
            "assertion_level_semantic_diff": "BLOCKED until concrete path completeness"}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", type=Path, required=True)
    directory = parser.parse_args().output_dir
    w.require(directory.is_dir(), "output directory absent")
    for label, achieved in (("full", [f"B{i:02}" for i in range(1, 17)]),
                            ("early", ["B01", "B04"])):
        result = collect(achieved)
        path = directory / f"R5_3-{label}-restarted-coverage.json"
        path.write_bytes(w.encoded(result))
        print(json.dumps({"history": label, "path": str(path),
                          "direct_assertions": len(result["direct_assertions"]),
                          "cli_sites": len(result["cli_sites"]),
                          "unmapped_source_channels": len(result["unmapped_source_channels"]),
                          "first_witness": result["unmapped_source_channels"][0]
                          if result["unmapped_source_channels"] else None}, sort_keys=True))


if __name__ == "__main__":
    main()
