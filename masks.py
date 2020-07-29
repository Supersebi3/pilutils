from PIL import Image, ImageDraw

def ellipse(size, invert=False):
    """Returns a mask for an ellipse of the given size. The mask is an image with mode "1"."""
    fg, bg = (0, 1) if invert else (1, 0)
    mask = Image.new("1", size, bg)
    d = ImageDraw.Draw(mask)
    d.ellipse((0, 0, *size), fill=fg)
    return mask


