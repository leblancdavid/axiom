import argparse
import sys

from .generator import write
from .parser import AirError, load
from .validator import validate


def main(argv=None):
    parser = argparse.ArgumentParser(prog="air-compiler")
    parser.add_argument("operation", choices=("validate", "generate"))
    parser.add_argument("air_file")
    parser.add_argument("output", nargs="?")
    args = parser.parse_args(argv)
    if args.operation == "generate" and not args.output:
        parser.error("generate requires output path")
    try:
        program = validate(load(args.air_file))
        if args.operation == "generate":
            write(program, args.output)
    except (AirError, OSError) as exc:
        print(f"AIR error: {exc}", file=sys.stderr)
        return 1
    print(f"AIR {args.operation}: ok")
    return 0


if __name__ == "__main__":
    sys.exit(main())
