# shared.py -- what every mode of mode-template.py shares.
#
# mode-template.py loads one mode at a time and throws the last one away,
# so a mode cannot keep anything that another mode (or the main loop)
# needs. Those things live here instead, because this module is loaded
# once, before any mode, and stays loaded:
#
#   speaker     the sound engine, started once and kept running
#   alarm       the alarm time, its tone, on/off, and whether it is ringing
#   chime       is the hourly chime on?
#   weather     the last forecast, so modes 1 and 2 share one download
#   sync_time() and fetch_weather(), which use WiFi
#
# A mode reads and writes these as shared.alarm_hour, shared.speaker, ...

import gc
import time

import sound
import wifi_time

# --- the speaker -------------------------------------------------------------
# On the Pico W, start the sound engine BEFORE the first mode draws: drawing
# leaves RAM in small pieces, and the I2S driver needs one free 4 KB block.
# (See "THE SOUND" in main-template.py.)
#
# WIFI_STOPS_SOUND: True stops the sound while WiFi is in use and starts it
# again afterwards. False leaves it running on core 1 the whole time --
# measured on the kit (2026-11-06): a tone played straight through an NTP
# sync and a weather download with no dropouts. Leaving it running also
# means the I2S buffer is never asked for again on a crowded heap.
WIFI_STOPS_SOUND = False
VOLUME_STEP = 10


class Speaker:
    def __init__(self, volume):
        self.running = False
        sound.volume(volume)

    def start(self):
        if not self.running:
            gc.collect()                # one unbroken block for the I2S buffer
            sound.init(rate=16000, ibuf=4096)
            self.running = True

    def off(self):
        if self.running:
            sound.deinit()
            self.running = False

    def play(self, name):
        """A named sound from sfx.py, such as "chime"."""
        if self.running:
            sound.play(name)

    def beep(self, freq=880, ms=120, level=1.0):
        """A short tone, cutting off anything still playing."""
        if self.running:
            sound.stop()
            sound.tone(freq, ms, level=level, release=min(40, ms // 3))

    def stop(self):
        if self.running:
            sound.stop()

    def busy(self):
        return self.running and sound.busy()

    def volume(self, change=0):
        """Move the volume by `change` (0 to 100), and return it."""
        return sound.volume(sound.volume() + change)


speaker = None           # made by start_speaker()

# A drawing buffer for the railway clock (lib/mondaine.py), made at power-up
# while RAM is still in one piece. By the time you reach mode 7, an unbroken
# 11.5 KB block may no longer be free.
band = None


def start_speaker(volume):
    """Start the sound, and set aside the big buffers, before any mode."""
    global speaker, band
    speaker = Speaker(volume)
    speaker.start()
    # The size of mondaine.BAND_BYTES: 16 rows of 360 pixels, 2 bytes each.
    # (Worked out here rather than imported, so lib/mondaine.py is only
    # loaded while mode 7 is showing.)
    band = bytearray(16 * 360 * 2)


# --- the hourly chime --------------------------------------------------------
chime_on = True
QUIET_START = 22         # no chime from 10 PM ...
QUIET_END = 7            # ... until 7 AM


def quiet_hour(hour):
    return hour >= QUIET_START or hour < QUIET_END


# --- the alarm ---------------------------------------------------------------
# Sounds from sfx.py the alarm can wake you with.
TONES = ("reminder", "doorbell", "bird", "chime", "magic", "powerup",
         "siren")
alarm_on = False
alarm_hour = 7
alarm_minute = 0
alarm_tone = 0           # an index into TONES
ringing = False          # set by the main loop when the alarm time comes
ring_started = 0         # time.ticks_ms() when it started

# --- time and weather over WiFi ----------------------------------------------
synced = time.localtime()[0] >= 2025      # Thonny or mpremote set it?
weather = None
weather_ticks = 0        # time.ticks_ms() of the last good download


def _online_begin():
    if WIFI_STOPS_SOUND and speaker is not None:
        speaker.off()


def _online_end():
    if speaker is not None:
        speaker.start()


def sync_time(display=None):
    """Set the clock from the internet. True if it worked."""
    global synced
    _online_begin()
    try:
        ok = wifi_time.sync_time(display)
    finally:
        _online_end()
    synced = synced or ok
    return ok


def weather_minutes():
    """How many minutes old the weather is, or None if there is none."""
    if weather is None:
        return None
    return time.ticks_diff(time.ticks_ms(), weather_ticks) // 60000


def fresh_weather(max_minutes=30):
    """The weather if it is younger than max_minutes, otherwise None."""
    age = weather_minutes()
    if age is None or age >= max_minutes:
        return None
    return weather


def fetch_weather():
    """Download new weather. Returns it, or None (the old weather is kept)."""
    global weather, weather_ticks
    import forecast
    _online_begin()
    try:
        new = forecast.fetch()
    finally:
        _online_end()
    if new is not None:
        weather = new
        weather_ticks = time.ticks_ms()
    gc.collect()
    return new
