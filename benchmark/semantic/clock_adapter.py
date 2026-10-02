"""Subprocess bootstrap for disposable, controlled UTC-clock scenarios.

Run as ``python clock_adapter.py UTC_INSTANT app.py [args...]``. The application
is loaded only after the process-wide datetime clock has been bound. This is
an execution adapter, not a change to either benchmark application.
"""

import datetime
import runpy
import sys


def main():
    # Import here so the bootstrap can run without adding the repository to
    # the application's import path. Reject non-UTC/malformed bindings.
    from datetime import timezone

    value = sys.argv[1]
    if not value.endswith("Z"):
        raise ValueError("controlled clock requires UTC Z instant")
    fixed = datetime.datetime.fromisoformat(value[:-1] + "+00:00")
    if fixed.tzinfo != timezone.utc:
        raise ValueError("controlled clock requires UTC instant")
    original = datetime.datetime

    class ControlledDateTime(original):
        @classmethod
        def now(cls, tz=None):
            if tz is None:
                raise ValueError("controlled clock requires explicit timezone")
            return fixed.astimezone(tz)

        @classmethod
        def utcnow(cls):
            raise ValueError("controlled clock requires timezone-aware UTC now")

    datetime.datetime = ControlledDateTime
    sys.argv = sys.argv[2:]
    runpy.run_path(sys.argv[0], run_name="__main__")


if __name__ == "__main__":
    main()
