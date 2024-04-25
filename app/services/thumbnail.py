import io
from typing import Literal, BinaryIO

from PIL import Image

from app.media_storage import AbstractStorage

thumbnail_sizes = {"small": (160, 240), "medium": (260, 380)}


def get_thumbnail(image: str, size_name: Literal["small", "medium"]) -> str:
    return image.replace(".png", f"_thumb_{size_name}.png")


async def create_thumbnails(storage: AbstractStorage, original_image: str) -> None:
    """Create a thumbnails of the given image."""
    for size_name, size in thumbnail_sizes.items():
        with storage.get_file_binary(original_image) as file:  # type: BinaryIO
            img = Image.open(file)
            img.thumbnail(size)
            image_data = io.BytesIO()
            img.save(image_data, format="PNG")
            await storage.upload_file(
                original_image.replace(".png", f"_thumb_{size_name}.png"),
                image_data.getvalue(),
            )
