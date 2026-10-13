# Lab 07: Controls on the Screen

![The screen says Controls at the top, with two gray boxes labeled K0 and PUSH. The K0 box fills with green, then the PUSH box fills with yellow. Then the line Knob: 0 changes to Knob: 5, the gray words "turn the knob" change to "clockwise" in cyan, and a white marker slides to the right along a gray track.](img/07-controls-display-test.gif){ width="336" }

Labs 04, 05, and 06 tested the controls one at a time, with words in the
Thonny shell. This lab puts all three on the screen at once, so you can
watch the kit react to your hands.

| What you do | What the screen does |
|---|---|
| Hold down **K0** | The K0 box fills with green |
| Press the knob down | The PUSH box fills with yellow |
| Turn the knob | The number counts the clicks, and the white marker slides |

!!! mascot-welcome "Welcome to Lab 07"
    ![Chrono waving welcome](../../img/mascot/welcome.png){ class="mascot-admonition-img" }
    This is the first time the screen answers your hands, and every later
    clock works the same way. You will also teach the Pico to keep count
    of the knob, even when you spin it fast. Let's make time tick!

## What You Will Learn

- what an **interrupt** is, and why the knob needs one
- why the two buttons get by without one
- why an interrupt function should be short
- how to redraw only what changed on the screen

## Run It

1. Open `07-controls-display-test.py` in Thonny and click **Run**.
2. Hold down **K0**, the square button. Its box fills with green until
   you let go.
3. Press the knob straight down. The PUSH box fills with yellow.
4. Turn the knob one click clockwise. The number goes up by one and the
   marker moves one notch right. Turning back does the opposite.
5. Spin the knob fast. In lab 06 that printed `missed a step`. This time
   the count keeps up.

The Thonny shell keeps a log of everything you do:

```text
07-controls-display-test.py v1.1
Press K0, press the knob, and turn the knob. Ctrl-C to stop.
K0 pressed
K0 released
PUSH pressed
PUSH released
knob clockwise -- clicks 1
knob clockwise -- clicks 2
knob clockwise -- clicks 3
knob counter-clockwise -- clicks 2
```

## A Doorbell for the Knob

In labs 04 to 06, a loop looked at the pins over and over. This loop has
drawing to do, and it rests between trips. It comes around only about 50
times a second. A knob step that comes and goes between two looks would
be lost.

Think about waiting for a friend to visit. You could walk to the door
every minute and look outside. A short visit between two looks would be
missed. A doorbell is better. It tells you the moment someone arrives.

An **interrupt** is a doorbell for a pin. You ask MicroPython to call one
of your functions by itself, the moment the pin changes. It does not
matter what the loop is doing right then.

```python
a.irq(knob_moved, Pin.IRQ_RISING | Pin.IRQ_FALLING)
b.irq(knob_moved, Pin.IRQ_RISING | Pin.IRQ_FALLING)
```

- `a.irq(...)` puts a doorbell on A, one of the knob's two switches.
  The second line does the same for B. `irq` is short for *interrupt
  request*.
- `knob_moved` is the function to call when the bell rings.
- The last part says when to ring: when the pin rises to 1, and when it
  falls to 0. That is every change.

You may have met `irq()` in
[chapter 6 of Learning MicroPython](https://dmccreary.github.io/learning-micropython/chapters/06-digital-io-interrupts/),
where it counted button presses.

K0 and PUSH need no doorbell. A press lasts far longer than one trip
around the loop, so the loop always catches it.

## Count Fast, Draw Later

Here is the function the doorbell calls. It is the counting code from
[lab 06](06-encoder-rotation-test.md), moved into a function:

```python
def knob_moved(pin):
    global steps, last
    now = CLOCKWISE.index((a.value(), b.value()))
    move = (now - last) % 4
    last = now
    if move == 1:
        steps += 1
    elif move == 3:
        steps -= 1
```

- `global steps, last` lets the function change two variables that were
  made outside it.
- `now` is which of the four positions A and B are in, from 0 to 3.
  `last` is where they were the time before.
- `move` is how far around that loop of four the knob went. A 1 is one
  step clockwise. A 3 is one step back.

The main loop turns `steps` into clicks, two steps to a click, as in
lab 06.

!!! mascot-thinking "Notice What Is Missing"
    ![Chrono thinking](../../img/mascot/thinking.png){ class="mascot-admonition-img" }
    Look at what `knob_moved()` does not do: it draws nothing and prints
    nothing. An interrupt cuts in on the rest of your program, so its
    function should write down a number and leave. The slow job of
    drawing waits for the main loop.

## Only Draw What Changed

The main loop checks both buttons each time around. These lines, part of
the program, run once for each button:

```python
down = pin.value() == 0
if down != held[i]:
    held[i] = down
    draw_box(x, color, down)
```

- `down` is `True` while the button is pressed. A pressed button reads 0,
  as lab 04 showed.
- `held[i]` remembers what that button's box shows right now.
- The `if` is true only at the moment those two differ. Only then is the
  box painted.

Hold K0 for ten seconds and its box is painted once, not 500 times. Every
lab after this one follows the same rule: redraw only what changed.

!!! tip "Try This"
    1. In `BUTTONS`, near the top of the program, change `config.GREEN`
       to `config.RED`. Which box changes color?
    2. Change `NOTCHES = 20` to `NOTCHES = 10`. How many clicks does the
       marker need to cross the track now?
    3. Change the last line, `time.sleep_ms(20)`, to
       `time.sleep_ms(500)`. The loop now looks only twice a second, so
       it misses some quick taps of K0. Spin the knob. The number waits,
       then jumps to the right count, because the interrupt kept
       counting. Change the line back to 20.

## If It Doesn't Work

- **A box never fills.** That control is not reaching its pin. Run lab 04
  again for K0, or lab 05 for PUSH.
- **The number counts the wrong way, or not one per click.** Lab 06
  shows what to fix in `config.py`.
- **The screen stays blank.** Go back to lab 03 and get the display
  working first.

!!! mascot-celebration "The Screen Answers Back!"
    ![Chrono celebrating](../../img/mascot/celebration.png){ class="mascot-admonition-img" }
    You gave the knob a doorbell with `irq()`, kept its interrupt
    function short, and redrew only what changed. Next comes a quick
    test of the light inside the screen.

**Next:** [Lab 08: Test the Backlight](08-backlight-test.md)
