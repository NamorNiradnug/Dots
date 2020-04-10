from PyQt5.Qt import QImage


class Resources:
    """This is the structure for storing images."""

    images = {}

    def __getattr__(self, item: str) -> QImage:
        if item in self.images:
            return self.images[item]
        image = QImage(f"resources/{item}.png")
        if image.isNull():
            raise AttributeError(f"No resource {item}.png in dir 'resources/'.")
