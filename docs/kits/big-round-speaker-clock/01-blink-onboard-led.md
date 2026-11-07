# Lab 01: Blink the Onboard LED

![A Raspberry Pi Pico with its small green LED blinking](../../img/blink-on-board-led.gif){ width="300" }

Before you trust the screen or the speaker, make sure the Pico itself
works. This lab uses nothing but the board: one tiny light, on and off,
twice a second.

!!! mascot-welcome "Welcome to Lab 01"
    ![Chrono waving welcome](../../img/mascot/welcome.png){ class="mascot-admonition-img" }
    A blinking light is the "hello" of hardware. When it blinks, you know
    the board, the cable, and MicroPython all work, so any problem later
    is in the wiring or the code. Let's make time tick!

## What You Will Learn

- how to run a program on the Pico from Thonny
- how to turn a pin on and off
- why the Pico W's light is called `"LED"` and not a pin number

## Run It

Open `01-blink-onboard-led.py` in Thonny and click **Run**. The shell
prints `01-blink-onboard-led.py v1.0`, and the small LED next to the USB
socket starts blinking. Click **Stop** to end it.

## The Code

```python
from machine import Pin
from time import sleep

led = Pin("LED", Pin.OUT)

while True:
    led.toggle()
    sleep(0.5)
```

- `Pin("LED", Pin.OUT)` gets the onboard light, ready to switch.
- `while True:` repeats the indented lines forever. That's a **loop**.
- `led.toggle()` flips the light: on if it was off, off if it was on.
- `sleep(0.5)` waits half a second.

On a plain Pico the LED is on pin 25. On a Pico W it is wired to the WiFi
chip instead, so you must use the name `"LED"`. `Pin(25)` does nothing on
a Pico W.

!!! tip "Try This"
    1. Change `0.5` to `0.1`. How fast can it blink before it looks like
       it's always on?
    2. Make it blink like a heartbeat: two quick blinks, then a pause.

## If It Doesn't Work

- **The LED stays dark.** Check that you put the **Pico W** version of
  MicroPython on the board (`RPI_PICO_W`), not the plain Pico version.
- **Thonny can't find the board.** Try another USB cable. Some cables only
  carry power, not data.

!!! mascot-celebration "The Board Is Alive!"
    ![Chrono celebrating](../../img/mascot/celebration.png){ class="mascot-admonition-img" }
    You ran your first program and switched a pin on and off. That proves
    the Pico, the cable, and MicroPython all work, which is the base every
    other lab stands on.

**Next:** [Lab 02: Give the Kit a Checkup](02-probe.md)
