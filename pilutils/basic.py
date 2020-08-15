import random
import shutil
import itertools
import colorsys
from PIL import Image, ImageDraw

__all__ = [
    "STANDARD_MODES",
    "SPECIAL_MODES",
    "ALL_MODES",
    "hex_to_rgb",
    "hex_to_rgba",
    "rgb_to_hex",
    "rgba_to_hex",
    "random_color",
    "iter_pixels",
    "color_distance",
    "eval_pixel",
    "mix",
    "show_cli",
    "rgb_to_hsv",
    "hsv_to_rgb",
    "colorize",
    "align_bbox",
    "round_corner",
    "round_rectangle",
]

STANDARD_MODES = ("1", "L", "P", "RGB", "YCbCr", "LAB", "HSV", "RGBA", "CMYK", "I", "F")
SPECIAL_MODES = (
    "LA",
    "PA",
    "RGBX",
    "RGBa",
    "La",
    "I;16",
    "I;16L",
    "I;16B",
    "I;16N",
    "BGR;15",
    "BGR;16",
    "BGR;24",
    "BGR;32",
)
ALL_MODES = STANDARD_MODES + SPECIAL_MODES


def hex_to_rgb(rgb):
    """Convert a 6-digit hexadecimal RGB number to an RGB tuple.

    Args:
        rgb (:obj:`int`): 6-digit hex number to convert to a tuple.

    Returns:
        Tuple[ :obj:`int`]: RGB tuple.

    Note:
        This function converts an int into a tuple of ints. To parse strings, check :obj:`~.parse.parse`.
    """
    if not 0 <= rgb <= 0xFFFFFF:
        raise ValueError(f"{rgb!r} is not an RGB number.")
    return (rgb >> 16, (rgb >> 8) % 256, rgb % 256)


def hex_to_rgba(rgba):
    """Convert an 8-digit hexadecimal RGBA number to an RGBA tuple.

    Args:
        rgba (:obj:`int`): 8-digit hex number to convert to a tuple.

    Returns:
        Tuple[ :obj:`int` ]: RGBA tuple.
    """
    if not 0 <= rgba <= 0xFFFFFFFF:
        raise ValueError("{rgba!r} is not an RGBA number.")

    return (rgba >> 24, (rgba >> 16) % 256, (rgba >> 8) % 256, rgba % 256)


def rgb_to_hex(rgb):
    """Convert an RGB tuple into a 6-digit hexadecimal RGB number.

    Args:
        rgb (Tuple[ :obj:`int` ]): Tuple to convert to hex.

    Returns:
        :obj:`int`: RGB hex.
    """
    if not all(isinstance(n, int) and 0 <= n < 256 for n in rgb) or len(rgb) != 3:
        raise ValueError("{rgb!r} is not an RGB tuple.")
    r, g, b = rgb
    return r << 16 | g << 8 | b


def rgba_to_hex(rgba):
    """Convert an RGBA tuple into an 8-digit hexadecimal RGBA number.

    Args:
        rgba (Tuple[ :obj:`int` ]): Tuple to convert to hex.

    Returns:
        :obj:`int`: RGBA hex.
    """
    if not all(isinstance(n, int) and 0 <= n < 256 for n in rgba) or len(rgba) != 4:
        raise ValueError("{rgba!r} is not an RGBA tuple.")
    r, g, b, a = rgba
    return r << 24 | g << 16 | b << 8 | a


def _raise_unsupported_mode(mode):
    if mode in ALL_MODES:
        raise ValueError(f"Mode {mode!r} is currently not supported.")
    else:
        raise ValueError(f"Unknown mode {mode!r}. Make sure capitalization is correct.")


def random_color(mode="RGB"):
    """Generate a random color in the specified `mode`.

    Args:
        mode (:obj:`str`): Mode that the generated colour should be in. Defaults to `"RGB"`

    Returns:
        Union[ :obj:`int`, Tuple[ :obj:`int` ]]: Random colour.
    """
    if mode == "1":
        return random.randint(0, 1)
    elif mode in ("L", "P"):
        return random.randint(0, 255)
    elif mode in ("RGB", "YCbCr", "LAB", "HSV"):
        return tuple(random.randint(0, 255) for i in range(3))
    elif mode in ("RGBA", "CMYK"):
        return tuple(random.randint(0, 255) for i in range(4))
    elif mode == "I":
        return random.randint(-(2 ** 31), 2 ** 31 - 1)
    else:
        _raise_unsupported_mode(mode)


def iter_pixels(img):
    """Returns a generator that iterates through every pixel of an image, yielding (x, y, color) tuples on every step.

    Args:
        img (:obj:`PIL.Image.Image`): Image object to iterate through the pixels for.

    Yields:
        Tuple[ `x`, `y`, `pixel colour` ]: Pixel coordinate and colour of the pixel.
    """
    for y in range(img.height):
        for x in range(img.width):
            yield (x, y, img.getpixel((x, y)))


def color_distance(col1, col2):
    """Calculates the distance between two colors of equal modes.

    Args:
        col1: First colour to compare.
        col2: Second colour to compare.

    Returns:
        Union[ :obj:`int`, :obj:`float` ]: Distance between the colours.
    """
    if isinstance(col1, (int, float)):
        return float(abs(col1 - col2))
    return sum((b1 - b2) ** 2 for b1, b2 in zip(col1, col2)) ** 0.5


def eval_pixel(func, img):
    """Evaluate `func` at every pixel of `img` and return a new Image with those modified values.
    `func` should take 1 argument representing the original color in the mode of `img` and return a new
    color of the same mode. This is unlike :obj:`PIL.Image.eval`, which is evaluated on every subpixel on every band,
    not on every full pixel for multiband images.

    Args:
        func (Callable[[ `pixel colour` ], `pixel colour` ]): Function to call to modify the pixel colour value.
        img (:obj:`PIL.Image.Image`): Image to modify the pixels of.

    Returns:
        :obj:`PIL.Image.Image`: Modified image object.
    """
    cache = {}
    new = img.copy()
    for x, y, col in iter_pixels(img):
        if col in cache:
            newcol = cache[col]
        else:
            newcol = func(col)
            cache[col] = newcol
        new.putpixel((x, y), newcol)
    return new


def mix(col1, col2, p=0.5):
    """Mix two colors according to percentage p where
    - p=0 returns col1
    - p=1 returns col2
    - p=0.5 returns an equal mix of col1 and col2
    - p=0.25 returns a color containing 75% of col1 and 25% of col2
    etc.

    Args:
        col1: First colour to be mixed.
        col2: Second colour to be mixed.
        p (:obj:`float`): Number indicating the colour mix proportion.

    Returns:
        Tuple[ :obj:`int` ]: New colour after mixing.
    """
    p = min(max(0, p), 1)
    if isinstance(col1, (int, float)):
        return type(col1)(col1 * (1 - p) + col2 * p)
    ret = []
    for band1, band2 in zip(col1, col2):
        ret.append(int(band1 * (1 - p) + band2 * p))
    return tuple(ret)


def show_cli(img):
    """NOTE: This experimental function is for debug purposes only. It may not work in all terminals."""
    img = img.convert("RGB")
    tw, th = shutil.get_terminal_size((80, 24))
    nw = tw // 2
    nh = img.height * nw // img.width
    img = img.resize((nw, nh))
    for y in range(img.height):
        for x in range(img.width):
            r, g, b = img.getpixel((x, y))
            ansi = f"\33[48;2;{r};{g};{b}m  \33[49m"
            print(ansi, end="")
        print()


def rgb_to_hsv(rgb):
    """Convert an RGB tuple to an HSV tuple for the same color. Both tuples should obey PIL rules,
    e.g. have 3 integers each ranging 0-255.

    Args:
        rgb (Tuple[ :obj:`int` ]): RGB tuple to convert to HSV.

    Returns:
        Tuple[ :obj:`int` ]: HSV tuple.
    """
    r, g, b = rgb
    fr, fg, fb = r / 255, g / 255, b / 255
    fh, fs, fv = colorsys.rgb_to_hsv(fr, fg, fb)
    h, s, v = round(fh * 255), round(fs * 255), round(fv * 255)
    return h, s, v


def hsv_to_rgb(hsv):
    """Convert an HSV tuple to an RGB tuple for
the same color. Both tuples should obey PIL rule
s,
    e.g. have 3 integers each ranging 0-255.

    Args:
        hsv (Tuple[ :obj:`int` ]): HSV tuple to convert to RGB.

    Returns:
        Tuple[ :obj:`int` ]: RGB tuple.
    """
    h, s, v = hsv
    fh, fs, fv = h / 255, s / 255, v / 255
    fr, fg, fb = colorsys.hsv_to_rgb(fh, fs, fv)
    r, g, b = round(fr * 255), round(fg * 255), round(fb * 255)
    return r, g, b


def colorize(img, color):
    """Colorize an image with `color` (an RGB tuple). Always returns an RGB image."""
    h, _, _ = rgb_to_hsv(color)
    img = img.convert("HSV")

    def f(hsv):
        _, s, v = hsv
        return h, s, v

    new = eval_pixel(f, img).convert("RGB")
    return new


def align_bbox(frame, size, align=5, margin=0, topleft_only=False, suppress_wrong_size=False):
    """Align a smaller bounding box of size `size` (a 2-tuple of width and height) into a larger bounding box given by `frame`, a 4-tuple holding (x0, y0, x1, y1) coordinates. x1 and y1 are just outside the box, so a full image has the bounding box (0, 0, width, height). The function returns a second (x0, y0, x1, x2) tuple corresponding to the bounding box that will be aligned. `align` can have any integer value from 1 to 9 corresponding to alignments based on the common number pad layout:
    7 8 9
    4 5 6
    1 2 3

    If `suppress_wrong_size` is `True`, the function will not raise an error if the box does not fit inside the frame. It will instead return a box placement outside of the frame. Note that this may mean negative coordinates."""
    fx0, fy0, fx1, fy1 = frame
    fx0 += margin
    fy0 += margin
    fx1 -= margin
    fy1 -= margin
    fw = fx1 - fx0
    fh = fy1 - fy0
    bw, bh = size
    if (fw < bw or fh < bh) and not suppress_wrong_size:
        raise ValueError("Bounding box does not fit into frame.")
    if not 0 < align < 10 or not isinstance(align, int):
        raise ValueError(f"Invalid alignment value {align!r}.")

    if align == 1:
        box = (fx0, fy1 - bh, fx0 + bw, fy1)
    elif align == 2:
        dx = (fw - bw) // 2
        box = (fx0 + dx, fy1 - bh, fx0 + dx + bw, fy1)
    elif align == 3:
        box = (fx1 - bw, fy1 - bh, fx1, fy1)
    elif align == 4:
        dy = (fh - bh) // 2
        box = (fx0, fy0 + dy, fx0 + bw, fy0 + dy + bh)
    elif align == 5:
        dx = (fw - bw) // 2
        dy = (fh - bh) // 2
        box = (fx0 + dx, fy0 + dy, fx0 + dx + bw, fy0 + dy + bh)
    elif align == 6:
        dy = (fh - bh) // 2
        box = (fx1 - bw, fy0 + dy, fx1, fy0 + dy + bh)
    elif align == 7:
        box = (fx0, fy0, fx0 + bw, fy0 + bh)
    elif align == 8:
        dx = (fw - bw) // 2
        box = (fx0 + dx, fy0, fx0 + dx + bw, fy0 + bh)
    elif align == 9:
        box = (fx1 - bw, fy0, fx1, fy0 + bh)

    if topleft_only:
        return (box[0], box[1])
    return box


def round_corner(radius, fill, bg=(0, 0, 0, 0)):
    """Draw a round corner"""
    corner = Image.new("RGBA", (radius, radius), bg)
    draw = ImageDraw.Draw(corner)
    draw.pieslice((0, 0, radius * 2, radius * 2), 180, 270, fill=fill)
    return corner


def round_rectangle(size, radius, fill, bg=(0, 0, 0, 0), snap=True):
    """Draw a rounded rectangle"""
    width, height = size
    if snap:
        m = min(width, height)
        radius = min(radius, m // 2)
    rectangle = Image.new("RGBA", size, fill)
    corner = round_corner(radius, fill, bg)
    rectangle.paste(corner.rotate(270), (width - radius, 0))
    rectangle.paste(corner.rotate(180), (width - radius, height - radius))
    rectangle.paste(corner.rotate(90), (0, height - radius))
    rectangle.paste(corner, (0, 0))
    return rectangle
