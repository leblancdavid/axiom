import argparse
import json
import sys

from .generator import write
from .parser import AirError, load
from .semantics import inspect, diff
from .validator import validate


def main(argv=None):
    parser = argparse.ArgumentParser(prog="axiom")
    parser.add_argument("operation", choices=("validate", "generate", "inspect", "diff"))
    parser.add_argument("air_file")
    parser.add_argument("output", nargs="?")
    args = parser.parse_args(argv)
    if args.operation == "generate" and not args.output:
        parser.error("generate requires output path")
    if args.operation in ("inspect", "diff") and not args.output:
        parser.error(f"{args.operation} requires an entity ID or second model")
    try:
        program = validate(load(args.air_file))
        if args.operation == "generate":
            write(program, args.output)
        elif args.operation == "inspect":
            print(json.dumps(inspect(program, args.output), indent=2, sort_keys=True))
            return 0
        elif args.operation == "diff":
            print(json.dumps(diff(program, validate(load(args.output))), indent=2, sort_keys=True))
            return 0
    except (AirError, OSError) as exc:
        print(f"Axiom error: {exc}", file=sys.stderr)
        return 1
    print(f"Axiom {args.operation}: ok")
    return 0


if __name__ == "__main__":
    sys.exit(main())
