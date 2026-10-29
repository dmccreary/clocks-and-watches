"""The mondaine kit (src/kits/mondaine): its labs run, its face draws the
Swiss-railway dial, the stop-at-12 timing is right, and the incremental
repaint in lib/mondaine.py leaves exactly the pixels a from-scratch draw
would. This check always uses the mondaine kit, whatever $GC9B72_KIT says.
"""

import datetime
import math
import os
import random

from _setup import KIT as _first_kit, screen, W, expect, finish, runner, hardware

D = datetime.datetime
KIT = runner.use_kit(os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                  "..", "..", "..", "kits", "mondaine"))

import config                                               # noqa: E402
import mondaine                                             # noqa: E402

WHITE = config.WHITE
BLACK = config.BLACK
RED = config.RAIL_RED
CENTER = W / 2 - 0.5


def wipe():
    """Clear the simulated glass. (clear() also forgets which pin is the
    display's DC line, so put that back or the display's next command is
    read as pixel data.)"""
    dc = screen.dc_pin
    screen.clear()
    screen.dc_pin = dc


def lit():
    return sum(1 for p in screen.px if p != WHITE)


def count(color):
    return sum(1 for p in screen.px if p == color)


def reach():
    """Distance from the center of the farthest non-white pixel."""
    return max((math.hypot(i % W - CENTER, i // W - CENTER)
                for i, p in enumerate(screen.px) if p != WHITE), default=0)


print("The labs run and draw")
for lab, ms in (("01-hello-display.py", 1000), ("02-dial-dots.py", 1000),
                ("03-hour-markers.py", 1000), ("04-minute-markers.py", 1500),
                ("05-black-hands.py", 1500), ("06-red-second-hand.py", 1500),
                ("07-read-the-time.py", 1500), ("08-wifi-sync-time.py", 3000),
                ("09-tick-tock.py", 3000), ("10-smooth-sweep.py", 3000),
                ("11-stop-at-twelve.py", 3000), ("12-minute-jump.py", 3000),
                ("13-button-test.py", 1000), ("14-set-time.py", 1000),
                ("15-mondaine-clock.py", 4000)):
    runner.run_lab(lab, ms)
    expect("%s runs and draws (%d non-white pixels)" % (lab, lit()), lit() > 500)

print("The finished face (lab 06) is the Swiss railway dial")
runner.run_lab("06-red-second-hand.py", 1500)
expect("black bars and hands, red second hand both present",
       count(BLACK) > 4000 and count(RED) > 1000)
expect("nothing drawn beyond the visible glass (reach %.1f px, limit %d)"
       % (reach(), config.SAFE_RADIUS), reach() <= config.SAFE_RADIUS)
# 12 + 48 bars: count the black blobs touching the ring at radius 160
ring = set()
for i, p in enumerate(screen.px):
    if p == BLACK and abs(math.hypot(i % W - CENTER, i // W - CENTER) - 160) < 1.0:
        angle = math.degrees(math.atan2(i % W - CENTER, CENTER - i // W)) % 360
        ring.add(int(round(angle / 6)) % 60)
expect("a bar at each of the 60 minute positions (%d seen)" % len(ring), len(ring) == 60)

print("Lab 06 and lab 07 agree with lib/mondaine.py (same bars, same hands)")
runner.run_lab("06-red-second-hand.py", 1500)
lab06 = list(screen.px)
display = config.init_display()
face = mondaine.Face(display)
face.draw_dial()
face.show(10 * 30 + 10 * 0.5, 10 * 6, 25 * 6)
mine = list(screen.px)
differ = sum(1 for a, b in zip(lab06, mine) if a != b)
expect("the lab's drawing and the module's differ in %d of %d pixels"
       % (differ, W * W), differ < 120)

print("The stop-and-go timing")
h, m = 10, 9
expect("red hand starts at 12", mondaine.hand_angles(h, m, 0)[2] == 0)
expect("red hand is opposite at half a lap (29,250 ms)",
       abs(mondaine.hand_angles(h, m, 29250)[2] - 180) < 1e-3)
expect("red hand reaches 12 after 58.5 s", abs(mondaine.hand_angles(h, m, 58500)[2] - 360) < 1e-3)
expect("red hand waits at 12 from 58.5 s to 60 s",
       all(mondaine.hand_angles(h, m, ms)[2] == 360 for ms in range(58500, 60000, 100)))
expect("minute hand has not moved before the hop (58,650 ms)",
       mondaine.hand_angles(h, m, 58650)[1] == m * 6 == mondaine.hand_angles(h, m, 0)[1])
expect("minute hand has hopped one minute by 59,370 ms",
       abs(mondaine.hand_angles(h, m, 59370)[1] - (m + 1) * 6) < 1e-3)
expect("the hop happens while the red hand is stopped",
       58500 <= mondaine.ADVANCE_START_MS and
       mondaine.ADVANCE_START_MS + mondaine.ADVANCE_MS <= 60000)
hop = [mondaine.hand_angles(h, m, ms)[1] for ms in range(58650, 59371, 10)]
expect("the hop never goes backward",
       all(b >= a for a, b in zip(hop, hop[1:])))
expect("the hop eases: the first and last 100 ms move less than the middle 100 ms",
       (hop[10] - hop[0]) < (hop[41] - hop[31]) > (hop[72] - hop[62]))
expect("hour hand creeps a half degree during the hop",
       abs(mondaine.hand_angles(h, m, 59400)[0] - mondaine.hand_angles(h, m, 0)[0] - 0.5) < 1e-3)
for hour, minute in ((10, 59), (23, 59), (0, 0), (11, 59), (12, 30)):
    before = mondaine.hand_angles(hour, minute, 59999)
    nxt_h, nxt_m = ((hour + (minute + 1) // 60) % 24, (minute + 1) % 60)
    after = mondaine.hand_angles(nxt_h, nxt_m, 0)
    ok = all(abs((a - b + 180) % 360 - 180) < 0.01 for a, b in zip(before[:2], after[:2]))
    expect("no jump in the black hands across %02d:%02d to %02d:%02d" % (hour, minute, nxt_h, nxt_m), ok)

print("The clock follows the RTC and re-syncs at rest")
# Start 10:09:50; 75 s later it is 10:11:05
ns, snaps = runner.run_lab("12-minute-jump.py", 75000,
                           snap_at=[8000, 9500, 10500, 12000, 69500],
                           start=D(2026, 9, 25, 10, 9, 50))
clock = ns["clock"]
hour, minute, ms = clock.now()
expect("lab 12's clock agrees with the RTC after 75 s (%02d:%02d, %d ms into it)"
       % (hour, minute, ms), (hour, minute) == (10, 11) and 4000 < ms < 7000)

print("The red hand really stops while the minute hand moves (lab 12)")
START = D(2026, 9, 25, 10, 9, 0)
times = [57500, 58000, 58400, 58600, 58900, 59200, 59500, 59900, 60500, 61000]
ns, snaps = runner.run_lab("12-minute-jump.py", 62000, snap_at=times, start=START)


def pixels(t, color):
    return {i for i, p in enumerate(snaps[t]) if p == color}


# The simulator's clock starts mid-second, so the lab waits for the next
# second before it begins; the minute therefore rolls at about 60.0 s on
# the fake clock less the wait. Find where the second hand is stationary.
red = {t: pixels(t, RED) for t in times}
black = {t: pixels(t, BLACK) for t in times}
expect("red hand moves while gliding (57.5 s -> 58.0 s)", red[57500] != red[58000])
expect("red hand sits still in the wait (59.2 s, 59.5 s, 59.9 s)",
       red[59200] == red[59500] == red[59900])
expect("red hand sits still across the whole hop (58.9 s -> 59.5 s)",
       red[58900] == red[59500])
# (The red disc brushes the 12 o'clock bar and the red stem crosses the black
# hands at the pin, so "black" is allowed to change by a handful of pixels.)
moved = len(black[58600] ^ black[59500])
expect("minute hand moved during the wait (%d black pixels changed)" % moved, moved > 400)
rest_before = len(black[58000] ^ black[58400])
rest_after = len(black[59500] ^ black[59900])
expect("minute hand is at rest before and after the hop (%d and %d pixels changed)"
       % (rest_before, rest_after), rest_before < 120 and rest_after < 120)
expect("red hand glides again after the wait (59.9 s -> 61.0 s)", red[59900] != red[61000])

print("The incremental repaint equals a from-scratch draw")
random.seed(12)


def from_scratch(display, angles):
    saved = list(screen.px)
    wipe()
    f = mondaine.Face(display)
    f.draw_dial()
    f.show(*angles)
    return saved, list(screen.px)


def sequence(label, steps, check_every=4):
    display = config.init_display()
    f = mondaine.Face(display)
    wipe()
    f.draw_dial()
    bad = None
    for n, angles in enumerate(steps):
        f.show(*angles)
        if n % check_every == check_every - 1 or n == len(steps) - 1:
            saved, fresh = from_scratch(display, angles)
            if saved != fresh and bad is None:
                bad = (n, angles, sum(1 for a, b in zip(saved, fresh) if a != b))
            # carry on from the incremental screen, not the fresh one
            screen.px[:] = saved
    expect("%s (%d frames)%s" % (label, len(steps),
                                 "" if bad is None else "  first bad: %r" % (bad,)),
           bad is None)


# a full lap of the red hand at 10:10, ~1.5 degrees a frame
sequence("a whole lap of the red hand over the 10:10 hands",
         [(305, 60, s * 1.5) for s in range(240)])
# the red hand across 12 with the minute hand also at 12
sequence("the red hand crossing 12 while the minute hand points there",
         [(0, 0, 340 + s * 0.5) for s in range(80)])
# the minute hand hopping through every minute, hour hand creeping
steps = []
for minute in range(60):
    for k in range(0, 11):
        e = mondaine.smootherstep(k / 10.0)
        steps.append((300 + (minute + e) * 0.5, (minute + e) * 6, 360))
sequence("the minute hop, all sixty of them, red hand parked at 12", steps, 25)
# both black hands overlapping the red one and each other, random jumps
sequence("random jumps of all three hands",
         [(random.uniform(0, 360), random.uniform(0, 360), random.uniform(0, 360))
          for _ in range(80)], 2)
# the disc brushing every five-minute bar
sequence("the disc passing every five-minute bar",
         [(90, 270, 30 * k + d) for k in range(12) for d in (-6, -3, -1, 0, 1, 3, 6)], 7)

print("Lab 15: the set modes, the long press, and the nightly WiFi chore")
import contextlib                                           # noqa: E402
import io                                                   # noqa: E402
import tempfile                                             # noqa: E402

YELLOW = config.YELLOW


def run15(limit, presses=(), snap_at=(), start=D(2026, 9, 25, 10, 9, 20), edits=()):
    """Run lab 15 (optionally with edits to its source); return its
    printed output and its snapshots."""
    source = open(os.path.join(KIT, "15-mondaine-clock.py")).read()
    for old, new in edits:
        assert old in source, old
        source = source.replace(old, new)
    with tempfile.TemporaryDirectory() as folder:
        path = os.path.join(folder, "15-edited.py")
        open(path, "w").write(source)
        buffer = io.StringIO()
        with contextlib.redirect_stdout(buffer):
            _, snaps = runner.run_lab(path, limit, presses, snap_at, start)
    return buffer.getvalue(), snaps


presses = [("mode", 4000, 4080),                              # -> set hour
           ("up", 5000, 5080), ("up", 5400, 5480),            # 10 -> 12
           ("mode", 6000, 6080),                              # -> set minute
           ("up", 7000, 7080), ("up", 7400, 7480), ("up", 7800, 7880),   # 09 -> 12
           ("mode", 9000, 9080)]                              # -> run
text, snaps = run15(12000, presses, snap_at=[3500, 5700, 8500, 11500])
now = runner.localtime()
expect("MODE, UP x2, MODE, UP x3, MODE set the RTC to 12:12 (%02d:%02d:%02d)"
       % now[3:6], (now[3], now[4]) == (12, 12) and now[5] < 8)
expect("running: no label on the face", YELLOW not in snaps[3500])
expect("set hour: the yellow SET HOUR label is showing (%d yellow pixels)"
       % snaps[5700].count(YELLOW), snaps[5700].count(YELLOW) > 100)
expect("set minute: the yellow SET MINUTE label is showing (%d yellow pixels)"
       % snaps[8500].count(YELLOW), snaps[8500].count(YELLOW) > 100)
expect("back to running: the label is gone and the red hand is drawn",
       YELLOW not in snaps[11500] and snaps[11500].count(RED) > 1000)
expect("the hands moved with the buttons (set hour face differs from running face)",
       snaps[5700] != snaps[3500])

text, snaps = run15(7000, [("mode", 3000, 4300)], snap_at=[6500])
expect("holding MODE sets the clock from the internet (%d WiFi joins)"
       % text.count("Joining"), text.count("Joining") == 2)
expect("...and the face comes back afterward",
       snaps[6500].count(RED) > 1000 and snaps[6500].count(BLACK) > 4000)

# At 3:00:59.4 AM on a NEW day the clock asks the internet again. Pretend
# today's sync never happened, so the first rest after 3 AM counts.
text, snaps = run15(40000, start=D(2026, 9, 25, 3, 0, 40),
                    edits=[("synced_day = time.localtime()[2]", "synced_day = -1")],
                    snap_at=[39500])
expect("at rest after 3 AM it asks the internet once more (%d WiFi joins)"
       % text.count("Joining"), text.count("Joining") == 2)
expect("...and before 3 AM it does not",
       run15(40000, start=D(2026, 9, 25, 2, 0, 40),
             edits=[("synced_day = time.localtime()[2]", "synced_day = -1")])[0]
       .count("Joining") == 1)
expect("...and the clock still runs afterward (red hand drawn)", snaps[39500].count(RED) > 1000)

print("How many drawing commands a frame costs")
display = config.init_display()
wipe()
cost = {"commands": 0, "pixels": 0}
real_hline = display.hline
real_blit = display.blit_buffer


def counting_hline(x, y, length, color):
    cost["commands"] += 1
    cost["pixels"] += length
    real_hline(x, y, length, color)


def counting_blit(buffer, x, y, width, height):
    cost["commands"] += 1
    cost["pixels"] += width * height
    real_blit(buffer, x, y, width, height)


face = mondaine.Face(display)
face.draw_dial()
display.hline = counting_hline
display.blit_buffer = counting_blit
face.show(305, 60, 0)
first_draw = dict(cost)


def worst(frames):
    commands = pixels = 0
    for angles in frames:
        cost["commands"] = cost["pixels"] = 0
        face.show(*angles)
        commands = max(commands, cost["commands"])
        pixels = max(pixels, cost["pixels"])
    return commands, pixels


# the red hand steps 0.3 degree a frame (20 frames a second) all the way round
sweep = worst((305, 60, d * 0.3) for d in range(1, 1200))
# one degree at a time, at every angle
sweep_1 = worst((305, 60, d) for d in range(1, 360))
face.show(0, 0, 0)
hop = worst((e * 0.5, e * 6, 0) for e in [mondaine.smootherstep(k / 14.0) for k in range(1, 15)])
print("  first draw of the hands: %d commands, %d pixels" % (first_draw["commands"], first_draw["pixels"]))
print("  worst sweep frame at 0.3 degree: %d commands, %d pixels sent" % sweep)
print("  worst sweep frame at 1 degree:   %d commands, %d pixels sent" % sweep_1)
print("  worst frame of a 14-step hop:    %d commands, %d pixels sent" % hop)
expect("a sweep frame costs at most 20 drawing commands", sweep_1[0] <= 20 and sweep[0] <= 20)
expect("a hop frame costs at most 40 drawing commands", hop[0] <= 40)
expect("a sweep frame sends under 6,000 pixels", sweep_1[1] < 6000)
expect("a hop frame sends under 20,000 pixels", hop[1] < 20000)
finish()
