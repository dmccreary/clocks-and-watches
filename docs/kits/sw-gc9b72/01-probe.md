# Lab 01: Give the Kit a Checkup

![The probe's screen: "Probe OK", red, green, blue, and white color bars, and the memory and speed numbers](img/01-probe.png){ width="360" }

When you visit a doctor for a checkup, they test your heart, your
breathing, and your reflexes. This program does the same thing for your
kit. It tests everything a program *can* test:

- the Pico and its version of MicroPython
- how much **memory** (RAM) and **storage** (flash) it has
- whether all the kit's files are on the Pico
- whether it can see your WiFi network
- whether the three buttons are wired correctly
- whether the display is working

Run this lab whenever something isn't working. It usually tells you
exactly what's wrong.

!!! mascot-welcome "Welcome to Lab 01"
    ![Chrono waving welcome](../../img/mascot/welcome.png){ class="mascot-admonition-img" }
    I like checkups. They're how a robot like me finds a loose wire before
    it turns into a mystery. After this lab, you'll have a tool that finds
    most kit problems for you. Let's make time tick!

## What You Will Learn

- the difference between **RAM** and **flash** memory
- how a program can check its own hardware
- why some checks still need your eyes

## Run It

Open `01-probe.py` in Thonny and click **Run**. It prints a long report
in Thonny's shell, the text area at the bottom of the window. At the end
it draws on the screen:

- **four color bars**: red, green, blue, and white, from left to right
- **"Probe OK"** in green if every check passed, or **"Probe: 2 warn"** in
  yellow, with the problems listed underneath

Here's part of the report, from a real kit:

```text
========================================================
1. Board and firmware
========================================================
board     : Raspberry Pi Pico 2 W with RP2350
build     : RPI_PICO2_W
MicroPython 1.29.0 -- v1.29.0 on 2026-08-24
CPU clock : 150 MHz

========================================================
2. RAM
========================================================
chip SRAM : 520 KB (RP2350 datasheet)
heap total: 446,656 bytes (436.2 KB)
heap free : 431,616 bytes (421.5 KB)

========================================================
3. Flash
========================================================
flash chip: 4.00 MB (found by address wrap-around)
firmware  : 1.50 MB reserved for MicroPython itself
filesystem: 2,621,440 bytes (2560.0 KB)

...

========================================================
Summary
========================================================
Everything software can check looks good.
```

## RAM and Flash: Two Kinds of Memory

The Pico has two kinds of memory, and they do different jobs:

| | **RAM** | **Flash** |
|---|---|---|
| Like... | a whiteboard | a notebook |
| Holds | what the program is working on right now | your program files |
| How much | 520 KB | 4 MB (4,000 KB) |
| When you unplug the Pico | erased | kept |

A **KB** (kilobyte) is about 1,000 bytes, and one byte can hold one letter.
So the Pico's RAM could hold about half a million letters.

!!! note "A clever trick for measuring flash"
    MicroPython won't tell you how big the flash chip is. So the probe
    uses a trick. Imagine a street where the house numbers only go up to
    99. If you ask for house number 105, you end up at house number 5,
    because the numbers wrap around. The flash chip works the same way:
    reading 4 MB past the start gives you the same bytes as the start. The
    smallest jump that "wraps around" tells you the chip's size.

## Why the Color Bars?

A program can check that the display is *plugged in*, but not whether it
looks right, because the display can't send pictures back to the Pico. So
the probe draws something only your eyes can check. If you see red,
green, blue, and white in that order, the colors are right. If red and
blue are swapped, the display needs a different color setting.

!!! tip "Try This"
    1. Hold down one of the buttons while you run the probe. What does
       section 8, Buttons, say?
    2. Find the line `heap free` in the report. That's how much RAM is
       left over for your programs. Is it more or less than 400 KB?

## If It Doesn't Work

- **The report says `MISSING lib/gc9b72.py`.** The kit's files aren't on
  the Pico yet. Copy them over (see Before You Start on the
  [kit's main page](index.md)).
- **It says your network was not found.** Check the spelling of the
  network name in `secrets.py`. Also, the Pico only works with 2.4 GHz
  WiFi, not 5 GHz.

**Next:** [Lab 02: Hello, World!](02-hello.md)
