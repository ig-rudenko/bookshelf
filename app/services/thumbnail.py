from pathlib import Path

from PIL import Image


def create_thumbnail(image_path: Path, size: tuple[int, int]) -> None:
    """Create a thumbnail of the given image."""
    img = Image.open(image_path.absolute().as_posix())
    img.thumbnail(size)
    img.save(image_path.parent / image_path.name.replace(".png", "_thumb.png"))
