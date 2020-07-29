from io import BytesIO

import requests
from PIL import Image, UnidentifiedImageError

__all__ = ["image_from_url"]


def image_from_url(url):
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
