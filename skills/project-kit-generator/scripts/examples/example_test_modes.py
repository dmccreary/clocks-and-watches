import sys, os, math, traceback, tempfile
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import simlib
simlib.install()
from simlib import CLOCK, Display, snapshot, outside_pixels, text_box_problems
from PIL import Image, ImageDraw
import config
from display_ctx import Context
from records import Records

OUT = os.path.join(os.path.abspath(os.environ.get("OUT_DIR", os.getcwd())), "modes")   # pictures go to OUT_DIR or the current folder, never next to this script
os.makedirs(OUT, exist_ok=True)
tmp = tempfile.mkdtemp()
os.chdir(tmp)

from mode_classic import ClassicMode
from mode_buddy import BuddyMode
from mode_live import LiveMode
from mode_ring import RingMode
from mode_finger import FingerMode
from mode_hilo import HiLoMode

problems = []
budgets = []


def make_ctx(index, use_f=True):
    if os.path.exists(config.RECORDS_FILE):
        os.remove(config.RECORDS_FILE)
    ctx = Context(Display(), Records(config.RECORDS_FILE, 60), 6)
    ctx.mode_index = index
    ctx.use_fahrenheit = use_f
    return ctx


def feed(ctx, temp_f, hum):
    ctx.add_reading((temp_f - 32.0) * 5.0 / 9.0, hum)
    ctx.records.update(ctx.temp_f, ctx.humidity)


def measure(label, fn):
    d = Display.last
    c0, t0 = d.calls, CLOCK.now
    fn()
    return d.calls - c0, CLOCK.now - t0


def check(name, ctx):
    d = ctx.display
    bad = text_box_problems(d)
    out = outside_pixels(d)
    if bad:
        problems.append("%s: text outside safe circle: %r" % (name, bad))
    if out:
        problems.append("%s: %d pixels drawn outside the glass" % (name, out))


def sheet(name, shots):
    """Put several snapshots side by side with a caption under each."""
    imgs = [Image.open(p) for p, _ in shots]
    w, h = imgs[0].size
    cols = min(3, len(imgs)); rows = (len(imgs) + cols - 1) // cols
    sh = Image.new("RGB", (cols * w, rows * (h + 22)), (30, 30, 34))
    dr = ImageDraw.Draw(sh)
    for i, (im, (_, cap)) in enumerate(zip(imgs, shots)):
        x, y = (i % cols) * w, (i // cols) * (h + 22)
        sh.paste(im, (x, y)); dr.text((x + 8, y + h + 4), cap, fill=(230, 230, 230))
    sh.save(os.path.join(OUT, "sheet_%s.png" % name))


def run_scenarios(mode_cls, index, name, scenarios, use_f=True):
    shots = []
    for label, temp, hum in scenarios:
        try:
            ctx = make_ctx(index, use_f)
            mode = mode_cls()
            ctx.display.calls = 0
            e_calls, e_ms = measure("enter", lambda: mode.enter(ctx))
            feed(ctx, temp, hum)
            u1_calls, u1_ms = measure("update1", lambda: mode.update(ctx))
            feed(ctx, temp + 0.1, hum + 0.2)
            u2_calls, u2_ms = measure("update2", lambda: mode.update(ctx))
            budgets.append((name, label, e_calls, e_ms, u1_calls, u1_ms, u2_calls, u2_ms))
            check("%s/%s" % (name, label), ctx)
            path = os.path.join(OUT, "%s_%s.png" % (name, label.replace(" ", "_").replace("/", "-")))
            snapshot(ctx.display, path)
            shots.append((path, "%s %s" % (name, label)))
        except Exception:
            problems.append("%s/%s CRASHED:\n%s" % (name, label, traceback.format_exc()))
    if shots:
        sheet(name, shots)


# ------------------------------------------------------------------ Watch, Buddy, Ring
run_scenarios(ClassicMode, 0, "watch", [("comfy 72F", 72.5, 48.2), ("cold 45F", 45.0, 8.0), ("hot 95F", 95.0, 88.0)])
run_scenarios(ClassicMode, 0, "watchC", [("comfy in C", 72.5, 48.2)], use_f=False)
run_scenarios(BuddyMode, 1, "buddy", [
    ("freezing 45F", 45.0, 40.0), ("cool 60F", 60.0, 40.0), ("comfy 72F", 72.5, 48.0),
    ("comfy but dry 20pct", 72.5, 20.0), ("warm 84F", 84.0, 50.0), ("hot 95F sticky", 95.0, 85.0)])
run_scenarios(RingMode, 3, "ring", [("comfy 72F", 72.5, 48.2), ("cold 52F dry", 52.0, 15.0), ("hot 95F damp", 95.0, 90.0),
                                    ("off the scale 40F 0pct", 40.0, 0.0), ("off the scale 105F 100pct", 105.0, 100.0)])
run_scenarios(RingMode, 3, "ringC", [("in Celsius", 72.5, 48.2)], use_f=False)

# ------------------------------------------------------------------ Live
try:
    shots = []
    ctx = make_ctx(2); mode = LiveMode()
    mode.enter(ctx)
    costs = []
    for i in range(240):                                   # 240 readings: the graph wraps at 180
        t = 72.0 + 2.5 * math.sin(i / 14.0) + (0.02 * i)
        if 130 <= i < 140:
            t += 9.0                                       # a spike (a warm finger)
        feed(ctx, t, 45.0)
        c, ms = measure("u", lambda: mode.update(ctx))
        costs.append(c)
        if i in (40, 130, 175, 200, 239):
            p = os.path.join(OUT, "live_%03d.png" % i); snapshot(ctx.display, p)
            shots.append((p, "live after %d readings" % (i + 1)))
    check("live", ctx)
    steady = sorted(costs)[len(costs) // 2]
    budgets.append(("live", "240 readings", 0, 0, max(costs), 0, steady, 0))
    sheet("live", shots)
    # unit change re-enters the mode: history must be replotted at once
    ctx.use_fahrenheit = False
    e_calls, e_ms = measure("enter", lambda: mode.enter(ctx))
    u_calls, u_ms = measure("update", lambda: mode.update(ctx))
    p = os.path.join(OUT, "live_C.png"); snapshot(ctx.display, p)
    budgets.append(("live", "re-enter in C", e_calls, e_ms, u_calls, u_ms, 0, 0))
except Exception:
    problems.append("live CRASHED:\n" + traceback.format_exc())

# ------------------------------------------------------------------ Finger
try:
    shots = []
    ctx = make_ctx(4); mode = FingerMode()
    mode.enter(ctx)
    states = []
    # a few readings of a 72 F room, then a finger warms the sensor to 93 F, then it cools
    seq = [72.0, 72.1, 71.9, 72.0, 72.1] + [72 + 21 * (1 - math.exp(-k / 6.0)) for k in range(1, 26)] + [93 - 1.2 * k for k in range(1, 16)]
    snaps = {3: "measuring", 8: "ready", 16: "warming", 22: "almost", 30: "done", 44: "cooling"}
    for i, t in enumerate(seq):
        feed(ctx, t, 45.0)
        mode.update(ctx)
        CLOCK.advance(config.FINGER_READ_MS)
        mode.tick(ctx, CLOCK.ms())
        if i in snaps:
            p = os.path.join(OUT, "finger_%02d.png" % i); snapshot(ctx.display, p)
            shots.append((p, "finger: %s (%.1f F, level %.2f)" % (snaps[i], t, mode.level)))
            states.append((snaps[i], mode.state))
    check("finger", ctx)
    sheet("finger", shots)
    print("finger states reached:", states)
    # flashing message while DONE
    for _ in range(4):
        CLOCK.advance(400); mode.tick(ctx, CLOCK.ms())
except Exception:
    problems.append("finger CRASHED:\n" + traceback.format_exc())

# ------------------------------------------------------------------ Hi/Lo
try:
    shots = []
    for label, use_f, fill in (("empty records", True, False), ("records in F", True, True), ("records in C", False, True)):
        ctx = make_ctx(5, use_f); mode = HiLoMode()
        mode.enter(ctx)
        if fill:
            for t, h in ((70.0, 40.0), (92.3, 80.0), (61.2, 22.0), (75.0, 50.0)):
                feed(ctx, t, h)
        else:
            ctx.add_reading(22.0, 40.0)          # a reading exists but the records were cleared
        e = measure("u", lambda: mode.update(ctx))
        budgets.append(("hilo", label, 0, 0, e[0], e[1], 0, 0))
        check("hilo/" + label, ctx)
        p = os.path.join(OUT, "hilo_%s.png" % label.replace(" ", "_")); snapshot(ctx.display, p)
        shots.append((p, "hilo: " + label))
    # the cleared message
    mode.cleared(ctx, CLOCK.ms())
    p = os.path.join(OUT, "hilo_cleared.png"); snapshot(ctx.display, p); shots.append((p, "hilo: just cleared"))
    CLOCK.advance(2500); mode.tick(ctx, CLOCK.ms())
    sheet("hilo", shots)
except Exception:
    problems.append("hilo CRASHED:\n" + traceback.format_exc())

# ------------------------------------------------------------------ Buddy blink
try:
    ctx = make_ctx(1); mode = BuddyMode(); mode.enter(ctx); feed(ctx, 72.5, 48.0); mode.update(ctx)
    CLOCK.advance(config.BUDDY_BLINK_MS + 10); c1 = measure("blink", lambda: mode.tick(ctx, CLOCK.ms()))
    p = os.path.join(OUT, "buddy_blink_closed.png"); snapshot(ctx.display, p)
    closed = mode.eyes_open
    CLOCK.advance(200); c2 = measure("open", lambda: mode.tick(ctx, CLOCK.ms()))
    p2 = os.path.join(OUT, "buddy_blink_open.png"); snapshot(ctx.display, p2)
    print("buddy blink: closed step %d calls, eyes_open=%s -> reopened %d calls, eyes_open=%s" % (c1[0], closed, c2[0], mode.eyes_open))
    check("buddy blink", ctx)
except Exception:
    problems.append("blink CRASHED:\n" + traceback.format_exc())

# ------------------------------------------------------------------ report
print("\nDRAW-CALL BUDGETS (simulated ms assume %.1f ms per call - a guess, not a measurement)" % simlib.COST_MS)
print("%-8s %-28s %8s %7s | %8s %7s | %8s %7s" % ("mode", "scenario", "enter", "ms", "update#1", "ms", "update#2", "ms"))
for b in budgets:
    print("%-8s %-28s %8d %7.0f | %8d %7.0f | %8d %7.0f" % b)
print("\nPROBLEMS: %d" % len(problems))
for p in problems:
    print(" -", p)
