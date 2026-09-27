# GC9B72 Smartwatch Kit: Prompt Log

This is an exact record of every prompt used to build the GC9B72
Smartwatch Kit, in order, in one Claude Code session on September 25,
2026 (plus the final two prompts on September 27). The design decisions
behind each step are in the companion
[session log](sw-gc9b72-kit.md).

**How to read it**

- Every prompt is copied **word for word**, typos and double spaces
  included, in a text block.
- **(While Claude was working)** marks a message sent as an interruption
  while Claude was in the middle of a task. Claude folded it into the work
  in progress.
- Below each prompt is a short note on what it led to, and the commit it
  produced, if any.

**By the numbers:** 42 prompts. 9 were sent while Claude was working, and
10 were reports from the real hardware. 8 were "publish", "commit and
push", or similar, which together produced 9 commits.

---

## Part 1: The Prompts

### Getting started: the kit, the driver, and the hardware (Sept 25)

**1.**

```text
I have a new project.  It is a Raspberry Pi Pico 2W with a smartwatch display that uses the driver gc9b72
```

Claude found the empty `src/kits/sw-gc9b72/lib/` folder and searched the
web for the GC9B72: it drives 360×360 round panels, and the only public
initialization code comes from the xboot project.

**2. (While Claude was working)**

```text
look in the ../stem-robots for examples
```

`stem-robots` wasn't on disk at that path. Searching GitHub found a
hardware-tested driver in both `stem-robots` and `robot-faces`, and the
two copies were identical. That driver, its fonts, and `shapes.py` were
reused unchanged.

**3. (While Claude was working)**

```text
make sure that secrets.py is in the .gitignore file
```

Added `secrets.py` to `.gitignore` for every folder. Two `secrets.py`
files were already tracked in git; see prompt 16.

**4. (While Claude was working)**

```text
please add an upload-code.sh program to this kit.  There are examples in other repo src/kit dirs
```

Wrote `upload-code.sh`, based on the robot-faces version. It uploads
`secrets.py` if present and never uploads the template.

**5. (While Claude was working)**

```text
This kit has 3 buttons  on GPIO 15, 14, and 13.  13 is the mode button an 14 and 15 change the setting up or down
```

Added the buttons to `config.py`, with the pin names the repo's other
clock kits use, and wrote the button test and set-time labs.

**6. (While Claude was working)**

```text
I quit Thonny
```

This freed the USB port, so Claude could reach the real Pico from here
on. It turned out to be a Pico 2 W running MicroPython 1.29.0, and Claude
measured its SPI speeds.

**7. (While Claude was working)**

```text
write a detailed 01-probe.py that checks the hardware status including RAM and flash size
```

Wrote the probe. The labs were renumbered so it could be lab 01. Claude
tested how to detect the flash chip's size on the real board before
writing it into the probe.

**8. (While Claude was working)**

```text
I have created a secrets.py for us to use
```

Claude checked that the file was ignored by git and used the expected
key names, without printing the values.

**9. (While Claude was working)**

```text
I see the Probe OK WOW!
```

The first confirmation on real hardware that the display works.

**10.**

```text
I am running Thonny now
```

Claude stopped using the USB port and listed the checks that were left
to do by eye.

**11.**

```text
the buttons all work
```

This came with Thonny's shell output pasted in:

```text
MODE pressed
MODE released
UP pressed
UP released
DOWN pressed
DOWN released
UP pressed
UP released
MODE pressed
MODE released
```

The buttons were confirmed on hardware.

**12.**

```text
When a program starts up, please print the program name and a version so can confirm I am running the right program
```

Every lab now prints `NAME vX.Y` as its first line. This was saved as a
standing preference for future sessions.

**13.**

```text
the set time works perfectly!  Nice job.
```

**14.**

```text
in lab 2 the red ring at the edge of the display is perfect
```

This confirmed `SAFE_RADIUS = 168`, so the comments stopped calling it
an estimate.

**15.**

```text
the color bars are red, green, blue, white (left to right)
```

The color order was confirmed, so no driver change was needed.

**16.**

```text
yes, untrack the secrets.py files in the GitHub repo
```

This answered Claude's question about the two already-tracked
`secrets.py` files, and it led to the first publish. → `d879e14b`
(untrack secrets) and `f1f91081` (the kit, labs 00–07).

### New watch faces (Sept 25)

**17.**

```text
Now I want you to create some new watch faces.  How about a digital clock face 08-digital-watch-face.py - make the main time digits large so they can be read across the room.  Add the date in the small font below the main time digits.  Make sure there is a minimum of flicker by only redrawing the pixels that change.
```

Built seven-segment digits from rectangles, repainting only the segments
that change. A normal second sends 333 pixels, and all 333 change.

**18.**

```text
The leftmost digit has the ability to display each of the 7 segments.  But it will only need the "1" or no segments lit.  The digits are hard to read because the corners and intersections are all black.  Please make them white.
```

Filled in the corners and joints so each digit is one solid shape, and
made the leftmost digit a half-width "1" with the row re-centered.

**19. (While Claude was working)**

```text
much nicer!
```

**20.**

```text
publish
```

→ `07056cf1` (the digital face, lab 08)

**21.**

```text
create another watch face 09-weather-clock.py that also gets the weather forecast.  Make the digits smaller and summarize the weather as high and low temp for today and for tomorrow.  Add icons for sunny, cloudy, partial clouds, and rain.  To do this find a web service that gives use the forecast.  The ../learning-micropython course has examples of the code to get the predicted lows and highs, but I don't know if it gets the sun/cloud/rain data.
```

Claude compared the course's OpenWeatherMap examples with Open-Meteo and
chose Open-Meteo: no API key, and 435 bytes per forecast. It added a
fifth icon, snow, for Minnesota winters, and drew the icons off-screen so
they never flicker.

**22.**

```text
The display is beautiful!
```

**23.**

```text
publish
```

→ `427f68d8` (the weather clock, lab 09)

### Stopwatch, timer, and one watch with five modes (Sept 25)

**24.**

```text
Do you have any other suggestions for watch faces?
```

Claude suggested eight ideas, including a stopwatch and timer, a mode
switcher, and a word clock. They were later saved in `ideas.md`.

**25.**

```text
I love the idea of a stopwatch and a timer.  I would like you to first create standalone versions of both stopwatch and countdown timer that are controlled by the tree buttons.
```

Built labs 10 and 11 on a new shared module, `lib/watchparts.py`. Both
use the same button pattern, and the timer is organized as a six-state
machine.

**26.**

```text
Stopwatch works great!
```

**27.**

```text
I love the lap timer!
```

**28.**

```text
add the fastest lap highlight and average
```

The fastest lap is shown in green, and a "Best" and "Avg" line appears
once there are two laps. The Best line keeps showing the fastest lap
after it scrolls off the list.

**29.**

```text
I am also testing the countdown timer now - works perfect!  But it reminds me I need to add a small speaker!
```

Claude gave advice on wiring: a passive piezo buzzer, or a small speaker
with an amplifier.

**30.**

```text
Yes, I have several max98357a-amps and I really love them and I have some great little speakers.  The sound quality is fantastic!  I also have some small piezo speakers that might be OK for this kit so that might be a project for later.
```

Claude pointed out that the MAX98357A needs I2S rather than a simple tone
pin, and proposed wiring on GP10–12 that avoids the buttons.

**31.**

```text
Let's put your ideas for the other clock in a file called ideas.md for the short term.  Now lets create a 12-main-template.py that will allow you to use the mode button to change the mode of the clock.  Make the default be the weather clock, but allow the user to change to an analog, digital, stopwatch, or timer.  To do this the samples modes should each be loaded when needed.  Also display a row of five dots at the bottom to indicate the current mode we are in.
```

Wrote `ideas.md`, five `mode_*.py` modules, and lab 12:
- Each mode is loaded only when it's shown, and fully unloaded after.
- A running stopwatch or timer keeps going in the background.
- Buttons now catch quick taps with an interrupt.

**32.**

```text
please commit and publish
```

→ `2c9270c0` (labs 10–12, the mode modules, `watchparts`, and `ideas.md`)

### Documentation (Sept 25)

**33.**

```text
Now let's work on the documentation for this beautiful kit.  Put the documentation in @docs/kits/sw-gc9b72/index.md - have separate files that describe each program from 00 to 12.  Make sure to use your display simulator generate tool to create actual images of the labs.  Assume your audience is a 6th grade student about 11 years old.
```

The `@docs/...` form is Claude Code's way of mentioning a file. This
produced a student home page, 13 lab pages, and a teacher-notes page,
with 26 images made by running each lab's real code in the simulator.

**34.**

```text
I placed an actual photo of the kit in @docs/kits/sw-gc9b72/large-smartwatch-clock.jpg
```

The photo leads the home page. Zooming into it showed that the notes had
the display's SCL and SDA pads in the wrong order, and that was
corrected.

**35.**

```text
publish
```

→ `d309eed5` (student documentation)

**36.**

```text
update the image metadata in the @docs/kits/sw-gc9b72/index.md so the social media preview works
```

Claude brought in the `social_override.py` hook from ibook-skills and
cropped the photo to 1200×630 for the preview image.

**37.**

```text
publish
```

→ `a34b5121` (social media preview)

### Logs and the simulator (Sept 25 and 27)

**38.**

```text
I am super happy with all this work.  Please create a detailed session log of all the design decisions you have made and write the session log to logs/sw-gc9b72-kit.md
```

**39.**

```text
commit and push
```

→ `bf793600` (the session log)

**40.**

```text
Please add the display simulator code to src/display-simulators/gc9b72 so it will not be uploaded by the upload-code.sh program.  Note that other projects that use the display should use this display simulator to generate documentation.
```

Turned the scratch simulator into a reusable package. It regenerates all
26 images identically and renders all 35 robot-faces labs. The rule that
GC9B72 projects use it was added to the global `~/.claude/CLAUDE.md`.

**41.**

```text
publish
```

→ `fea76200` (the display simulator)

(The next commit, `54a3e1ed` "Remove unused cursor rules file", was made
by hand, not from a prompt.)

**42.**

```text
Please create a new log file with an exact record of every prompt that I used to create this fantastic kit.  Add any information about how others could reproduce this if they didn't have the same context I had.  Put the prompts into logs/sw-gc9b72-kit-prompts.md
```

This file.

---

## Part 2: Reproducing This Without the Same Context

The prompts above are short because a lot of context was already in
place. Someone starting fresh needs to supply that context. Here is what
it was, and how to replace it.

### What the author had that the prompts don't mention

| Context | Why it mattered | How to supply it |
|---|---|---|
| **The hardware**, on a desk and plugged in | Claude reached the Pico over USB with `mpremote` to measure the board, upload code, and time drawing. The author checked what only eyes can: colors, the bezel edge, buttons. | Build the kit (see the wiring below). Without a board, use the simulator for pictures and logic, but some things still need real hardware. |
| **A tested GC9B72 driver** in the robot-faces and stem-robots repos | The GC9B72 has no public datasheet. Reusing a driver already brought up on hardware saved the hardest step. | Point Claude at `src/kits/sw-gc9b72/lib/gc9b72.py` in [robot-faces](https://github.com/dmccreary/robot-faces) or in this repo. |
| **This repo** (clocks-and-watches) | Claude followed its conventions: the button pin names, the MkDocs layout, the style of existing labs, and upload scripts from sibling repos. | Work inside a clone of [clocks-and-watches](https://github.com/dmccreary/clocks-and-watches), or describe your own conventions. |
| **learning-micropython** weather examples | Prompt 21 pointed to them. Claude chose a different service, Open-Meteo, anyway. | Not needed: tell Claude to use Open-Meteo (free, no API key). |
| **ibook-skills' `social_override.py`** | Prompt 36 relied on a hook the author had already written for another project. | It's now in this repo at `plugins/social_override.py`. |
| **A standing definition of "publish"** in `~/.claude/CLAUDE.md` | Every "publish" meant: stage the relevant files, commit with a "why" message, push, and `mkdocs gh-deploy`. | Add the same instruction to your own `CLAUDE.md` (text below), or spell the steps out each time. |
| **A WiFi network and `secrets.py`** | Needed for time sync and the forecast. | Copy `secrets-template.py` to `secrets.py`. |
| **A photo of the finished kit** | Used on the home page and for the social preview. | Take your own. |

### The hardware

| Part | Notes |
|---|---|
| Raspberry Pi Pico 2 W | Flash the `RPI_PICO2_W` MicroPython firmware (1.29 was used), not plain `RPI_PICO2`. |
| GC9B72 2.1" 360×360 round SPI display | Pads left to right: GND VCC SCL SDA RST DC CS BL SDO TE |
| 3 push buttons | Each from a pin to GND |

| Signal | Pico 2 W pin |
|---|---|
| Display SCL / SDA / RST / DC / CS / BL | GP2 / GP3 / GP4 / GP5 / GP6 / GP7 |
| Display VCC / GND | 3V3 (not 5 V) / GND |
| Buttons MODE / UP / DOWN | GP13 / GP14 / GP15 |

Tools: Thonny, and [`mpremote`](https://docs.micropython.org/en/latest/reference/mpremote.html)
(`pip install mpremote`). Quit Thonny before `mpremote` or
`upload-code.sh` can use the USB port.

### A context message to start with

Paste something like this as the first message, before prompt 1. Or put
it in the project's `CLAUDE.md`:

```text
Context for this project:
- Hardware: Raspberry Pi Pico 2 W (MicroPython 1.29, RPI_PICO2_W firmware) wired
  to a 2.1" 360x360 round GC9B72 SPI display: SCL GP2, SDA GP3, RST GP4, DC GP5,
  CS GP6, BL GP7, VCC 3V3. Three buttons to GND: MODE GP13, UP GP14, DOWN GP15.
- A hardware-tested MicroPython driver for the GC9B72 exists: reuse
  src/kits/sw-gc9b72/lib/gc9b72.py (with shapes.py and the vga1 fonts) from
  https://github.com/dmccreary/robot-faces unchanged. There is no public datasheet.
- The board is connected by USB; you may use mpremote to query it and upload code
  when I say Thonny is closed.
- Put the kit in src/kits/sw-gc9b72 with a config.py holding every pin number, and
  an upload-code.sh that copies lib/, config.py, secrets.py, and the labs.
- Every program must print its file name and version first, before any imports.
- Keep WiFi credentials in secrets.py, never commit it, and commit a
  secrets-template.py instead.
- When I say "publish": git add only the files that are part of the change, commit
  with a message explaining why, push, and run mkdocs gh-deploy.
```

### Prompts that need extra words without the author's context

Most prompts work as written once the context message is in place. These
depended on things only the author had:

| # | Original | Say this instead |
|---|---|---|
| 2 | `look in the ../stem-robots for examples` | Covered by the context message: the driver and wiring come from robot-faces. |
| 4 | "There are examples in other repo src/kit dirs" | "Base it on `src/kits/sw-gc9b72/upload-code.sh` in https://github.com/dmccreary/robot-faces." |
| 21 | "The ../learning-micropython course has examples…" | "Use the Open-Meteo daily forecast API (free, no key): `weather_code`, `temperature_2m_max`, and `temperature_2m_min` for 2 days." |
| 33 | "use your display simulator generate tool" | The simulator was built during this session and now exists: "Generate the images with `src/display-simulators/gc9b72` (see its README)." |
| 36 | "so the social media preview works" | "Use `plugins/social_override.py` (a MkDocs hook) with `image:` front matter and a 1200×630 image." |

Prompts 6, 8, and 10 tell Claude about the author's setup: Thonny open or
closed, and `secrets.py` created. Prompts 9, 11, 13–15, 19, 22, and 26–29
report what the real hardware showed. Without a board, replace those
reports by running the simulator's checks
(`python3 src/display-simulators/gc9b72/checks/run_all.py`) and looking
at the rendered images. Three things can only be checked on a real
board: the color order, where the bezel cuts off the glass, and the
button wiring.

### What to expect

- **The same prompts won't produce the same code.** Claude's choices vary
  from run to run. The session log records why each choice was made here,
  which is the best guide to steering a new run toward the same result.
- **Verification is part of the method.** Much of this kit's quality came
  from checking every change, on the real board where possible and in the
  simulator otherwise, before committing. Ask for checks the same way:
  "test it on the board", "compare against a fresh render", "make sure
  nothing overlaps".
- **Now that the kit exists,** the quickest route is simply to clone this
  repo and start from `src/kits/sw-gc9b72`. These prompts are most useful
  as a guide to building a *different* kit the same way.

### What worked well in these prompts

- **Short prompts with a clear goal and a clear standard.** "Large enough
  to read across the room" and "only redraw the pixels that change" gave
  Claude something to measure against.
- **Reporting what the hardware showed.** "The corners and intersections
  are all black" (prompt 18) led straight to a better design.
- **Interrupting mid-task.** Details like the button pins and the
  `.gitignore` rule arrived as soon as the author thought of them, and
  Claude folded them into the work in progress.
- **Asking for ideas** (prompt 24) before choosing the next feature.
- **Naming the audience.** "A 6th grade student about 11 years old"
  shaped every sentence of the documentation.
- **A one-word "publish"**, defined once in `CLAUDE.md`, made every commit
  consistent.
