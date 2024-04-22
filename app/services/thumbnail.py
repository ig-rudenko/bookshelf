from pathlib import Path
from typing import Literal

from PIL import Image

thumbnail_sizes = {
    "small": (160, 240),
    "medium": (260, 380)
}


def get_thumbnail(image: str, size: Literal["small", "medium"]) -> str:
    return image.replace(".png", f"_thumb_{size}.png")


def create_thumbnails(image_path: Path) -> None:
    """Create a thumbnails of the given image."""
    img = Image.open(image_path.absolute().as_posix())
    for size_name, size in thumbnail_sizes.items():
        img.thumbnail(size)
        img.save(image_path.parent / image_path.name.replace(".png", f"_thumb_{size_name}.png"))
