# Lab 03: Hello, World!

![A black screen with a thin white line around its edge. "Hello World!" is at the top in small white letters, and "ST7735S" is below it in big green letters. Under them are three colored bars, red, green and blue, each with its name below it in tiny white letters: RED, GREEN, BLUE.](img/03-hello-world.png){ width="336" }

Programmers have a tradition. The first program on a new gadget says
hello to the world. This lab puts "Hello World!" on your screen, with a
white line around the edge and three colored bars.

The picture is also a test. It checks three screen settings that nobody
can know until a real picture is on the glass.

!!! mascot-welcome "Welcome to Lab 03"
    ![Chrono waving welcome](../../img/mascot/welcome.png){ class="mascot-admonition-img" }
    This is the lab where the screen wakes up and says its first words.
    Once you can put words and shapes anywhere you like, you can draw any
    clock face you can imagine. Let's make time tick!

## What You Will Learn

- how **coordinates**, the two numbers that say where a dot goes, work
- how to write text in three sizes
- why a drawing shows up the moment you ask for it
- how to fix a picture that is upside down, shifted, or the wrong color

## Run It

1. Hold the kit so the knob is on the right.
2. Open `03-hello-world.py` in Thonny.
3. Click **Run**.
4. Compare the screen with the picture above. Look for the white line on
   all four edges, and for RED, GREEN, BLUE in that order.

The shell prints:

```text
03-hello-world.py v1.1
Check the screen: a white border, Hello World!, and red, green
and blue bars from left to right.
```

## Where Is Everything? Coordinates

The screen is made of tiny dots called **pixels**: 160 across and 128
down. Every pixel has an address made of two numbers, x and y:

- **x** counts across, from 0 at the left edge to 159 at the right.
- **y** counts *down*, from 0 at the top to 127 at the bottom.

So bigger y means **lower**, not higher. The turtle's `goto(x, y)` in
[chapter 7 of Learning Python](https://dmccreary.github.io/learning-python/chapters/07-for-loops-and-shapes/)
worked the other way, with y going up.

The program starts by painting the screen black and drawing the line:

```python
display = config.init_display()

display.fill(config.BLACK)

# A white line one pixel thick around the very edge of the screen.
display.rect(0, 0, config.WIDTH, config.HEIGHT, config.WHITE)
```

- `config.init_display()` wakes up the screen and names it `display`.
- `display.fill(config.BLACK)` paints every pixel black.
- `display.rect(...)` draws the outline of a rectangle. It starts at
  x = 0, y = 0, the top-left corner. It is 160 wide and 128 tall, so it
  runs along all four edges.

## Three Sizes of Letters

This screen has no lettering built in. The kit brings three **fonts**,
which are sets of pictures of letters:

| Font | Each letter is | Letters across the screen |
|---|---|---|
| `config.TINY_FONT` | 8 × 8 pixels | 20 |
| `config.SMALL_FONT` | 8 × 16 pixels | 20 |
| `config.BIG_FONT` | 16 × 32 pixels | 10 |

The two lines of words use two of them:

```python
# The small font: 8 pixels wide, 16 tall.
config.centered_text(display, config.SMALL_FONT, "Hello World!", 8)

# The big font: 16 x 32, readable from across the room.
config.centered_text(display, config.BIG_FONT, "ST7735S", 28, config.GREEN)
```

`config.centered_text()` needs the display, a font, the words, and y.
The y is the row where the tops of the letters go. A color at the end is
extra: leave it out and you get white.

The function works out x for you. "Hello World!" is 12 characters long,
counting the space and the exclamation mark. At 8 pixels each, that is
96 pixels. That leaves 160 - 96 = 64 pixels. Half go on each side, so
the words start at x = 32.

ST7735S is the name of the chip that runs your screen.

## No show() Needed

Some screens make you call `show()` before anything appears. This one
does not. Each drawing line goes straight down the wires, like paint
going straight onto a wall. It is on the glass before the next line
runs. The loop that draws the bars works that way:

```python
font = config.TINY_FONT
x = (config.WIDTH - 3 * BAR_WIDTH - 2 * GAP) // 2
for label, color in BARS:
    display.fill_rect(x, 68, BAR_WIDTH, BAR_HEIGHT, color)
    label_x = x + (BAR_WIDTH - len(label) * font.WIDTH) // 2
    display.text(font, label, label_x, 106, config.WHITE, config.BLACK)
    x += BAR_WIDTH + GAP
```

- The second line centers the three bars. The first one starts at
  x = 10.
- The `for` loop runs once for each name and color in `BARS`.
- `display.fill_rect(...)` draws a solid bar at x, 68 pixels down.
- `display.text(...)` writes the name under the bar, at `label_x`. It
  takes a font first, then the words, x, y, and two colors.
- `x += BAR_WIDTH + GAP` moves 50 pixels right for the next bar.

## Three Settings to Check

Screens of this kind are not all built alike, so `config.py` has four
lines to match yours:

```python
ROTATION = 1
X_OFFSET = 0
Y_OFFSET = 0
BGR = False
```

These values are right for this kit's screen. If your picture looks
wrong, change one setting, save `config.py` to the Pico, and run again:

| If you see this | Change this |
|---|---|
| the picture is upside down | `ROTATION = 3` |
| one side of the white line is missing, or an edge has a strip of colored specks | `X_OFFSET` or `Y_OFFSET` to 1, then 2 |
| the RED bar is blue and the BLUE bar is red | `BGR = True` |

BGR stands for blue, green, red: the same colors in the opposite order.

!!! tip "Try This"
    1. Change `"Hello World!"` to your own name. Up to 19 letters fit
       inside the white line.
    2. Change `config.GREEN` to `config.YELLOW`, or mix your own color
       with `config.color565(255, 128, 0)`. The numbers are red, green,
       and blue.
    3. Change the 28 in the `"ST7735S"` line to 34. Which way do the big
       letters move?
    4. Add `import time` under `import config`. Then add `time.sleep(1)`
       as a new last line inside the `for` loop, lined up with the line
       above it. Watch the bars arrive one at a time.

## If It Doesn't Work

- **The screen stays dark.** Check the screen's wires against
  [How It Is Wired](index.md#how-it-is-wired).
- **`ImportError: no module named 'st7735s'`.** The `lib` folder is not
  on the Pico yet. See [Before You Start](index.md#before-you-start).

!!! mascot-celebration "Hello, Screen!"
    ![Chrono celebrating](../../img/mascot/celebration.png){ class="mascot-admonition-img" }
    You can now start the screen, place anything by its x and y, and
    write text in three sizes. You also know which settings fix a
    picture that looks wrong. Next, you will test the K0 button.

**Next:** [Lab 04: Test the K0 Button](04-button-test.md)
