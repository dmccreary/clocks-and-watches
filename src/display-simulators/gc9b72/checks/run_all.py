#!/usr/bin/env python3
"""Run every check_*.py in this folder, each in its own process (the
simulator's fakes are process-wide), and print a one-line summary each.

    python3 src/display-simulators/gc9b72/checks/run_all.py
    GC9B72_KIT=/path/to/kit python3 .../run_all.py      # another kit

Exits 0 only if every check passed. Takes a few minutes: the checks run
labs through the real driver, pixel by pixel.
"""

import glob
import os
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
env = dict(os.environ, PYTHONDONTWRITEBYTECODE="1")
failed = []
for path in sorted(glob.glob(os.path.join(HERE, "check_*.py"))):
    name = os.path.basename(path)
    start = time.time()
    result = subprocess.run([sys.executable, path], capture_output=True, text=True,
                            cwd=HERE, env=env)
    ok = result.returncode == 0
    print("%-26s %s  (%.0f s)" % (name, "ok" if ok else "FAILED", time.time() - start))
    if not ok:
        failed.append(name)
        lines = [line for line in result.stdout.splitlines() if "WRONG" in line]
        for line in lines or (result.stdout + result.stderr).splitlines()[-15:]:
            print("    " + line)
print("ALL CHECKS PASSED" if not failed else "%d FAILED: %s" % (len(failed), ", ".join(failed)))
sys.exit(1 if failed else 0)
