# 01. Choosing the hardware: find the "window"

Read this at the start of a kit, before any code exists.

## The idea

A sensor by itself is invisible: it prints a number in a console and nothing in the room seems
to change. The whole trick of this kit style is to put the sensor on a **cheap, colorful
display** so students watch it react to their breath and fingertips. The display is not the
point. It is a *window on the sensor*. Say so in the lesson ("We are not building a
smartwatch. This screen is a low-cost part made for smartwatches, about $5, and we use it as a
window"), and keep the sensor's best facts in front (precision, speed) because those are what
the window lets students see.

## Step 1. Find out what the user really has

List every extra part you are tempted to design around (display, push button, LED strip, buzzer,
extra LEDs) and mark each one **confirmed** or **assumed**. Ask about the assumed ones before you
build on them; this is the one place where asking is cheaper than guessing.

Why: on the SHT40 kit the NeoPixel lab was carried over from the parent kit and its pin moved to
avoid a clash. Two turns later the user said "this kit has no NeoPixel strip", and the lab, its
settings and its docs all had to be removed. A single question would have saved that.

If the user cannot answer yet, design only around the parts you can name, and put the open
question at the top of your report.

Also decide with the user what is **out of scope**. On the SHT40 kit the user dropped pressure
because the SHT40 cannot measure it; one line ("pressure needs a second sensor, skip it?") settled
it, and the layout was designed for exactly two readings.

## Step 2. Choose the display

Target: about **$5**, **SPI**, **3.3 V**, a **MicroPython driver that already runs in one of the
user's kits**. Then rank the rest.

| Criterion | What to check | Why it matters |
|-----------|---------------|----------------|
| Price | about $5 in single quantity (eBay, AliExpress). Screenshot the listing for the docs | keeps a classroom set affordable |
| Interface | SPI with 7 pins: VCC, GND, SCL, SDA, DC, CS, RST (some add BL) | few wires, fast pictures |
| Voltage | 3.3 V logic and supply. Never power from VBUS (5 V) | protects the parts |
| Driver | a MicroPython driver exists **and is already used in a kit here** | you can copy known-good pins and code |
| Shape | round 240x240 (GC9A01) is a face, a dial, a gauge: it looks like a toy, not a lab | delight |
| Header | male pins stick out (needs female-to-male wires) or holes (needs soldering: avoid) | "no soldering" is a promise on the box |
| Colour | full colour (RGB565) | gradients, mood colours |

Known good picks (verify against what the user owns):

- **GC9A01, 1.28 inch round, 240x240, SPI, about $5.** The pure-Python `gc9a01` driver, two
  bitmap fonts and a `shapes.py` helper are already vendored in `stem-robots` and
  `learning-micropython` kits. Pins that were confirmed on a Pico: SPI0, SCK GP2, MOSI GP3, DC GP4,
  CS GP5, RST GP6, 60 MHz.
- **ST7789, 240x240 or 240x320, SPI, about $5.** Same idea, square, many drivers.
- **SSD1306, 128x64 OLED, I2C.** Monochrome but very fast (it is built on `framebuf`, which has
  ellipse, poly and text built in). Use the `micropython-oled-render` skill to preview.

Where to look: search "1.28 inch round GC9A01 240x240 SPI TFT" on eBay or AliExpress. Take a
screenshot of the listing (price, pin labels) and keep it in the kit's docs folder. It is the
citation for "about $5", not box art.

## Step 3. Read the driver before you design (it changes the design)

Open the driver file and answer these. Each one shaped the SHT40 kit:

1. **Is there a frame buffer?** The GC9A01 driver has none. Every drawing call sends bytes down
   the wire, so you cannot "clear and redraw"; wiping 57,600 pixels every second strobes. This
   drives the whole display design (see 03-display-design.md).
2. **What does a call cost?** Read `pixel`, `hline`, `line`. In the GC9A01 driver `hline` and
   `vline` are just `fill_rect`, and `pixel` sets a window per dot, so a `pixel()` costs about as
   much as a whole rectangle and `line()` costs one call per dot. Draw with rectangles.
3. **Which characters exist?** Read the font header: `FIRST = 0x20`, `LAST = 0x7f` means ASCII
   only and `text()` silently skips anything else. There is no degree symbol; draw a small ring.
4. **What does `text()` do at the edge?** It skips characters that would overrun the screen. A
   silent skip looks like a missing letter; the simulator raises instead (05-verification.md).
5. **Backlight, rotation, inversion, baud rate?** Note any pin (BL) students may need to wire.

## Step 4. Plan the pins

Put every pin in `config.py` (template: `assets/templates/config.template.py`) and run:

    python3 scripts/pin_check.py path/to/config.py

It finds duplicate GPIOs and pins that are invalid for their bus, and prints the table with
physical pin numbers for the README and lesson. Rules that came from real conflicts:

- RP2040 bus pins are fixed by hardware. SPI0: SCK on GP2/6/18, MOSI on GP3/7/19. I2C0: GP0/1,
  GP4/5, GP8/9 and so on. A sensor on GP0/GP1 and a display on GP2-GP6 do not collide.
- **Keep the sensor's existing wiring.** The user's boards are already built; moving GP0/GP1
  would mean rewiring for no benefit. Only move a pin if it truly clashes.
- **Use a contiguous block of physical pins for the display** (pins 4,5,6,7,8,9, with GND at
  pin 8, plus 3V3 at pin 36). Students can wire "the six pins in a row" without a table.
- The button goes on **GP15 (pin 20)**, the bottom-left corner of the Pico with USB up, easy to
  find, with GND at pin 18. The onboard LED needs no wire.
- Do not take a pin from a part the kit does not have. Delete its settings.

## Step 5. Bill of materials and cost

Write a parts table with prices and notes (sensor about $1.65 on eBay, display about $5, Pico about
$4, breadboard, jumper wires, USB data cable). For classroom quantities, an existing
`purchasing-guide-generator` skill turns the list into a teacher-ready purchasing page with photos
and search terms. Warn about mislabelled listings (a cheap "SHT40" may be an SHT30/31, which use the
same wiring and commands but are less precise); a scanner lab that prints what it found is the fix.

## Step 6. Decide the hook for this sensor

The SHT40 hook is "a thermometer that is a mood ring": the temperature becomes a colour, a face, a
graph, a gauge, a race to 90 F. Find the equivalent for your sensor by asking which of these it
supports:

| Idea | SHT40 example | Other sensors |
|------|---------------|---------------|
| Make the invisible visible | big number in a colour that follows the value | distance: proximity bar; light: sky colour; sound: level ring |
| Give it a face | Buddy shivers, smiles, sweats | any "comfort" reading can drive a face |
| Show history | live sweep graph | anything that changes slowly |
| Show extremes | hi/lo records saved in flash | peaks, minimums, "loudest so far" |
| Touch it | finger test fills a thermometer | proximity, tilt, light shadow |
| Gauge it | rainbow ring gauges | any 0-100 quantity |
| Compare | two units (F and C) on one screen | two axes, two channels |

Avoid "contests" that push students into unsafe behaviour. A breath race that rewards blowing on
a humidity sensor as hard and fast as possible was rejected because it could make students
hyperventilate. One gentle breath to watch humidity jump is fine and is in the lesson.

## Step 7. Name the kit for what students do or see

"Mood Ring Thermometer" sells better than "SHT40 Temperature and Humidity Kit with GC9A01
Display". Use the fun name on the box cover and the lesson title; keep the part numbers in
the subtitle. Keep the fun name honest: it must describe what the kit really does.
