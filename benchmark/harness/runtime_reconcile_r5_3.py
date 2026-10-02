"""Conservative runtime/static R5.3 reconciliation; unresolved sites stay open.

An observed source line is never by itself proof of semantic equivalence. This
report deliberately refuses to certify an assertion-level diff from proximity.
"""

import argparse
import json
from pathlib import Path

import coverage_gate_r5_3 as coverage
import workspace as w


def reconcile(static, trace):
    w.require(static["achieved"] == trace["achieved"], "achieved histories differ")
    executed = {}
    for index, event in enumerate(trace["events"]):
        sites = [event.get("source")]
        if event["kind"] == "helper_enter":
            sites.append(event.get("caller"))
        for site in sites:
            if site:
                executed.setdefault((event["method"], site), []).append(index)
    rows = []
    for candidate in static["unmapped_source_channels"]:
        indices = executed.get((candidate["method"], candidate["source"]), [])
        relevant = [i for i in indices if (
            (candidate["channel"] == "direct_assertion" and trace["events"][i]["kind"] in
             ("assertion", "source_path")) or
            (candidate["channel"] == "CLI" and trace["events"][i]["kind"] == "helper_enter" and
             trace["events"][i].get("caller") == candidate["source"]))]
        # Source-path execution is only a reachability witness. It does not
        # create a missing root or establish that two assertions are equivalent.
        rows.append({**candidate, "runtime_event_indices": relevant,
                     "runtime_reached": bool(relevant), "disposition": "UNEXPLAINED",
                     "reason": ("Executed site has no proven semantic root mapping" if relevant else
                                "Unobserved site needs static controlling-condition proof")})
    root_to_events = {}
    event_to_roots = {}
    for channel in ("direct_assertions", "cli_sites"):
        for site in static[channel]:
            if not site["roots"] or site["disposition"] == "unreachable":
                continue
            indices = executed.get((site["method"], site["source"]), [])
            for i in indices:
                event = trace["events"][i]
                if channel == "direct_assertions" and event["kind"] not in ("assertion", "source_path"):
                    continue
                if channel == "cli_sites" and (event["kind"] != "helper_enter" or
                                               event.get("caller") != site["source"]):
                    continue
                # Candidate correlation only: line and method plus channel
                # cannot establish operation/inputs/expectation equivalence.
                for root in site["roots"]:
                    root_to_events.setdefault(root, set()).add(i)
                    event_to_roots.setdefault(i, set()).add(root)
    semantic = [i for i, event in enumerate(trace["events"])
                if event["kind"] in ("assertion", "cli") or
                event["kind"] == "source_path" and event["site"]["kind"] == "Assert"]
    return {"achieved": static["achieved"], "trace_sha256": trace["events_sha256"],
            "source_candidates": rows,
            "candidate_counts": {key: sum(row["disposition"] == key for row in rows)
                                 for key in ("EXECUTED_SEMANTIC", "REPRESENTED_INDIRECTLY", "UNREACHABLE",
                                             "INFRASTRUCTURE_ONLY", "DUPLICATE_REPRESENTATION", "UNEXPLAINED")},
            "candidate_reachability": {"observed": sum(row["runtime_reached"] for row in rows),
                                       "unobserved": sum(not row["runtime_reached"] for row in rows)},
            "provisional_site_root_to_events": {key: sorted(value) for key, value in sorted(root_to_events.items())},
            "provisional_site_event_to_roots": {str(key): sorted(value) for key, value in sorted(event_to_roots.items())},
            "events_without_provisional_site_roots": [i for i in semantic if i not in event_to_roots],
            "semantic_event_to_roots": {}, "semantic_root_to_events": {},
            "rejection_path_completeness": "NOT ESTABLISHED",
            "assertion_level_semantic_diff": "BLOCKED"}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--static", type=Path, required=True)
    parser.add_argument("--trace", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    result = reconcile(json.loads(args.static.read_text(encoding="utf-8")),
                       json.loads(args.trace.read_text(encoding="utf-8")))
    w.require(args.output.parent.is_dir(), "output parent missing")
    args.output.write_bytes(w.encoded(result))
    print(json.dumps({"achieved": result["achieved"], "candidate_counts": result["candidate_counts"],
                      "candidate_reachability": result["candidate_reachability"],
                      "events_without_provisional_site_roots": len(result["events_without_provisional_site_roots"]),
                      "provisionally_correlated_roots": len(result["provisional_site_root_to_events"])}, sort_keys=True))


if __name__ == "__main__":
    main()
