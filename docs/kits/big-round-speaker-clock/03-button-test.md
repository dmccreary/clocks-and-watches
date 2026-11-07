# Lab 03: Test the Buttons

This lab checks that MODE, UP, and DOWN are each wired to the right pin.
It uses nothing but the buttons and the Pico's LED, so if a button
doesn't show up, the problem has to be that button's two wires.

!!! mascot-welcome "Welcome to Lab 03"
    ![Chrono waving welcome](../../img/mascot/welcome.png){ class="mascot-admonition-img" }
    Three buttons control every mode of this clock, so they need to work
    perfectly. This test also shows you something buttons do that most
    people never notice. Let's make time tick!

## What You Will Learn

- how a button connects a pin to ground
- what a **pull-up** is
- what **contact bounce** is, and why the clock has to filter it out

## Run It

Open `03-button-tests.py` and click **Run**. Press each button once. The
LED stays lit while any button is held. Here is what the shell printed
for one press of each button:

```text
Starting state (all three should say 'up'):
  MODE  GP13  up
  UP    GP14  up
  DOWN  GP15  up

Press each button. Ctrl-C to stop.
MODE  down   (1 of 3 buttons seen)
MODE  up
MODE  down   (1 of 3 buttons seen)
MODE  up
UP    down   (2 of 3 buttons seen)
UP    up
UP    down   (2 of 3 buttons seen)
UP    up
DOWN  down   (3 of 3 buttons seen)
      All three buttons work!
DOWN  up
DOWN  down   (3 of 3 buttons seen)
DOWN  up
```

Wait: each button was pressed **once**, but it shows up **twice**!

## How a Button Talks to the Pico

Each button has one leg on a Pico pin and the other on GND. Inside the
Pico, a **pull-up** gently holds the pin at 1. Pressing the button
connects the pin straight to ground, so it reads 0.

```python
mode = Pin(BUTTON_MODE_PIN, Pin.IN, Pin.PULL_UP)
```

So on this kit, **0 means pressed** and **1 means not pressed**.

## Why Did One Press Print Twice?

A button is two pieces of metal that touch. When they meet, they bounce
apart and together again a few times in a few thousandths of a second.
The Pico reads its pins fast enough to see some of those bounces, so one
press can look like two. This is called **contact bounce**.

!!! mascot-thinking "A test that shows the problem on purpose"
    ![Chrono thinking](../../img/mascot/thinking.png){ class="mascot-admonition-img" }
    This lab prints every change it sees, bounces and all, so you can
    watch bounce happen. The finished clock is smarter: it ignores any
    change that comes too soon after the last one. That is called
    **debouncing**, and it's why one tap of MODE moves exactly one mode.

You might see one line per press, or two or three. It changes from press
to press and from button to button.

!!! tip "Try This"
    1. Hold UP and press DOWN. Does the LED stay lit? The Pico reads each
       pin on its own, so it can tell any mix of buttons apart.
    2. Change `time.sleep_ms(10)` to `time.sleep_ms(500)`. Tap a button
       quickly. Why are some taps missed now?

## If It Doesn't Work

- **A button prints nothing.** One of its wires is loose, or it's on the
  wrong pin. Does a *different* name print when you press it?
- **A button says PRESSED before you touch it.** It's turned a quarter
  turn the wrong way in the breadboard, so its legs are always connected.

!!! mascot-celebration "Buttons Tested!"
    ![Chrono celebrating](../../img/mascot/celebration.png){ class="mascot-admonition-img" }
    You know how a pull-up turns a button press into a 0, and you've seen
    contact bounce with your own eyes. That's exactly the problem the
    clock's debounced buttons solve.

**Next:** [Lab 04: Hello, Round Screen](04-display-test.md)
