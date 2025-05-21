from typing import Self

from sorl.thumbnail import delete, get_thumbnail

from .constants import (
    THUMBNAIL_CROP,
    THUMBNAIL_GEOMETRY,
    THUMBNAIL_QUALITY,
)


class ThumbnailImage:
    """
    Context manager.
    Creates a thumbnail of image and removes it after use.
    """

    def __init__(self, image_path: str) -> None:
        self.image_path = image_path
        self.thumbnail = None

    def __enter__(self) -> Self:
        if self.image_path:
            self.thumbnail = get_thumbnail(
                self.image_path,
                THUMBNAIL_GEOMETRY,
                crop=THUMBNAIL_CROP,
                quality=THUMBNAIL_QUALITY,
            )
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        if self.thumbnail is not None:
            delete(self.thumbnail)
