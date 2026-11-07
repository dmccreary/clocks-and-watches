"""End-to-end tests: run the REAL 08 and 09 labs on the fake hardware."""
import sys, os, io, math, re, runpy, tempfile, contextlib, traceback
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import simlib
simlib.install()
from simlib import CLOCK, World, Pin, Display, press, snapshot, reset_clock, SimDone, outside_pixels, text_box_problems
import config

OUT = os.path.join(os.path.abspath(os.environ.get("OUT_DIR", os.getcwd())), "app")   # pictures go to OUT_DIR or the current folder, never next to this script
os.makedirs(OUT, exist_ok=True)
WORK = tempfile.mkdtemp()
os.chdir(WORK)

results = []      # (ok, description)


def expect(ok, text):
    results.append((bool(ok), text))
    print(("  PASS  " if ok else "  FAIL  ") + text)


class Console:
    def __init__(self):
        self.lines = []; self.partial = ""
    def write(self, s):
        self.partial += s
        while "\n" in self.partial:
            line, self.partial = self.partial.split("\n", 1)
            self.lines.append((CLOCK.now, line))
    def flush(self): pass


def fresh_world(profile=None):
    reset_clock()
    World.profile = staticmethod(profile or (lambda t: (22.5, 48.2)))
    World.fail_windows = []
    World.reset_fails_until = 0
    World.reads = []
    Pin.instances.clear()
    import random
    Pin.rng = random.Random(11)      # soft-IRQ handlers run a little late, like the real thing


def run_lab(name, end_ms):
    CLOCK.end = end_ms
    con = Console()
    err = None
    with contextlib.redirect_stdout(con):
        try:
            runpy.run_path(simlib.KIT + "/" + name, run_name="__main__")
        except SimDone:
            pass
        except Exception:
            err = traceback.format_exc()
    return con, err


def snap_at(t, name, checks=True):
    def fn():
        d = Display.last
        snapshot(d, os.path.join(OUT, name + ".png"))
        if checks:
            bad = text_box_problems(d); out = outside_pixels(d)
            if bad or out:
                results.append((False, "%s: text outside circle %r / %d stray pixels" % (name, bad, out)))
    CLOCK.at(t, fn)


def led_beats():
    led = Pin.instances.get("LED")
    if not led:
        return []
    return [t for (t, v) in led.writes if v == 1]


def mode_sequence(con):
    seq = []
    for t, line in con.lines:
        m = re.match(r"^([A-Za-z/]+): [-\d.]+ F", line)
        if m and (not seq or seq[-1][1] != m.group(1)):
            seq.append((t, m.group(1)))
    return seq


# ======================================================================= A: navigation
print("\nA. Navigation, units, bounce, LED")
fresh_world(lambda t: (22.5 + 0.3 * math.sin(t / 4000.0), 48.0 + 2 * math.sin(t / 3000.0)))
for i, t in enumerate((3500, 6500, 9500, 12500, 15500, 18500)):
    press(t, 80)
for t, nm in ((3400, "A1_watch"), (6300, "A2_buddy"), (9300, "A3_live"), (12300, "A4_ring"), (15300, "A5_finger"),
              (18300, "A6_hilo"), (21300, "A7_watch_again")):
    snap_at(t, nm)
press(22000, 1000)                       # hold 1 s: F -> C
snap_at(24000, "A8_watch_in_C")
press(25000, 90, bounce=True)            # a bouncy tap: must count once
snap_at(27500, "A9_buddy_in_C")
press(28000, 80); press(28150, 80)       # two quick taps
snap_at(31000, "A10_after_double_tap")
con, err = run_lab("09-display-modes-capstone.py", 32000)
expect(err is None, "lab 09 ran 32 s of scripted use with no exception" + ("" if err is None else "\n" + err))
seq = [n for _, n in mode_sequence(con)]
expect(seq == ["Classic", "Buddy", "Live", "Ring", "Finger", "Hi/Lo", "Classic", "Buddy", "Live", "Ring"],
       "modes in order: 6 taps with wrap-around, then one bouncy tap (+1 mode), then a double tap (+2 modes): %s" % seq)
expect(any("Got Ctrl-C" in l for _, l in con.lines), "the Ctrl-C shutdown path ran")
beats = led_beats()
reads = World.reads
expect(len(reads) > 40 and abs(len(beats) - len(reads)) <= 2,
       "LED beat once per successful read (%d reads, %d beats)" % (len(reads), len(beats)))
gaps_normal = [b - a for a, b in zip(reads, reads[1:]) if 300 < a and b < 3450]
expect(gaps_normal and all(950 <= g <= 1100 for g in gaps_normal), "reads are 1 s apart in the Classic mode: %s" % [int(g) for g in gaps_normal])
finger_reads = [r for r in reads if 12700 <= r <= 15400]
fg = [b - a for a, b in zip(finger_reads, finger_reads[1:])]
expect(fg and all(290 <= g <= 420 for g in fg), "reads are ~0.3 s apart in Finger mode (LED blinks faster): %s" % [int(g) for g in fg[:6]])
expect(any("F  " in l and "C" in l for _, l in con.lines), "console prints readings")
print("  mode changes at (ms):", [(int(t), n) for t, n in mode_sequence(con)])

# ======================================================================= B: finger, records, persistence
print("\nB. Finger test, Hi/Lo records, clearing, saving, reloading")
if os.path.exists(config.RECORDS_FILE):
    os.remove(config.RECORDS_FILE)


def finger_profile(t):
    if t < 10000: c = 22.0
    elif t < 20000: c = 22.0 + 12.0 * (1 - math.exp(-(t - 10000) / 3500.0))     # finger warms the sensor
    elif t < 24000: c = 34.0
    else: c = 22.0 + 12.0 * math.exp(-(t - 24000) / 6000.0)                     # finger removed
    return c, 45.0 + (10 if 10000 < t < 20000 else 0)


fresh_world(finger_profile)
for t in (2000, 3500, 5000, 6500):
    press(t, 80)                          # Buddy, Live, Ring, Finger
for t, nm in ((9000, "B1_finger_ready"), (13000, "B2_finger_warming"), (17000, "B3_finger_almost"),
              (21000, "B4_finger_done"), (21400, "B4b_finger_done_flash"), (27000, "B5_finger_cooling")):
    snap_at(t, nm)
press(28000, 80)                          # -> Hi/Lo
snap_at(30000, "B6_hilo_records")
press(31000, 3200)                        # hold 3.2 s in Hi/Lo: clear
snap_at(35000, "B7_hilo_cleared")
snap_at(40000, "B8_hilo_after_clear")
con, err = run_lab("09-display-modes-capstone.py", 66000)
expect(err is None, "lab 09 ran 66 s with no exception" + ("" if err is None else "\n" + err))
saved = open(config.RECORDS_FILE).read().split() if os.path.exists(config.RECORDS_FILE) else None
expect(saved is not None and len(saved) == 4, "records file written: %s" % saved)
if saved:
    hi_f, lo_f, hi_h, lo_h = [float(x) for x in saved]
    expect(hi_f < 80.0, "records were cleared at 34 s, so the 93 F peak (t=20 s) is gone (hi now %.1f F)" % hi_f)
    expect(65 < lo_f <= hi_f < 80, "records restarted from live readings: hi %.1f lo %.1f F" % (hi_f, lo_f))

print("  ...second boot: records must load from the file")
saved_before = open(config.RECORDS_FILE).read()
fresh_world(lambda t: (22.5, 48.0))
for t in (2000, 3500, 5000, 6500, 8000):
    press(t, 80)                          # Buddy, Live, Ring, Finger, Hi/Lo
snap_at(10500, "B9_second_boot_hilo")
con, err = run_lab("09-display-modes-capstone.py", 11000)
expect(err is None, "second boot ran with no exception")
from records import Records
expect(open(config.RECORDS_FILE).read().split()[0] != "", "records file still readable after second boot")
print("  (file before second boot: %r)" % saved_before.strip())

# ======================================================================= C: sensor failures
print("\nC. Sensor failure and recovery")
fresh_world()
World.fail_windows = [(5000, 9000), (14000, 17000)]
press(2000, 80); press(3000, 80)          # Buddy, Live
press(3800, 80)                           # Ring
press(11500, 80)                          # Finger
press(12200, 80)                          # Hi/Lo
press(12900, 80)                          # Watch
press(13400, 80)                          # Buddy
snap_at(7500, "C1_ring_sensor_fail")
snap_at(11000, "C2_ring_recovered")
snap_at(16000, "C3_buddy_sensor_fail")
snap_at(19500, "C4_buddy_recovered")
con, err = run_lab("09-display-modes-capstone.py", 20000)
expect(err is None, "lab 09 survived two sensor outages with no exception" + ("" if err is None else "\n" + err))
fails = [l for _, l in con.lines if l.startswith("Sensor problem")]
expect(len(fails) == 2, "\"Sensor problem\" printed once per outage (2 outages): %d" % len(fails))
led = Pin.instances["LED"]
in_outage = [(t, v) for (t, v) in led.writes if 5000 <= t < 9000 and v == 1]
expect(len(in_outage) >= 6, "LED double-blinks during an outage (%d rising edges in 4 s, normal is 4)" % len(in_outage))
expect(len(World.reads) > 5, "readings resumed after each outage (%d good reads)" % len(World.reads))

print("\nC2. Sensor dead at boot, then wakes up")
fresh_world()
World.fail_windows = [(0, 3000)]
World.reset_fails_until = 3000
snap_at(2000, "C5_boot_sensor_dead")
snap_at(5000, "C6_boot_sensor_alive")
con, err = run_lab("09-display-modes-capstone.py", 6000)
expect(err is None, "lab 09 did not quit when the sensor was dead at boot" + ("" if err is None else "\n" + err))
expect(any("not answering" in l for _, l in con.lines), "boot warning printed")
expect(len(World.reads) >= 2, "watch came alive by itself once the sensor answered (%d reads)" % len(World.reads))

# ======================================================================= D: button test lab
print("\nD. Lab 08: button and LED test")
fresh_world()
press(1500, 120); press(3000, 1100); press(4600, 3300)
con, err = run_lab("08-button-and-led-test.py", 9000)
text = "\n".join(l for _, l in con.lines)
expect(err is None and "TEST PASS" in text, "lab 08 prints TEST PASS after 3 presses" + ("" if err is None else "\n" + err))
expect("tap" in text and "hold (switch F and C)" in text and "long hold" in text, "lab 08 names a tap, a hold and a long hold")
beats = led_beats()
expect(len(beats) >= 3, "lab 08 heartbeat LED blinked %d times" % len(beats))
print("  console:"); [print("    " + l) for _, l in con.lines]

fresh_world()
con, err = run_lab("08-button-and-led-test.py", 4000)
text = "\n".join(l for _, l in con.lines)
expect("TEST FAIL" in text, "lab 08 prints TEST FAIL when no press ever comes (Ctrl-C after 4 s)")

# ======================================================================= summary
bad = [t for ok, t in results if not ok]
print("\n%d checks, %d failed" % (len(results), len(bad)))
for b in bad:
    print(" FAILED:", b)
