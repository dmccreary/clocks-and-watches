# Lab 02: Give the Kit a Checkup

`02-probe.py` is a doctor's visit for your kit. It checks everything that
software can check and prints a report in Thonny's shell. Run it on a new
kit, and again any time something stops working.

!!! mascot-welcome "Welcome to Lab 02"
    ![Chrono waving welcome](../../img/mascot/welcome.png){ class="mascot-admonition-img" }
    This program does the detective work for you. In about half a minute
    it tells you whether a problem is the board, the files, the wiring, or
    your own code. Let's make time tick!

## What You Will Learn

- what the Pico W has inside: its chip, memory, and storage
- which kit files must be on the board
- how to read a test report and act on its warnings

## Run It

Open `02-probe.py` in Thonny and click **Run**. The report has eleven
sections:

| Section | What it checks |
|---|---|
| 1. Board and firmware | Which chip, which MicroPython, how fast the processor runs |
| 2. RAM | How much working memory is free |
| 3. Flash | How big the storage is, and every file on it |
| 4. Kit files | Are the display driver, fonts, `config.py`, and sound files on the board? |
| 5. Power and sensors | USB power, the chip's temperature, the BOOTSEL button |
| 6. WiFi | The board's MAC address and the networks it can see |
| 7. Real-time clock | Has anything set the time yet? |
| 8. Buttons | Are MODE, UP, and DOWN all reading "not pressed"? |
| 9. SPI bus | The speed the display connection really runs at |
| 10. Speaker | The BCLK/LRC pin rule, the GAIN pin, and three rising beeps |
| 11. Display | Starts the screen and draws color bars and "Probe OK" |

The report ends with a **Summary** that lists every warning. Fix those
first.

!!! mascot-thinking "Why can't it check the screen and speaker by itself?"
    ![Chrono thinking](../../img/mascot/thinking.png){ class="mascot-admonition-img" }
    Notice that the Pico only *sends* to the display and the amplifier;
    neither one can answer back. So the last two checks need your senses:
    if you see "Probe OK" and hear three rising beeps, both work.

## Nothing Can Break

The probe only reads. It never writes a file or changes a setting, so it
is always safe to run. Set `PLAY_BEEPS = False` at the top of the file for
a silent checkup.

## If It Doesn't Work

- **"... is not on the board -- run upload-code.sh".** The kit's files
  aren't on the Pico yet. Close Thonny and run `upload-code.sh`.
- **A button reads "pressed" when you aren't touching it.** That button is
  turned the wrong way in the breadboard, so its legs are always connected.
  Turn it a quarter turn.
- **An error in the speaker section.** BCLK and LRC are swapped. See the
  wiring warning on the [kit's main page](index.md).

!!! mascot-celebration "Checkup Complete!"
    ![Chrono celebrating](../../img/mascot/celebration.png){ class="mascot-admonition-img" }
    You can now read a hardware report and turn each warning into a fix.
    When something goes wrong later, run this lab first.

**Next:** [Lab 03: Test the Buttons](03-button-test.md)
