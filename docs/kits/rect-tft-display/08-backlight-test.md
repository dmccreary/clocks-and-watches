# Lab 08: Test the Backlight

![A white screen with black words: "Backlight Test" and, below it, "BLK on GP7"](img/08-backlight-test.png){ width="336" }

The wire that switches the light inside the screen has not been tested
yet. This lab blinks that light five times. The picture shows the bright
half of a blink. In the dark half, the whole screen goes black.

!!! mascot-welcome "Welcome to Lab 08"
    ![Chrono waving welcome](../../img/mascot/welcome.png){ class="mascot-admonition-img" }
    This quick lab is the last test before your kit becomes a clock. You
    will also find out where the light in a screen really comes from.
    Let's make time tick!

## What You Will Learn

- what a **backlight** is, and why this screen needs one
- how the Pico switches it on and off
- how a blink can prove that a wire is in the right place

## Run It

1. Open `08-backlight-test.py` in Thonny and click **Run**.
2. The screen turns white, with `Backlight Test` and `BLK on GP7` in
   black letters.
3. Watch the screen and the shell together. The screen goes dark each
   time the shell prints `backlight OFF`.

```text
08-backlight-test.py v1.1
backlight OFF
backlight ON
backlight OFF
backlight ON
backlight OFF
backlight ON
backlight OFF
backlight ON
backlight OFF
backlight ON
Done. The backlight is on.
```

## A Light Behind Tiny Shutters

Your screen is an **LCD**, short for *liquid crystal display*. An LCD
makes no light of its own. Its picture is a layer of tiny shutters, and
behind them sits a white light called the **backlight**.

Think of a stained-glass window at night. The picture is still in the
glass, but you cannot see it with no light behind it. Switching off the
backlight does the same to your screen.

```python
for i in range(5):
    print("backlight OFF")
    config.set_backlight(False)
    time.sleep(1)
    print("backlight ON")
    config.set_backlight(True)
    time.sleep(1)
```

- `for i in range(5):` repeats the six lines under it five times.
- `config.set_backlight(False)` puts a 0 on the Pico's pin GP7, and the
  light goes out. `True` puts a 1 there, and the light comes back.
- `time.sleep(1)` gives you one second to look.

## What the Blink Proves

A wire runs from the display's **BLK** pin to GP7 on the Pico, as
[How It Is Wired](index.md#how-it-is-wired) shows. If the screen goes
dark in step with the shell, that wire is in the right place.

!!! tip "Try This"
    1. Change `range(5)` to `range(10)` for ten blinks.
    2. Change both `time.sleep(1)` lines to `time.sleep(0.2)`. How fast
       does it blink now?
    3. Change `display.fill(config.WHITE)` to
       `display.fill(config.BLACK)`. In a dim room, is black just as
       dark with the backlight on as with it off?

## If It Doesn't Work

- **The screen stays lit the whole time.** BLK is not on GP7. Many
  display boards light up by themselves when nothing drives BLK. So a
  wrong pin looks like "always on." Move the wire to GP7.

!!! mascot-celebration "Backlight Tested!"
    ![Chrono celebrating](../../img/mascot/celebration.png){ class="mascot-admonition-img" }
    You know what a backlight is, and you proved that pin GP7 switches
    yours. Next, your kit becomes a real clock!

**Next:** [Lab 09: A Digital Clock](09-digital-clock.md)
