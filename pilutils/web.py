from io import BytesIO

import requests
from PIL import Image, UnidentifiedImageError

__all__ = ["image_from_url"]


def image_from_url(url):
    """
    Gets the :obj:`PIL.Image.Image` from a given image URL.

    Args:
        url (:obj:`str`): URL to get the image object from.

    Returns:
        :obj:`PIL.Image.Image`: Image object for the given URL.
    """
    resp = requests.get(url)
    resp.raise_for_status()
    bio = BytesIO(resp.content)
    bio.seek(0)
    try:
        img = Image.open(bio)
    except UnidentifiedImageError:
        raise ValueError(
            f"URL {url!r} does not seem to point to a valid image resource."
        )
    return img
