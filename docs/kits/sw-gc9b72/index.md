# GC9B72 Smartwatch Kit (Pico 2 W)

This kit pairs a **Raspberry Pi Pico 2 W** with a **2.1" round 360×360
display** driven by the GalaxyCore **GC9B72** controller, plus three push
buttons. It has 2.25 times the pixels of our 240×240
[GC9A01 kit](../gc9a01/index.md), and because the Pico 2 W has WiFi, the
watch can set its own clock from the internet every time it powers up.

All of the code lives in
[`src/kits/sw-gc9b72`](https://github.com/dmccreary/clocks-and-watches/tree/main/src/kits/sw-gc9b72).

## Parts

| Part | Notes |
|---|---|
| Raspberry Pi Pico 2 W | RP2350 at 150 MHz, 520 KB RAM, 4 MB flash, 2.4 GHz WiFi |
| GC9B72 round display | 2.1" 360×360 SPI TFT. Silkscreen reads "Driver IC: GC9B72, Resolution: 360x360". |
| 3 momentary push buttons | Mode, Up, Down |
| Breadboard and jumper wires | |

!!! note "Ignore the 640×640 listings"
    Some online listings for this panel claim a 640×640 resolution. The
    silkscreen on the panel says 360×360, and that is what the driver uses.

## Wiring

The display's 10-pad breakout reads, left to right:
`GND VCC SDA SCL RST DC CS BL SDO TE`. Only 8 are wired: `SDO`
(read-back) and `TE` (tearing sync) are not used.

| Display pin | Pico 2 W pin | Wire color |
|---|---|---|
| GND | GND | black |
| VCC | 3V3 (**not** 5 V) | red |
| SDA / MOSI | GP3 | yellow |
| SCL / CLK | GP2 | orange |
| RST | GP4 | green |
| DC | GP5 | blue |
| CS | GP6 | purple |
| BL (backlight) | GP7 | gray |

Each button connects its GPIO pin to GND. The Pico's internal pull-up
resistors hold the pins high, so a pin reads `1` until its button is
pressed and `0` while it is held.

| Button | Pico 2 W pin | What it does |
|---|---|---|
| Mode | GP13 | Steps through what the Up/Down buttons change |
| Up | GP14 | The current setting goes up |
| Down | GP15 | The current setting goes down |

These are the same pin numbers and names (`BUTTON_MODE_PIN`,
`BUTTON_INCREMENT_PIN`, `BUTTON_DECREMENT_PIN`) our other clock kits use.
Every pin number lives in one file, `config.py`, which every lab imports.

!!! warning "Pico 2 W pins you cannot use"
    GP23, GP24, GP25, and GP29 are connected to the WiFi chip. The onboard
    LED hangs off the WiFi chip too, so use `Pin("LED")`, never `Pin(25)`.

## Getting Started

1. **Flash MicroPython.** Use the `RPI_PICO2_W` firmware from
   [micropython.org](https://micropython.org/download/RPI_PICO2_W/), not
   the plain `RPI_PICO2` build. The plain build has no WiFi and no
   `Pin("LED")`.
2. **Add your WiFi network.** Copy `secrets-template.py` to `secrets.py`
   and fill in your network name and password. `secrets.py` is listed in
   `.gitignore`, so your password is never committed. The Pico 2 W only
   connects to 2.4 GHz networks.
3. **Set your time zone.** Edit `TIMEZONE_HOURS` in `config.py`: -5
   Eastern, -6 Central, -7 Mountain, -8 Pacific. Set `USE_US_DST = False`
   if your area does not change its clocks.
4. **Upload the code.** Quit Thonny first, since only one program can use
   the Pico's USB serial port at a time. Then run:

    ```bash
    cd src/kits/sw-gc9b72
    ./upload-code.sh
    ```

    The script needs [`mpremote`](https://docs.micropython.org/en/latest/reference/mpremote.html)
    (`pip install mpremote`). It uploads the driver, fonts, and
    `shapes.py` to `/lib`, then `config.py`, your `secrets.py`, and all the
    labs.
5. **Run the probe.** Open `01-probe.py` in Thonny and run it. If the
   screen shows red, green, blue, and white bars and **Probe OK**, the
   whole kit is working.

## Labs

| Lab | File | What it teaches |
|---|---|---|
| 0 | `00-blink-onboard-led.py` | The board works: blink the LED with `Pin("LED")` |
| 1 | `01-probe.py` | A full hardware report: board, RAM, flash, kit files, WiFi, clock, buttons, SPI speed, display |
| 2 | `02-hello.py` | The display works, and `text()` needs a font module |
| 3 | `03-digital-clock.py` | Time, day, and date, redrawing only what changed |
| 4 | `04-wifi-sync-time.py` | Set the clock from an internet time server (NTP), with time zone and daylight saving |
| 5 | `05-analog-watch-face.py` | A full analog watch face that sets its own time. Meant to become `main.py`. |
| 6 | `06-button-test.py` | See each button's state live |
| 7 | `07-set-time.py` | Set the time by hand: Mode picks the field, Up/Down change it, with debounce and hold-to-repeat |

Every lab has been run on a real Pico 2 W and GC9B72 panel. The colors
come out in the right order, all three buttons work, and the edge of the
visible circle matches `SAFE_RADIUS` in `config.py`. Each program prints
its name and version when it starts, so you can check in Thonny's shell
which one is running.

### What the probe reports

`01-probe.py` checks everything software can check. Here is what it
measured on our kit:

| Check | Result |
|---|---|
| Board | Raspberry Pi Pico 2 W with RP2350, MicroPython 1.29.0, 150 MHz |
| RAM | 436 KB of Python heap (of the chip's 520 KB) |
| Full frame buffer | A 360×360 RGB565 buffer (253 KB) **fits** |
| Flash | 4 MB chip: 1.5 MB firmware, 2.5 MB filesystem |
| SPI | Asked for 24 MHz, got 24 MHz |
| Full-screen fill | 131 ms, so at most about 8 full redraws per second |

The flash chip size is not something MicroPython will tell you. The probe
finds it with a trick: the flash chip ignores address bits it does not
have, so on a 4 MB chip, reading 4 MB past the start "wraps around" and
returns the same bytes as the start.

## The Driver

GalaxyCore has never published a public datasheet for the GC9B72. The
register start-up sequence in `lib/gc9b72.py` comes from the xboot
project's [`fb-gc9b72.c`](https://github.com/xboot/xstar/blob/main/xstar/driver/framebuffer/fb-gc9b72.c), by way of
the [MaliosDark/Arduino_GC9B72](https://github.com/MaliosDark/Arduino_GC9B72)
Arduino driver (MIT). It was translated to MicroPython for the
[robot-faces](https://github.com/dmccreary/robot-faces) project, where it
was first tested on real hardware. This kit uses that same file, unchanged.

The driver works like the GC9A01 driver in our other smartwatch kit:

- **There is no frame buffer and no `show()`.** Every drawing call sends
  its pixels over SPI immediately.
- **There is no built-in font.** `text()` takes a font module as its first
  argument: `config.SMALL_FONT` (8×16) or `config.BIG_FONT` (16×32).
- **There is no `ellipse()` or `poly()`.** `lib/shapes.py` builds circles,
  rings, polygons, and triangles from the horizontal lines the driver can
  draw.

### SPI speed

MicroPython makes the SPI clock by dividing a 48 MHz peripheral clock, and
it rounds *down* to the nearest speed it can make. That gives 24 MHz or
12 MHz, with nothing in between and nothing above 24:

| You ask for | You get |
|---|---|
| 20,000,000 | 12,000,000 |
| 24,000,000 | 24,000,000 |
| 62,500,000 | 24,000,000 |

The kit runs at 24 MHz. If you see speckled pixels on long wires, change
`BAUDRATE` in `config.py` to `12_000_000`.

## How the Watch Face Avoids Flicker

A full-screen fill takes 131 ms. Clearing and redrawing the whole face
every second would make the screen flash. So `05-analog-watch-face.py`
draws the dial **once** and then, each second:

1. erases the old second hand by drawing it again in black
2. if the minute changed, erases the old minute and hour hands the same way
3. repairs whatever the erased second hand passed over
4. draws all three hands at their new angles

Step 3 stays small because of how the dial is laid out:

- The ticks sit **outside** the tip of the longest hand, so no hand ever
  touches them.
- The numerals sit **outside** the minute and hour hands, so only the
  second hand crosses them, and only the numeral nearest to it at that.
- The hour and minute hands get redrawn every second anyway.

Measured on the real kit, drawing the dial takes 617 ms at start-up, and
each second's update takes at most 232 ms (302 ms when the minute changes).

To check this layout, we ran the watch face against a simulated screen
and compared every second's partial redraw, pixel by pixel, with a fresh
drawing of the same time. They matched at every step, including noon,
midnight, and large time jumps. Making the minute hand long enough to
reach the numerals broke the match 208 times. Lab 05's comments suggest
trying this yourself.

## Making the Watch Start by Itself

MicroPython runs `main.py` from the Pico's filesystem at power-up. To turn
the kit into a standalone watch, copy `05-analog-watch-face.py` to the
Pico as `main.py`. With `SYNC_WITH_WIFI = True` it sets its clock over
WiFi at power-up and again at 3:00 AM every night. If WiFi is not
available it keeps running on whatever time the clock already has.

## Troubleshooting

| Symptom | Likely cause |
|---|---|
| `mpremote: failed to access ... (it may be in use by another program)` | Thonny is still connected. Quit it or click Stop/Disconnect. |
| `ImportError: no module named 'gc9b72'` | The `lib/` files did not upload. Run `upload-code.sh` again. |
| Screen stays black | Check the five signal wires (SCL, SDA, RST, DC, CS). Swapped SCL and SDA is the most common mistake. Check that VCC is on 3V3. |
| The LED does not blink in lab 00 | You flashed the plain `RPI_PICO2` firmware. Use `RPI_PICO2_W`. |
| The clock shows the wrong time on battery | The Pico has no clock battery. Thonny sets the clock while it is connected. Use lab 04, or `SYNC_WITH_WIFI` in lab 05. |
| Time is off by one hour | Check `TIMEZONE_HOURS` and `USE_US_DST` in `config.py`. |
| The probe says your network was not found | Check the spelling in `secrets.py`, and that the network is 2.4 GHz. |
| A button does nothing | An unwired button reads "not pressed" forever. Use lab 06 to test each one. |
