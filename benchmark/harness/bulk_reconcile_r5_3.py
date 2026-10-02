"""Evidence-preserving first pass over the saved R5.3 executed candidates.

This is a reconciliation worksheet, not an equivalence certificate. In
particular, an assertion observed in a helper is not covered by a caller-site
root merely because that helper was invoked there.
"""

import argparse
import ast
from collections import Counter
import json
from pathlib import Path

import semantic_channels_r5_3 as channels
import workspace as w


DISPOSITIONS = ("SEMANTIC_ROOT", "SEMANTIC_COMPONENT", "DUPLICATE_OBSERVATION",
                "HARNESS_MECHANIC", "CONTROL_FLOW", "UNEXPLAINED")


def reconcile(baseline, trace, source_roots):
    w.require(baseline["achieved"] == trace["achieved"] and
              baseline["trace_sha256"] == trace["events_sha256"],
              "saved candidate inventory / runtime trace mismatch")
    events = trace["events"]
    roots = {}
    provisional = {}
    event_to_roots = {}
    rows = []
    for candidate in baseline["source_candidates"]:
        row = {**candidate, "disposition": "UNEXPLAINED", "canonical_roots": [],
               "reason": "No checked assertion/CLI runtime witness"}
        witnesses = candidate["runtime_event_indices"]
        for index in witnesses:
            event = events[index]
            if candidate["channel"] == "direct_assertion":
                if event["kind"] != "assertion" or event["source"] != candidate["source"]:
                    continue
                if not event["passed"]:
                    raise ValueError(f"failed authoritative assertion: {index}")
                if not candidate["expression"].startswith("self." + event["assertion"] + "("):
                    # Some assertions are invoked through test.assert* rather
                    # than self.assert*; preserve them for explicit review.
                    continue
                expression = ast.parse(candidate["expression"], mode="eval").body
                if not isinstance(expression, ast.Call) or len(expression.args) != len(event["arguments"]):
                    continue
                family = ("file_bytes" if ".read_bytes()" in candidate["expression"] else
                          "file_existence" if ".exists()" in candidate["expression"] else
                          "persisted_field" if ".read_text(" in candidate["expression"] else
                          "returned_or_derived_assertion")
                identity = {"method": candidate["method"], "source": candidate["source"],
                            "column": candidate["column"], "event": index,
                            "kind": "direct_assertion"}
                root = {"id": w.digest(w.encoded(identity)), **identity,
                        "expression": candidate["expression"],
                        "assertion": event["assertion"],
                        "family": family,
                        "source_operands": [ast.unparse(arg) for arg in expression.args],
                        "expected_result": (event["arguments"][1] if len(event["arguments"]) > 1 else
                                            event["assertion"] in ("assertTrue", "assertIsNotNone")),
                        "operands": event["arguments"], "keywords": event["keywords"],
                        "observation_phase": "filesystem" if any(word in candidate["expression"]
                             for word in (".read_bytes()", ".exists()", ".read_text(")) else "assertion",
                        "prior_cli_event_ids": [i for i in range(index) if
                             events[i]["method"] == candidate["method"] and
                             events[i]["kind"] == "cli"]}
                provisional[root["id"]] = root
                for canonical in source_roots.get(candidate["method"], []):
                    if (canonical["assertion"] != candidate["source"] or
                            canonical["assertion_column"] != candidate["column"] or
                            canonical["phase"] != "persisted_state"):
                        continue
                    if canonical["operation"] == "file-existence":
                        if (family != "file_existence" or
                                event["assertion"] not in ("assertFalse", "assertTrue") or
                                ast.unparse(expression.args[0].func.value) != canonical["path_expression"] or
                                event["arguments"][0] != canonical["expected_result"]):
                            continue
                    elif canonical["operation"] == "file-bytes-equality":
                        if (family != "file_bytes" or event["assertion"] != "assertEqual" or
                                ast.unparse(expression.args[0].func.value) != canonical["path_expression"] or
                                len(event["arguments"]) != 2 or
                                event["arguments"][0] != event["arguments"][1] or
                                canonical["snapshot"]["source"] not in
                                [step["source"] for step in canonical["prior_steps"]]):
                            continue
                    elif canonical["operation"] == "persisted-json-field-equality":
                        if (family != "persisted_field" or event["assertion"] != "assertEqual" or
                                ast.unparse(expression.args[0].slice) != repr(canonical["field"]) or
                                ast.unparse(expression.args[0].value.args[0].func.value) !=
                                canonical["path_expression"] or
                                len(event["arguments"]) != 2 or
                                event["arguments"][1] != canonical["expected_result"] or
                                event["arguments"][0] != canonical["expected_result"]):
                            continue
                    else:
                        continue
                    checked = {**canonical, "runtime_assertion_event": index,
                               "runtime_operands": event["arguments"],
                               "provenance": {"carrier": candidate["method"],
                                              "assertion": candidate["source"]}}
                    row["canonical_roots"].append(checked["id"])
                    roots[checked["id"]] = checked
                    event_to_roots.setdefault(str(index), []).append(checked["id"])
            elif candidate["channel"] == "CLI":
                if (event["kind"] != "helper_enter" or
                        event.get("caller") != candidate["source"]):
                    continue
                invocation = event["invocation"]
                terminal = next((i for i in range(index + 1, len(events)) if
                                 events[i]["method"] == candidate["method"] and
                                 events[i]["kind"] == "helper_return" and
                                 events[i]["invocation"] == invocation), None)
                if terminal is None:
                    continue
                # Only a single-command helper call can be made canonical at
                # this site. Composite helpers require their own path expansion.
                children = [i for i in range(index + 1, terminal) if
                            events[i]["method"] == candidate["method"] and
                            events[i]["kind"] == "cli"]
                if len(children) != 1:
                    continue
                cli = events[children[0]]
                arguments = event.get("arguments", {})
                error = arguments.get("error", arguments.get("kwargs", {}).get("error"))
                expected_exit = 1 if error is not None else 0
                if cli["returncode"] != expected_exit or (error is not None and
                        cli["error"] != {"error": error}):
                    raise ValueError(f"frozen CLI result differs from source helper: {index}: "
                                     f"{candidate['expression']} / {event['arguments']} / "
                                     f"{cli['command']} / {cli['returncode']} / {cli['error']}")
                identity = {"method": candidate["method"], "source": candidate["source"],
                            "column": candidate["column"], "event": index,
                            "kind": "CLI_outcome"}
                root = {"id": w.digest(w.encoded(identity)), **identity,
                        "expression": candidate["expression"],
                        "family": "CLI_rejection" if error is not None else "CLI_success",
                        "helper": event["helper"], "arguments": event["arguments"],
                        "command": cli["command"], "expected_exit": expected_exit,
                        "expected_error": error, "observation_phase": "CLI_outcome",
                        "runtime_cli_event": children[0], "runtime_return_event": terminal,
                        "prior_cli_event_ids": [i for i in range(index) if
                             events[i]["method"] == candidate["method"] and
                             events[i]["kind"] == "cli"]}
                provisional[root["id"]] = root
        row["provisional_witness_ids"] = [key for key, value in provisional.items()
                                          if value["method"] == candidate["method"] and
                                          value["source"] == candidate["source"] and
                                          value["column"] == candidate["column"] and
                                          value["event"] in witnesses]
        if row["canonical_roots"]:
            row["disposition"] = "SEMANTIC_ROOT"
            row["reason"] = "Source-derived persisted-state root agrees with runtime assertion and snapshot"
        elif row["provisional_witness_ids"]:
            row["reason"] = ("Executed assertion/CLI outcome has a checked event correlation, but "
                             "its complete source-derived preconditions, phase and lineage have not "
                             "been verified against a canonical root")
        rows.append(row)
    counts = Counter(row["disposition"] for row in rows)
    root_to_events = {key: [root["runtime_assertion_event"]] for key, root in roots.items()}
    semantic_events = [i for i, event in enumerate(events) if event["kind"] in ("assertion", "cli") or
                       event["kind"] == "source_path" and event["site"]["kind"] == "Assert"]
    return {"achieved": trace["achieved"], "baseline_candidates": len(rows),
            "trace_sha256": trace["events_sha256"],
            "candidate_counts": {key: counts[key] for key in DISPOSITIONS},
            "source_candidates": rows, "canonical_roots": roots,
            "provisional_runtime_witnesses": provisional,
            "runtime_event_to_roots": event_to_roots, "canonical_root_to_events": root_to_events,
            "mapped_root_count": len(root_to_events), "unmapped_root_count": len(roots) - len(root_to_events),
            "unmapped_semantic_runtime_events": [i for i in semantic_events if str(i) not in event_to_roots],
            "rejection_path_completeness": "NOT ESTABLISHED",
            "assertion_level_semantic_diff": "BLOCKED"}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--baseline", type=Path, required=True)
    parser.add_argument("--trace", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    result = reconcile(json.loads(args.baseline.read_text(encoding="utf-8")),
                       json.loads(args.trace.read_text(encoding="utf-8")),
                       channels.collect(json.loads(args.trace.read_text(encoding="utf-8"))["achieved"])[
                           "direct_assertion_roots"])
    w.require(args.output.parent.is_dir(), "output parent missing")
    args.output.write_bytes(w.encoded(result))
    print(json.dumps({"candidates": result["baseline_candidates"],
                      "counts": result["candidate_counts"],
                      "canonical_roots": len(result["canonical_roots"]),
                      "unmapped_semantic_runtime_events": len(result["unmapped_semantic_runtime_events"])},
                     sort_keys=True))


if __name__ == "__main__":
    main()
