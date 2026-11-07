# The Sensor Display: six modes, one button
#
# Run 01, 02, 06 and 08 first. If all of them print "TEST PASS", this
# program will work too.
#
# One push button switches between six screens:
#
#   1. Classic  the classic face from program 07
#   2. Buddy    a face that feels the air. Its face is the mood-ring color!
#   3. Live     a graph of the last few minutes of temperature
#   4. Ring     rainbow ring gauges for temperature and humidity
#   5. Finger   touch the sensor and fill the thermometer
#   6. Hi/Lo    the hottest and coldest readings, saved even when unplugged
#
# The button (see config.py for the wiring):
#   tap                the next mode
#   hold 0.8 seconds   switch between F and C
#   hold 3 seconds     (in Hi/Lo only) clear the records
#
# The green LED on the Pico blinks once every time the sensor is read.
# Two quick blinks mean a reading failed. If the blinking STOPS, the
# program has stopped.
#
# upload-code.sh also saves a copy of THIS program on the Pico as main.py.
# A Pico runs main.py by itself when it gets power, so the display starts
# with no computer at all.
#
# HOW THE PROGRAM IS BUILT
#   sht40.py       reads the sensor
#   button.py      the button, with an interrupt so no press is missed
#   heartbeat.py   the blinking LED
#   records.py     the high and low records
#   widgets.py     colors, icons and gauges
#   display_ctx.py   everything the modes share, and the pattern each mode follows
#   mode_*.py      one small file for each mode
# Every file is in the lib folder on the Pico. Open them and read them!

import gc
import time
from machine import Pin, I2C
import config
from sht40 import SHT40
from button import Button
from heartbeat import Heartbeat, onboard_led
from records import Records
from display_ctx import Context
import vga1_8x16 as SMALL_FONT

gc.collect()


def load_modes():
    """Load the six mode files one at a time, tidying memory as we go."""
    from mode_classic import ClassicMode
    gc.collect()
    from mode_buddy import BuddyMode
    gc.collect()
    from mode_live import LiveMode
    gc.collect()
    from mode_ring import RingMode
    gc.collect()
    from mode_finger import FingerMode
    gc.collect()
    from mode_hilo import HiLoMode
    gc.collect()
    return [ClassicMode(), BuddyMode(), LiveMode(), RingMode(), FingerMode(), HiLoMode()]


# --- Set up the hardware ---------------------------------------------
i2c = I2C(config.I2C_BUS,
          sda=Pin(config.I2C_SDA_PIN),
          scl=Pin(config.I2C_SCL_PIN),
          freq=config.I2C_BUS_FREQ)
sensor = SHT40(i2c, config.SHT40_ADDR, config.SHT40_CMD_MEASURE_HIGH,
               config.SHT40_CMD_SOFT_RESET, config.SHT40_MEASURE_MS)
display = config.init_display()
button = Button(config.BUTTON_PIN, config.BUTTON_DEBOUNCE_MS)
led = Heartbeat(onboard_led(config.BUILT_IN_LED_PIN), config.HEARTBEAT_MS)
records = Records(config.RECORDS_FILE, config.RECORDS_SAVE_SECONDS)

modes = load_modes()
ctx = Context(display, records, len(modes))
print("Display ready. {} modes. Free memory: {} bytes.".format(
    len(modes), gc.mem_free()))

# Give the sensor a clean start.
#
# If the last program was stopped in the middle of a reading, the sensor can
# be left half way through a conversation. If it still will not answer, we
# do not quit. We show SENSOR FAIL and keep trying, so the display comes alive
# by itself as soon as the sensor answers.
try:
    sensor.reset()
except OSError:
    ctx.sensor_ok = False
    print("The sensor is not answering. Unplug the Pico and plug it back in.")


def show_mode(ctx, mode):
    """Wipe the screen, draw the mode, and fill in the latest numbers."""
    mode.enter(ctx)
    if ctx.have_reading():
        mode.update(ctx)
    gc.collect()


mode = modes[ctx.mode_index]
show_mode(ctx, mode)
next_read = time.ticks_ms()       # take the first reading right away

try:
    while True:
        now = time.ticks_ms()

        # --- 1. The button. Handle every press that is waiting. -------------
        redraw = False
        cleared = False
        while True:
            press = button.next_press()
            if press == 0:
                break
            print("Button: {} ms".format(press))    # so you can see every press
            if press < config.LONG_PRESS_MS:
                ctx.mode_index = (ctx.mode_index + 1) % len(modes)     # next mode
                redraw = True
            elif press >= config.CLEAR_PRESS_MS and hasattr(modes[ctx.mode_index], "cleared"):
                records.clear()                  # a long hold in Hi/Lo
                if ctx.have_reading():
                    records.update(ctx.temp_f, ctx.humidity)
                cleared = True
                redraw = True
            else:
                ctx.use_fahrenheit = not ctx.use_fahrenheit            # F <-> C
                redraw = True

        if redraw:
            mode = modes[ctx.mode_index]
            show_mode(ctx, mode)
            if cleared:
                mode.cleared(ctx, now)
            # Ask for a fresh reading soon, so the new screen is up to date.
            next_read = time.ticks_add(now, 50)

        # --- 2. The sensor. -------------------------------------------------
        if time.ticks_diff(now, next_read) >= 0:
            next_read = time.ticks_add(now, mode.READ_MS)
            try:
                temp_c, humidity = sensor.read()
            except (OSError, ValueError) as error:
                led.alarm(now)                       # two quick blinks
                if ctx.sensor_ok:
                    ctx.sensor_ok = False
                    mode.draw_status(ctx, False)     # the title turns into SENSOR FAIL
                    print("Sensor problem:", error)
                try:
                    sensor.reset()                   # try to wake it up
                except OSError:
                    pass
            else:
                led.beat(now)                        # one blink
                ctx.add_reading(temp_c, humidity)
                records.update(ctx.temp_f, ctx.humidity)
                records.save_if_due(now)
                if not ctx.sensor_ok:
                    ctx.sensor_ok = True
                    mode.draw_status(ctx, True)
                mode.update(ctx)
                print("{}: {:.1f} F  {:.1f} C  {:.1f} %".format(
                    mode.NAME, ctx.temp_f, temp_c, humidity))

        # --- 3. Small animations (Buddy's blink, the flashing message) ----
        mode.tick(ctx, now)
        led.tick(now)

        time.sleep_ms(10)

except KeyboardInterrupt:
    print("Got Ctrl-C, stopping.")
    led.off()
    if records.changed:
        records.save()
    display.fill(config.BLACK)
    text = "Stopped"
    display.text(SMALL_FONT, text, config.CENTER_X - (len(text) * SMALL_FONT.WIDTH) // 2,
                 config.CENTER_Y - 8, config.WHITE, config.BLACK)
