"""Answers a real Raspberry Pi Pico 2 W gave, for programs that inspect
the board itself -- like the sw-gc9b72 kit's 01-probe.py.

    from gc9b72_sim import pico2w
    pico2w.pretend()

These are the values measured on a Pico 2 W running MicroPython 1.29.0.
The unique ID and MAC address are made up, so documentation never shows
a real board's identity.
"""

import gc
import os
import sys
import types

from . import hardware

FLASH_BYTES = 4 * 1024 * 1024


class _Mem8:
    """Reads of the flash window at 0x10000000. A 4 MB chip ignores the
    address bits it doesn't have, so reads 'wrap around' every 4 MB --
    the trick 01-probe.py uses to measure the chip."""

    def __getitem__(self, addr):
        return (addr - 0x10000000) % FLASH_BYTES * 7 % 251


class _ADC:
    def __init__(self, channel):
        self.channel = channel

    def read_u16(self):
        return 13987            # the temperature sensor at about 28 C


class _Uname:
    sysname = nodename = "rp2"
    release = "1.29.0"
    version = "v1.29.0 on 2026-08-24"
    machine = "Raspberry Pi Pico 2 W with RP2350"


def pretend(fill_us=None):
    """Install the board's answers into the fake machine, rp2, os, sys,
    and gc modules.

    fill_us: if given, time.ticks_us() moves forward exactly this much
    per call, so a program that times a full-screen fill reports the real
    board's figure (131_300 us at 24 MHz) instead of how long the
    simulator took."""
    if fill_us:
        import time
        clock = [0]

        def ticks_us():
            clock[0] += fill_us
            return clock[0]
        time.ticks_us = ticks_us
    m = hardware.machine
    m.freq = lambda *a: 150_000_000
    m.unique_id = lambda: bytes.fromhex("e6614103abcd1234")
    m.PWRON_RESET, m.WDT_RESET = 1, 3
    m.reset_cause = lambda: 1
    m.mem8 = _Mem8()
    m.ADC = _ADC
    rp2 = types.ModuleType("rp2")
    rp2.bootsel_button = lambda: 0
    sys.modules["rp2"] = rp2
    sys.implementation._machine = _Uname.machine
    sys.implementation._build = "RPI_PICO2_W"
    os.uname = lambda: _Uname()
    os.statvfs = lambda p: (4096, 4096, 640, 623, 623, 0, 0, 0, 0, 255)
    os.ilistdir = lambda p="/": iter([])
    gc.mem_free = lambda: 431_616
    gc.mem_alloc = lambda: 15_040
