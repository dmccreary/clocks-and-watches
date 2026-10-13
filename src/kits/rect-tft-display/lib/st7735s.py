"""
MicroPython driver for the Sitronix ST7735S SPI display controller, as
found on 1.8" 128x160 color TFT boards.

It has the same shape as lib/gc9b72.py in the sw-gc9b72 kit, which in
turn follows Russ Hughes' GC9A01 driver: the same method names, the same
arguments, the same font modules. A lab written for one of those
displays ports to this one by changing its sizes and positions.

Like them, this driver has no frame buffer: every drawing call streams
straight over SPI, and there is no show().

The register init sequence is the long-standing one for 1.8" ST7735
panels (it comes from Adafruit's ST7735 library by way of lib/ST7735.py
in this repository's st7735 kit), confirmed on a "1.8 TFT + EC11" board.
"""

import time
from micropython import const
import ustruct as struct

_SWRESET = const(0x01)
_SLPIN = const(0x10)
_SLPOUT = const(0x11)
_NORON = const(0x13)
_INVOFF = const(0x20)
_DISPON = const(0x29)
_CASET = const(0x2A)
_RASET = const(0x2B)
_RAMWR = const(0x2C)
_MADCTL = const(0x36)
_COLMOD = const(0x3A)

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

# MADCTL bits: MY flips rows, MX flips columns, MV swaps rows and columns.
_MY = const(0x80)
_MX = const(0x40)
_MV = const(0x20)
_BGR = const(0x08)

# The glass is 128 wide and 160 tall. Rotations 1 and 3 turn it on its
# side, 160 wide and 128 tall.
_ROTATIONS = (
    _MX | _MY,   # 0 - portrait
    _MY | _MV,   # 1 - landscape
    0x00,        # 2 - portrait, upside down
    _MX | _MV,   # 3 - landscape, upside down
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


class ST7735S:
    """
    ST7735S driver class for 128x160 SPI TFT panels.

    Args:
        spi (SPI): configured SPI bus (required)
        dc (Pin): data/command pin (required)
        cs (Pin): chip-select pin (optional)
        reset (Pin): reset pin (optional but strongly recommended)
        backlight (Pin): backlight pin (optional)
        rotation (int): 0-3, see _ROTATIONS
        bgr (bool): True if red and blue come out swapped
        x_offset, y_offset (int): shift the picture, for panels whose
            glass does not start at the controller's first row or column
    """

    def __init__(
            self,
            spi=None,
            dc=None,
            cs=None,
            reset=None,
            backlight=None,
            rotation=0,
            bgr=False,
            x_offset=0,
            y_offset=0):
        if spi is None:
            raise ValueError("SPI object is required.")
        if dc is None:
            raise ValueError("dc pin is required.")

        self.width = 128
        self.height = 160
        self.spi = spi
        self.dc = dc
        self.cs = cs
        self.reset = reset
        self.backlight = backlight
        self._bgr = bgr
        self._x_offset = x_offset
        self._y_offset = y_offset

        self.hard_reset()
        self._write(_SWRESET)
        time.sleep_ms(150)
        self._write(_SLPOUT)
        time.sleep_ms(150)

        self._write(0xB1, b'\x01\x2C\x2D')              # frame rate, normal
        self._write(0xB2, b'\x01\x2C\x2D')              # frame rate, idle
        self._write(0xB3, b'\x01\x2C\x2D\x01\x2C\x2D')  # frame rate, partial
        self._write(0xB4, b'\x07')                      # no inversion
        self._write(0xC0, b'\xA2\x02\x84')              # power control 1-5
        self._write(0xC1, b'\xC5')
        self._write(0xC2, b'\x0A\x00')
        self._write(0xC3, b'\x8A\x2A')
        self._write(0xC4, b'\x8A\xEE')
        self._write(0xC5, b'\x0E')                      # VCOM
        self._write(_INVOFF)
        self._write(_COLMOD, b'\x05')  # 16 bits/pixel, RGB565
        self._write(0xE0, b'\x02\x1C\x07\x12\x37\x32\x29\x2D'   # gamma +
                          b'\x29\x25\x2B\x39\x00\x01\x03\x10')
        self._write(0xE1, b'\x03\x1D\x07\x06\x2E\x2C\x29\x2D'   # gamma -
                          b'\x2E\x2E\x37\x3F\x00\x00\x02\x10')
        self._write(_NORON)
        time.sleep_ms(10)
        self._write(_DISPON)
        time.sleep_ms(100)

        self.rotation(rotation)

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
        """Set display rotation: 0-3, see _ROTATIONS. Rotations 1 and 3
        swap the width and the height."""
        self._rotation = rotation % 4
        madctl = _ROTATIONS[self._rotation]
        if self._bgr:
            madctl |= _BGR
        self._write(_MADCTL, bytes([madctl]))
        if self._rotation % 2:
            self.width, self.height = 160, 128
        else:
            self.width, self.height = 128, 160

    def _set_window(self, x0, y0, x1, y1):
        self._write(_CASET, _encode_pos(x0 + self._x_offset,
                                        x1 + self._x_offset))
        self._write(_RASET, _encode_pos(y0 + self._y_offset,
                                        y1 + self._y_offset))
        self._write(_RAMWR)

    def pixel(self, x, y, color):
        """Draw a single pixel. Pixels off the screen are ignored."""
        if 0 <= x < self.width and 0 <= y < self.height:
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
        angle -- shapes.poly() and the clock hands both need it.
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
        """Draw a filled rectangle. The part of it that is off the screen
        is left out."""
        if x < 0:
            width += x
            x = 0
        if y < 0:
            height += y
            y = 0
        width = min(width, self.width - x)
        height = min(height, self.height - y)
        if width <= 0 or height <= 0:
            return

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
        Draw text using a bitmap font module (see lib/vga1_8x8.py,
        lib/vga1_8x16.py and lib/vga1_bold_16x32.py) -- there is no
        built-in font. A character that would not fit on the screen
        whole is skipped.

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
                    and 0 <= x0 and x0 + font.WIDTH <= self.width
                    and 0 <= y0 and y0 + font.HEIGHT <= self.height):
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
