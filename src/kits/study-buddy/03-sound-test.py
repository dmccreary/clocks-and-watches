# Lab 03: Speaker Test
# Puts sound.py through its paces, shows what it can do, and then runs the
# experiment that explains how it is built: why the sound comes from the
# Pico's SECOND processor core.
#
#   1. A tone         one steady note
#   2. A scale        eight notes, each named on the screen as it plays
#   3. Named sounds   the Study Buddy's own beeps (right, wrong, chime ...)
#   4. Two cores      the same tone, with the Pico frozen for over a second
#                     in the middle -- first with core 0 in charge of the
#                     sound, then core 1. LISTEN for the gap.
#   5. Drawing        a tone while the screen is repainted again and again
#
# The Pico 2 W has two cores that run at the same time. Core 0 runs your
# program. Core 1 usually has nothing to do, so sound.py gives it a job:
# calculate the sound and feed the amplifier, over and over. Then core 0 can
# be as busy, or as stuck, as it likes. (One exception: writing a file.
# Flash writes turn off interrupts, which the sound hardware needs, so they
# can still cause a click. See docs/kits/study-buddy/06-multicore-guide.md.)
# Part 4 proves it:
#
#   core 0 in charge:  the freeze stops the sound too -> a gap you can hear
#   core 1 in charge:  the freeze never reaches the sound -> no gap
#
# The numbers on the screen come from sound.stats(). "Dropouts" is how many
# times the amplifier ran out of sound to play. The "reserve" is how much
# sound is stored up ahead of the speaker (256 ms here); a freeze longer
# than that empties it.

NAME = "03-sound-test.py"
VERSION = "1.0"
print("{} v{}".format(NAME, VERSION))

import time

import config
import sound

BIG = config.BIG_FONT
SMALL = config.SMALL_FONT
HEADER = config.CYAN
DIM = config.color565(150, 150, 150)
WIDTH_BIG = 18        # characters of the big font that fit near the middle
WIDTH_SMALL = 34

display = config.init_display()
sound.volume(config.VOLUME)


def put(text, y, font=BIG, color=config.WHITE, width=WIDTH_BIG):
    """Draw text centered, padded to a fixed width so it covers whatever
    was there before."""
    config.centered_text(display, font, text.center(width), y, color)


def stage(number, name):
    """Clear the screen and show which part of the lab this is."""
    display.fill(config.BLACK)
    put("LAB 03  PART {} OF 5".format(number), 44, SMALL, HEADER, 26)
    put(name, 86, BIG, config.WHITE, 16)
    print()
    print("Part {}: {}".format(number, name))


def wait_for_sound():
    sound.wait()
    time.sleep_ms(150)


results = []

# ---------------------------------------------------------------------
# 1. A tone
# ---------------------------------------------------------------------
sound.init()
stage(1, "A tone")
put("A4  440 Hz", 150, BIG, config.YELLOW)
put("one steady sine wave", 200, SMALL, DIM, WIDTH_SMALL)
sound.tone(440, 1200)
time.sleep_ms(sound.latency_ms())
wait_for_sound()

# ---------------------------------------------------------------------
# 2. A scale
# ---------------------------------------------------------------------
stage(2, "A scale")
put("C major, one octave", 200, SMALL, DIM, WIDTH_SMALL)
SCALE = ("C4", "D4", "E4", "F4", "G4", "A4", "B4", "C5")
NOTE_MS = 320
for name in SCALE:
    sound.tone(sound.note_freq(name), NOTE_MS, release=40)
# The notes wait in the reserve before they reach the speaker, so wait
# that long before showing the first one. Picture and sound then line up.
time.sleep_ms(sound.latency_ms())
for name in SCALE:
    freq = sound.note_freq(name)
    put(name, 130, BIG, config.GREEN, 8)
    put("{} Hz".format(round(freq)), 166, SMALL, config.WHITE, 12)
    time.sleep_ms(NOTE_MS)
wait_for_sound()

# ---------------------------------------------------------------------
# 3. Named sounds
# ---------------------------------------------------------------------
stage(3, "Named sounds")
put("from sfx.py", 200, SMALL, DIM, WIDTH_SMALL)
for name in ("start", "right", "wrong", "chime", "done", "reminder"):
    sound.play(name)
    time.sleep_ms(sound.latency_ms())
    put(name, 140, BIG, config.YELLOW, 14)
    wait_for_sound()
    time.sleep_ms(250)


# ---------------------------------------------------------------------
# 4. Two cores
# ---------------------------------------------------------------------
def freeze_trial(core):
    """Play a 3.5 s tone, freeze core 0 for a while in the middle, and
    report what the sound did."""
    sound.init(core=core)
    sound.tone(440, 3500, release=50)
    time.sleep_ms(sound.latency_ms() + 600)      # let it settle
    sound.reset_stats()
    put("FREEZING core 0", 190, BIG, config.RED, 18)
    started = time.ticks_ms()
    # One long call that never looks up: core 0 can do nothing else until
    # it finishes, like a slow WiFi connection would.
    max(range(1_000_000))
    frozen = time.ticks_diff(time.ticks_ms(), started)
    time.sleep_ms(400)
    stats = sound.stats()
    wait_for_sound()
    return frozen, stats


stage(4, "Two cores")
put("Listen for a gap!", 150, BIG, config.YELLOW, 18)
put("core 0 freezes for over a second", 200, SMALL, DIM, WIDTH_SMALL)
time.sleep_ms(1800)

for core in (0, 1):
    display.fill_rect(30, 120, 300, 130, config.BLACK)
    put("Core {} in charge".format(core), 126, BIG, config.WHITE, 18)
    frozen, stats = freeze_trial(core)
    gap = stats["underruns"] > 0
    color = config.RED if gap else config.GREEN
    put("core 0 was frozen {} ms".format(frozen), 166, SMALL, DIM, WIDTH_SMALL)
    put("{} dropout{}".format(stats["underruns"],
                              "" if stats["underruns"] == 1 else "s"),
        190, BIG, color, 18)
    put("reserve fell to {} ms of {}".format(
        stats["min_headroom_ms"], stats["reserve_ms"]), 232, SMALL, DIM,
        WIDTH_SMALL)
    print("core {}: frozen {} ms, dropouts {}, reserve fell to {} of {} ms,"
          " longest wait {} ms".format(
              core, frozen, stats["underruns"], stats["min_headroom_ms"],
              stats["reserve_ms"], stats["max_gap_ms"]))
    results.append((core, stats["underruns"]))
    time.sleep_ms(2200)

# ---------------------------------------------------------------------
# 5. Drawing
# ---------------------------------------------------------------------
sound.init()
stage(5, "Drawing")
put("a tone while the screen repaints", 200, SMALL, DIM, WIDTH_SMALL)
sound.tone(660, 3000, release=50)
time.sleep_ms(sound.latency_ms() + 400)
sound.reset_stats()
shades = (config.color565(30, 30, 60), config.color565(60, 30, 30))
fills = 0
started = time.ticks_ms()
while time.ticks_diff(time.ticks_ms(), started) < 2200:
    display.fill(shades[fills % 2])        # every one takes about 130 ms
    fills += 1
stats = sound.stats()
wait_for_sound()
display.fill(config.BLACK)
put("LAB 03  PART 5 OF 5", 44, SMALL, HEADER, 26)
put("{} full repaints".format(fills), 110, BIG, config.WHITE, 18)
put("{} dropouts".format(stats["underruns"]), 160, BIG,
    config.GREEN if stats["underruns"] == 0 else config.RED, 14)
put("reserve fell to {} ms of {}".format(
    stats["min_headroom_ms"], stats["reserve_ms"]), 210, SMALL, DIM,
    WIDTH_SMALL)
print("drawing: {} full-screen fills, dropouts {}, reserve fell to {} of {} ms"
      .format(fills, stats["underruns"], stats["min_headroom_ms"],
              stats["reserve_ms"]))
time.sleep_ms(2500)

# ---------------------------------------------------------------------
# The verdict
# ---------------------------------------------------------------------
display.fill(config.BLACK)
put("LAB 03 DONE", 60, BIG, config.GREEN, 14)
for i, (core, dropouts) in enumerate(results):
    put("core {}: {}".format(core, "gap" if dropouts else "no gap"),
        124 + 42 * i, BIG, config.RED if dropouts else config.GREEN, 18)
put("Core 1 keeps the sound going", 232, SMALL, config.WHITE, WIDTH_SMALL)
put("when the Pico freezes.", 252, SMALL, config.WHITE, WIDTH_SMALL)
sound.play("chime")
sound.wait()
sound.deinit()

# Try This
#   1. In freeze_trial(), change 1_000_000 to 300_000, so core 0 freezes for
#      about 0.35 s. Does core 0 in charge still make a gap? (The reserve
#      is 256 ms, so only just.)
#   2. In freeze_trial(), change sound.init(core=core) to
#      sound.init(core=core, ibuf=16384). The reserve doubles to 512 ms.
#      How long must the freeze be now before core 0 makes a gap?
#   3. Change sound.volume(config.VOLUME) to sound.volume(80). Louder is
#      not cleaner: listen for the speaker buzzing at the top.
