# shapes.py -- the drawing commands the GC9B72 driver does not have.
#
# The OLED kits got ellipse(), poly(), and blit() for free, because the
# SSD1306 driver is built on MicroPython's framebuf module and framebuf
# ships those three compiled into the firmware.
#
# This driver is not built on framebuf. It talks to the glass directly,
# and it only knows how to draw pixels, horizontal runs, vertical runs,
# lines, rectangles, text, and raw buffers. Everything else -- every hour
# marker and every watch hand in this kit -- has to be built out of
# those. That is what this file is.
#
# Copied unchanged (apart from this header) from the robot-faces
# sw-gc9b72 kit, where it was first written for the GC9A01 smartwatch.
#
# Each function takes the display as its first argument, so a lab reads:
#
#     shapes.ellipse(display, 120, 100, 30, 24, WHITE, FILL)
#
# One rule shapes everything below: ON THIS DISPLAY, DRAWING IS SENDING.
# There is no buffer in RAM to scribble in. Every pixel you draw is bytes
# going down an SPI wire, and every separate drawing call costs a command
# sequence on top of the pixels. So these functions work in horizontal
# RUNS wherever they can -- one hline of forty pixels is far cheaper than
# forty calls to pixel().

from math import sqrt

# Quadrant codes, the same numbers framebuf uses, so the masks you learned
# on the OLED still mean the same thing here.
TOP_RIGHT = 1
TOP_LEFT = 2
BOTTOM_LEFT = 4
BOTTOM_RIGHT = 8
ALL_QUADRANTS = 15
TOP_HALF = TOP_RIGHT + TOP_LEFT           # 3  -- an arc that frowns
BOTTOM_HALF = BOTTOM_LEFT + BOTTOM_RIGHT  # 12 -- an arc that smiles


def _half_width(dy, xr, yr):
    """How far the ellipse reaches sideways on the row dy above/below its
    center. This is the ellipse equation solved for x."""
    if yr <= 0:
        return xr
    inside = 1.0 - (float(dy) * dy) / (float(yr) * yr)
    if inside <= 0.0:
        return 0
    return int(xr * sqrt(inside) + 0.5)


def ellipse(display, x, y, xr, yr, color, fill=0, mask=ALL_QUADRANTS):
    """Draw an ellipse centered on (x, y) with radii xr and yr.

    Same arguments as framebuf's ellipse(), including the quadrant mask:
    1=top-right, 2=top-left, 4=bottom-left, 8=bottom-right, added together
    to combine them. The middle row belongs to both halves, so TOP_HALF
    and BOTTOM_HALF each draw the widest row and the arcs meet cleanly.

    Built one row at a time. For a filled shape each row is a single
    hline; for an outline each row is the short run between where this
    row's edge sits and where the row above it sat -- which is what keeps
    a steep curve from breaking into disconnected dots."""
    if xr < 0 or yr < 0:
        return

    previous = None
    for dy in range(-yr, yr + 1):
        edge = _half_width(dy, xr, yr)

        if dy <= 0:
            left_on = mask & TOP_LEFT
            right_on = mask & TOP_RIGHT
        if dy >= 0:
            # The equator row is drawn if EITHER half asked for it.
            if dy == 0:
                left_on = mask & (TOP_LEFT | BOTTOM_LEFT)
                right_on = mask & (TOP_RIGHT | BOTTOM_RIGHT)
            else:
                left_on = mask & BOTTOM_LEFT
                right_on = mask & BOTTOM_RIGHT

        row = y + dy

        if fill:
            if left_on and right_on:
                display.hline(x - edge, row, edge * 2 + 1, color)
            elif left_on:
                display.hline(x - edge, row, edge + 1, color)
            elif right_on:
                display.hline(x, row, edge + 1, color)
            previous = edge
            continue

        # Outline. Draw the horizontal run between this row's edge and the
        # previous row's edge, so the curve stays connected no matter how
        # fast it is turning.
        #
        # The edge GROWS on the way down to the equator and SHRINKS after
        # it, so the run has to be measured between the two edges without
        # assuming which is larger. Get that wrong and the bottom half of
        # every arc comes out as a row of disconnected ticks.
        if previous is None:
            near, far = edge, edge
        else:
            near = min(edge, previous)
            far = max(edge, previous)
        run = far - near + 1

        if right_on:
            display.hline(x + near, row, run, color)
        if left_on:
            display.hline(x - far, row, run, color)

        previous = edge


def circle(display, x, y, r, color, fill=0, mask=ALL_QUADRANTS):
    """A circle is an ellipse whose radii match. Same as on the OLED."""
    ellipse(display, x, y, r, r, color, fill, mask)


def ring(display, x, y, r, color, thickness=1):
    """A circle outline `thickness` pixels thick. Handy on a round screen,
    where a ring just inside the rim is the natural frame for a face."""
    for step in range(thickness):
        circle(display, x, y, r - step, color, 0)


def _points(x, y, coords):
    """Turn a flat array of x,y offsets into a list of absolute points."""
    return [(x + coords[i], y + coords[i + 1])
            for i in range(0, len(coords) - 1, 2)]


def poly(display, x, y, coords, color, fill=0):
    """Draw a polygon from a flat array of x,y offsets, the same shape
    framebuf's poly() takes: array('h', [x0,y0, x1,y1, ...]).

    The outline is one line() per edge. The fill is a scanline fill: for
    every row the shape covers, work out where the edges cross that row,
    sort the crossings, and fill between them in pairs. That is the same
    algorithm every 2-D graphics library uses, written out where you can
    read it."""
    points = _points(x, y, coords)
    if len(points) < 2:
        return

    if not fill:
        for i in range(len(points)):
            x0, y0 = points[i]
            x1, y1 = points[(i + 1) % len(points)]
            display.line(x0, y0, x1, y1, color)
        return

    top = min(p[1] for p in points)
    bottom = max(p[1] for p in points)

    for row in range(top, bottom + 1):
        crossings = []
        for i in range(len(points)):
            x0, y0 = points[i]
            x1, y1 = points[(i + 1) % len(points)]
            if y0 == y1:
                continue                      # horizontal edge: no crossing
            if min(y0, y1) <= row < max(y0, y1):
                # Where does this edge sit at this row?
                t = (row - y0) / float(y1 - y0)
                crossings.append(int(x0 + t * (x1 - x0) + 0.5))

        crossings.sort()
        for i in range(0, len(crossings) - 1, 2):
            start = crossings[i]
            run = crossings[i + 1] - start + 1
            if run > 0:
                display.hline(start, row, run, color)


def triangle(display, x0, y0, x1, y1, x2, y2, color, fill=0):
    """Three points, spelled out. Easier to read than a poly() array when
    the shape really is just a triangle."""
    from array import array
    poly(display, 0, 0, array('h', [x0, y0, x1, y1, x2, y2]), color, fill)


def sprite(width, height, background=0x0000):
    """Make a blank RGB565 sprite buffer you can blit later.

    Two bytes per pixel, most significant byte first -- that is what
    blit_buffer() expects to receive."""
    high = (background >> 8) & 0xFF
    low = background & 0xFF
    return bytearray(bytes((high, low)) * (width * height))


def sprite_pixel(buffer, width, x, y, color):
    """Set one pixel inside a sprite buffer made by sprite()."""
    offset = (y * width + x) * 2
    buffer[offset] = (color >> 8) & 0xFF
    buffer[offset + 1] = color & 0xFF


def blit_keyed(display, buffer, x, y, width, height, key=0x0000):
    """Stamp a sprite, skipping every pixel that matches `key`.

    display.blit_buffer() is much faster than this, but it is opaque --
    it paints the sprite's background over whatever was underneath. When
    you need the background to show through, you have to find the runs of
    non-key pixels yourself and send those. That is all this does, and it
    is worth reading once to see what framebuf's blit(key=...) was doing
    for you on the OLED."""
    high_key = (key >> 8) & 0xFF
    low_key = key & 0xFF

    for row in range(height):
        run_start = -1
        for column in range(width + 1):
            if column < width:
                offset = (row * width + column) * 2
                transparent = (buffer[offset] == high_key
                               and buffer[offset + 1] == low_key)
            else:
                transparent = True            # forces the last run to close

            if not transparent and run_start < 0:
                run_start = column
            elif transparent and run_start >= 0:
                length = column - run_start
                start = (row * width + run_start) * 2
                display.blit_buffer(
                    buffer[start:start + length * 2],
                    x + run_start, y + row, length, 1)
                run_start = -1
