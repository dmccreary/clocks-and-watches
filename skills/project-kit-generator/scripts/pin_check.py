#!/usr/bin/env python3
"""pin_check.py -- catch pin mistakes in a kit's config.py BEFORE anyone wires anything.

    python3 pin_check.py path/to/config.py [--allow NAME_A=NAME_B ...] [--markdown]

What it checks (Raspberry Pi Pico / RP2040 pin functions):
  * every *_PIN setting is a real GPIO number, and no two settings use the same GPIO
    (unless you list them with --allow, for pins that are meant to share a net)
  * if the config has I2C_BUS + I2C_SDA_PIN + I2C_SCL_PIN, the pins are valid for that
    I2C bus; if it has SPI_ID + SCK_PIN + MOSI_PIN (+ MISO_PIN), they are valid for that
    SPI bus
  * prints a table with the physical Pico pin number for each GPIO, ready to paste into
    the kit README and lesson (--markdown)

Why: on the SHT40 display kit the NeoPixel lab and the display's SPI clock both wanted
GP2. That was only noticed by reading two files side by side. This finds it in a second.

For a board other than a Pico, treat the function tables below as a starting point and
check the datasheet.
"""
import sys, types, importlib.util

# GPIO number -> physical pin on a Raspberry Pi Pico (GP23-25 are not on the header)
PHYSICAL = {0: 1, 1: 2, 2: 4, 3: 5, 4: 6, 5: 7, 6: 9, 7: 10, 8: 11, 9: 12, 10: 14, 11: 15,
            12: 16, 13: 17, 14: 19, 15: 20, 16: 21, 17: 22, 18: 24, 19: 25, 20: 26, 21: 27,
            22: 29, 26: 31, 27: 32, 28: 34,
            25: "onboard LED"}      # GP25 is the LED on a plain Pico; it has no header pin
GND_PINS = (3, 8, 13, 18, 23, 28, 33, 38)

# RP2040 GPIO function table (datasheet, "GPIO Functions")
I2C = {0: {"SDA": {0, 4, 8, 12, 16, 20}, "SCL": {1, 5, 9, 13, 17, 21}},
       1: {"SDA": {2, 6, 10, 14, 18, 26}, "SCL": {3, 7, 11, 15, 19, 27}}}
SPI = {0: {"SCK": {2, 6, 18}, "MOSI": {3, 7, 19}, "MISO": {0, 4, 16}},
       1: {"SCK": {10, 14, 26}, "MOSI": {11, 15, 27}, "MISO": {8, 12, 28}}}


class _Stub(types.ModuleType):
    """Stands in for machine, gc9a01, fonts... so config.py imports even off the board."""
    def __getattr__(self, name):
        if name.startswith("__"):
            raise AttributeError(name)
        return _Stub(name)
    def __call__(self, *a, **k):
        return _Stub("call")


def load_config(path):
    for _ in range(12):
        spec = importlib.util.spec_from_file_location("kit_config", path)
        mod = importlib.util.module_from_spec(spec)
        try:
            spec.loader.exec_module(mod)
            return mod
        except ImportError as e:
            missing = getattr(e, "name", None)
            if not missing:
                raise
            sys.modules[missing] = _Stub(missing)       # stub it and try again
    raise SystemExit("could not import %s" % path)


def main(argv):
    if len(argv) < 2:
        raise SystemExit(__doc__)
    path = argv[1]
    allow = set()
    for i, a in enumerate(argv):
        if a == "--allow" and i + 1 < len(argv):
            allow.add(frozenset(argv[i + 1].split("=")))
    markdown = "--markdown" in argv
    cfg = load_config(path)

    pins = {n: v for n, v in vars(cfg).items()
            if n.endswith("_PIN") and isinstance(v, int) and not isinstance(v, bool)}
    problems = []

    # 1. real GPIOs, no duplicates
    by_gpio = {}
    for n, v in sorted(pins.items(), key=lambda kv: kv[1]):
        if v not in PHYSICAL:
            problems.append("%s = %d is not a usable GPIO on a Pico (GP23 and GP24 are internal; a Pico W's LED is not GP25)" % (n, v))
        by_gpio.setdefault(v, []).append(n)
    for gpio, names in by_gpio.items():
        if len(names) > 1 and not any(frozenset(pair) in allow
                                      for pair in [(a, b) for a in names for b in names if a != b]):
            problems.append("GP%d is used by more than one setting: %s" % (gpio, ", ".join(names)))

    # 2. peripheral pin validity
    def check(kind, table, bus, roles):
        for role, name in roles:
            v = getattr(cfg, name, None)
            if v is None:
                continue
            if v not in table[bus][role]:
                problems.append("%s%d %s on GP%d (%s) is not valid. Valid GPIOs: %s"
                                % (kind, bus, role, v, name, sorted(table[bus][role])))
    if hasattr(cfg, "I2C_BUS") and cfg.I2C_BUS in I2C:
        check("I2C", I2C, cfg.I2C_BUS, [("SDA", "I2C_SDA_PIN"), ("SCL", "I2C_SCL_PIN")])
    if hasattr(cfg, "SPI_ID") and cfg.SPI_ID in SPI:
        check("SPI", SPI, cfg.SPI_ID, [("SCK", "SCK_PIN"), ("MOSI", "MOSI_PIN"), ("MISO", "MISO_PIN")])

    # 3. the table
    print("| Setting | GPIO | Physical pin |" if markdown else "%-22s %-6s %s" % ("setting", "GPIO", "physical pin"))
    if markdown:
        print("|---------|------|--------------|")
    for n, v in sorted(pins.items(), key=lambda kv: PHYSICAL.get(kv[1], 99) if isinstance(PHYSICAL.get(kv[1], 99), int) else 90):
        pin = PHYSICAL.get(v, "?")
        print(("| %s | GP%d | %s |" % (n, v, pin)) if markdown else "%-22s GP%-4d %s" % (n, v, pin))
    print("\nGND pins on a Pico: %s" % ", ".join(str(p) for p in GND_PINS))
    used = sorted(PHYSICAL[v] for v in pins.values() if isinstance(PHYSICAL.get(v), int))
    if used:
        run = []
        for p in used:
            if run and p != run[-1] + 1:
                run = [p]
            else:
                run.append(p)
        print("Physical pins in use: %s" % ", ".join(str(p) for p in used))

    if problems:
        print("\nPROBLEMS (%d):" % len(problems))
        for p in problems:
            print("  -", p)
        return 1
    print("\nOK: no duplicate GPIOs and every bus pin is valid for its peripheral.")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
