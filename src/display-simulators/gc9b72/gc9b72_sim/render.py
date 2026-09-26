"""Turn simulated screens into documentation images.

    from gc9b72_sim import render
    render.save_png(pixels, "docs/img/05-analog.png")
    render.save_gif([frame1, frame2], "docs/img/05-analog.gif", ms=1000)

Screens are drawn as a round watch: a dark bezel, with the glass cut to
the visible circle. PNGs have a transparent background, so they suit
light and dark pages; GIFs use white, since GIF transparency is poor.
"""

import os

from PIL import Image, ImageDraw

from .hardware import W

VISIBLE_RADIUS = 171        # the glass the bezel leaves showing


def to_rgb(px):
    """RGB565 pixel values -> (r, g, b) tuples."""
    return [(((p >> 11) & 31) * 255 // 31, ((p >> 5) & 63) * 255 // 63,
             (p & 31) * 255 // 31) for p in px]


def screen_image(px):
    """The plain 360 x 360 screen, corners and all."""
    img = Image.new("RGB", (W, W))
    img.putdata(to_rgb(px))
    return img


def watch_image(px, background=None):
    """The screen as a round watch, 400 x 400."""
    size = W + 40
    out = Image.new("RGBA", (size, size), background or (0, 0, 0, 0))
    draw = ImageDraw.Draw(out)
    draw.ellipse((2, 2, size - 3, size - 3), fill=(45, 45, 50, 255))    # bezel
    draw.ellipse((12, 12, size - 13, size - 13), fill=(20, 20, 22, 255))
    mask = Image.new("L", (W, W), 0)
    c, r = W // 2, VISIBLE_RADIUS
    ImageDraw.Draw(mask).ellipse((c - r, c - r, c + r, c + r), fill=255)
    out.paste(screen_image(px), (20, 20), mask)
    return out


def save_png(px, path):
    os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
    watch_image(px).save(path, optimize=True)
    print("wrote", path)


def save_gif(frames, path, ms=800):
    """An animated GIF, ms milliseconds per frame, looping forever."""
    os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
    imgs = [watch_image(px, (255, 255, 255, 255)).convert("RGB")
            .convert("P", palette=Image.ADAPTIVE, colors=128) for px in frames]
    imgs[0].save(path, save_all=True, append_images=imgs[1:], duration=ms,
                 loop=0, optimize=True)
    print("wrote", path, "(%d frames)" % len(frames))


def contact_sheet(paths, out_path, columns=3, cell=340):
    """Lay several PNGs out on one white sheet, for reviewing them."""
    rows = (len(paths) + columns - 1) // columns
    sheet = Image.new("RGBA", (columns * (cell + 10), rows * (cell + 10)),
                      (255, 255, 255, 255))
    for k, p in enumerate(paths):
        im = Image.open(p).convert("RGBA").resize((cell, cell))
        sheet.paste(im, ((k % columns) * (cell + 10), (k // columns) * (cell + 10)), im)
    sheet.save(out_path)
    return out_path
