"""
MicroPython driver for the GalaxyCore GC9B72 SPI display controller.

The GC9B72 drives 2.1" round SPI TFT panels (silkscreen: "Driver IC:
GC9B72", "Resolution: 360x360") sold on AliExpress/Amazon under generic
names. There was no public MicroPython driver for this chip at the time
this was written -- only a C++ Arduino_GFX driver, MaliosDark/Arduino_GC9B72
(MIT), whose author ported the register init sequence from the xboot
project's fb-gc9b72.c, "the only known-good public GC9B72 init." The
init sequence below is that same sequence, translated to MicroPython.

Everything else about this driver follows the shape of Russ Hughes'
GC9A01 driver already vendored in this repo (lib/gc9a01.py), so labs
written for one round display port easily to the other. Like the GC9A01,
this chip has no frame buffer: every drawing call streams straight over
SPI, and there is no show().
"""

import time
from micropython import const
import ustruct as struct

_SLPIN = const(0x10)
_SLPOUT = const(0x11)
_DISPON = const(0x29)
_CASET = const(0x2A)
_RASET = const(0x2B)
_RAMWR = const(0x2C)
_COLMOD = const(0x3A)
_MADCTL = const(0x36)

# Color definitions
BLACK = const(0x0000)
BLUE = const(0x001F)
RED = const(0xF800)
GREEN = const(0x07E0)
CYAN = const(0x07FF)
MAGENTA = const(0xF81F)
YELLOW = const(0xFFE0)
WHITE = const(0xFFFF)

_BUFFER_PIXELS = const(256)

# MADCTL values for the four rotations the upstream Arduino driver
# confirms. The GC9B72 has no documented mirrored modes beyond these.
_ROTATIONS = (
    0x00,        # 0 - normal
    0x20 | 0x40,  # 1 - MV | MX
    0x40 | 0x80,  # 2 - MX | MY
    0x20 | 0x80,  # 3 - MV | MY
)


def color565(red, green=0, blue=0):
    """Convert red, green, blue (0-255) into a 16-bit 565 encoded color."""
    try:
        red, green, blue = red  # see if the first arg is a tuple/list
    except TypeError:
        pass
    return (red & 0xF8) << 8 | (green & 0xFC) << 3 | blue >> 3


def _encode_pos(a, b):
    return struct.pack(">HH", a, b)


def _encode_pixel(color):
    return struct.pack(">H", color)


class GC9B72:
    """
    GC9B72 driver class for 360x360 round SPI TFT panels.

    Args:
        spi (SPI): configured SPI bus (required)
        dc (Pin): data/command pin (required)
        cs (Pin): chip-select pin (optional)
        reset (Pin): reset pin (optional but strongly recommended)
        backlight (Pin): backlight pin (optional)
        rotation (int): 0-3, see _ROTATIONS
    """

    def __init__(
            self,
            spi=None,
            dc=None,
            cs=None,
            reset=None,
            backlight=None,
            rotation=0):
        if spi is None:
            raise ValueError("SPI object is required.")
        if dc is None:
            raise ValueError("dc pin is required.")

        self.width = 360
        self.height = 360
        self.spi = spi
        self.dc = dc
        self.cs = cs
        self.reset = reset
        self.backlight = backlight
        self._rotation = rotation % 4

        self.hard_reset()
        time.sleep_ms(120)

        # Register init sequence ported from the xboot project's
        # fb-gc9b72.c reference driver. Every value below is
        # vendor-specific and undocumented in any public datasheet --
        # don't "clean up" the magic numbers, there is nothing to check
        # them against.
        self._write(0xFE)
        self._write(0xEF)
        self._write(0x80, b'\x19')
        self._write(0x82, b'\x09')
        self._write(0x83, b'\x03')
        self._write(0x88, b'\x00')
        self._write(0x89, b'\x38')
        self._write(0x8A, b'\x40')
        self._write(0x8B, b'\x0A')
        self._write(0x8C, b'\x00')
        self._write(0x81, b'\xFF')
        self._write(0x84, b'\xFF')
        self._write(0x85, b'\xFF')
        self._write(0x86, b'\xFF')
        self._write(0x87, b'\xFF')
        self._write(0x8E, b'\xFF')
        self._write(0x8F, b'\xFF')
        self._write(0x98, b'\x3E')
        self._write(0x99, b'\x3E')
        self._write(0x7D, b'\x72')
        self._write(0x70, b'\x02\x03\x03\x06\x03\x03\x09\x07\x09\x03')
        self._write(0x90, b'\x06\x06\x01\x01')
        self._write(0x93, b'\x02\xFF\x00')
        self._write(0xCB, b'\x02')
        self._write(0xFB, b'\x00\x00')
        self._write(0xF6, b'\xC0')
        self._write(0x6C, b'\x00\x00\x22\x00\xCC\x04\x58')
        self._write(0xAA, b'\x0B\x00')
        self._write(0xEC, b'\x07')
        self._write(0xF9, b'\x40')
        self._write(0xEB, b'\x01\x67')
        self._write(0x74, b'\x01\x60\x00\x00\x00\x00')
        self._write(0xB5, b'\x14\x14\x14')
        self._write(0x6E, b'\x0B\x0B\x09\x09\x13\x13\x11\x11'
                           b'\x16\x15\x01\x04\x00\x0D\x1D\x00'
                           b'\x00\x1D\x0D\x00\x04\x08\x15\x16'
                           b'\x12\x12\x14\x14\x0A\x0A\x0C\x0C')
        self._write(0x60, b'\x38\x1C\x13\x56')
        self._write(0x61, b'\xF8\x0A\x13\x56')
        self._write(0x62, b'\xF8\x0B\x13\x56')
        self._write(0x63, b'\x38\x1C\x13\x56')
        self._write(0x64, b'\x38\x20\x72\xF8\x13\x56')
        self._write(0x65, b'\x78\x1A\x70\x0B\x56\x13')
        self._write(0x66, b'\x38\x24\x72\xFC\x13\x56')
        self._write(0x68, b'\xB3\x08\x0E\x08\x0E\x0A\x0A')
        self._write(0x69, b'\xB3\x08\x0E\x08\x0E\x0A\x0A')
        self._write(0x6A, b'\x00\x00')
        self._write(_COLMOD, b'\x05')  # 16 bits/pixel, RGB565
        self._write(_MADCTL, b'\x00')  # overwritten by rotation() below
        self._write(0x7C, b'\xB6\x29')
        self._write(0xAC, b'\x40')
        self._write(0xC3, b'\x1A')
        self._write(0xC4, b'\x24')
        self._write(0xC9, b'\x2F')
        self._write(0xF0, b'\x11\x17\x08\x06\x05\x38')
        self._write(0xF1, b'\x4D\x72\x72\x2D\x34\x8F')
        self._write(0xF2, b'\x11\x17\x08\x06\x05\x38')
        self._write(0xF3, b'\x4D\x72\x72\x2D\x34\x8F')
        self._write(0xB4, b'\x0A')
        self._write(0x35, b'\x00')
        self._write(0xFE)
        self._write(0xEE)

        self._write(_SLPOUT)
        time.sleep_ms(120)
        self._write(_DISPON)
        time.sleep_ms(20)

        self.rotation(self._rotation)

        if backlight is not None:
            backlight.value(1)

    def _write(self, command=None, data=None):
        """SPI write to the device: a command byte, then optional data."""
        if self.cs:
            self.cs.off()

        if command is not None:
            self.dc.off()
            self.spi.write(bytes([command]))
        if data is not None:
            self.dc.on()
            self.spi.write(data)

        if self.cs:
            self.cs.on()

    def hard_reset(self):
        """Toggle the RST pin. Skipped if no reset pin was given."""
        if self.reset:
            if self.cs:
                self.cs.off()

            self.reset.on()
            time.sleep_ms(50)
            self.reset.off()
            time.sleep_ms(50)
            self.reset.on()
            time.sleep_ms(150)

            if self.cs:
                self.cs.on()

    def sleep_mode(self, value):
        """Enable (True) or disable (False) display sleep mode."""
        self._write(_SLPIN if value else _SLPOUT)

    def rotation(self, rotation):
        """Set display rotation: 0-3, see _ROTATIONS."""
        self._rotation = rotation % 4
        self._write(_MADCTL, bytes([_ROTATIONS[self._rotation]]))

    def _set_window(self, x0, y0, x1, y1):
        self._write(_CASET, _encode_pos(x0, x1))
        self._write(_RASET, _encode_pos(y0, y1))
        self._write(_RAMWR)

    def pixel(self, x, y, color):
        """Draw a single pixel."""
        self._set_window(x, y, x, y)
        self._write(None, _encode_pixel(color))

    def blit_buffer(self, buffer, x, y, width, height):
        """Copy a buffer of 565-encoded pixels to the display."""
        self._set_window(x, y, x + width - 1, y + height - 1)
        self._write(None, buffer)

    def line(self, x0, y0, x1, y1, color):
        """
        Draw a single pixel wide line from (x0, y0) to (x1, y1), one
        pixel() call per step (Bresenham's algorithm). Slower than a run
        of hline()/vline() calls, but the only way to draw anything at an
        angle -- shapes.poly() and face.py's eyebrows both need it.
        """
        steep = abs(y1 - y0) > abs(x1 - x0)
        if steep:
            x0, y0 = y0, x0
            x1, y1 = y1, x1
        if x0 > x1:
            x0, x1 = x1, x0
            y0, y1 = y1, y0
        dx = x1 - x0
        dy = abs(y1 - y0)
        err = dx // 2
        ystep = 1 if y0 < y1 else -1
        while x0 <= x1:
            if steep:
                self.pixel(y0, x0, color)
            else:
                self.pixel(x0, y0, color)
            err -= dy
            if err < 0:
                y0 += ystep
                err += dx
            x0 += 1

    def hline(self, x, y, length, color):
        self.fill_rect(x, y, length, 1, color)

    def vline(self, x, y, length, color):
        self.fill_rect(x, y, 1, length, color)

    def rect(self, x, y, w, h, color):
        """Draw an unfilled rectangle outline."""
        self.hline(x, y, w, color)
        self.hline(x, y + h - 1, w, color)
        self.vline(x, y, h, color)
        self.vline(x + w - 1, y, h, color)

    def fill_rect(self, x, y, width, height, color):
        """Draw a filled rectangle."""
        self._set_window(x, y, x + width - 1, y + height - 1)
        pixel = _encode_pixel(color)
        chunks, rest = divmod(width * height, _BUFFER_PIXELS)
        self.dc.on()
        if chunks:
            row = pixel * _BUFFER_PIXELS
            for _ in range(chunks):
                self._write(None, row)
        if rest:
            self._write(None, pixel * rest)

    def fill(self, color):
        """Fill the entire screen with one color."""
        self.fill_rect(0, 0, self.width, self.height, color)

    def text(self, font, text, x0, y0, color=WHITE, background=BLACK):
        """
        Draw text using a bitmap font module (see lib/vga1_8x16.py and
        lib/vga1_bold_16x32.py) -- there is no built-in font.

        Args:
            font (module): font module to use, e.g. vga1_8x16
            text (str): text to write
            x0 (int): column to start drawing at
            y0 (int): row to start drawing at
            color (int): 565 encoded color to use for characters
            background (int): 565 encoded color to use for background
        """
        bytes_per_row = font.WIDTH // 8
        rows_per_pass = 8
        passes = font.HEIGHT // rows_per_pass
        glyph_bytes = bytes_per_row * font.HEIGHT

        for char in text:
            ch = ord(char)
            if not (font.FIRST <= ch < font.LAST
                    and x0 + font.WIDTH <= self.width
                    and y0 + font.HEIGHT <= self.height):
                x0 += font.WIDTH
                continue

            idx0 = (ch - font.FIRST) * glyph_bytes

            for p in range(passes):
                buffer = bytearray(font.WIDTH * rows_per_pass * 2)
                pos = 0
                base = idx0 + p * rows_per_pass * bytes_per_row
                for row in range(rows_per_pass):
                    row_base = base + row * bytes_per_row
                    for b in range(bytes_per_row):
                        byte = font.FONT[row_base + b]
                        for bit in range(8):
                            on = byte & (0x80 >> bit)
                            struct.pack_into(
                                ">H", buffer, pos,
                                color if on else background)
                            pos += 2
                self.blit_buffer(
                    buffer, x0, y0 + rows_per_pass * p,
                    font.WIDTH, rows_per_pass)

            x0 += font.WIDTH
