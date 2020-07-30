from PIL import Image, ImageDraw

__all__ = ["ellipse"]


def ellipse(size, invert=False):
    """Returns a mask for an ellipse of the given size. The mask is an image with mode "L"."""
    fg, bg = (0, 255) if invert else (255, 0)
    mask = Image.new("L", size, bg)
    d = ImageDraw.Draw(mask)
    d.ellipse((0, 0, *size), fill=fg)
    return mask
