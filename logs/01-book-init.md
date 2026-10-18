# Session Log 01: The Study Buddy Kit, Multicore Audio, and Taxonomy Changes

| | |
|---|---|
| **Dates** | 2026-10-03 to 2026-10-18 (work happened on 10-03, 10-04, 10-05, 10-06, and 10-18) |
| **Assistant** | Claude Sonnet 5.5, in Claude Code (desktop app) |
| **User** | Dan McCreary |
| **Repository** | `clocks-and-watches`, branch `main` |
| **Hardware** | Raspberry Pi Pico 2 W (RP2350), MicroPython 1.29.0 (2026-08-24), GC9B72 2.1" 360x360 round display, three buttons, MAX98357A I2S amplifier, 8 ohm 2 W speaker |
| **Result** | A new Study Buddy kit: a 7-page design spec, 8 labs that all run on the board, a sound module that plays from the Pico's second core, a measured analysis of dual-core audio, and two learning-graph changes |

This log records what was asked, what was decided, what was built, what was measured,
what went wrong, and what is still open. It is written to be read cold by someone who
did not see the session. Credentials and personal details are deliberately left out.

!!! note "Not everything in the repo from this period came from this session"
    Dan made two commits of his own during the window (`a81276a4`, 2026-10-06, and
    `c230558d`, 2026-10-13), and `src/kits/study-buddy/main-template.py` and the
    "One program, all the sound demos" section of that kit's README arrived in the
    second one. They were **not** written in this session and are listed under
    [Changes by others](#changes-by-others-during-the-window).

## 1. Summary

1. **Designed** the Study Buddy: the GC9B72 smartwatch kit plus a speaker, with study
   modes (quiz reminders, flash quizzes, daily quotes, study timer), downloadable modes
   and decks, and a Library used by both students and instructors.
2. **Wrote a 7-page specification** in `docs/kits/study-buddy/` (about 1,970 lines
   including the multicore guide) and added it to the site navigation.
3. **Brought up the hardware**: labs 01 (blink) and 02 (probe, with a new speaker
   section) ran on the real board, and the I2S pin rule was verified.
4. **Built `sound.py`**: a synthesizer that calculates sound on the Pico and feeds the
   amplifier from **core 1**, plus `sfx.py` (21 named effects).
5. **Wrote labs 03 to 08**: speaker test, hearing-range sweep, five waveforms, sound
   effects gallery, ringtones, button theremin. All six were run on the board by Dan and
   work.
6. **Measured dual-core audio** and wrote a detailed guide. Core 1 keeps the sound clean
   through display repaints, WiFi, and garbage collection. **Flash writes still make an
   audible glitch**, confirmed by ear.
7. **Identified the speaker**: no markings, so Dan measured 7.4 ohms with a multimeter,
   which makes it the 8 ohm, 2 W version.
8. **Changed the learning graph**: renamed the DISP taxonomy to "Display Graphics",
   added concept 351 "Display Shapes", kept "Round Display", and made Round Display
   depend on the existing "Clipping Region" concept (#290).
9. **Published** five times. The learning-graph changes are **not yet committed**.

## 2. Timeline

### Phase 1: Design (2026-10-03)

- **Request:** design a "Study Buddy" on the same hardware as `docs/kits/sw-gc9b72`,
  with a speaker added. The clock has fixed modes, but new modes can be downloaded.
  Example features: remind me of my next algebra quiz, quiz me on state capitals, give me
  encouraging quotes about education.
- Read the kit's index, lab 12 (the five-mode template), teacher notes, and lab 09; then
  the real code: `config.py`, `12-main-template.py`, `mode_timer.py`, the `lib/` helpers,
  and `ideas.md` (which already proposed a MAX98357A on GP10 to GP12).
- **Mid-turn correction from Dan:** "we can upgrade to the Pico 2 W with more memory".
  The kit already runs on a Pico 2 W (`config.py` and the teacher notes say so), so I
  said so, and explained that more memory would mean a PSRAM board, and that flash, not
  RAM, is what limits recorded audio.
- **Design delivered in chat:**
  - Two kinds of downloads: **packs** (data, safe, anyone can write) and **modes** (code,
    unsandboxed, teacher-published).
  - A Library mode that fetches a manifest with SHA-256 hashes.
  - The `modes.json` list replacing the hard-coded `MODES` tuple.
  - A reminder check on the **wall clock**, because `ticks_ms()` wraps after about 12
    days on this port.
  - Three speech levels: synthesized tones, composed phrases, recorded clips.
  - A flash budget: about 80 s of 16 kHz audio in the 2.5 MB filesystem.
- **Confirmed with Dan:** "yes, create a new dir in docs/kits/study-buddy and put the
  specs there".
- **Wrote the spec**: `index.md`, `01-architecture.md`, `02-features.md`,
  `03-pack-formats.md`, `04-audio.md`, `05-roadmap.md`. Added the nav entry in
  `mkdocs.yml`. Fixed a broken anchor found by `mkdocs build --strict`.
- **Decisions from Dan:**
  - "the code goes in a new src/kits/study-buddy folder"
  - "Both the students and the instructors use the library". This reshaped the Library
    design: plain-language screens, Browse and Installed tabs, a free-space display, a
    `LIBRARIES` list in `config.py` with a per-library `modes` flag, and a manifest
    script for the teacher.
- **Scaffolding:** created `src/kits/study-buddy/` with copies of `lib/`, `config.py`,
  `wifi_time.py`, `secrets-template.py`, and `upload-code.sh`. My first attempt to
  adapt those copies was interrupted by Dan and not retried until later.

### Phase 2: Hardware bring-up (2026-10-04)

- **Request:** Dan connected the new kit (a MAX98357A and speaker added to the watch
  hardware) and asked for labs 01 (blink the onboard LED) and 02 (a probe like the watch
  kit's). Pins: LRC GP21, BCLK GP20, DIN GP19, GAIN GP18. He asked me to check the rule
  that BCLK must be one pin below LRC.
- **Verified the pin rule** in the MicroPython docs ("The `ws` pin number must be one
  greater than the `sck` pin number"). Dan's wiring follows it.
- **Found GAIN usable from software** (Adafruit's page): floating 9 dB, GND 12 dB, VIN
  6 dB. Added `GAIN_DB` and `config.set_gain()`.
- **Wrote lab 01** (`01-blink-onboard-led.py`) and **lab 02** (`02-probe.py`), adapted
  from the watch kit's probe, with a new speaker section (pin rule, gain, I2S start,
  timing, three beeps). Moved the speaker section before the display section so a
  speaker warning reaches the "Probe OK" screen.
- **Board facts found:** Pico 2 W with RP2350 on MicroPython 1.29.0, 150 MHz, empty
  filesystem, 4 MB flash.
- Uploaded with `upload-code.sh` and ran both labs. The probe reported everything good,
  with one false alarm: Dan's WiFi network was visible but weak (about -72 dBm), and a
  single scan missed it. The probe now rescans twice before warning.
- **Dan confirmed by ear and eye:** "I hear it!!!" and "Screen is working great also!"
- **Renumbered the spec:** the kit has its own labs starting at 01, so the speaker test
  became lab 03 and everything after shifted.
- Updated the spec to the real pins (GP18 to GP21, not GP10 to GP12) and noted that GP8
  to GP12 stay free for an SD card on hardware SPI1.
- **Published (1 of 5):** commit `8479704f`. The first push was rejected because the
  remote had moved (a "Chrono Smart Clock Kit" rename and chapter content). Rebased
  without conflict, rebuilt, pushed, deployed. Excluded ten unrelated, already-dirty
  `docs/sims/*/metadata.json` files.

### Phase 3: `sound.py` and the core-1 design (2026-10-04 to 2026-10-05)

- **Request:** "start on Lab 03 sound.py - the kit has a VERY high quality speaker so add
  some fun labs that show the range of sound it can create".
- **Wrote `sound.py`:** a "viper" (compiled) synthesizer with sine, square, triangle,
  saw, and noise waves, glides, fades, a note queue, held notes, an I2S interrupt feed,
  and a headroom counter. Wrote `sfx.py` with 21 effects as plain data.
- **First on-board test:** Dan heard the scale clearly ("I heard the tone scale - very
  clear"). My test script then hung because of a bug: `busy()` never returned false,
  since every silent chunk reset `_audible_until`. Fixed by noting the moment sound goes
  quiet once.
- **Stress test, one core:** a 3 s tone through 21 full-screen fills (130 ms each) left
  252 of 256 ms in reserve, so drawing alone never needed a second core.
- **Dan's reminder:** "Recall there are two cores on this device that can both be running
  independantly". I agreed core 1 could keep audio alive through freezes that stall core
  0, and set out to test it.
- **The "wedged board" episode:** two test programs seemed to lock up the Pico, and I
  suspected a spinning core-1 thread starving core 0. The USB port stayed present but
  nothing answered, so I stopped and asked Dan to replug. Later I found the real cause
  ([section 8](#8-mistakes-corrections-and-surprises)): my own test used
  `sum(range(9_000_000))`, which takes **66 seconds** on MicroPython. The board was busy,
  not wedged.
- **Dan:** "publish everything to github - I will continue later - off to run a demo
  now" (**publish 1**, above), then "I replugged the Pico, now test whether core 1 runs in
  parallel".
- **Parallel test (bounded work, real timeout):** core 0 alone 1014 ms, core 1 alone
  1024 ms, both at once 1121 ms each. About 10% slower, not 2x, so true parallelism.
- **Added a core-1 mode to `sound.py`:** `init(core=1)` is the default; `core=0` keeps
  the older interrupt-callback version. Added a lock around the note queue.
- **Freeze test:** a 1.2 s freeze on core 0 made the core-0 version run dry (1 underrun,
  reserve -878 ms of 256), while the core-1 version stayed at 254 ms with no underrun.
- **Real-job test (core 1):** a 40 KB flash write, 20 garbage collections, and a 9.45 s
  WiFi connect plus NTP sync all showed 0 underruns.
- Updated the spec's audio page with the design, the measurements, and rules for modes.

### Phase 4: Labs 03 to 08 (2026-10-05)

- **Dan:** "go ahead with the Lab 03 program and the fun labs".
- Added `latency_ms()`, `rtttl_notes()`, and `tone(link=True)` to `sound.py`; the last
  stops a click at the joins of a sweep built from several notes.
- **Wrote six labs:**

  | Lab | File | What it does |
  |---|---|---|
  | 03 | `03-sound-test.py` | tones, a scale, named sounds, then the one-core-versus-two-cores experiment |
  | 04 | `04-hear-the-range.py` | 20 Hz to 20 kHz sweep; press UP when you first hear it and when it vanishes |
  | 05 | `05-waveforms.py` | five waves, drawn on the screen, with a short tune each |
  | 06 | `06-sound-effects.py` | gallery of 21 effects, each showing its recipe |
  | 07 | `07-ringtones.py` | four traditional tunes stored as RTTTL text |
  | 08 | `08-button-theremin.py` | hold UP or DOWN to slide the pitch; shows the nearest note and cents off |

- **Checked the screens without the board** by rendering each lab's real display code in
  the repo's GC9B72 simulator, with scripted button presses and a stand-in `sound`
  module (the simulator cannot run the real compiled synthesizer). Fixed text that was
  too wide for the circle, `random.uniform` (swapped for `getrandbits`, which every
  MicroPython build has), and stale state in labs 07 and 08.
- The board then dropped off USB, so the new labs could not be uploaded that day.
- Rewrote the roadmap: sound labs 03 to 08, study features from lab 09 on.

### Phase 5: Results and publishing (2026-10-06)

- **Dan ran lab 03:** "the sounds all worked great!"
- **Speaker identity:** Dan asked me to read the AliExpress listing in his Chrome. The
  listing sells both a 4 ohm 3 W and an 8 ohm 2 W speaker and does not say which was
  bought. I did not open his order page (it holds his address and payment details)
  without asking. Dan asked how to test a speaker with no markings; I gave a multimeter
  method and a Pico-and-resistor method. **Measured: 7.4 ohms, so the 8 ohm 2 W
  version.** Recorded in the spec.
- **Publish 2:** commit `7cbfed5b` (labs 03 to 08, core-1 audio, speaker).
- **Dan:** "In your analysis, does using both cores work? Does it help?" Answered from the
  numbers, with the limits: the counters measure supply, not sound.
- **Dan pasted lab 03's own output**, which matched my test scripts to within a few
  milliseconds. **Publish 3** (`d00a5fdd`) added that reproduction to the audio page.
- **Dan ran lab 04 three times** and shared the results (see
  [section 6](#6-measurements)). The low end contradicted the lab's claim that a small
  speaker is silent below a few hundred hertz. **Publish 4** (`73e5e710`) reworded the
  lab's text and the spec.
- **Dan confirmed labs 05, 06, 07, and 08 work.** **Publish 5** (`c6cc8c1a`) marked labs
  01 to 08 as run on the board.

### Phase 6: The multicore guide and stress test (2026-10-06)

- **Request:** a detailed "Guide to Multicore Processing on the Study Buddy" with an
  analysis of the findings, stressing that display, WiFi, and sound must all work
  smoothly together, plus an explanation of how I2S works and the hope that the PIO can
  offload moving sound to the speaker.
- **Read the MicroPython v1.29.0 source** for the facts the guide needed
  ([section 7](#7-source-facts-read-from-micropython-v1290)). Two findings changed what
  I had told Dan: flash writes disable interrupts and pause core 1 while the I2S driver
  depends on an interrupt about every 2 ms, and the core-1 loop's `write()` busy-waits
  instead of sleeping.
- **Wrote `06-multicore-guide.md`** (about 725 lines): the three workloads and their
  deadlines, the hardware, how I2S works with a frame diagram, how MicroPython moves
  sound through ring buffer, interrupt, DMA, and PIO, every measurement, rules for a
  program that does all three, and ten experiments.
- **Wrote `multicore-stress-test.py`:** a steady tone on core 1 while core 0 does one
  kind of load per phase, then the board asks the listener to press UP for "heard a
  click or gap" or DOWN for "clean". Also a speed phase.
- **Corrected earlier docs and comments** that said `write()` sleeps and that a flash
  write was safe.
- **Dan ran the stress test.** Phases 0 to 5 (baseline, repaints, WiFi scans, connect,
  web request, garbage collection) were clean. **Phases 6 to 8 (all the flash writes)
  were audible.** In those phases the ring buffer never ran dry (low points 168, 56, and
  27 ms), so the glitch came after the ring, at the interrupt-fed DMA buffer, as the
  source predicted.
- Updated the guide with the results, the cost to core 0 (about 6 to 10%), and a new
  experiment E10 (does a flash write during silence pop?), and added a silent-write
  phase to the script.

### Phase 7: Learning-graph changes (2026-10-18)

- **Request 1:** rename the taxonomy "Round Display Graphics" to "Display Graphics"
  because students may swap in a square display.
  - The exact phrase did not exist anywhere (working tree, all branches, remote). I
    asked rather than guessed. **Dan chose to rename the DISP category** ("Displays and
    Drawing", 66 concepts).
  - Changed five files: `taxonomy-names.json`, `learning-graph.json`,
    `concept-taxonomy.md`, `taxonomy-distribution.md` (including the bar chart
    padding), and `taxonomy-mapping.py`.
- **Request 2:** add "Display Shapes" as an independent concept, and keep "Round Display"
  because round displays have their own clipping rules.
  - Added **concept 351, "Display Shapes"**, depending on Display Resolution (279) and
    Display Coordinates (288). Round Display (162) was left unchanged at this point.
  - The committed JSON has a `cis` (Concept Impact Score) per node that the repo's
    `csv-to-json.py` (v0.03) does not produce, so regenerating would have dropped it.
    I verified my own calculation reproduces all 350 committed scores, then added the
    node and two edges and recomputed the scores (20 existing concepts changed by a few
    points each).
  - Regenerated `quality-metrics.md` and `taxonomy-distribution.md` with the project's
    scripts (a baseline run showed they reproduce the committed files exactly). The
    graph is still a valid DAG: 0 cycles, 0 orphans, terminal nodes 35.0%.
- **Request 3 (sent while this log was being written):** also link Round Display to the
  existing Clipping Region concept (#290).
  - Changed Round Display's row from `153|279` to `153|279|290`, so it now **depends on**
    Clipping Region. This puts the clipping rules that round displays need into the graph.
  - Checked first that it cannot make a cycle: none of Clipping Region's 24 prerequisites
    is Round Display, and nothing depended on Clipping Region before.
  - Added the edge to `learning-graph.json` in its CSV position and recomputed every
    `cis` score (25 concepts changed; Clipping Region went from 1 to 10, Round Display
    stayed at 9). Regenerated `quality-metrics.md`.
  - **Side effect:** the longest dependency chain grew from 14 to 16, because Round
    Display now sits on the path Ohms Law, Voltage Levels, LED Basics, LED Display,
    Display Resolution, OLED Display, Framebuffer, Pixel Drawing, Line Drawing, Rectangle
    Drawing, Bounding Box, Clipping Region, Round Display, GC9A01 Driver, Smartwatch
    Display, Watch Band Integration. The report flags it as informational ("ensure
    students can follow extended learning paths"). The graph is still a valid DAG with
    0 cycles and 0 orphans, and terminal nodes are 34.8%.

## 3. Decisions

| # | Decision | Who | Date |
|---|---|---|---|
| 1 | The Study Buddy is the GC9B72 watch hardware plus a MAX98357A speaker; it reuses the five-mode template | Dan, via the request | 10-03 |
| 2 | Docs go in `docs/kits/study-buddy/` | Dan | 10-03 |
| 3 | Code goes in a new `src/kits/study-buddy/` folder, self-contained like the other kits | Dan | 10-03 |
| 4 | Students and instructors both use the Library | Dan | 10-03 |
| 5 | Packs (data) can be written by anyone; modes (code) are teacher-published; the `modes` flag on each library can hide code downloads | Claude, then Dan's decision 4 | 10-03 |
| 6 | Reminders compare the wall clock, never `ticks_ms()` | Claude | 10-03 |
| 7 | Speaker on GP18 to GP21 (LRC 21, BCLK 20, DIN 19, GAIN 18) | Dan | 10-04 |
| 8 | The Study Buddy has its own lab numbers: 01 blink, 02 probe, 03 to 08 sound | Dan, via the request | 10-04 |
| 9 | Sound plays from core 1 by default; `core=0` stays available | Claude, after Dan's two-cores reminder | 10-05 |
| 10 | The speaker is the 8 ohm 2 W version | Dan, by measurement (7.4 ohms) | 10-06 |
| 11 | Reword lab 04's bass and hearing claims, and record its results anonymously | Dan | 10-06 |
| 12 | No mode may write files while a sound plays | Claude, after the stress test | 10-06 |
| 13 | Rename the DISP category to "Display Graphics" | Dan | 10-18 |
| 14 | Add "Display Shapes" as concept 351; keep "Round Display" | Dan | 10-18 |
| 15 | Round Display depends on Clipping Region (#290) | Dan | 10-18 |
| 16 | Leave unrelated dirty files (ten `docs/sims/*/metadata.json`) out of every commit | Claude, repeated each publish | 10-04 on |

## 4. Files

### Created in this session

| Path | Lines | Purpose |
|---|---|---|
| `docs/kits/study-buddy/index.md` | 163 | overview, parts, speaker, wiring, pin rule |
| `docs/kits/study-buddy/01-architecture.md` | 241 | modes, packs, Library, template changes |
| `docs/kits/study-buddy/02-features.md` | 262 | each feature's screens, buttons, behavior |
| `docs/kits/study-buddy/03-pack-formats.md` | 190 | JSON formats for decks, quotes, events, manifest, progress |
| `docs/kits/study-buddy/04-audio.md` | 227 | the sound module, speech levels, flash budget, core-1 design and measurements |
| `docs/kits/study-buddy/05-roadmap.md` | 159 | labs 01 to 15, risks, decisions, open questions |
| `docs/kits/study-buddy/06-multicore-guide.md` | 725 | the multicore guide |
| `docs/kits/study-buddy/img/speaker-on-aliexpress.png` | | Dan's screenshot of the speaker listing |
| `src/kits/study-buddy/01-blink-onboard-led.py` | 24 | lab 01 |
| `src/kits/study-buddy/02-probe.py` | 491 | lab 02 |
| `src/kits/study-buddy/03-sound-test.py` | 214 | lab 03 |
| `src/kits/study-buddy/04-hear-the-range.py` | 220 | lab 04 |
| `src/kits/study-buddy/05-waveforms.py` | 160 | lab 05 |
| `src/kits/study-buddy/06-sound-effects.py` | 119 | lab 06 |
| `src/kits/study-buddy/07-ringtones.py` | 154 | lab 07 |
| `src/kits/study-buddy/08-button-theremin.py` | 165 | lab 08 |
| `src/kits/study-buddy/sound.py` | 611 | the sound module |
| `src/kits/study-buddy/sfx.py` | 90 | 21 named sound effects |
| `src/kits/study-buddy/multicore-stress-test.py` | 289 | the by-ear stress test |
| `src/kits/study-buddy/README.md` | 93 | kit overview (a section was added later by someone else) |

### Copied from `sw-gc9b72` and adapted

`config.py` (I2S pins, gain, volume, `set_gain()`), `upload-code.sh`,
`secrets-template.py`, `wifi_time.py`, and `lib/` (driver, fonts, shapes, `watchparts.py`).
`lib/` and `wifi_time.py` are copies, so a fix in one kit must be repeated in the other.

### Modified outside the kit

| Path | Change |
|---|---|
| `mkdocs.yml` | "Study Buddy (Spec)" nav section, later with the multicore guide |
| `docs/learning-graph/` (8 files) | the rename and concept 351 (see phase 7) |

### Not committed yet

The eight learning-graph files: `concept-list.md`, `concept-taxonomy.md`,
`learning-graph.csv`, `learning-graph.json`, `quality-metrics.md`,
`taxonomy-distribution.md`, `taxonomy-mapping.py`, `taxonomy-names.json`.

### Changes by others during the window

| Commit | Author | Date | What |
|---|---|---|---|
| `a81276a4` "updating content" | Dan | 10-06 | swept in my uncommitted multicore guide, stress script, and related edits (7 files) |
| `c230558d` "Added the new skill that generates 30-second promo videos" | Dan | 10-13 | also added `src/kits/study-buddy/main-template.py` (744 lines, labs 04 to 08 as five demos in one program) and the README section describing it |
| `aa5b0a91`, `c4f1d68a`, `c749c9c5`, `ed647668` | Dan | 10-06 to 10-13 | a merge with the new Knob Clock kit, a rect-tft kit, a license badge fix, and a skill link; unrelated to this work |

## 5. Hardware and configuration

| Item | Value |
|---|---|
| Board | Raspberry Pi Pico 2 W, RP2350, MicroPython 1.29.0, 150 MHz |
| Heap | 436 KB total, 419 KB free after the probe loaded |
| Flash | 4 MB chip, 2.5 MB filesystem, 2.4 MB free with the kit on it |
| Display | GC9B72 on SPI0: SCL GP2, SDA GP3, RST GP4, DC GP5, CS GP6, BL GP7 |
| Buttons | MODE GP13, UP GP14, DOWN GP15 |
| Amplifier | LRC GP21, BCLK GP20, DIN GP19, GAIN GP18 (software-selectable 6, 9, or 12 dB) |
| Speaker | 3525/2535 size, 8 ohm 2 W (7.4 ohms measured), no markings |
| Sound defaults | `rate=16000`, `ibuf=8192` (256 ms reserve), `VOLUME=40`, `GAIN_DB=9` |
| USB port | `/dev/cu.usbmodem14301`, later `/dev/cu.usbmodem14201` (macOS renames it per jack) |

**The I2S pin rule:** LRC must be the pin right after BCLK. MicroPython drives both from a
single PIO instruction using "side-set", which needs adjacent pins, and its code raises an
error if `ws != sck + 1`.

## 6. Measurements

All on the real kit unless noted.

### Probe (lab 02, 2026-10-04)

| Check | Result |
|---|---|
| I2S timing | 0.76 s of audio accepted in 0.63 s, as a 16 kHz clock should give |
| Display | four color bars shown, full-screen fill 130 ms |
| WiFi | visible but weak, about -72 dBm; one scan sometimes misses it |

### Do the cores run in parallel?

| | Time for 150,000 steps |
|---|---|
| core 0 alone | 1014 ms |
| core 1 alone | 1024 ms |
| both at once | 1121 ms each (about 10% slower) |

### A freeze on core 0 (a steady tone plays; core 0 sits in `max(range(1_000_000))`)

| Audio fed by | Core 0 frozen | Underruns | Reserve at its lowest | Longest wait |
|---|---|---|---|---|
| core 0 (interrupt callback) | 1163 ms | 1 | -878 ms | 1192 ms |
| core 1 (thread) | 1284 ms | 0 | 254 of 256 ms | 64 ms |
| lab 03, core 0 | 1164 ms | 1 | -867 ms | 1182 ms |
| lab 03, core 1 | 1284 ms | 0 | 254 ms | 64 ms |

### Drawing

21 full-screen fills with core-0 audio left 252 ms of 256; lab 03 ran 17 fills with core-1
audio and also left 252 ms. No underruns either way.

### Stress test by ear (2026-10-06)

| # | Phase | Took | Reserve at its lowest | Heard a problem? |
|---|---|---|---|---|
| 0 | baseline | 3000 ms | 254 ms | no |
| 1 | 23 repaints | 3017 ms | 254 ms | no |
| 2 | three WiFi scans | 3200 ms | 254 ms | no |
| 3 | WiFi connect and time sync | 5783 ms | 254 ms | no |
| 4 | web request | 5658 ms | 254 ms | no |
| 5 | 20 garbage collections | 188 ms | 245 ms | no |
| 6 | 5 small flash writes | 2745 ms | 168 ms | **yes** |
| 7 | one 200 KB flash write | 695 ms | 56 ms | **yes** |
| 8 | everything in turn | 5830 ms | 27 ms | **yes** |

Underruns were 0 in every phase.

### Cost of the sound to core 0 (same 150,000-step loop)

| Audio state | Time | Slower by |
|---|---|---|
| none | 1040 ms | |
| audio loop, silence | 1107 ms | 6.4% |
| 16 kHz tone | 1114 ms | 7.1% |
| 44.1 kHz tone | 1142 ms | 9.8% |

Single run; differences of about a percent are noise.

### Hearing range (lab 04, three sweeps by one adult tester, volume capped at 30)

| Run | First heard | Stopped hearing |
|---|---|---|
| 1 | 73 Hz | 11,068 Hz |
| 2 | 107 Hz | 11,122 Hz |
| 3 | 57 Hz | 10,171 Hz |

The high end was steady (about 10 to 11 kHz). The low end was a surprise: a speaker this
small should make little true bass, so what was heard from 57 to 107 Hz is probably
distortion or buzz.

### Speaker resistance

7.4 ohms by multimeter (a 4 ohm speaker reads about 3 to 3.5, an 8 ohm one about 6 to 7.5).

## 7. Source facts read from MicroPython v1.29.0

I read these through a tool that fetches a file and answers questions about it, so they
are summaries, not line-by-line reads. Names are worth confirming in the files before a
design decision rests on one detail.

| File | Fact |
|---|---|
| `ports/rp2/machine_i2s.c` | PIO programs of 8 instructions; side-set pins must be sequential; `ws != sck + 1` raises an error; PIO clock is `rate x 2 x bits x 2`; two chained DMA channels over a 256-byte buffer in two 128-byte halves; a DMA interrupt (`dma_irq_handler`, `feed_dma()`) refills them from the ring buffer; underrun fills with zeros; mono is duplicated into both slots |
| `extmod/machine_i2s.c` | blocking `write()` busy-waits in C with no timeout or scheduler call; the non-blocking callback is scheduled with `mp_sched_schedule()`; the ring buffer is single-producer, single-consumer |
| `ports/rp2/mpthreadport.c` | core 1 starts through `multicore_launch_core1_with_stack`; default stack 4096 bytes; a recursive mutex guards atomic sections while core 1 is active; core 1 is registered as a lockout victim |
| `ports/rp2/mpconfigport.h` | `MICROPY_PY_THREAD_GIL (0)`, so there is no interpreter lock |
| `ports/rp2/rp2_flash.c` | every erase and program runs under `begin_critical_flash_section()`: the other core is paused and interrupts are disabled |
| `ports/rp2/machine_spi.c` | writes of 32 bytes or more use DMA and wait for it to finish; shorter writes call the SDK's blocking write; no scheduler call during the wait |

Other sources: the MicroPython docs (I2S pin rule), and Adafruit's MAX98357A page (GAIN
and SD pins).

## 8. Mistakes, corrections, and surprises

| # | What happened | How it was caught | Fix |
|---|---|---|---|
| 1 | Stray thinking-out-loud text was left in the architecture page, in a paragraph about Library tabs | Reading the file back | Rewrote the paragraph |
| 2 | `sound.busy()` never returned false, so `wait()` hung | A test timed out | Note the moment sound goes quiet once, instead of on every silent chunk |
| 3 | I used `sum(range(9_000_000))` to keep core 0 busy. It takes **66 seconds** because the total outgrows small integers and every addition allocates. The board looked dead, I killed my tool, and I wrongly suspected a spinning second core had starved the first | A calibration run showed the 66 s | Used `max(range(1_000_000))` (about 1.2 s, no allocation); retracted the theory |
| 4 | I wrote that the core-1 loop "sleeps inside `write()`". It busy-waits | Reading `extmod/machine_i2s.c` | Fixed the `sound.py` comment, the audio page, and the guide |
| 5 | I wrote that the ring buffer protects the sound through a flash write, and then that the counters "cannot see" a flash glitch | The source read, then Dan's by-ear result | The guide now says: confirmed audible; the counters did see core 1 pause (reserve fell to 27 to 168 ms) but not the interrupt starvation |
| 6 | Lab 04's text said a speaker this small is silent below a few hundred hertz | Dan heard something from 57 Hz | Reworded to say small speakers mostly buzz down low |
| 7 | A security-scan `grep` used a `*.py` pattern that also matched Dan's gitignored `secrets.py`, printing his WiFi name and password into the session | Seeing the output | Told Dan at once and recommended changing the router password. It was never staged or committed |
| 8 | The probe falsely reported Dan's WiFi network as missing | A repeat scan showed it at -72 dBm | The probe rescans twice before warning |
| 9 | A test harness quirk: code run through `mpremote run` executes in a separate namespace, so a thread's global lookups failed | A `NameError` | Shared state through a closure |
| 10 | macOS has no `timeout` command, and an unmatched zsh glob aborted a command chain | A command-not-found error and a chain that silently did nothing | Used `python3` subprocess timeouts and avoided unmatched globs |
| 11 | The display simulator's fake clock does not advance while drawing, so a "repaint for 2.2 s" loop ran thousands of slow fills | A run that never finished | Limited that loop in the scratch copy only |
| 12 | "Round Display Graphics" did not exist anywhere | A search of the tree, history, and remote | Asked Dan instead of guessing |

Surprises worth remembering:

- **The MicroPython I2S refill is interrupt-driven with a 2 ms deadline** (0.73 ms at
  44.1 kHz), so the 256 ms ring buffer is not what protects the last step to the hardware.
- **The cores really run in parallel** (no interpreter lock), at about a 10% cost when both
  are busy.
- **Drawing never needed a second core.** The display driver makes many short writes, and
  the scheduler runs between them.
- **The board changes its USB port name** each time it moves to another jack.

## 9. Verification used

- `mkdocs build --strict` into a scratch folder after every docs change. The only
  warning seen was a pre-existing `license.md` image link, which was fixed upstream on
  its own (commit `c749c9c5`). `mkdocs serve` was never started.
- `python3 -m py_compile` on every Python file written.
- The GC9B72 simulator, for the screens of labs 03 to 08.
- Real runs on the board, always bounded and under a hard timeout.
- A baseline check before regenerating learning-graph files, to be sure the scripts
  reproduce what is committed.
- Dan's own runs and ears, which were the only test of sound quality.

## 10. Publishing

| # | Commit | Date | What | `gh-pages` |
|---|---|---|---|---|
| 1 | `8479704f` (rebased from `9295800b`) | 10-04 | the spec, labs 01 and 02, `sound.py`, `sfx.py` | `32780d0e` |
| 2 | `7cbfed5b` | 10-06 | labs 03 to 08, core-1 audio, speaker | `c6a26df8` |
| 3 | `d00a5fdd` | 10-06 | lab 03's on-board reproduction | `856bc0ff` |
| 4 | `73e5e710` | 10-06 | lab 04 rewording and results | `528598a6` |
| 5 | `c6cc8c1a` | 10-06 | labs 01 to 08 marked as run | `e712345b` |

Each publish followed Dan's `CLAUDE.md` routine: add the files, commit, push, then
`mkdocs gh-deploy`. Every commit ended with the Claude co-author line. The ten dirty
`docs/sims/*/metadata.json` files were left out each time.

## 11. Tools and methods

- **Shell:** `mpremote` for the board, Python for scripts, `git`, and a conda `mkdocs`
  environment.
- **Web:** `WebFetch` for the MicroPython docs and source and Adafruit's page, and Claude
  in Chrome (a new tab, closed afterward) for the AliExpress listing. No order pages were
  opened.
- **Questions:** `AskUserQuestion` once, when the taxonomy name did not exist.
- **Simulator:** `src/display-simulators/gc9b72` for screen checks.
- **Standing rules followed:** no `mkdocs serve`, no git worktrees, scratch files in the
  session scratchpad, no `navigation.tabs`, instructor-facing docs without the mascot.

## 12. Open items

| Item | Notes |
|---|---|
| **Commit and publish the learning-graph changes** | Eight files, uncommitted. Dan has not yet said to publish them |
| **E10: does a flash write during silence pop?** | Added as phase 9 of the stress script; not run. Decides whether "no writes while a sound plays" is enough |
| **Fix the flash glitch itself** | Ideas A to E in the guide: our own I2S with a large DMA ring (the real fix), I2S on core 1, a paced producer, DMA for the display's SPI wait, and a PIO state machine that times the WS edges as a meter |
| **E5** | Animate the display during a web fetch and watch for stalls |
| **Was the core-0 gap in lab 03 audible?** | The counters show it; Dan has not said whether he heard it |
| **Labs 09 to 15** | Study Timer, Quote of the Day, Flash Quiz, a deck of your own, Next Quiz, the Library, events from a phone |
| **Features not built** | `modes.json`, `LIBRARIES` in `config.py`, the reminder service, packs, the Library, the manifest script |
| **`main-template.py`** | Added by Dan on 10-13; the spec does not mention it yet |
| **Spec items marked "verify"** | the PSRAM board, 5 V amplifier power next to WiFi, TLS to GitHub Pages, mDNS, a long flash write |
| **Possible lab** | "Measure your speaker with the Pico" using a 100 ohm resistor; offered, not built |
| **The `lib/` and `wifi_time.py` copies** | A later cleanup to a shared library if they drift |

## 13. User prompts, in order

Verbatim, with two edits: a personal detail Dan shared about himself is omitted, and a URL's
tracking query string is dropped. Pasted program output is described, not repeated (the
numbers are in [section 6](#6-measurements)).

1. Help me design a "Study Buddy" using the same hardware as this clock: @docs/kits/sw-gc9b72 but with a speaker added. The clock has specific modes, but new modes can be downloaded. Suggest features like "Remind me when my next algebra quiz is" - "Help quiz me on state capitols" and "Give Me encouraging and inspirational quotes about education"
2. *(sent mid-turn)* Also note that we can upgrade to the Pico 2 W with more memory
3. yes, create a new dir in docs/kits/study-buddy and put the specs there
4. the code goes in a new src/kits/study-buddy folder
5. Both the students and the instructors use the library
6. I now have a new "Study Buddy" hardware kit I have connected to the USB port. Please create a new source dir at src/kits/study-buddy and populate it with some initial setup configuration files. Make lab 01 be a blink the onboard LED and 02 be a probe like the @src/kits/sw-gc9b72 kit. The display has the same pins and the mode buttons also are the same pins, but I have added a MAX98357A connected to a speaker for generating sound. The pins are on GPIO 18, 19, 20 and 21. From the top row on the breadboard to the MAX98357A I have the following connections: GPIO 21 = LRC, GPIO 20 = BCLK, GPIO 19 = DIN, GPIO 18 = GAIN. Check that there is a rule that the BCLK must be on the GPIO pin that is one less than the LRC pin.
7. *(sent mid-turn)* I added the secrets.py and put in the information for my house
8. *(sent mid-turn)* I hear it!!!
9. *(sent mid-turn)* Screen is working great also!
10. yes, start on Lab 03 sound.py - the kit has a VERY high quality speaker so add some fun labs that show the range of sound it can create
11. The speaker's description from AliExpress is here: @docs/kits/study-buddy/img/speaker-on-aliexpress.png
12. *(sent mid-turn)* I heard the tone scale - very clear
13. Recall there are two cores on this device that can both be running independantly
14. publish everything to github - I will continue later - off to run a demo now
15. I replugged the Pico, now test whether core 1 runs in parallel
16. go ahead with the Lab 03 program and the fun labs
17. I ran the 03-sound-test.py and the sounds all worked great!
18. I do not know if the speaker is 4 or 8 ohms. Here is the description on AliExpress of the speakers that I purchased (open in Chrome) https://www.aliexpress.us/item/3256807204066808.html *(query string dropped)*
19. how can I test the speaker? There are no markings on the front or back.
20. I tested the speaker resistance with a multimeter and I got 7.4 ohms
21. publish everything now
22. In your analysis, does using both cores work? Does it help?
23. *(pasted: the output of lab 03 on the board)*
24. yes, add it to the audio page and publish
25. Here are the results of what range I can hear. *(personal detail omitted)* *(pasted: three sweeps of lab 04)*
26. yes, soften the text and update the roadmap, then publish
27. waveforms works as expected
28. All the sound effect work
29. ringtones work fine
30. theremin works too, publish everything
31. please create a detailed guide called "Guide to Multicore Processing on the Study Buddy" and give a detailed analysis of your findings. Note that it is critical that the display, wifi and sound all work smoothly with each other. Describe how the I2S bus works and how the hope is that the PIO circuits can be used to offload tasks like moving sound to the speaker.
32. *(pasted: the output of the stress test)*
33. Please change the taxonomy "Round Display Graphics" to just be "Display Graphics" since the students might want to swap in a square display also
34. *(answer to a question)* Rename the DISP category
35. Add the "Display Shapes" as an independent concept but also keep the "Round Display" as a concept since there are specific clipping rules associated with round displays
36. first create a detailed session log of this session and put it in logs/01-book-init.md
37. *(sent mid-turn, while the log was being written)* also link Round Display to the existing Clipping Region concept (#290).
