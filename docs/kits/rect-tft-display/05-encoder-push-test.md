# Lab 05: Test the Knob's Push Switch

The knob on your kit does two jobs. You can turn it, and you can press
it straight down like a button. A switch inside the knob closes when you
press. The code calls that switch **PUSH**.

In the clock labs, PUSH is the second action after K0: lap, reset, or
set. This lab checks that it is wired correctly.

!!! mascot-welcome "Welcome to Lab 05"
    ![Chrono waving welcome](../../img/mascot/welcome.png){ class="mascot-admonition-img" }
    Surprise: your kit has a button you may not have noticed, hiding
    inside the knob. Find it now, and one hand can soon turn and press to
    set a clock. Let's make time tick!

## What You Will Learn

- that the knob is also a button
- how one changed line points a program at a different pin
- why each part gets its own test before the parts work together

## Run It

1. Open `05-encoder-push-test.py` in Thonny.
2. Click **Run**.
3. Hold the kit steady with one hand.
4. Put a fingertip on top of the knob. Press straight down until you
   feel a click, then let go.
5. Do it once more, and read the shell.

```text
05-encoder-push-test.py v1.0
Press the knob straight down. Ctrl-C to stop.
PUSH pressed   (press number 1)
PUSH released
PUSH pressed   (press number 2)
PUSH released
```

## Same Idea, Different Pin

This program is lab 04 again, aimed at another pin. PUSH reads 1 while
the knob is up and 0 while it is pressed, just like K0. The names and
the printed words are new, but the change that matters is the pin:

```python
push = Pin(config.ENCODER_PUSH_PIN, Pin.IN, Pin.PULL_UP)

print("Press the knob straight down. Ctrl-C to stop.")
```

`config.ENCODER_PUSH_PIN` is 10, so PUSH is on GP10. The file name says
"encoder" because this kind of knob is called a **rotary encoder**. It
tells a computer which way it turned, and how far.

| | Lab 04 | Lab 05 |
|---|---|---|
| Control | K0 button | the knob's push switch |
| Name in the code | `k0` | `push` |
| Setting in `config.py` | `BUTTON_K0_PIN` | `ENCODER_PUSH_PIN` |
| Pico pin | GP11 | GP10 |

## Press, Don't Turn

Pressing the knob without turning it takes a steady hand. This program
only watches PUSH, so a small turn by mistake does no harm here. In
later labs a turn changes a number, so practice a clean press now.

## Why Test One Part at a Time?

Lab 04 tested K0 alone. This lab tests PUSH alone, and lab 06 tests
turning alone. Lab 07 then puts all three on the screen together.

A band does a sound check the same way: each player plays alone first.
Then a wrong note is easy to find. If lab 07 fails after these three
labs pass, the button and knob wires are not to blame.

!!! tip "Try This"
    1. Turn the knob without pressing it. Does anything print? Why not?
    2. Change `print("PUSH released")` to
       `print("PUSH released", presses)`. What is new in the shell?
    3. In the `push = Pin(...)` line, change `config.ENCODER_PUSH_PIN` to
       `config.BUTTON_K0_PIN`. Which control makes it print now? Change
       it back when you are done.

## If It Doesn't Work

- **Nothing prints when you press the knob.** PUSH is not connected to
  GP10. As in lab 04, a missing wire looks just like a knob nobody is
  pressing. Check the PUSH wire against
  [How It Is Wired](index.md#how-it-is-wired).
- **It prints "PUSH pressed" before you touch the knob.** The pin is
  stuck at ground. Look for a wire in the wrong place.

!!! mascot-celebration "Two Buttons Found!"
    ![Chrono celebrating](../../img/mascot/celebration.png){ class="mascot-admonition-img" }
    You found the switch inside the knob. You also saw how one changed
    line aims the same program at a new pin. Next, you will find out how
    the knob knows which way it is turning.

**Next:** [Lab 06: Test the Knob's Rotation](06-encoder-rotation-test.md)
