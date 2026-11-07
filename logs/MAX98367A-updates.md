# MAX98357A SD and GAIN Pins Session Log

**Date:** 2026-10-31
**Task:** Explain the MAX98357A's SD pin and why some designs wire it to
3.3 V, add that to the Study Buddy audio chapter checked against the real
datasheet, summarize why examples wire GAIN to GND, and fix the
sample-rate problems the datasheet check turned up.
**Part:** MAX98357A I2S Class D amplifier, on an Adafruit-style breakout,
driving the Study Buddy kit's speaker
**Commit:** [`2e9e6ac0`](https://github.com/dmccreary/clocks-and-watches/commit/2e9e6ac0),
pushed to `main`, site deployed to `gh-pages`

(The file name keeps the original spelling of the part number. The part is
the MAX98357A.)

## Results

| Metric | Value |
|---|---|
| Files changed | 6 (3 docs pages, 3 Python files) |
| Lines | 207 added, 19 removed |
| Commits | 1, pushed and deployed |
| New doc section | "The Amplifier's SD and GAIN Pins" in `04-audio.md`, 6 subsections |
| Strict site build (`mkdocs build --strict`) | passed after each round of edits |
| Python syntax check (`ast.parse`) | passed for all 3 changed files |

**Hardware status:** nothing in this session was tried on the real board.
The SD and GAIN section comes from the datasheet and Adafruit's page. The
change from 22,050 Hz to 16,000 Hz in the theremin mode and Lab 08 has been
parsed but not heard.

## Sources

- MAX98357A/MAX98357B datasheet, Rev 13, 7/19, document 19-6779. Read from a
  third-party copy of that revision, because analog.com did not respond from
  the session. The chapter cites it by revision and number and has no
  hyperlink to it, to avoid a dead link.
- [Adafruit MAX98357 pinout page](https://learn.adafruit.com/adafruit-max98357-i2s-class-d-mono-amp/pinouts)
  for the breakout's 1 MΩ SD pull-up.
- [MicroPython `machine.I2S` docs](https://docs.micropython.org/en/latest/library/machine.I2S.html)
  for "MONO writes each sample to both channels".

## What the datasheet says

**SD (`SD_MODE`).** One pin does shutdown and channel select, read as a
voltage. There is a 100 kΩ (±8%) pulldown inside the chip, so a bare
floating pin means shutdown.

| SD voltage | Amplifier | Trip point (min / typical / max) |
|---|---|---|
| Below B0 | Shutdown | B0: 0.08 / 0.16 / 0.355 V |
| B0 to B1 | (Left + Right) / 2 | B1: 0.65 / 0.77 / 0.825 V |
| B1 to B2 | Right | B2: 1.245 / 1.4 / 1.5 V |
| Above B2 | Left | |

Pull-up resistors for the right channel and the mix, from Table 6 at 3.3 V
logic: 210.2 kΩ and 634 kΩ (formulas: R_SMALL = 94.0 × VDDIO − 100 kΩ,
R_LARGE = 222.2 × VDDIO − 100 kΩ). SD must stay below VDD + 0.3 V. If VDD
can drop under 3.0 V while SD is driven from 3.3 V, add about 2 kΩ in series.

**Power and timing (25 °C, no speaker).**

| State | Typical supply current |
|---|---|
| Running, clocks on | 2.75 mA at 5 V, 2.4 mA at 3.7 V |
| Standby (SD high, BCLK stopped; automatic) | 340 µA |
| Shutdown (SD low) | 0.6 µA (2 µA max) |

Turn-on time is 7 ms typical, 7.5 ms maximum. The order of SD and the clocks
does not change the click-and-pop level, but there is no volume ramp-down
into shutdown, so end a sound with a fade first.

**GAIN (`GAIN_SLOT`).** Wired to GND through 100 kΩ: 15 dB. GND: **12 dB**.
Open: 9 dB. VIN: 6 dB. VIN through 100 kΩ: 3 dB. The trip points are
fractions of VDD. Full-scale digital output is 2.1 dBV. The output-power
rating (3.2 W into 4 Ω at 5 V, 10% distortion) and the typical curves are
specified at 12 dB, and the datasheet's own circuit and layout examples use
12 dB. That is why examples tie GAIN to GND.

**Sample rates.** LRCLK supports only 8, 16, 32, 44.1, 48, 88.2, and 96 kHz.
11.025, 12, 22.05, and 24 kHz are **not supported**. At 8 kHz the bit clock
is 256 kHz, a special case that requires the clocks to start after the
amplifier is enabled, a 10 µs wait after SD goes high, and **SD low before
the clocks stop**.

## Corrections made along the way

- My first answer said a tied-high SD "never sleeps" and idles at about
  2.4 mA. The datasheet says the chip drops to standby (340 µA) by itself
  when BCLK stops. The 2.4 mA figure applies only while clocks keep running.
  The chapter has the corrected table.
- The thresholds I gave from memory (0.16, 0.77, 1.4 V) were right. The
  chapter now adds the per-chip tolerances.
- A thin margin turned up that I had not mentioned. On a 3.3 V board the
  breakout's 1 MΩ pull-up holds SD at about 0.30 V, while the datasheet
  allows the shutdown edge as high as 0.355 V. A typical chip is fine, but
  this is marked "verify on the bench" in the chapter. It is arithmetic, not
  an observed failure.
- The chapter recommended 11.025 kHz clips. That rate is unsupported, so the
  advice was replaced with 16 kHz and 8 kHz.

## Files Changed

- [`docs/kits/study-buddy/04-audio.md`](../docs/kits/study-buddy/04-audio.md):
  - new section "The Amplifier's SD and GAIN Pins": what SD does, why a
    breakout works with SD unconnected, three ways to wire SD, why designs
    tie SD to 3.3 V, what shutdown saves, driving SD from a GPIO (with a
    code example using GP17, not yet in `config.py`), a warning that 8 kHz
    audio needs SD under software control, and why examples tie GAIN to GND
    (with a rough clipping estimate)
  - Flash Budget: removed the 11.025 kHz row, added a note on supported
    rates, new sizes (Spanish deck 1.6 MB at 16 kHz or 0.8 MB at 8 kHz),
    and "Record at 8 kHz instead of 16 kHz" with its SD-on-a-GPIO caveat
  - Level 2 size estimate, the WAV note (converter writes 16 or 8 kHz and
    the player checks the rate), a new "Still to measure" item on the
    theremin, and a pointer from the click item to the new section
- [`docs/kits/study-buddy/index.md`](../docs/kits/study-buddy/index.md): the
  "Leave SD unconnected" line now links to the new section.
- [`docs/kits/study-buddy/05-roadmap.md`](../docs/kits/study-buddy/05-roadmap.md):
  the flash-space mitigation says "8 kHz clips first" and why.
- [`src/kits/study-buddy/main-template.py`](../src/kits/study-buddy/main-template.py)
  and [`08-button-theremin.py`](../src/kits/study-buddy/08-button-theremin.py):
  the theremin now opens I2S at 16,000 Hz instead of 22,050 Hz; comments
  updated to "about 128 ms"; both bumped to v1.1.
- [`src/kits/study-buddy/sound.py`](../src/kits/study-buddy/sound.py): the
  `init()` docstring lists the rates the amplifier accepts.

## Decisions

- **`ibuf` stays 4096** for the theremin. A chunk is 1,024 samples (2,048
  bytes), so 4096 holds two chunks, the value labs 05 to 07 already use at
  16 kHz. A smaller value was untested. The cost is a reserve of 128 ms
  instead of 93 ms. The chapter suggests trying `ibuf=3072` (96 ms) if the
  pitch lags.
- **Version bumps to 1.1** on the two changed files, so the startup banner
  shows which build is on the board.
- **The multicore guide's 22,050 Hz tables were left alone.** They record
  real measurements.
- **No mascot admonitions** were added, because the page does not use them.

## Open Items

1. Try the theremin mode and Lab 08 on the board at 16 kHz. Listen for
   lag in the pitch and for buzzier square and saw voices at the top of the
   range (the synthesizer does not filter harmonics above half the rate).
2. Check on the bench whether a 3V3-powered breakout with SD unconnected
   stays on across several boards.
3. `sound.wav()` and the clip converter are still unwritten. When they are,
   they must write 16 kHz or 8 kHz files, and 8 kHz needs SD on a GPIO
   (there is no `I2S_SD_PIN` in `config.py` yet).
4. The same datasheet check was not applied to the other kits that use an
   I2S amplifier. `src/kits/sw-gc9b72/ideas.md` mentions the MAX98357A.

## How the Work Was Checked

- The datasheet could not be read by the web fetch or the PDF reader (no
  poppler installed). Its text was extracted with `pypdf` in a throwaway
  virtual environment inside the session's scratchpad, so nothing was
  installed on the system and no scratch files are in the repo.
- Each round of edits was followed by `mkdocs build --strict` into the
  scratchpad (not the tracked `site/` folder). The built HTML was checked
  for the new heading IDs, the cross-links, the tables, the warning
  admonition, and the code block.
- The diff was scanned for secrets before the commit, and only the six
  intended files were staged.
