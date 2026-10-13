"""Run the rect-tft-display kit's real labs on a simulated Pico.

This is a thin layer over the GC9B72 simulator next door
(../gc9b72/gc9b72_sim). That simulator already has the fake Pico, the
fake clock, the SPI decoder, and the stand-ins for WiFi and framebuf.
This file changes only what is different about this kit:

  - the screen is 160 x 128 and rectangular
  - the driver is lib/st7735s.py
  - it has a rotary knob, so interrupts fire on both edges, and turns of
    the knob can be scripted
  - pictures are drawn as a plain rectangle, not a round watch

    import st7735s_sim as sim
    sim.use_kit("src/kits/rect-tft-display")
    ns, shots, final = sim.shots("12-set-time.py", 3000,
                                 presses=[("push", 1000, 1100)],
                                 turns=[(1500, 3)], at=[2500])
    sim.save_png(shots[0], "set-hour.png")

Buttons are named "push" (pressing the knob) and "k0". A turn is
(start_ms, clicks): positive is clockwise.
"""

import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.dont_write_bytecode = True
sys.path.insert(0, os.path.join(HERE, "..", "gc9b72"))

from gc9b72_sim import hardware, runner, pico2w   # noqa: E402,F401
from PIL import Image                               # noqa: E402

W, H = 160, 128
hardware.W, hardware.H = W, H
hardware.screen.clear()
Pin = hardware.Pin


# MicroPython's irq() takes the handler first, and an interrupt can fire
# on either edge. The handler runs after the pin has its new value.
def _irq(self, handler=None, trigger=Pin.IRQ_FALLING | Pin.IRQ_RISING, **kwargs):
    self.handler = handler
    self.trigger = trigger


def _set_level(self, v):
    old, self.v = self.v, v
    if old != v and getattr(self, "handler", None):
        trigger = getattr(self, "trigger", Pin.IRQ_FALLING)
        if (v == 0 and trigger & Pin.IRQ_FALLING) or (v == 1 and trigger & Pin.IRQ_RISING):
            self.handler(self)


Pin.irq = _irq
Pin.set_level = _set_level

# ---------------------------------------------------------------------------
# The knob
# ---------------------------------------------------------------------------
# The four positions of (A, B) in clockwise order, as in the kit's lab 06.
_LOOP = ((0, 0), (1, 0), (1, 1), (0, 1))
_knob = {}                  # "a" / "b" -> Pin
_events = []                # (ms, "a" or "b", level)
_position = [2]             # index into _LOOP: at rest with A and B both 1

_real_tick = runner._tick


def _tick():
    _real_tick()
    t = runner.state["ms"]
    while _events and _events[0][0] <= t:
        _, name, level = _events.pop(0)
        if name in _knob:
            _knob[name].set_level(level)


runner._tick = _tick


def _queue_turn(start_ms, clicks, step_ms=6):
    """Two steps of (A, B) per click, like the kit's real knob."""
    t = start_ms
    for _ in range(abs(clicks) * 2):
        new = (_position[0] + (1 if clicks > 0 else -1)) % 4
        for name, old, now in (("a", _LOOP[_position[0]][0], _LOOP[new][0]),
                               ("b", _LOOP[_position[0]][1], _LOOP[new][1])):
            if old != now:
                _events.append((t, name, now))
        _position[0] = new
        t += step_ms
    _events.sort()


# ---------------------------------------------------------------------------
# Choosing the kit and running labs
# ---------------------------------------------------------------------------
def use_kit(path):
    """Point the simulator at the kit folder: its labs, config.py, and lib/."""
    path = os.path.abspath(path)
    if not os.path.exists(os.path.join(path, "lib", "st7735s.py")):
        raise FileNotFoundError("no lib/st7735s.py in " + path)
    runner.KIT = hardware.KIT = path
    sys.path[:0] = [path, os.path.join(path, "lib")]

    # Watch the driver to learn which pin is its DC line.
    import st7735s
    real_init = st7735s.ST7735S.__init__

    def init(self, spi=None, dc=None, *args, **kwargs):
        hardware.screen.dc_pin = dc
        real_init(self, spi, dc, *args, **kwargs)
    st7735s.ST7735S.__init__ = init

    # Watch config.init_controls() to learn which pin is which control.
    import config
    real_controls = config.init_controls

    def init_controls():
        a, b, push, k0 = real_controls()
        a.v = b.v = 1
        _knob.update(a=a, b=b)
        runner.state["pins"].update(push=push, k0=k0)
        return a, b, push, k0
    config.init_controls = init_controls
    return path


def shots(lab, limit_ms, presses=(), turns=(), at=(), start=None):
    """Run a lab on the fake clock. Returns (the lab's globals, the
    screens at the `at` times in order, the final screen)."""
    _knob.clear()
    del _events[:]
    _position[0] = 2
    for start_ms, clicks in turns:
        _queue_turn(start_ms, clicks)
    here = os.getcwd()
    os.chdir(runner.KIT)        # some labs look for kit files by relative path
    try:
        ns, snaps = runner.run_lab(lab, limit_ms, presses, at, start)
    finally:
        os.chdir(here)
    return ns, [snaps[t] for t in sorted(snaps)], list(hardware.screen.px)


# ---------------------------------------------------------------------------
# Pictures
# ---------------------------------------------------------------------------
SCALE = 2
BEZEL = 8
BEZEL_COLOR = (45, 45, 50)


def to_rgb(px):
    """RGB565 pixel values -> (r, g, b) tuples."""
    return [(((p >> 11) & 31) * 255 // 31, ((p >> 5) & 63) * 255 // 63,
             (p & 31) * 255 // 31) for p in px]


def screen_image(px, scale=SCALE, bezel=BEZEL):
    """The screen, enlarged, inside a dark frame like the edge of the glass."""
    img = Image.new("RGB", (W, H))
    img.putdata(to_rgb(px))
    img = img.resize((W * scale, H * scale), Image.NEAREST)
    out = Image.new("RGB", (W * scale + 2 * bezel, H * scale + 2 * bezel), BEZEL_COLOR)
    out.paste(img, (bezel, bezel))
    return out


def save_png(px, path):
    os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
    screen_image(px).save(path, optimize=True)
    print("wrote", path)


def save_gif(frames, path, ms=800):
    """An animated GIF, ms milliseconds per frame, looping forever."""
    os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
    imgs = [screen_image(px).convert("P", palette=Image.ADAPTIVE, colors=128)
            for px in frames]
    imgs[0].save(path, save_all=True, append_images=imgs[1:], duration=ms,
                 loop=0, optimize=True)
    print("wrote", path, "(%d frames)" % len(frames))
