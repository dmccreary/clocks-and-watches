# Lab 05: Test the Speaker

This lab plays a steady 400 Hz tone for two seconds. It talks to the
amplifier directly, without the kit's sound library, so the only things
that can stop it are the wires and the amplifier.

!!! mascot-welcome "Welcome to Lab 05"
    ![Chrono waving welcome](../../img/mascot/welcome.png){ class="mascot-admonition-img" }
    This is the lab where your clock finds its voice. One steady beep
    today means chimes, alarms, and timer beeps later. Let's make time
    tick!

## What You Will Learn

- how a computer makes sound out of numbers
- what **samples** and **sample rate** mean
- how the Pico sends sound to the amplifier over **I2S**

## Run It

Keep the speaker away from your ear, open `05-speaker-test.py`, and click
**Run**. You should hear a two-second beep. The shell prints:

```text
05-speaker-test.py v1.0
I2S started: BCLK GP9, LRC GP10, DIN GP11, gain 9 dB
Playing 400 Hz for 2 seconds at volume 40 -- listen now
Done after 2122 ms.
Heard it? The amp and speaker work. Heard nothing? See the list at
the top of this file.
```

## Sound Is a List of Numbers

A speaker makes sound by pushing its cone out and pulling it back, very
fast. A 400 Hz tone pushes and pulls 400 times a second. To describe that
movement, the program sends a number for where the cone should be,
16,000 times every second. Each number is a **sample**, and 16,000 per
second is the **sample rate**.

```python
RATE = 16000            # samples per second
FREQ = 400              # 16000 / 400 = exactly 40 samples per wave
```

!!! mascot-thinking "A wave, one number at a time"
    ![Chrono thinking](../../img/mascot/thinking.png){ class="mascot-admonition-img" }
    Think of a flip book. Each page is one sample, and flipped fast enough
    the pages become smooth motion. Here, 40 numbers trace one full wave,
    and 400 of those waves every second are the beep you hear.

The program works out one chunk of the wave with `math.sin()` and sends
it again and again. The first chunk fades in and the last fades out, so
the tone starts and stops without a click.

## Sending It: I2S

The samples travel to the amplifier on three wires, called **I2S**:

| Wire | Pico pin | What it does |
|---|---|---|
| BCLK | GP9 | Ticks once for every bit of every sample |
| LRC | GP10 | Marks where each sample starts |
| DIN | GP11 | The bits of the samples themselves |

```python
config.set_gain()
audio = I2S(0, sck=Pin(config.I2S_BCLK_PIN), ws=Pin(config.I2S_LRC_PIN),
            sd=Pin(config.I2S_DIN_PIN), mode=I2S.TX, bits=16,
            format=I2S.MONO, rate=RATE, ibuf=4096)
```

`config.set_gain()` sets the amplifier's GAIN pin. On this kit the GAIN
wire goes to a Pico pin, so a program can pick 6, 9, or 12 **decibels**
of boost (`GAIN_DB` in `config.py`).

!!! tip "Try This"
    1. Change `FREQ` to `800`. The pitch goes up an octave. Keep `FREQ` a
       number that divides 16,000 exactly, like 200, 500, 800, or 1000.
    2. Change `VOLUME` in `config.py` to 10, then 80. Which is
       comfortable?
    3. Change `GAIN_DB` in `config.py` to 12. How much louder is it?

## If It Doesn't Work

- **No sound at all.** Check the amplifier's VIN and GND first: with no
  power it is silent. Then check that DIN goes to GP11, and that the
  speaker's wires are in the amplifier's + and − terminals.
- **An error when `I2S()` starts.** BCLK and LRC are swapped. LRC must be
  on the pin right after BCLK.
- **`GAIN_DB must be 6, 9, or 12`.** Fix the number in `config.py`.

!!! mascot-celebration "Your Clock Has a Voice!"
    ![Chrono celebrating](../../img/mascot/celebration.png){ class="mascot-admonition-img" }
    You turned a list of numbers into a real sound, and you know what
    samples, sample rate, and I2S mean. Every chime and alarm in this kit
    is built the same way.

**Next:** [Lab 06: Check Your WiFi](06-test-wifi.md)
