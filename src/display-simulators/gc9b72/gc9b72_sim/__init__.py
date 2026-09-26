"""A desktop simulator for the GC9B72 360x360 round display.

It runs a kit's real MicroPython labs in CPython, through the kit's own
lib/gc9b72.py driver, and captures every pixel the driver sends. Use it to
make documentation images and to check labs without a board.

    from gc9b72_sim import runner, render
    runner.use_kit("src/kits/sw-gc9b72")
    ns, snaps = runner.run_lab("02-hello.py", 2000)
    render.save_png(runner.screen.px, "docs/kits/sw-gc9b72/img/02-hello.png")

Importing this package replaces machine, network, time.ticks_ms, and
friends for the whole Python process -- run it in its own process, not
inside other code.
"""

from . import hardware, runner, render      # noqa: F401  (installs the fakes)
from .runner import use_kit, run_lab, screen, Stop, START   # noqa: F401
