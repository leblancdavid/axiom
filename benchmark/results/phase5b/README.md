# Phase 5B artifacts

This directory contains only Phase 5B protocol and validation evidence. The
Phase 5A pilot and frozen requirements remain untouched. Start at `FROZEN.md`.

`baseline-manifest.json` pins every file in the original pilot archive, the
track-specific projections, and all twenty requirements. Six checkpoint JSONs
and matching `snapshot-*.tar` archives record restorable achieved states.
`validation.json` records command stdout/stderr, preflight results, negative
probes, and regression/internal-suite results. Temporary validation working
directories are deliberately discarded after their byte-for-byte snapshots
have been verified.
