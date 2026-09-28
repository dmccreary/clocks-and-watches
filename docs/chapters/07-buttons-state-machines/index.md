---
title: Buttons, Interrupts, and State Machines
description: Push buttons, debouncing, interrupts, state machines, mode cycling, and rotary encoders for setting the time.
generated_by: claude skill chapter-content-generator
date: 2026-09-28 14:34:31
version: 1.10
---

# Buttons, Interrupts, and State Machines

## Summary

Students wire buttons, filter switch bounce in hardware and software, and respond with interrupt handlers. They build state machines to cycle clock modes. After this chapter they can let users set the time with buttons or an encoder.

## Concepts Covered

This chapter covers the following 13 concepts from the learning graph:

| Concept | Concept Impact Score |
|---------|-----------------------|
| Momentary Push Button | 6 |
| Button Wiring | 5 |
| Button Debouncing | 4 |
| State Machine | 12 |
| Hardware Debounce | 1 |
| Callback Functions | 15 |
| Interrupt Handlers | 14 |
| Software Debounce | 2 |
| IRQ Falling Edge | 1 |
| Mode Cycling | 7 |
| Rotary Encoder | 3 |
| Encoder Direction | 2 |
| Encoder Acceleration | 1 |

## Prerequisites

This chapter builds on concepts from:

- [Chapter 1: Computational Thinking and Physical Computing](../01-foundations/index.md)
- [Chapter 2: Electronics Fundamentals and Breadboard Wiring](../02-electronics-fundamentals/index.md)
- [Chapter 3: MicroPython Basics: Variables and Data Types](../03-micropython-basics/index.md)
- [Chapter 4: Control Flow, Functions, and Modules](../04-control-flow-functions/index.md)
- [Chapter 5: The Pico Platform: Pins, Files, and Firmware](../05-pico-platform/index.md)
- [Chapter 6: Getting the Time in MicroPython](../06-getting-time/index.md)

---

!!! mascot-welcome "Give Your Clock Some Buttons"
    ![Chrono waving welcome](../../img/mascot/welcome.png){ class="mascot-admonition-img" }
    A clock that can't be set is just a fancy paperweight. In this chapter you'll add buttons, tame their jittery signals, and build the mode-cycling logic that lets anyone set the hour and minute. Let's make time tick!

## Letting People Talk to the Clock

So far your programs have only *output* information. To set the time or an alarm, a person must send information *in*. The simplest input device is a push button, and this chapter takes you from one wire on a breadboard to a complete "run / set hour / set minute" menu. Along the way you will meet the two hard problems of buttons, **bounce** and **timing**, and the tools for solving them: debouncing, interrupts, and state machines. The chapter ends with the rotary encoder, a knob that makes setting the time faster.

## Momentary Push Button

A **momentary push button** is a switch that connects its terminals only while you hold it down and disconnects when you let go. "Momentary" is the opposite of a light switch that stays in position. The small square buttons in your kit are called **tactile switches** and have four legs.

The four legs are connected in two pairs inside the case. Legs on the same side are always joined, and pressing the button joins the two pairs. So the button acts as a single switch connected between *either* leg of one pair and *either* leg of the other. If you wire two legs on the same side, the button will never seem to work.

Because it has no memory and no power of its own, a button is a **sensor** in the sense of Chapter 1: it reports "pressed" or "not pressed" and nothing more.

## Button Wiring

Wire the button between a GPIO pin and ground and let the internal pull-up from Chapter 5 do the rest:

1. Place the button across the center gap of the breadboard so its two pairs of legs land in different strips.
2. Connect one leg to the GPIO pin (for example GP14).
3. Connect the opposite-side leg to a ground rail.
4. In code, configure the pin with `Pin.PULL_UP`.

The standard kits use GP14 for the **mode** button and GP15 for the **cycle** button, in the lower-left corner of the Pico. The pin reads 1 when idle and 0 when pressed (active low). You need no external resistor, and no 3.3 V wire.

```python
from machine import Pin
mode_button = Pin(14, Pin.IN, Pin.PULL_UP)
cycle_button = Pin(15, Pin.IN, Pin.PULL_UP)
```

## Button Debouncing

A mechanical switch is not a clean on/off device. When the metal contacts collide, they spring apart and touch again several times, sending a burst of rapid on/off pulses before settling. This is called **contact bounce**, and it typically lasts a few milliseconds up to about 20 ms.

A human sees one press. The Pico is fast enough to see the burst as **ten presses**. **Debouncing** is any technique that ignores the bounce so one physical press counts as exactly one event.

!!! mascot-warning "One Press, Ten Counts"
    ![Chrono warning](../../img/mascot/warning.png){ class="mascot-admonition-img" }
    If your counter jumps by 3 or 7 when you press a button once, that's bounce, not a bug in your wiring. It happens because real contacts chatter as they close. The fix is to ignore any change that arrives within about 50 ms of the last one.

#### Diagram: Button Bounce Oscilloscope

<details markdown="1">
<summary>Button Bounce Oscilloscope</summary>
Type: MicroSim
**sim-id:** button-bounce-scope<br/>
**Library:** p5.js<br/>
**Status:** Specified

**Learning objective:** Students will *analyze* how bounce creates false presses and *evaluate* the effect of a debounce delay (Bloom: Analyzing, Evaluating).

**Visual elements:** A scrolling oscilloscope-style trace of the pin voltage (3.3 V high, 0 V low). Below it, a counter shows the number of presses counted.

**Controls:**

- "Press button" generates a realistic bounce burst (random 3 to 12 transitions over 1 to 15 ms).
- Slider "Debounce window (ms)": 0 to 100, default 0.
- Toggle "Hardware filter (0.1 µF)" that smooths the trace.

**Behavior:** With the window at 0, one press increments the counter several times. As the window grows past the bounce length the counter increments once.

**Responsive design:** The trace fills the container width.

Implementation: p5.js with a timestamped event list.
</details>

### Hardware Debounce

**Hardware debouncing** filters the bounce in the circuit itself. The simple version places a **0.1 µF capacitor** across the button, between the GPIO pin and ground. The capacitor smooths out the rapid changes because it charges and discharges slowly through the pull-up resistor. With the internal pull-up of about 50 kΩ, the time constant is

\[ \tau = R \times C = 50{,}000 \times 0.0000001 = 5\ \text{ms} \]

which is on the order of the bounce time. It costs one small part and no code. In practice, software debouncing is more common in this course because it needs no extra parts.

### Software Debounce

**Software debouncing** ignores extra events in code. The most reliable method is a time window: remember when you last accepted a press, and reject any new one that arrives too soon.

```python
from time import ticks_ms, ticks_diff

last_press = 0
DEBOUNCE_MS = 50

def accept_press():
    global last_press
    now = ticks_ms()
    if ticks_diff(now, last_press) > DEBOUNCE_MS:
        last_press = now
        return True
    return False
```

A window of 20 to 50 ms stops bounce but still feels instant. Larger values, like the 200 ms sometimes used in examples, also work, but make fast repeated presses feel sluggish.

## Interrupt Handlers

Reading a button in a loop is called **polling**: you keep asking "pressed yet?" It works, but if your loop is busy redrawing the display, a short press can slip by unnoticed. An **interrupt** is a different approach. The hardware watches the pin and, the moment it changes, pauses your main code and runs a special function called an **interrupt handler** (also called an interrupt service routine or ISR). When the handler finishes, your main code resumes.

You attach a handler with the pin's `irq()` method:

```python
def on_press(pin):
    print("pressed", pin)

button.irq(trigger=Pin.IRQ_FALLING, handler=on_press)
```

The handler receives one argument: the pin that triggered it. Interrupts make sure a press is never missed, even when the main loop is busy.

### IRQ Falling Edge

An **edge** is the moment a signal changes level. A **falling edge** is the change from high (1) to low (0), and a **rising edge** is low to high. The `trigger` argument chooses which edge starts the handler.

| Trigger | Fires when | With a pull-up button |
|---------|-----------|------------------------|
| `Pin.IRQ_FALLING` | Signal goes 1 to 0 | The instant the button is pressed |
| `Pin.IRQ_RISING` | Signal goes 0 to 1 | The instant the button is released |
| Both constants combined | Either change | Press and release |

To listen for both edges, combine the two constants with the `|` operator. Because a pull-up button is active low, `IRQ_FALLING` is the right trigger for "the user pressed the button."

### Callback Functions

A **callback function** is a function you give to some other code, so that code can call it back later when something happens. The handler above is a callback: you do not call `on_press()` yourself; you hand it to `irq()`, and the hardware calls it. Callbacks appear whenever your code must react to events instead of running in a fixed order.

The rules for a good interrupt callback are simple:

- Keep it **short and fast**. Do not draw on the display or use long `sleep()` calls inside it.
- Do only the minimum: set a **flag** (a variable) or increment a counter.
- Let the main loop notice the flag and do the real work.

!!! mascot-tip "Flag It and Leave"
    ![Chrono with a tip](../../img/mascot/tip.png){ class="mascot-admonition-img" }
    Inside an interrupt handler, just set `pressed = True` and return. Your main loop checks the flag, clears it, and does the heavy work. Handlers stay fast and your display code stays out of trouble.

Here is the complete pattern, combining an interrupt, a debounce window, and a flag. The handler needs the `global` keyword from Chapter 4 to change variables outside itself.

```python
NAME = "07-button-irq.py"
VERSION = "1.0"
print("{} v{}".format(NAME, VERSION))

from machine import Pin
from time import ticks_ms, ticks_diff, sleep

button = Pin(14, Pin.IN, Pin.PULL_UP)
pressed = False
last = 0

def on_press(pin):
    global pressed, last
    now = ticks_ms()
    if ticks_diff(now, last) > 50:    # ignore bounce
        last = now
        pressed = True

button.irq(trigger=Pin.IRQ_FALLING, handler=on_press)

count = 0
while True:
    if pressed:
        pressed = False
        count += 1
        print("presses:", count)
    sleep(0.01)
```

## State Machine

A **state machine** is a way of organizing a program around a small set of named **states**, where each state defines what the program does and which events cause a change to a different state. A traffic light is a state machine: green, yellow, and red are states, and a timer is the event that moves it along.

For a clock, the states are the modes the user is in, and the event is a button press. Consider a simple three-state design:

| State | What the display shows | Mode button press goes to |
|-------|------------------------|----------------------------|
| RUN | The current time | SET_HOUR |
| SET_HOUR | The hour, flashing | SET_MINUTE |
| SET_MINUTE | The minute, flashing | RUN |

A drawing of the same idea, with circles for states and arrows for transitions, makes the logic obvious at a glance and is a good way to plan before coding.

!!! mascot-thinking "Ask 'What State Am I In?'"
    ![Chrono thinking](../../img/mascot/thinking.png){ class="mascot-admonition-img" }
    A state machine turns a mess of `if` statements into one question: what state am I in, and what does this event do *there*? The same button press can mean different things in different states, and that is exactly how a two-button clock does so much.

#### Diagram: Clock Mode State Machine

<details markdown="1">
<summary>Clock Mode State Machine</summary>
Type: interactive diagram
**sim-id:** clock-mode-state-machine<br/>
**Library:** vis-network<br/>
**Status:** Specified

**Learning objective:** Students will *apply* a state machine to predict what a button press does in each mode (Bloom: Applying).

**Layout:** Circles for RUN, SET_HOUR, SET_MINUTE (and optionally SET_ALARM_HOUR, SET_ALARM_MINUTE). Arrows are labeled "Mode press."

**Interactions:**

- Two on-screen buttons, "Mode" and "Cycle." Pressing Mode moves the highlighted state along the arrows; pressing Cycle changes the value shown in a mock clock face beside the diagram (hour +1 in SET_HOUR, minute +1 in SET_MINUTE, no effect in RUN).
- Clicking a state opens an infobox describing what the display shows and what each button does there.
- A "Predict" toggle asks the student to name the next state before it moves.

**Responsive design:** The canvas fills the container and calls `network.fit()` on resize.

Implementation: vis-network with three nodes and scripted highlighting.
</details>

### Mode Cycling

**Mode cycling** is stepping through the states in a loop, one press at a time, wrapping from the last mode back to the first. It uses the modulo trick from Chapter 4:

```python
MODES = ["RUN", "SET_HOUR", "SET_MINUTE"]
mode = 0

def next_mode():
    global mode
    mode = (mode + 1) % len(MODES)
```

After three presses you are back to RUN. The second button, the **cycle** button, changes the value that belongs to the current mode, again with a wrap: hours go through 0 to 23 (`% 24`) and minutes 0 to 59 (`% 60`).

Combining the flag pattern, the mode list, and the wrap-around gives a complete time-setting program that prints instead of drawing:

```python
NAME = "07-set-time.py"
VERSION = "1.0"
print("{} v{}".format(NAME, VERSION))

from machine import Pin
from time import ticks_ms, ticks_diff, sleep

MODES = ["RUN", "SET_HOUR", "SET_MINUTE"]
mode_btn = Pin(14, Pin.IN, Pin.PULL_UP)
cycle_btn = Pin(15, Pin.IN, Pin.PULL_UP)

mode = 0
hour, minute = 12, 0
mode_flag = cycle_flag = False
last_mode = last_cycle = 0

def mode_isr(pin):
    global mode_flag, last_mode
    now = ticks_ms()
    if ticks_diff(now, last_mode) > 50:
        last_mode = now
        mode_flag = True

def cycle_isr(pin):
    global cycle_flag, last_cycle
    now = ticks_ms()
    if ticks_diff(now, last_cycle) > 50:
        last_cycle = now
        cycle_flag = True

mode_btn.irq(trigger=Pin.IRQ_FALLING, handler=mode_isr)
cycle_btn.irq(trigger=Pin.IRQ_FALLING, handler=cycle_isr)

while True:
    if mode_flag:
        mode_flag = False
        mode = (mode + 1) % len(MODES)
        print("Mode:", MODES[mode])
    if cycle_flag:
        cycle_flag = False
        if MODES[mode] == "SET_HOUR":
            hour = (hour + 1) % 24
        elif MODES[mode] == "SET_MINUTE":
            minute = (minute + 1) % 60
        print(f"{hour:02d}:{minute:02d}")
    sleep(0.01)
```

Note that when the user enters a setting mode, the value they change should start from the *current* time, not from zero. The program starts at 12:00 here only to keep the example short.

## Rotary Encoder

A **rotary encoder** is a knob that turns endlessly and reports each small step of rotation, along with the direction. Unlike a potentiometer, it has no stops and no fixed position. It is a nicer way to set a time because turning one knob is faster than pressing a button 40 times.

A typical encoder module has five pins: **GND**, **+** (3.3 V), **CLK** (also called A), **DT** (also called B), and **SW** (a push button built into the knob). CLK and DT are two switches that open and close as you turn, and the important thing is the *order* in which they change.

### Encoder Direction

Both switches produce a pattern called **quadrature**: A and B change in a fixed sequence, offset by a quarter of a cycle. Turning clockwise gives one sequence, and counterclockwise gives the reverse.

| Turn | A and B (in order) |
|------|--------------------|
| Clockwise | 00, 10, 11, 01 |
| Counterclockwise | 00, 01, 11, 10 |

The simplest decoding method uses only one edge. When A has a falling edge, look at B at that moment. If B is 1, the knob is turning one way, and if B is 0 it is turning the other way. (Swap the two directions if your knob feels backward.)

```python
from machine import Pin

a = Pin(10, Pin.IN, Pin.PULL_UP)
b = Pin(11, Pin.IN, Pin.PULL_UP)
value = 0

def on_turn(pin):
    global value
    if b.value():
        value += 1      # one direction
    else:
        value -= 1      # the other

a.irq(trigger=Pin.IRQ_FALLING, handler=on_turn)
```

!!! mascot-encourage "Quadrature Takes a Minute"
    ![Chrono encouraging](../../img/mascot/encouraging.png){ class="mascot-admonition-img" }
    Two signals that change in a sequence can feel confusing at first. Try it on paper: write A and B for each click of a clockwise turn, then read the sequence backward for counterclockwise. Once you see the pattern, the code is only three lines.

#### Diagram: Quadrature Encoder Simulator

<details markdown="1">
<summary>Quadrature Encoder Simulator</summary>
Type: MicroSim
**sim-id:** quadrature-encoder-sim<br/>
**Library:** p5.js<br/>
**Status:** Specified

**Learning objective:** Students will *understand* how the A and B signals encode rotation direction (Bloom: Understanding).

**Visual elements:** A draggable knob on the left. On the right, two square-wave traces for A and B scrolling in time, with a vertical line at each falling edge of A showing the value of B at that instant. A counter shows the running value.

**Controls:** Drag the knob clockwise or counterclockwise, or use "Step CW" and "Step CCW" buttons; a "Show table" toggle displays the state sequence.

**Responsive design:** Knob and traces scale with the container.

Implementation: p5.js with angle-to-signal mapping.
</details>

### Encoder Acceleration

**Encoder acceleration** makes the value change faster when the user turns the knob faster. Moving from minute 0 to minute 45 one click at a time is tedious, but a quick spin should jump by larger steps. The trick is to measure the time between clicks with `ticks_ms()`.

```python
last = 0

def step_size():
    global last
    now = ticks_ms()
    gap = ticks_diff(now, last)
    last = now
    if gap < 30:
        return 10       # very fast turning
    elif gap < 80:
        return 5
    return 1            # slow: precise control
```

Multiply the direction (+1 or -1) by `step_size()` to get the change. Slow turns still give one-at-a-time precision, so the user can fine-tune the last few minutes.

## Putting It Together

| Problem | Solution |
|---------|----------|
| Which pin for a button? | Any GPIO with `Pin.PULL_UP`, wired to ground |
| One press counts many times | Debounce with a 20 to 50 ms window |
| Presses are missed | Use `irq()` with `IRQ_FALLING` |
| What do the buttons mean now? | A state machine with mode cycling |
| Setting the time is slow | Rotary encoder with acceleration |

## Key Takeaways

- A push button wired between a pin and ground, with `Pin.PULL_UP`, reads 0 when pressed.
- Contact bounce makes one press look like many; debounce with a short time window or a small capacitor.
- Interrupt handlers catch presses immediately; keep them short and set a flag.
- A state machine plus `(mode + 1) % n` implements mode cycling.
- A rotary encoder reports direction using quadrature signals, and timing between clicks enables acceleration.

!!! mascot-celebration "Your Clock Listens Now"
    ![Chrono celebrating](../../img/mascot/celebration.png){ class="mascot-admonition-img" }
    You can now debounce a button, catch presses with interrupts, and cycle through set-hour and set-minute modes using a state machine. That is a fully settable clock interface. Every second counts!

## Practice Questions

1. Why does a button wired to ground use `Pin.PULL_UP`, and what does `value()` return while it is pressed?
2. A counter increases by 5 when you press once. Name the problem and give two ways to fix it.
3. Why should an interrupt handler set a flag instead of drawing on the display?
4. Draw the state machine for a clock with modes RUN, SET_HOUR, SET_MINUTE, SET_ALARM_HOUR, and SET_ALARM_MINUTE.
5. Write `step_size()` thresholds so that turning the encoder very fast changes the minute by 10 per click.
