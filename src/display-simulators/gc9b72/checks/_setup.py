"""Shared start-up for the checks: load the simulator and point it at a
kit (this repo's sw-gc9b72, or the folder in $GC9B72_KIT)."""

import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))

from gc9b72_sim import runner, hardware, render     # noqa: E402,F401
from gc9b72_sim.hardware import screen, W            # noqa: E402,F401

KIT = runner.use_kit(os.environ.get(
    "GC9B72_KIT", os.path.join(HERE, "..", "..", "..", "kits", "sw-gc9b72")))

results = []


def expect(label, ok):
    results.append(bool(ok))
    print("  %-66s %s" % (label, "ok" if ok else "WRONG"))


def finish():
    """Print the verdict and exit with 0 (all good) or 1."""
    ok = all(results)
    print("ALL CLEAN" if ok else "FAILURES")
    sys.exit(0 if ok else 1)


def lab_definitions(lab, stop_at="display = config.init_display()", replace=()):
    """Run the top of a lab -- its constants and functions -- without
    starting its display or its loop. Returns the lab's globals.
    replace: (old, new) pairs to change in the source first."""
    path = os.path.join(KIT, lab)
    source = open(path).read()
    for old, new in replace:
        assert old in source, old
        source = source.replace(old, new)
    ns = {"__name__": "lab"}
    exec(compile(source[:source.index(stop_at)], path, "exec"), ns)
    return ns
