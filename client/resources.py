from PyQt5.Qt import QImage
from PyQt5.QtCore import QPoint, Qt
from PyQt5.QtGui import QBrush, QColor, QPainter, QPen


class _ResourcesManager:
    """This is the structure for storing images."""

    images = {}

    @staticmethod
    def _gear() -> QImage:
        image = QImage(64, 64, QImage.Format_ARGB32)
        image.fill(Qt.transparent)
        painter = QPainter(image)
        color = Qt.gray
        pen = QPen(color)
        pen.setWidth(10)
        painter.setPen(pen)
        painter.translate(32, 32)
        painter.drawEllipse(-16, -16, 32, 32)
        painter.setPen(color)
        painter.setBrush(QBrush(color, Qt.SolidPattern))
        for _ in range(8):
            painter.rotate(45)
            painter.drawPolygon(QPoint(-6, -16), QPoint(-3, -32), QPoint(3, -32), QPoint(6, -16))
        painter.end()
        return image

    def __init__(self):
        self.gear = self._gear()

    def __getattr__(self, item: str) -> QImage:
        if item in self.images:
            return self.images[item]
        image = QImage(f"resources/{item}.png")
        if image.isNull():
            raise AttributeError(f"No resource {item}.png in dir 'resources/'.")
        return image


Resources = _ResourcesManager()
