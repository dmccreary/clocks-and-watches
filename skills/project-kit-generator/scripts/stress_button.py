"""Usage: KIT_DIR=<kit> python3 stress_button.py <path/to/button.py> <label> [debounce_ms=50]

Stress-test a Button implementation with chattering contacts, late soft-IRQ handlers,
long redraws (the main loop is blind for 0.3-0.9 s), long holds and quick double taps."""
import sys, os, random, importlib.util, statistics
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import simlib
simlib.install()
from simlib import CLOCK, Pin, press, reset_clock


def load(path):
    spec = importlib.util.spec_from_file_location("button_under_test", path)
    m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
    return m


DEBOUNCE = int(sys.argv[3]) if len(sys.argv) > 3 else 50


def trial(mod, holds, gap=(300, 700), busy_prob=0.0, seed=1, n=None, label="", noise=0):
    reset_clock(); Pin.instances.clear()
    rng = random.Random(seed); Pin.rng = random.Random(seed + 1)
    btn = mod.Button(15, DEBOUNCE)
    truth, t = [], 1000.0
    for i in range(n):
        hold = rng.choice(holds)
        truth.append((t, hold)); press(t, hold, seed=seed * 1000 + i)
        t += hold + rng.uniform(*gap)
    end = t + 800
    for k in range(noise):
        g = rng.uniform(1000, end - 200)
        if all(not (a - 5 <= g <= a + h + 5) for a, h in truth):
            simlib.CLOCK.at(g, lambda: Pin.instances[15].edge(0))
            simlib.CLOCK.at(g + 0.3, lambda: Pin.instances[15].edge(1))
    events = []
    while CLOCK.now < end:
        CLOCK.advance(rng.uniform(300, 900) if rng.random() < busy_prob else 10)
        while True:
            d = btn.next_press()
            if d == 0:
                break
            events.append((CLOCK.now, d))
    got = len(events)
    truth_long = sum(1 for _, h in truth if h >= 800)
    bogus_long = max(0, sum(1 for _, d in events if d >= 800) - truth_long)
    missed = max(0, n - got); extra = max(0, got - n)
    errs = [abs(d - h) for (_, d), (_, h) in zip(events, truth)] if got == n else []
    wrongkind = sum(1 for (_, d), (_, h) in zip(events, truth) if (d < 800) != (h < 800)) if got == n else None
    dropped = Pin.instances[15].dropped
    print("  %-46s presses=%3d detected=%3d missed=%3d extra=%3d bogus-long=%d %s%s" % (
        label, n, got, missed, extra, bogus_long,
        ("max length error %4.0f ms" % max(errs)) if errs else "(lengths not compared)",
        ("  | tap/hold misclassified: %d" % wrongkind) if wrongkind else ""))
    return missed + bogus_long * 1000, extra, wrongkind


def suite(mod, name):
    print("\n=== %s" % name)
    r = []
    r.append(trial(mod, (70, 100, 150, 200, 300), n=300, seed=1, label="taps 70-300 ms, chattering contacts, idle loop"))
    r.append(trial(mod, (70, 100, 150, 200, 300), n=300, seed=2, busy_prob=0.5, label="taps while the screen is redrawing (50%)"))
    r.append(trial(mod, (900, 1100, 3200), gap=(500, 900), n=60, seed=3, label="long holds (0.9 s, 1.1 s, 3.2 s)"))
    r.append(trial(mod, (70, 90), gap=(80, 200), n=200, seed=4, label="quick double taps (70-90 ms taps, 80-200 ms gaps)"))
    r.append(trial(mod, (70, 100, 150), n=200, seed=5, busy_prob=0.9, label="taps, screen almost always redrawing (90%)"))
    r.append(trial(mod, (100, 150), n=200, seed=6, noise=60, label="taps plus 60 stray 0.3 ms electrical glitches"))
    r.append(trial(mod, (100,), gap=(600, 900), n=1, seed=7, noise=150, label="ONLY glitches (150), 1 real tap"))
    tiny = trial(mod, (20, 35), n=100, seed=8, label="(info) taps SHORTER than 50 ms are treated as bounce")
    print("  (that last line is expected to miss: a 50 ms debounce ignores anything shorter)")
    bad = sum(m + e + (w or 0) for m, e, w in r)
    print("  -> total problems: %d" % bad)
    return bad


if __name__ == "__main__":
    if len(sys.argv) < 3:
        raise SystemExit("usage: KIT_DIR=<kit> python3 stress_button.py <button.py> <label> [debounce_ms]")
    suite(load(sys.argv[1]), sys.argv[2])
