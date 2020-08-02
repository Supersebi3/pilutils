"""Various functions to return alpha masks. All masks are mode L."""

import random as _random
from pilutils.basic import round_rectangle as draw_round_rectangle
from PIL import Image, ImageDraw

__all__ = ["ellipse", "rectangle", "round_rectangle"]


def ellipse(size, invert=False):
    """Returns an alpha mask in the shape of an ellipse."""
    fg, bg = (0, 255) if invert else (255, 0)
    mask = Image.new("L", size, bg)
    d = ImageDraw.Draw(mask)
    d.ellipse((0, 0, *size), fill=fg)
    return mask


def rectangle(size, invert=False):
    """Returns a rectangular alpha mask."""
    fg = 0 if invert else 255
    mask = Image.new("L", size, fg)
    return mask


def round_rectangle(size, radius, snap=True, invert=False):
    """Returns a rounded rectangle alpha mask."""
    fg, bg = (255, 255, 255, 255), (0, 0, 0, 255)
    fg, bg = (bg, fg) if invert else (fg, bg)
    mask = draw_round_rectangle(size, radius, fg, bg, snap).convert("L")
    return mask


def random(size, weight=0.5):
    """Returns a randomized map where `weight` of the pixels are white and the rest are black. `weight = 0` means all pixels are black, `weight = 0.75` means 3/4 of pixels are white etc."""
    img = Image.new("L", size)
    for y in range(img.height):
        for x in range(img.width):
            p = _random.random()
            if p < weight:
                img.putpixel((x, y), 255)
    return img
