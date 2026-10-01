import argparse
import json
import sys
from pathlib import Path

from .generator import write
from .parser import AirError, load
from .semantics import inspect, diff, impact
from .planning import load_plan, evaluate, apply
from .validator import validate


def main(argv=None):
    parser = argparse.ArgumentParser(prog="axiom")
    parser.add_argument("operation", choices=("validate", "generate", "inspect", "diff", "impact", "plan", "apply"))
    parser.add_argument("air_file")
    parser.add_argument("output", nargs="?")
    parser.add_argument("--manifest", help="optional generated artifact manifest for impact provenance")
    args = parser.parse_args(argv)
    if args.operation == "generate" and not args.output:
        parser.error("generate requires output path")
    if args.operation in ("inspect", "diff", "impact") and not args.output:
        parser.error(f"{args.operation} requires an entity ID or second model")
    try:
        if args.operation in ("plan", "apply"):
            plan = load_plan(args.air_file)
            report = evaluate(plan)[0] if args.operation == "plan" else apply(plan)
            print(json.dumps(report, indent=2, sort_keys=True))
            return int(any(d["severity"] == "ERROR" for d in report["diagnostics"]))
        program = validate(load(args.air_file))
        if args.operation == "generate":
            write(program, args.output)
        elif args.operation == "inspect":
            print(json.dumps(inspect(program, args.output), indent=2, sort_keys=True))
            return 0
        elif args.operation == "diff":
            print(json.dumps(diff(program, validate(load(args.output))), indent=2, sort_keys=True))
            return 0
        elif args.operation == "impact":
            report = impact(program, args.output)
            if args.manifest:
                manifest = json.loads(Path(args.manifest).read_text(encoding="utf-8"))
                if manifest.get("application_id") != program.document["application"]["id"]:
                    raise AirError("manifest application does not match model")
                report["artifact_provenance"] = [
                    {"path": artifact["path"], "sha256": artifact["sha256"], "relation": "GENERATES",
                     "scope": "artifact-wide", "via_entity_id": args.output}
                    for artifact in manifest["artifacts"] if args.output in artifact["entity_ids"]
                ]
            print(json.dumps(report, indent=2, sort_keys=True))
            return 0
    except (AirError, OSError) as exc:
        print(f"Axiom error: {exc}", file=sys.stderr)
        return 1
    print(f"Axiom {args.operation}: ok")
    return 0


if __name__ == "__main__":
    sys.exit(main())
