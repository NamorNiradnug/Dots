#!/usr/bin/env python3
from PyQt5.QtWidgets import QApplication, QMainWindow
from PyQt5.QtGui import QPainter, QMouseEvent
from PyQt5.Qt import QPaintEvent, QCloseEvent, QKeyEvent, Qt, QPoint

try:
	from .dots import Dots
except ImportError:  # for python <= 3.6
	from dots import Dots
	
from threading import Thread, Event
from types import FunctionType


class Interval(Thread):
	"""Periodical thread."""

	def __init__(self, interval: float, func: FunctionType):
		Thread.__init__(self)
		self.stopped = Event()
		self.interval = interval
		self.func = func

	def run(self):
		while not self.stopped.wait(self.interval):
			self.func()

	def cancel(self):
		self.stopped.set()


class Frame(QMainWindow):
	def __init__(self):
		super().__init__()
		self.dots = Dots(2)
		self.setWindowTitle("Dots")
		self.setWindowFlag(Qt.FramelessWindowHint)
		self.draw_thread = Interval(1 / 60, self.update)
		self.draw_thread.start()
		
		self.last_key = Qt.NoButton
		self.last_button = Qt.NoButton

	def closeEvent(self, _: QCloseEvent) -> None:
		self.draw_thread.cancel()

	def paintEvent(self, _: QPaintEvent) -> None:
		painter = QPainter(self)
		self.dots.draw(self.size(), self.coordsOnMap(self.cursor().pos() - self.pos()), painter)
		painter.end()

	def keyReleaseEvent(self, event: QKeyEvent) -> None:
		translate = None
		if event.key() == Qt.Key_Up:
			translate = 0, -10
		if event.key() == Qt.Key_Down:
			translate = 0, 10
		if event.key() == Qt.Key_Left:
			translate = -10, 0
		if event.key() == Qt.Key_Right:
			translate = 10, 0
		if translate:
			self.dots.translate(QPoint(*translate), self.size())

	def coordsOnMap(self, point: QPoint) -> QPoint:
		real_point = point + QPoint(self.dots.cam_x, self.dots.cam_y) - QPoint(self.width() // 2, self.height() // 2)
		return QPoint(round(real_point.x() / 16 - .5), round(real_point.y() / 16 - .5))

	def mouseReleaseEvent(self, event: QMouseEvent) -> None:
		if event.button() == Qt.LeftButton:
			self.dots.turn(self.coordsOnMap(event.pos()).x(), self.coordsOnMap(event.pos()).y())


if __name__ == '__main__':
	app = QApplication([])
	frame = Frame()
	frame.setMaximumSize(app.screens()[0].size())
	frame.showMaximized()
	app.exec_()
