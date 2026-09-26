# GC9B72 Smartwatch Kit Session Log

**Date:** 2026-09-25
**Task:** Build a new clock kit around a Raspberry Pi Pico 2 W and a 2.1"
360×360 round GC9B72 display: labs from blink to a five-mode watch, then
student documentation and a social media preview.
**Target board:** Raspberry Pi Pico 2 W (RP2350, MicroPython 1.29.0) + bare
GC9B72 module on SPI0, three buttons on GP13/14/15
**Starting point:** an empty `src/kits/sw-gc9b72/lib/` folder. A
hardware-tested GC9B72 driver already existed in two sibling repos
(robot-faces and stem-robots).

## Results

| Metric | Value |
|---|---|
| Labs in kit | 13 (`00`–`12`), 2,468 lines |
| Kit `.py` total | 5,045 lines |
| Shared modules | `config.py` (194), `wifi_time.py` (139), `forecast.py` (105), `lib/watchparts.py` (363) |
| Mode modules for lab 12 | 5 (`mode_*.py`), 969 lines |
| Vendored into `lib/` | `gc9b72.py` (347, unchanged), `shapes.py` (232, header only changed), two fonts |
| Doc pages | 15 (`index.md`, 13 labs, teacher notes), 1,758 lines |
| Doc images | 27 (7 animated GIFs), 420 KB, all rendered from real lab code |
| Commits | 7, all pushed and deployed |

**Hardware status:** every lab ran on the real board. The user
confirmed the display ("Probe OK"), the color order, the `SAFE_RADIUS`
ring, all three buttons, setting the time, the stopwatch, the countdown
timer, and the digital and weather faces. The five-mode template (lab 12)
was driven from code on the real board, and its full button workflow was
tested in the simulator, but it has not been exercised with the physical
MODE button.

## Files Created

- `src/kits/sw-gc9b72/`:
  - 13 labs, from `00-blink-onboard-led.py` to `12-main-template.py`
  - `config.py`, `wifi_time.py`, `forecast.py`, and `secrets-template.py`
  - five `mode_*.py` modules for lab 12
  - `upload-code.sh` and `ideas.md`
- `src/kits/sw-gc9b72/lib/`:
  - `gc9b72.py`, `shapes.py`, and the two font modules, copied from robot-faces
  - `watchparts.py`, which is new
- `docs/kits/sw-gc9b72/`:
  - the rewritten `index.md` and a page for each of labs 00 through 12
  - `teacher-notes.md`
  - 27 images in `img/`, and the user's photo `large-smartwatch-clock.jpg`
- `plugins/social_override.py`: the MkDocs hook, from ibook-skills, with one fix
- `logs/sw-gc9b72-kit.md` (this file)

## Files Modified

- `.gitignore`: ignore `secrets.py` everywhere
- `mkdocs.yml`: kit nav section (15 pages), Mermaid fences, `hooks:` entry
- `docs/kits/index.md`: link to the new kit
- `src/kits/large-oled/secrets.py`, `src/kits/current-clock/secrets.py`:
  untracked (still on disk)

## Commits

| Commit | What |
|---|---|
| `d879e14b` | Stop tracking WiFi `secrets.py` files |
| `f1f91081` | Add GC9B72 smartwatch kit for the Raspberry Pi Pico 2 W (labs 00–07) |
| `07056cf1` | Add a digital watch face with large seven-segment digits (lab 08) |
| `427f68d8` | Add a weather clock face (lab 09, `forecast.py`) |
| `2c9270c0` | Add stopwatch, countdown timer, and a five-mode main template (labs 10–12) |
| `d309eed5` | Write student documentation for the kit |
| `a34b5121` | Give the kit page a proper social media preview |

---

## 1. Reuse the Tested Driver, Don't Write a New One

GalaxyCore publishes no datasheet for the GC9B72. A web search found the
only known-good register init sequence: the xboot project's
`fb-gc9b72.c`, reached through the MaliosDark/Arduino_GC9B72 C++ driver.

Before writing anything, the user pointed at `../stem-robots`. It wasn't
at that path on disk, but `gh search code gc9b72 --owner dmccreary` found
the driver in two repos:
- `robot-faces/src/kits/sw-gc9b72/lib/gc9b72.py`, with 34 labs, docs, and a
  session log
- `stem-robots/src/kits/9-dof-imu-display/lib/gc9b72.py`

The two copies were **byte-identical** to each other and to robot-faces'
`src/lib/gc9b72.py`, so that was taken as the stable version.

**Decision:** vendor the driver, both fonts, and `shapes.py` unchanged, and
keep robot-faces' wiring (SCK GP2, MOSI GP3, RST GP4, DC GP5, CS GP6, BL
GP7). That wiring is hardware-confirmed and matches the user's physical
kit, which already had a `sw-gc9b72` folder created. The only edit was
`shapes.py`'s header comment, which referred to robot-faces labs and
faces.

**Correction found along the way:** robot-faces links the xboot source as
`xboot/xboot`. A `gh search` showed the file actually lives in
`xboot/xstar`, and the docs link there.

## 2. Adapting to the Pico 2 W

The robot-faces kit targets a plain Pico. The Pico 2 W differs in ways
that matter:

- **Onboard LED.** On the Pico 2 W, the LED hangs off the CYW43439 WiFi
  chip, not GP25. `config.LED_PIN = "LED"`, and every lab uses
  `Pin("LED")`.
- **Reserved pins.** GP23, 24, 25, and 29 belong to the WiFi chip. That is
  documented in `config.py` and the docs.
- **SPI speed, measured rather than assumed.** A sweep of requested rates
  on the real board produced the same ladder as the RP2040: peripheral
  clock 48 MHz, so 12 or 24 MHz, **nothing between, nothing above 24**,
  even though the CPU runs at 150 MHz. `BAUDRATE = 24_000_000` stays, and
  `config.py` now records the measured Pico 2 W table instead of the
  RP2040 one.
- **Memory.** 436 KB of heap (421 KB free at boot), 4 MB flash, 2.5 MB
  filesystem. A full 360×360 RGB565 frame buffer (253 KB) **fits**. That
  opened a later option (see ideas.md) but wasn't used: the proven
  direct-draw driver was kept.

## 3. Secrets and Repository Hygiene

- **Global `.gitignore` entry for `secrets.py`**, at the user's request,
  written as a bare pattern so it covers every kit.
- **Two `secrets.py` files were already tracked**, in `large-oled` and
  `current-clock`. `.gitignore` doesn't untrack files git already knows
  about, so they were untracked with `git rm --cached` in their own commit.
  A non-printing check compared their whole history against the user's
  current WiFi credentials and found **no match**, so no history rewrite
  was needed.
- **`secrets-template.py`** is committed; `upload-code.sh` never uploads
  the template.
- **Before every commit**, the staged diff was scanned, without printing
  anything, for the user's actual SSID and password,
  credential-looking assignments, and (for the docs) real network names,
  the board's MAC address, and its unique ID.
- **Simulator debris.** CPython `__pycache__` folders from the test runs
  got staged once. They were caught and removed, and tests afterward ran
  with `PYTHONDONTWRITEBYTECODE=1`.

## 4. The Upload Script

`upload-code.sh` is based on the robot-faces version (lib → config → labs,
port auto-detection, and a "quit Thonny first" warning), with changes:

- It uploads `secrets.py` if present and warns if missing, instead of
  failing the way the stem-robots wi-fi-bot script does.
- It skips `secrets-template.py`.
- **macOS lists every Pico twice**, as `/dev/cu.usbmodem*` and
  `/dev/tty.usbmodem*`, which caused a false "multiple devices" warning. The
  script now searches only `cu.*` on macOS.
- `mpremote fs cp` skips unchanged files, so re-uploads are quick.

## 5. Lab Numbering, Version Banners, and the Probe

- **Renumbering.** The user asked for `01-probe.py`, so labs 01–06 shifted
  up by one. Every cross-reference in comments ("see lab 04") was updated
  by a script that checks each replacement happens exactly once.
- **Name and version banner** (user request): every lab prints
  `NAME vX.Y` as its very first action, **before any import**, so the
  banner appears even when an import fails. This was saved as a standing
  preference in memory. Versions were bumped whenever an already-uploaded
  lab changed (probe 1.2, stopwatch 1.1, template 1.1).
- **Probe design choices:**
  - **Files first.** It checks that the kit's files exist *before*
    importing `config.py`, because `config.py` imports the driver and fonts,
    and a missing font would otherwise crash the probe instead of being
    reported.
  - **Flash chip size by address wrap-around.** MicroPython has no API for
    it. Reading the XIP window at 0x10000000 + N and comparing with offset
    0: a 4 MB chip ignores the upper address bits, so it aliases at 4 MB.
    This was **verified on the real board** before being written into the
    probe.
  - **Frame buffer test.** "Would a full frame buffer fit?" is answered by
    actually allocating one, since that is the only honest test of
    fragmentation.
  - **No VSYS reading.** On the Pico 2 W, the VSYS ADC pin (GP29) is shared
    with the WiFi chip's clock, and reading it can disrupt the radio.
  - **Color bars.** SDO isn't wired, so the display can't be read back. The
    red/green/blue/white bars are the check that needs human eyes. The user
    confirmed the order.

## 6. Setting the Time (`wifi_time.py`)

- Connect → `ntptime.settime()` (UTC) → apply the time zone and US daylight
  saving → write the RTC → **turn WiFi off**, since the radio is the
  biggest power draw.
- **DST computed in UTC.** Both edges are converted to UTC: 2:00 standard
  time on the second Sunday in March, and 2:00 daylight time on the first
  Sunday in November. An older clock lab in this repo computed DST from
  *today's* weekday, which is wrong; that approach wasn't copied.
- Tested at the exact edges for 2026 and 2027 (Central and Eastern) in
  CPython. On the board, the sync set 19:00:10 against the Mac's 19:00:11
  CDT.
- `sync_time()` reuses an existing connection, so the weather clock can
  fetch the forecast and sync the time with **one** WiFi connection.

## 7. Buttons

- **Pins and names** follow the repo's existing clock kits:
  `BUTTON_MODE_PIN = 13`, `BUTTON_INCREMENT_PIN = 14`,
  `BUTTON_DECREMENT_PIN = 15`. These matched the user's description
  exactly.
- **Lab 06** reads the raw levels. **Lab 07** adds a `Button` class with
  **40 ms debounce** and **hold-to-repeat** (500 ms, then every 120 ms).
  It was simulated with deliberate contact bounce before the user
  confirmed it on hardware.
- Later, the class moved into `lib/watchparts.py` and gained two features
  (see section 13).

## 8. The Analog Face (Lab 05): Erase and Repair

There is no frame buffer, and a full redraw takes 131 ms, so the dial is
drawn **once**. Each second the program erases the old second hand in
black, repairs what it crossed, and redraws the hands.

**The layout was designed so that "what did it cross?" has a small, fixed
answer:**
- Ticks sit outside the longest hand, so they're never touched.
- Numerals sit outside the minute and hour hands. The closest numeral-box
  corner is 96.3 px from center, which is where `MINUTE_LENGTH = 92` comes
  from.
- Only the numeral *nearest* the second hand can be crossed. The geometry
  shows 2 seconds (12°) can clip a box, but 3 seconds (18°) clears it.
- The hour and minute hands are redrawn every second anyway.

**Verification:** a simulator test compared every incremental frame
against a fresh render: 1,293 updates, including noon, midnight, and large
time jumps, with **0 mismatches**. A mutation test (`MINUTE_LENGTH = 120`)
produced **208 mismatches**, proving the test can fail. The lab tells
students to try that same break. On hardware, the dial takes 617 ms and a
second's update at most 232 ms (302 ms at a minute change).

## 9. The Simulator (Not Committed)

Most verification ran against a CPython simulator kept in the session
scratchpad:

- **`fakehw`** decodes the GC9B72's `CASET`/`RASET`/`RAMWR` byte stream
  into a 360×360 array, so the **real driver** is what gets tested. It
  counts pixels *sent* versus pixels *changed*, and can tag every pixel
  with the face element that drew it (from the call stack), for overlap
  and visibility checks.
- **`harness`** runs a lab's real main loop on a fake millisecond clock,
  with scripted button presses that bounce and fire pin interrupts. It
  also supplies a fake calendar, an RTC that remembers what it's set to,
  a `framebuf` that stores low byte first like the real one, and stand-ins
  for WiFi, NTP, and HTTP that serve a canned forecast.
- It found real issues: a `fill_rect` that cut the lab 03 ring, lab 07's
  RTC writes not reflected (a simulator gap, fixed), and the mode-dots
  collision checks.

It wasn't added to the repo. It's listed as a possible next step, since
robot-faces has its own `check-labs.py` / `check-circle.py` precedent.

## 10. The Digital Face (Lab 08): Send Only Changed Pixels

User requirement: large digits and minimal flicker.

- **Seven-segment digits from rectangles**, the cheapest thing this driver
  draws. Each digit's pattern is a 7-bit mask in the same a–g order as the
  repo's GC9A01 lab 06 table, so `old ^ new` is exactly the segments to
  repaint.
- **Ghost segments** (a dim color, not black): turning a segment off is a
  repaint, never an erase.
- **Fixed-width date** with per-character diff.
- **Measured exactness:** a normal second sends **333 pixels, and all 333
  change**. Minute and hour changes are exact too. Only the once-a-day date
  change resends unchanged background pixels inside glyph cells.
- **Tick shapes computed once** (`_RunRecorder` captures `shapes.poly()`'s
  runs). That cut the minute rollover from 419 to 295 ms. The rest is
  driver per-call overhead. The remaining 0.3 s sweep of 59 ticks going
  dark isn't flicker, since each pixel changes once, so it was kept. An
  "alternate the ring color each minute" option was offered and recorded
  in ideas.md.

**User feedback, round 2:** "the corners and intersections are all black;
make them white," and "the leftmost digit only needs 1 or blank."

- **13 pieces per digit:** the 7 segments plus 6 joint squares. A joint is
  lit whenever any adjoining segment is lit. The gaps are gone, and the
  bitmask XOR logic extends to 13 bits unchanged.
- **Half-width leading digit** in 12-hour mode (segments b and c only),
  and the row is **re-centered**, which also widened the clearance to the
  seconds ring from 8.5 to 21 px. 24-hour mode keeps a full digit, since it
  needs 0, 1, and 2.

## 11. The Weather Clock (Lab 09)

- **Open-Meteo over OpenWeatherMap.** The user's learning-micropython
  course uses OpenWeatherMap: it needs an API key, sends 40 three-hour
  slots (about 16 KB), and leaves daily highs and lows to be computed.
  Open-Meteo is **keyless** and returns the daily high, low, and WMO code
  directly, in **435 bytes**, over plain HTTP. It was verified from the Mac
  and then from the Pico (1.1 s to fetch and parse).
- **Default location: Minneapolis** (44.98, −93.27), matching the course's
  weather labs. The user's own town was deliberately not written into a
  public repo.
- **Five icons, not four.** The user asked for sunny, cloudy, partly
  cloudy, and rain. **Snow** was added so Minnesota winters aren't shown as
  rain. Fog maps to cloudy; drizzle, showers, freezing rain, and
  thunderstorms map to rain.
- **Icons drawn in a 64×64 `framebuf`, then blitted once.** That gives
  filled `ellipse()` and `poly()` in C, and an icon never appears
  half-built. `framebuf` stores RGB565 **low byte first**, which was
  verified on the board, so every color goes through `swapped()`.
- **Fixed-width temperature fields** (`"%3d"`, right-aligned), with degree
  signs drawn once at fixed spots.
- **Refresh at :00:30 and :30:30,** with a retry every 5 minutes after a
  failure. The fetch just after midnight rolls Tomorrow into Today. The
  schedule was tested in the simulator, including a failed startup.
- On hardware, a normal second takes 1.8 ms and a forecast change about
  190 ms. The user's reaction: "The display is beautiful!"

## 12. Stopwatch and Countdown Timer (Labs 10 and 11)

- **`lib/watchparts.py` instead of a fourth copy** of the digit code:
  `Digit`, `TickRing`, `TextLine`, and `Button`, each remembering what it
  last drew. Labs 07 and 08 stay unchanged as the teaching versions.
- **One button pattern for both:** UP starts and stops, DOWN resets (only
  when stopped or paused, so a bump can't wipe a run), and MODE does each
  tool's extra job (lap, set). An on-screen hint line always shows the
  current meaning.
- **Time comes from `ticks_ms`, never from summing loop steps.** The
  stopwatch banks elapsed time across stops. The timer computes its
  **end** tick and measures the distance to it.
- **The timer is written as an explicit six-state machine** (set minutes,
  set seconds, ready, running, paused, done), diagrammed in its header.
  That makes it teachable as "what a button does depends on the state."
- **The alarm is visual by default:** flashing red 00:00 and the LED. The
  kit has no speaker, so there is an optional `BUZZER_PIN` (default
  `None`), and the repo's older `timer` kit's GP10 speaker wasn't assumed.
- **Fastest lap and average** (user request): they appear from two laps
  on, since with one lap they'd just repeat it. The fastest row is green;
  newest is yellow unless it's also fastest. The **Best** line keeps
  showing the fastest lap after it scrolls off the three-row list.
- The user confirmed both on hardware ("I love the lap timer!").

## 13. One Watch, Five Modes (Lab 12)

**Requirements:** MODE cycles weather (default), analog, digital,
stopwatch, and timer; modes load when needed; five dots show the current
mode.

- **Labs can't be imported as modes.** They're scripts with endless loops,
  and their names start with digits. So each mode is a new module,
  `mode_*.py`, built on `watchparts`, exposing **four functions**:
  `start(display, up, down, saved)`, `update(now)`, `stop()`, and an
  optional `on_mode(kind)`.
- **Real unloading.** Before importing a mode, the template snapshots
  `sys.modules`. On a switch it deletes every module that appeared since
  (the mode *and* what it imported, such as `forecast` and `requests`),
  then runs `gc.collect()`. Measured: **364–400 KB free in every mode, not
  creeping down**, and 0.67–0.86 s from pressing MODE to fully drawn.
- **MODE semantics.** A short press, reported on release, switches modes.
  Because of that, the stopwatch laps with DOWN (the classic two-button
  layout), and the **timer is set with a 1 s long press**. The timer
  captures MODE while setting and during the alarm, so a press there
  can't switch modes by accident.
- **Background state.** Whatever `stop()` returns is handed back to
  `start()`. A running stopwatch keeps running, since its time is ticks
  based. A running timer returns `wake_at`, and the template switches to
  it at zero from any mode. The weather mode keeps its forecast when it's
  under 30 minutes old **and from today** (the date check covers leaving
  the mode before midnight).
- **Tap interrupt in `Button`.** The analog face spends up to 232 ms per
  second drawing, and a weather fetch blocks for 1–3 s, so a quick MODE tap
  could be missed entirely. A falling-edge IRQ records the time. A tap
  counts only if it came more than `DEBOUNCE_MS` after the last observed
  release, which rejects release bounce. The logic was unit-tested (quick
  tap counted once, no phantom presses), and labs 10 and 11 were
  re-verified with it.
- **Speed-ups found on the real board:**
  - The `TickRing` shapes are cached by geometry, so re-entering a ring
    mode skips the 0.6 s computation.
  - New `TextLine`s assume a cleared background, so blank lap lines cost
    nothing.
  - A `gc.collect()` was added before the "KB free" print, because the
    first numbers (84 KB free for analog) were uncollected garbage, not
    real usage.
- **The dots strip is reserved** (y = 316–328). No mode draws there, which
  was checked per mode in the simulator, including the analog second hand
  at :30. The analog mode drops its 6 o'clock marker (the dots take its
  place) and shortens the second hand from 138 to 134 px.
- **Dots center for any number of modes** (v1.1). This was found while
  writing the docs, whose "add a sixth mode" exercise would otherwise
  produce an off-center row.

## 14. Sound Plans (ideas.md)

The user has MAX98357A I2S amplifiers. Those are I2S, not PWM, so
`BUZZER_PIN` doesn't apply to them. The stem-robots amp kit used GP11–15,
which collides with this kit's buttons. The proposed layout is BCLK GP10,
LRC GP11 (the rp2 driver requires BCLK + 1), and DIN GP12, with GAIN and SD
unconnected. That leaves GP16 for a future piezo. It's recorded in
`ideas.md` together with the other face ideas (frame-buffer analog,
binary, word clock, Fibonacci, sun and moon, world clock). The user later
trimmed that file's "Done" section.

## 15. Student Documentation

**Audience: sixth graders (about 11 years old).**

- **Structure.** `index.md` became the kit's home page:
  - the user's photo of the real kit
  - a banner of five faces
  - parts and wiring tables, in kid language
  - one-time setup steps
  - a clickable thumbnail menu of the labs
  - "Words to Know"

  Each lab page follows one pattern: what you'll learn → run it → how it
  works (with snippets copied from the real code) → Try This → if it
  doesn't work → next lab. Analogies do the heavy lifting: a whiteboard
  versus a notebook for RAM and flash, wrapping house numbers for the flash
  probe, a bouncing basketball for debounce, a backpack for lazy loading,
  and video game states for the state machine.
- **Nothing accurate was deleted.** The previous adult-level write-up
  (driver history, measurements, flicker techniques) moved **verbatim** to
  `teacher-notes.md`.
- **Real images.** All 26 screen images and animations came from running
  each lab's real code in the simulator. They're drawn as a round watch
  (bezel, glass masked at radius 171) on a transparent background, and the
  GIFs use white.
  - Animations: the analog hands, the button tester, setting the time, the
    digital colon and ring, the stopwatch, the timer countdown and alarm,
    and the mode cycle.
  - Lab 00 reuses the site's existing photo-GIF, since it uses no display.
  - The probe image used stand-ins returning the **real board's measured
    values** but **made-up network names**, MAC address, and board ID.
- **Mermaid** was enabled in `mkdocs.yml` (Material's standard
  superfences config) for the timer's state diagram. It was checked in a
  browser.
- **The photo corrected the wiring notes.** Zooming into the photo showed
  the pads read **GND VCC SCL SDA…**; the robot-faces-derived notes said
  SDA SCL. The wiring itself was always right, since SCL→GP2 and SDA→GP3 is
  why the kit worked. The `config.py` comment was fixed, and the docs use
  the correct order.
- **Checks:** a clean `mkdocs build` (no broken links or images), visual
  review in the built-in browser at desktop size, and one unused image
  removed before commit.

## 16. Social Media Preview

- **Problem.** Material's `social` plugin generated a text card for the
  page, titled "Introduction" (the nav label) with the site-wide
  description. The sims pages' `image:` front matter had never taken
  effect in this repo.
- **Fix, following the user's existing convention.** The
  `plugins/social_override.py` hook was copied from ibook-skills and
  registered under `hooks:`. The front matter matches the ibook-skills
  pages: `title`, `description`, `image`, `og:image`, and `twitter:image`.
  Front-matter `title` does override the nav label in `og:title` (checked
  on a sims page).
- **The preview image** is a 1200×630 crop of the photo, centered on the
  watch (103 KB, no EXIF).
- **One improvement to the hook.** It swapped the image URL but left
  `og:image:type` as `image/png`, which mislabeled the JPEG. This repo's
  copy now sets the type from the file extension. The ibook-skills
  original still has the gap.
- **Side effect, checked first.** The four sims pages naming an `image:`
  now use their screenshots, and all four image files exist. Pages without
  an image keep their generated card.
- **Verified on the live site** about 40 s after deploy: the correct
  title, description, `og:image`, and `image/jpeg`, and the image serves
  HTTP 200.

## 17. What Is Verified, and How

| Item | Simulator | Real board | User confirmed |
|---|---|---|---|
| Driver, colors, `SAFE_RADIUS` | — | yes | yes |
| Probe | full run | full run | "Probe OK" |
| WiFi time sync, DST | DST edges | 1 s from the Mac | — |
| Buttons, debounce, hold-repeat | yes | — | yes |
| Analog redraw correctness | 1,293 frames, mutation-tested | timings | — |
| Digital face exactness | sent = changed | timings | "much nicer" |
| Weather layout and schedule | yes | live fetch | "beautiful" |
| Stopwatch laps, best/avg | yes | timings | yes |
| Timer states and alarm | yes | timings | "works perfect" |
| Five-mode switching, unloading, wake | yes | driven from code | not yet with the MODE button |
| Social preview | — | live site | — |

## 18. Open Items

- Try lab 12 with the physical MODE button: cycle the modes, hold MODE in
  the timer, and let a background timer take over the screen.
- Add `__pycache__/` to `.gitignore`. Every `mkdocs` build now imports the
  hook and leaves `plugins/__pycache__`.
- Port the `og:image:type` fix back to ibook-skills' `social_override.py`.
- Consider committing the simulator (with `check-labs`-style runners), as
  robot-faces did, so future labs can be verified the same way.
- Items in `ideas.md`: the MAX98357A `sound.py` module with a melodic
  timer alarm, the frame-buffer analog face, the digital ring's color
  alternation, and a stopwatch past 99:59.99.
