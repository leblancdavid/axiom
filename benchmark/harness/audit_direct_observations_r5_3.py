"""Prospective same-pattern audit of the loaded R5.2.2 CLI/assertion channels.

Site coverage is distinct from invocation/path completeness. A missing row is
decisive; zero missing rows is not a semantic-equivalence certificate.
"""

import ast
import json

import semantic_channels_r5_3 as channels


def audit(achieved):
    inventory = channels.collect(achieved)
    rows = []
    for method, entry in inventory["methods"].items():
        if entry["state"] not in ("active", "replacement", "restoration"):
            continue
        direct = inventory["direct_observation_roots"].get(method, [])
        loops = inventory["parameterized_roots"].get(method, [])
        for site in entry["channels"]:
            if not site["kind"].startswith("assert"):
                continue
            assertion = ast.parse(site["expression"], mode="eval").body
            if not assertion.args:
                continue
            cli_calls = [node for node in ast.walk(assertion.args[0])
                         if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute)
                         and node.func.attr == "call"]
            if not cli_calls:
                continue
            source = f"{entry['source']}:{site['line']}"
            matched = [root["id"] for root in direct
                       if root["assertion"] == source and
                       root["assertion_column"] == site["column"]]
            loop_matches = [root["id"] for root in loops
                            if root["site"] == source and root["kind"] == "call"]
            rows.append({"method": method, "assertion": source,
                         "expression": site["expression"], "state": entry["state"],
                         "cli_calls": len(cli_calls),
                         "disposition": "mapped" if matched else
                         "parameterized" if loop_matches else "UNMAPPED",
                         "roots": matched or loop_matches})
    return {"achieved": list(achieved), "pattern": "CLI call inside direct result assertion",
            "site_inventory": rows,
            "unmapped": [row for row in rows if row["disposition"] == "UNMAPPED"],
            "note": "This is a targeted site-pattern audit, not the exhaustive semantic rejection-path proof."}


if __name__ == "__main__":
    for history in ([f"B{i:02}" for i in range(1, 17)], ["B01", "B04"]):
        result = audit(history)
        print(json.dumps({"achieved": result["achieved"],
                          "sites": len(result["site_inventory"]),
                          "unmapped": result["unmapped"]}, sort_keys=True))
