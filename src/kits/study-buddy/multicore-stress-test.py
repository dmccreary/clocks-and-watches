# multicore-stress-test.py
# Does the sound stay clean while the display, WiFi, and flash are busy?
#
# A steady 440 Hz tone plays on core 1 while core 0 does ONE kind of heavy
# work per phase. After each phase the screen asks:
#
#     Heard a click or gap?      UP = yes      DOWN = no
#
# so YOUR EARS are part of the instrument. The counters from sound.stats()
# only know whether core 1 handed sound to the I2S ring buffer on time. They
# cannot see the DMA interrupt on core 0 being late, which is exactly what a
# flash write is expected to cause. See docs/kits/study-buddy/
# 06-multicore-guide.md for why.
#
# Phases:
#    0  baseline            nothing happens (a clean tone: your reference)
#    1  screen repaints     full-screen fills
#    2  WiFi scans          three scans
#    3  WiFi connect + time connect, ask the internet the time, disconnect
#    4  web request         connect and fetch a small web page
#    5  garbage collection  allocate and collect repeatedly
#    6  small flash writes  five 4 KB files, written and deleted
#    7  large flash write   one 200 KB file, written and deleted
#    8  everything in turn  fill, scan, small write, collect, three times
#    9  silent write        the large write again, with NO tone playing:
#                           listen for a pop even though nothing is playing
#    then: a speed test (how much slower is core 0 with sound playing?)
#
# Listen with the speaker close to your ear, at a normal volume.
#
# Run it from Thonny, then copy the table printed at the end.
# It writes and deletes temporary files in the Pico's flash (up to 200 KB)
# and makes WiFi connections using secrets.py. It never prints the password.

NAME = "multicore-stress-test.py"
VERSION = "1.0"
print("{} v{}".format(NAME, VERSION))

import gc
import os
import time

import config
import sound
from watchparts import Button

BIG = config.BIG_FONT
SMALL = config.SMALL_FONT
DIM = config.color565(150, 150, 150)
TONE_HZ = 440

display = config.init_display()
mode_button, up_button, down_button = [
    Button(pin) for pin in config.init_buttons()]


def put(text, y, font=SMALL, color=config.WHITE, width=34):
    config.centered_text(display, font, text.center(width), y, color)


def title(number, name, silent=False):
    display.fill(config.BLACK)
    put("STRESS TEST", 44, SMALL, config.CYAN, 26)
    put("phase {}".format(number), 84, SMALL, DIM, 20)
    put(name, 110, BIG, config.WHITE, 18)
    if silent:
        put("silence: listen for a pop", 170, SMALL, config.YELLOW, 30)
    else:
        put("listen for a click or gap", 170, SMALL, config.YELLOW, 30)


def ask():
    """Ask the listener. Returns True if they heard a problem."""
    display.fill(config.BLACK)
    put("Click or gap?", 100, BIG, config.WHITE, 16)
    put("UP = yes", 170, BIG, config.RED, 12)
    put("DOWN = no, it stayed clean", 214, SMALL, config.GREEN, 28)
    while True:
        now = time.ticks_ms()
        if up_button.pressed(now):
            return True
        if down_button.pressed(now):
            return False
        time.sleep_ms(10)


# --- the loads ---------------------------------------------------------
def load_baseline():
    time.sleep_ms(3000)


def load_repaints():
    shades = (config.color565(30, 30, 60), config.color565(60, 30, 30))
    n = 0
    start = time.ticks_ms()
    while time.ticks_diff(time.ticks_ms(), start) < 3000:
        display.fill(shades[n % 2])
        n += 1
    print("    ({} full-screen fills)".format(n))


def load_scans():
    import network
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    for _ in range(3):
        found = wlan.scan()
        print("    (scan found {} networks)".format(len(found)))
    wlan.active(False)


def load_wifi_sync():
    import wifi_time
    print("    (sync ok: {})".format(wifi_time.sync_time()))


def load_web_request():
    import network
    import secrets
    try:
        import requests
    except ImportError:
        import urequests as requests
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    wlan.connect(secrets.wifi_ssid, secrets.wifi_pass)
    waited = 0
    while not wlan.isconnected() and waited < 150:
        time.sleep_ms(100)
        waited += 1
    if not wlan.isconnected():
        wlan.active(False)
        raise RuntimeError("could not connect to WiFi")
    url = ("http://api.open-meteo.com/v1/forecast?latitude=44.98"
           "&longitude=-93.27&daily=weather_code&forecast_days=2")
    reply = requests.get(url)
    size = len(reply.text)
    reply.close()
    wlan.disconnect()
    wlan.active(False)
    print("    (fetched {} bytes)".format(size))


def load_gc():
    junk = []
    for _ in range(20):
        junk.append(bytearray(8000))
        gc.collect()


def write_file(name, size):
    block = b"x" * 4096
    with open(name, "wb") as f:
        for _ in range(size // 4096):
            f.write(block)
    os.remove(name)


def load_small_writes():
    for _ in range(5):
        write_file("stress_tmp.bin", 4096)
        time.sleep_ms(500)


def load_large_write():
    started = time.ticks_ms()
    write_file("stress_tmp.bin", 200 * 1024)
    print("    (200 KB write and delete took {} ms)".format(
        time.ticks_diff(time.ticks_ms(), started)))


def load_everything():
    for _ in range(3):
        load_repaints_short()
        load_scans_short()
        write_file("stress_tmp.bin", 4096)
        load_gc()


def load_repaints_short():
    shade = config.color565(30, 30, 60)
    for n in range(4):
        display.fill(shade if n % 2 else config.BLACK)


def load_scans_short():
    import network
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    wlan.scan()
    wlan.active(False)


PHASES = (
    ("baseline", load_baseline, 5000),
    ("repaints", load_repaints, 4500),
    ("WiFi scans", load_scans, 12000),
    ("WiFi connect", load_wifi_sync, 16000),
    ("web request", load_web_request, 20000),
    ("collect", load_gc, 3000),
    ("small writes", load_small_writes, 5000),
    ("large write", load_large_write, 8000),
    ("everything", load_everything, 20000),
    ("silent write", load_large_write, 0),      # 0 = no tone at all
)

# --- run ---------------------------------------------------------------
sound.volume(config.VOLUME)
sound.init(rate=16000, ibuf=8192)
rows = []
for number, (name, load, tone_ms) in enumerate(PHASES):
    title(number, name, silent=(tone_ms == 0))
    print("phase {}: {}".format(number, name))
    sound.reset_stats()
    if tone_ms:
        sound.tone(TONE_HZ, tone_ms, release=60)
    time.sleep_ms(sound.latency_ms() + 800)          # let the tone settle
    sound.reset_stats()
    started = time.ticks_ms()
    error = None
    try:
        load()
    except Exception as e:
        error = "{}: {}".format(type(e).__name__, e)
        print("    FAILED:", error)
    took = time.ticks_diff(time.ticks_ms(), started)
    time.sleep_ms(300)
    stats = sound.stats()
    sound.stop()
    sound.wait()
    heard = ask()
    rows.append((number, name, took, stats["underruns"],
                 stats["min_headroom_ms"], stats["max_gap_ms"], heard, error))
    print("    took {} ms, underruns {}, reserve low {} ms, longest wait {} ms,"
          " heard a problem: {}".format(
              took, stats["underruns"], stats["min_headroom_ms"],
              stats["max_gap_ms"], "YES" if heard else "no"))
    time.sleep_ms(400)

# --- speed: how much slower does core 0 run while sound plays? ----------
display.fill(config.BLACK)
put("SPEED TEST", 80, BIG, config.WHITE, 14)
put("no listening needed", 130, SMALL, DIM, 30)


def work(n=150000):
    x = 0
    start = time.ticks_ms()
    for i in range(n):
        x += i
    return time.ticks_diff(time.ticks_ms(), start)


sound.deinit()
time.sleep_ms(200)
alone = work()
sound.init(rate=16000, ibuf=8192)
time.sleep_ms(500)
silent = work()                 # the audio loop is running, making silence
sound.tone(TONE_HZ, 4000)
time.sleep_ms(sound.latency_ms() + 200)
playing = work()
sound.init(rate=44100, ibuf=16384)
sound.tone(TONE_HZ, 4000)
time.sleep_ms(sound.latency_ms() + 200)
playing44 = work()
sound.deinit()

print()
print("SPEED: the same 150,000-step loop on core 0")
print("  no audio at all        : {} ms".format(alone))
print("  audio loop, silence    : {} ms  ({:+.1f}%)".format(
    silent, 100 * (silent - alone) / alone))
print("  16 kHz tone playing    : {} ms  ({:+.1f}%)".format(
    playing, 100 * (playing - alone) / alone))
print("  44.1 kHz tone playing  : {} ms  ({:+.1f}%)".format(
    playing44, 100 * (playing44 - alone) / alone))

print()
print("RESULTS")
print("  # phase          ms   underruns  reserve-low  longest-wait  heard")
for number, name, took, under, low, gap, heard, error in rows:
    print("  {} {:<12} {:>6}   {:>6}     {:>6}      {:>6}       {}{}".format(
        number, name, took, under, low, gap, "YES" if heard else "no",
        "  ERROR " + error if error else ""))

display.fill(config.BLACK)
put("DONE", 120, BIG, config.GREEN, 8)
put("copy the table from the shell", 180, SMALL, DIM, 30)
