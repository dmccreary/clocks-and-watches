# Lab 06: Test the Knob's Rotation

Turn the knob and you feel it click. How does the Pico know that it
moved, and which way? This lab prints what the knob is doing, one tiny
move at a time.

A knob like this is a **rotary encoder**: it turns your twist into on-off
signals that a computer can count. Here you check its two wires, called
A and B.

!!! mascot-welcome "Welcome to Lab 06"
    ![Chrono waving welcome](../../img/mascot/welcome.png){ class="mascot-admonition-img" }
    This knob can spin forever, with no start and no end, and it still
    knows which way you turned it. Today you learn to read its secret
    two-wire code yourself. Let's make time tick!

## What You Will Learn

- how two switches inside the knob report a turn and its direction
- what a **step** is (one small move of the switches), and why one click
  of this knob is two steps
- why a fast spin can make a program miss a step

## Run It

1. Open `06-encoder-rotation-test.py` in Thonny.
2. Click **Run**.
3. Turn the knob clockwise, slowly, two clicks.
4. Turn it back the other way, slowly, two clicks.
5. Read the shell. Each click should print two lines.

```text
06-encoder-rotation-test.py v1.0
Turn the knob slowly. Ctrl-C to stop.
A=1 B=1   at rest
A=0 B=1   clockwise           steps=1    clicks=1
A=0 B=0   clockwise           steps=2    clicks=1
A=1 B=0   clockwise           steps=3    clicks=2
A=1 B=1   clockwise           steps=4    clicks=2
A=1 B=0   counter-clockwise   steps=3    clicks=2
A=0 B=0   counter-clockwise   steps=2    clicks=1
A=0 B=1   counter-clockwise   steps=1    clicks=1
A=1 B=1   counter-clockwise   steps=0    clicks=0
```

Your first line may say `A=0 B=0` instead, because the knob can rest
there too.

## Two Switches, Four Positions

Inside the knob are two switches, A and B. As the knob turns, they
change one after the other, never both at once. It is like walking:
left foot, right foot, never both together.

So the pair (A, B) walks around a loop of four positions:

| Position | A | B | The knob is... |
|---|---|---|---|
| 0 | 0 | 0 | resting in a click |
| 1 | 1 | 0 | halfway between clicks |
| 2 | 1 | 1 | resting in a click |
| 3 | 0 | 1 | halfway between clicks |

A clockwise turn goes down the table: 0, 1, 2, 3, then back to 0. A
counter-clockwise turn goes up it. Each move to the next row is one
step. The program sets this up first:

```python
a = Pin(config.ENCODER_A_PIN, Pin.IN, Pin.PULL_UP)
b = Pin(config.ENCODER_B_PIN, Pin.IN, Pin.PULL_UP)

# The four positions of (A, B), in the order a clockwise turn visits them.
CLOCKWISE = ((0, 0), (1, 0), (1, 1), (0, 1))

pair = (a.value(), b.value())
last = CLOCKWISE.index(pair)
steps = 0
```

- The first two lines set up A on GP8 and B on GP9. Each reads 1 or 0,
  like the button in lab 04.
- `CLOCKWISE` holds the four rows of the table, in order.
- `pair` is what both switches read right now.
- `CLOCKWISE.index(pair)` finds that pair's position number, 0 to 3.
  `last` remembers it.

!!! mascot-thinking "Why Two Switches?"
    ![Chrono thinking](../../img/mascot/thinking.png){ class="mascot-admonition-img" }
    One switch could only say "something moved." Two switches that take
    turns can also say which way. Notice that the order they change in
    is the message.

## Finding the Direction

Look at your printed lines. Turning clockwise from rest, A changed first
and B followed. Turning back, B changed first. The loop works that out
in two parts. First, how far did the pair move?

```python
while True:
    pair = (a.value(), b.value())
    now = CLOCKWISE.index(pair)
    if now != last:
        # How far round the loop did the pair move? 1 is one step
        # clockwise, 3 is one step back, and 2 is a jump across the loop.
        move = (now - last) % 4
        last = now
```

- `now` is the knob's position at this look.
- `if now != last:` means "only go on if the knob moved."
- `move = (now - last) % 4` counts the positions moved, going clockwise.
  `% 4` is the remainder after dividing by 4. It wraps the answer around
  the loop, the way a clock wraps from 12 to 1.

Second, which way was that? These lines come next, inside the same `if`:

```python
        if move == 1:
            steps += 1
            direction = "clockwise"
        elif move == 3:
            steps -= 1
            direction = "counter-clockwise"
        else:
            direction = "missed a step"
```

A `move` of 1 is one step clockwise, so `steps` goes up. A `move` of 3
is one step back, so `steps` goes down. On a loop of four, three steps
forward and one step back land in the same place.

Try it on your first lines:

| Line printed | Position | `move` |
|---|---|---|
| `A=1 B=1   at rest` | 2 | |
| `A=0 B=1   clockwise` | 3 | (3 - 2) % 4 = 1 |
| `A=0 B=0   clockwise` | 0 | (0 - 3) % 4 = 1 |

!!! mascot-encourage "Loop Math Takes Practice"
    ![Chrono encouraging](../../img/mascot/encouraging.png){ class="mascot-admonition-img" }
    If `(0 - 3) % 4 = 1` looks strange, that is normal. Put a finger on
    row 3 of the positions table and move one step clockwise. You wrap
    around to row 0, and that is all `% 4` is doing.

## Two Steps for Every Click

This knob clicks into place at position 0 and at position 2, where A
and B match. One click moves it from one resting place to the next,
which takes two steps. These lines, also inside the `if`, turn steps
into clicks:

```python
        # Round to the nearest whole click.
        per_click = config.ENCODER_STEPS_PER_CLICK
        clicks = (steps + per_click // 2) // per_click
```

- `config.ENCODER_STEPS_PER_CLICK` is 2 for this knob. Many knobs like
  it take 4, which is why it is a setting.
- `//` divides and throws away the remainder. With 2 steps per click,
  the last line works out to `(steps + 1) // 2`.
- The `+ 1` rounds a half-finished click up. That is why `steps=1` and
  `steps=2` both print `clicks=1`.

## Missed a Step

The loop ends with `time.sleep_ms(1)`, so it looks at the knob 1000
times a second. That is plenty for a slow turn. Spin the knob fast and
you will see this:

```text
A=0 B=0   clockwise           steps=2    clicks=1
A=1 B=1   missed a step       steps=2    clicks=1
A=0 B=1   clockwise           steps=3    clicks=2
```

Between two looks, the pair jumped from position 0 to position 2. Did
it go forward through 1, or backward through 3? There is no telling. It
is like blinking during a magic trick. The program leaves `steps`
alone, and the count is now wrong.

Lab 07 fixes this with **interrupts**, which let the Pico notice A or B
changing the moment it happens. The
[Rotary Encoder lesson in Learning MicroPython](https://dmccreary.github.io/learning-micropython/sensors/10-rotary-encoder/)
has more about this kind of knob.

!!! tip "Try This"
    1. Turn the knob exactly one click. How many lines print? Do A and B
       match on the last one?
    2. Spin the knob fast. How many `missed a step` lines can you get?
    3. Change `time.sleep_ms(1)` to `time.sleep_ms(20)`. Turn the knob at
       normal speed. Does `clicks` still match the clicks you feel?
       Put the 1 back when you are done.
    4. Change `per_click = config.ENCODER_STEPS_PER_CLICK` to
       `per_click = 4`. How many clicks must you feel now before
       `clicks` goes up by 1?

## If It Doesn't Work

- **Nothing prints when you turn the knob.** A and B are on the wrong
  pins. Check them against [How It Is Wired](index.md#how-it-is-wired).
- **Only A changes, or only B.** The one that never changes has its
  wire on the wrong pin.
- **It says clockwise when you turn the other way.** Swap the numbers of
  `ENCODER_A_PIN` and `ENCODER_B_PIN` in `config.py`.
- **`clicks` does not go up by one for each click you feel.** Count the
  lines one click prints. Set `ENCODER_STEPS_PER_CLICK` in `config.py`
  to that number.

!!! mascot-celebration "You Cracked the Knob's Code!"
    ![Chrono celebrating](../../img/mascot/celebration.png){ class="mascot-admonition-img" }
    You can now explain how two switches report a turn and its
    direction. You also know why this knob takes two steps per click.
    Next, you will put K0, PUSH, and the knob on the screen together.

**Next:** [Lab 07: Controls on the Screen](07-controls-display-test.md)
