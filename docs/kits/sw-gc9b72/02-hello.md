# Lab 02: Hello, World!

![The screen shows "Hello World!" in small white letters, "GC9B72" in big green letters, and a red ring around the edge](img/02-hello.png){ width="360" }

Programmers have a tradition: the first program in a new language, or on
a new gadget, says "Hello, World!" This lab puts it on your round screen,
along with a red ring around the edge.

!!! mascot-welcome "Welcome to Lab 02"
    ![Chrono waving welcome](../../img/mascot/welcome.png){ class="mascot-admonition-img" }
    This is the lab where the screen wakes up, and it's my favorite,
    because that screen is my face! Once you can put words and shapes
    anywhere you want, you can draw any watch face you can imagine.
    Let's make time tick!

## What You Will Learn

- how to start the display
- how to write text in two sizes
- how to draw a circle
- how pixel **coordinates** work on a round screen

## Run It

Open `02-hello.py` in Thonny and click **Run**. You should see the screen
from the picture above.

## The Code

```python
import config
import shapes

display = config.init_display()

display.fill(config.BLACK)

# The small font: 8 pixels wide, 16 tall.
config.centered_text(display, config.SMALL_FONT, "Hello World!", 150)

# The big font: 16 x 32, readable from across the room.
config.centered_text(display, config.BIG_FONT, "GC9B72", 175, config.GREEN)

shapes.ring(display, config.CENTER_X, config.CENTER_Y,
            config.SAFE_RADIUS, config.RED, 2)
```

- `import config` borrows the kit's settings file. It knows which pins the
  display uses, so your program doesn't have to.
- `config.init_display()` wakes up the display and gives it a name,
  `display`.
- `display.fill(config.BLACK)` paints every pixel black.
- `config.centered_text(...)` writes words in the middle of the screen.
  The number at the end (150, then 175) is how far down the screen the
  words go.
- `shapes.ring(...)` draws a circle 2 pixels thick.

## Where Is Everything? Coordinates

Every pixel has an address made of two numbers, **x** and **y**:

- **x** counts across, from 0 at the left edge to 359 at the right.
- **y** counts *down*, from 0 at the top to 359 at the bottom.

That second one surprises people: on a screen, bigger y means **lower**,
not higher. The center of the screen is at x = 180, y = 180. That's what
`config.CENTER_X` and `config.CENTER_Y` hold.

!!! note "The corners are missing!"
    The display chip thinks the screen is a 360 × 360 square. But the
    glass is round, so the corners of that square are hidden. Anything you
    draw in a corner is never seen. The red ring shows the biggest circle
    you can see all of. Its size, 168 pixels from the center, is saved in
    `config.SAFE_RADIUS`.

## Two Font Sizes

There's no built-in lettering on this display, so the kit brings two
**fonts**, sets of pictures of letters:

| Font | Each letter is | Letters across the screen |
|---|---|---|
| `config.SMALL_FONT` | 8 × 16 pixels | 45 |
| `config.BIG_FONT` | 16 × 32 pixels | 22 |

!!! tip "Try This"
    1. Change `"Hello World!"` to your own name.
    2. Change `config.GREEN` to `config.YELLOW`, `config.CYAN`, or
       `config.MAGENTA`.
    3. Make your own color with `config.color565(255, 128, 0)`. The three
       numbers are how much **red**, **green**, and **blue** to mix, from 0
       to 255. What color is `(255, 128, 0)`?
    4. Change the 150 to 100. Where do the words move?

## If It Doesn't Work

- **The screen stays black.** Check the display's wires against the
  wiring table on the [kit's main page](index.md). The most common mistake
  is swapping the SCL and SDA wires.
- **`ImportError: no module named 'gc9b72'`.** The `lib` folder with the
  display driver isn't on the Pico yet.

**Next:** [Lab 03: A Digital Clock](03-digital-clock.md)
