"""Functions for parsing various strings to RGB tuples."""
import json
import re
from pathlib import Path
import importlib.resources as resources

from pilutils.basic import hex_to_rgb, rough_color_distance

__all__ = [
    "parse_hex6",
    "parse_hex3",
    "parse_rgbfunc_int",
    "parse_rgbfunc_float",
    "parse_rgbfunc_percent",
    "parse_name_css",
    "parse_name_crayola",
    "parse_name_xkcd",
    "parse_name_meodai_best",
    "parse_name_meodai",
    "parse",
    "nearest_named_color",
]

_css_names = json.loads(resources.read_text("pilutils.colornames", "css.json"))
_crayola_names = json.loads(resources.read_text("pilutils.colornames", "crayola.json"))
_xkcd_names = json.loads(resources.read_text("pilutils.colornames", "xkcd.json"))
_meodai_best_names = json.loads(
    resources.read_text("pilutils.colornames", "meodai-best.json")
)
_meodai_names = json.loads(resources.read_text("pilutils.colornames", "meodai.json"))


def parse_hex6(hex6):
    """Example: #ab34df"""
    if m := re.match(r"^#?([0-9A-Fa-f]{6})$", hex6.strip()):
        h = int(m.group(1), 16)
        return hex_to_rgb(h)
    raise ValueError(f"String {hex6!r} does not match hex6 format.")


def parse_hex3(hex3):
    """Example: #a3d"""
    if m := re.match(r"^#?([0-9A-Fa-f]{3})$", hex3.strip()):
        h3 = m.group(1)
        return tuple(int(c * 2, 16) for c in h3)
    raise ValueError(f"String {hex3!r} does not match hex3 format.")


def parse_rgbfunc_int(rgbfunc):
    """Example: rgb(171, 52, 223)"""
    if m := re.match(
        r"^rgb\(\s*(\d{1,3})\s*,\s*(\d{1,3})\s*,\s*(\d{1,3})\s*\)$", rgbfunc.strip()
    ):
        t = tuple(map(int, m.groups()))
        if not any(n > 255 for n in t):
            return t
    raise ValueError(f"String {rgbfunc!r} does not match rgbfunc_int format.")


def parse_rgbfunc_float(rgbfunc):
    """Example: rgb(0.67, 0.2, 0.87)"""
    if m := re.match(
        r"^rgb\(\s*([01]\.\d+)\s*,\s*([01]\.\d+)\s*,\s*([01]\.\d+)\s*\)$",
        rgbfunc.strip(),
    ):
        t = tuple(map(float, m.groups()))
        if not any(n > 1 for n in t):
            return tuple(int(round(n * 255)) for n in t)
    raise ValueError(f"String {rgbfunc!r} does not match rgbfunc_float format.")


def parse_rgbfunc_percent(rgbfunc):
    """Example: rgb(67%, 20%, 87.5%)"""
    if m := re.match(
        r"^rgb\(\s*(\d{1,3}(?:\.\d+)?)%\s*,\s*(\d{1,3}(?:\.\d+)?)%\s*,\s*(\d{1,3}(?:\.\d+)?)%\s*\)$",
        rgbfunc.strip(),
    ):
        t = tuple(map(float, m.groups()))
        if not any(n > 100 for n in t):
            return tuple(int(round(n * 255 / 100)) for n in t)
    raise ValueError(f"String {rgbfunc!r} does not match rgbfunc_percent format.")


def parse_name_css(name):
    name = name.lower()
    if name not in _css_names:
        raise ValueError(f"Color {name!r} is not named in the CSS dataset.")
    return parse_hex6(_css_names[name])


def parse_name_crayola(name):
    name = name.lower()
    if name not in _crayola_names:
        raise ValueError(f"Color {name!r} is not named in the crayola dataset.")
    return parse_hex6(_crayola_names[name])


def parse_name_xkcd(name):
    name = name.lower()
    if name not in _xkcd_names:
        raise ValueError(f"Color {name!r} is not named in the xkcd dataset.")
    return parse_hex6(_xkcd_names[name])


def parse_name_meodai_best(name):
    name = name.lower()
    if name not in _meodai_best_names:
        raise ValueError(f"Color {name!r} is not named in the meodai-best dataset.")
    return parse_hex6(_meodai_best_names[name])


def parse_name_meodai(name):
    name = name.lower()
    if name not in _meodai_names:
        raise ValueError(f"Color {name!r} is not named in the meodai dataset.")
    return parse_hex6(_meodai_names[name])


def parse(
    colstr,
    *,
    hex6=True,
    hex3=True,
    rgbfunc_int=True,
    rgbfunc_float=True,
    rgbfunc_percent=True,
    name_css=True,
    name_crayola=True,
    name_xkcd=True,
    name_meodai_best=True,
    name_meodai=True,
):
    """Combine all other parse functions into one "universal" function. Use kwargs to disable certain parsers."""
    funcs = []
    if hex6:
        funcs.append(parse_hex6)
    if hex3:
        funcs.append(parse_hex3)
    if rgbfunc_int:
        funcs.append(parse_rgbfunc_int)
    if rgbfunc_float:
        funcs.append(parse_rgbfunc_float)
    if rgbfunc_percent:
        funcs.append(parse_rgbfunc_percent)
    if name_css:
        funcs.append(parse_name_css)
    if name_crayola:
        funcs.append(parse_name_crayola)
    if name_xkcd:
        funcs.append(parse_name_xkcd)
    if name_meodai_best:
        funcs.append(parse_name_meodai_best)
    if name_meodai:
        funcs.append(parse_name_meodai)

    res = None
    for func in funcs:
        try:
            res = func(colstr)
        except ValueError:
            pass
    if res is None:
        raise ValueError(f"Could not find a working parser for {colstr!r}.")
    return res


def nearest_named_color(col, css=True, crayola=True, xkcd=True, meodai_best=True, meodai=True):
    """Return the nearest named color from the selected color sets as a (name, rgb) tuple.

    NOTE: This function is pretty slow"""
    colorpool = {}
    if meodai:
        colorpool.update(_meodai_names)
    if meodai_best:
        colorpool.update(_meodai_best_names)
    if xkcd:
        colorpool.update(_xkcd_names)
    if crayola:
        colorpool.update(_crayola_names)
    if css:
        colorpool.update(_css_names)
    near_name, near_val = min(colorpool.items(), key=lambda d: rough_color_distance(col, parse_hex6(d[1])))
    return near_name, near_val
