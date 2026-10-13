# Lab 04: Test the K0 Button

K0 is the square push button below the knob. In the clock labs it starts
and stops things, like the stopwatch. First, this lab checks that K0 is
wired correctly.

The program is tiny on purpose. It skips the screen and prints to
Thonny's shell instead.

!!! mascot-welcome "Welcome to Lab 04"
    ![Chrono waving welcome](../../img/mascot/welcome.png){ class="mascot-admonition-img" }
    Until now your kit has only talked, and with a button it can listen.
    A quick test today saves a lot of head-scratching when the stopwatch
    will not start. Let's make time tick!

## What You Will Learn

- how a **pull-up**, a gentle tug that holds a pin at 1, makes a pressed
  button read 0
- how a program catches the moment a button changes
- why the program looks at the button 50 times a second

## Run It

1. Open `04-button-test.py` in Thonny.
2. Click **Run**.
3. Press K0 and let it go. Do that three times.
4. Read the shell. It should show the lines below.
5. Click **Stop** when you are done.

```text
04-button-test.py v1.0
Press the K0 button, below the knob. Ctrl-C to stop.
K0 pressed   (press number 1)
K0 released
K0 pressed   (press number 2)
K0 released
K0 pressed   (press number 3)
K0 released
```

## How a Button Talks to the Pico

A button is a switch. One side of K0 goes to a pin on the Pico. The
other side goes to **GND** (ground, the zero side of the circuit). The
program sets up that pin first:

```python
import time
from machine import Pin
import config

k0 = Pin(config.BUTTON_K0_PIN, Pin.IN, Pin.PULL_UP)
```

- `import config` borrows the kit's settings file, which knows the pin
  for each part. `config.BUTTON_K0_PIN` is 11, so K0 is on pin GP11.
- `Pin.IN` means the Pico *listens* on this pin.
- `Pin.PULL_UP` turns on the pull-up. Think of it as a weak spring that
  holds the pin up at 1.

Pressing the button connects the pin to ground. Ground is much stronger
than the spring, so the pin drops to 0.

| Button is... | Pin reads |
|---|---|
| not pressed | **1** |
| pressed | **0** |

!!! mascot-warning "Pressed Means 0 Here"
    ![Chrono warning](../../img/mascot/warning.png){ class="mascot-admonition-img" }
    Did you do the [Button lesson in Learning MicroPython](https://dmccreary.github.io/learning-micropython/basics/03-button/)?
    That button was wired the opposite way, so it read 1 when pressed.
    In this kit, always test for 0.

## Catching the Change

Here is the loop that watches the pin:

```python
presses = 0
was_down = False

while True:
    down = k0.value() == 0
    if down != was_down:
        was_down = down
        if down:
            presses += 1
            print("K0 pressed   (press number {})".format(presses))
        else:
            print("K0 released")
    time.sleep_ms(20)
```

- `down = k0.value() == 0` reads the pin. `down` is `True` while the
  button is held.
- `was_down` remembers what the button was doing at the last look.
- `if down != was_down:` asks if the button changed. Without this test,
  the program would print the whole time you hold the button.
- The inner `if` counts and prints each press, and prints each release.

## Why 50 Times a Second?

`time.sleep_ms(20)` waits 20 thousandths of a second, so the loop looks
at the button 50 times every second. That is fast enough to catch your
quickest press.

It is also slow enough to skip over **bounce**: the chatter of a
switch's metal parts as they close. They act like a dropped ball that
bounces before it lies still. Lab 12 tells the whole bounce story.

!!! tip "Try This"
    1. Hold K0 down for five seconds. How many lines print before you
       let go? Why?
    2. Change `time.sleep_ms(20)` to `time.sleep_ms(1000)`. Tap K0 very
       quickly a few times. Does the program catch every tap?
    3. Now try `time.sleep_ms(1)`. Does the count ever jump by two on
       one press? If it does, you saw bounce. Put the 20 back afterward.

## If It Doesn't Work

- **Nothing prints when you press K0.** K0 is not connected to GP11. A
  pull-up pin with nothing connected reads 1 forever, just like a button
  nobody is pressing. Check the K0 wire against
  [How It Is Wired](index.md#how-it-is-wired).
- **It prints "K0 pressed" before you touch anything.** The pin is stuck
  at ground. Look for a wire in the wrong place.

!!! mascot-celebration "K0 Is Listening!"
    ![Chrono celebrating](../../img/mascot/celebration.png){ class="mascot-admonition-img" }
    You now know why a pressed button reads 0, and how to catch a
    change by remembering the last look. Next, you will find a second
    button hidden inside the knob.

**Next:** [Lab 05: Test the Knob's Push Switch](05-encoder-push-test.md)
