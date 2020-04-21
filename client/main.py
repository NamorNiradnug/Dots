#!/usr/bin/env python3
from threading import Thread, Event
from types import FunctionType, LambdaType
from typing import List, Any, Set, Union

from PyQt5.QtCore import QSize, QRect, QPoint
from PyQt5.QtWidgets import QApplication, QMainWindow
from PyQt5.QtGui import QPainter, QMouseEvent, QWheelEvent, QColor, QFont, QPen, QImage, QFontMetrics, QResizeEvent
from PyQt5.Qt import QPaintEvent, QCloseEvent, QKeyEvent, Qt

try:
	from .dots import Dots
	from .resources import Resources
except ImportError:  # for python <= 3.6
	from dots import Dots
	from resources import Resources


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


class Button:
	def __init__(self,
	             rect: QRect,
	             func: Union[LambdaType, FunctionType] = lambda: None,
	             mouse_buttons=None,
	             text: str = '',
	             font: QFont = QFont('ubuntu', 20),
	             image: QImage = None):
		self.mouse_buttons = mouse_buttons
		if mouse_buttons is None:
			self.mouse_buttons = {Qt.LeftButton}
		self.rect = rect
		self.lines: List[str] = []
		self.image = image
		self.func = func
		self.font = font
		text = text.split(' ')
		metrics = QFontMetrics(font)
		if text:
			self.lines = [text[0]]
			for word in text[1::]:
				if metrics.width(self.lines[-1] + word) < rect.width() - 4:
					self.lines[-1] += ' ' + word
				else:
					self.lines.append(word)
	
	def event(self, event: QMouseEvent) -> bool:
		if event.pos() in self.rect and event.button() in self.mouse_buttons:
			self.func()
			return True
		return False
	
	def draw(self, painter: QPainter, cursor_pos: QPoint) -> None:
		if self.image is None:
			pen = QPen(Qt.black if cursor_pos not in self.rect else Qt.white)
			pen.setWidth(2)
			painter.setPen(pen)
			painter.setBrush(QColor(255, 217, 168))
			painter.drawRoundedRect(self.rect, 15, 15)
		else:
			if cursor_pos not in self.rect:
				painter.setOpacity(.6)
			painter.drawImage(self.rect, self.image)

		painter.setOpacity(1)
		painter.setFont(self.font)
		metrics = QFontMetrics(self.font)
		painter.setPen(QColor(30, 50, 40))
		for i in range(len(self.lines)):
			painter.drawText(self.rect.center().x() - metrics.width(self.lines[i]) // 2,
			                 self.rect.center().y() - metrics.height() * (len(self.lines) / 2 - i - 1) - 5,
			                 self.lines[i])


class Modes:
	"""Frame modes."""
	LocalGame = 0
	SingleGame = 1
	MultiplayerGame = 2
	GamePause = 3
	MainMenu = 4
	Settings = 5
	Rules = 7
	Games = {LocalGame, SingleGame, MultiplayerGame}
	Delevoping = {SingleGame, MultiplayerGame, Settings, Rules}


class Frame(QMainWindow):
	def __init__(self):
		super().__init__()
		self.dots = None
		self.setWindowTitle("Dots")
		self.draw_thread = Interval(1 / 60, self.update)
		self.draw_thread.start()

		self.buttons: Set[Button] = set()
		self.mode = None
		self.game_mode = None
		self.last_mode = Modes.MainMenu
		self.setMode(Modes.MainMenu)
		self.last_key = Qt.NoButton
		self.last_button = Qt.NoButton

	def setMode(self, mode: int, *args: List[Any]) -> None:
		if mode == Modes.LocalGame and self.dots is None:
			self.dots = Dots(*args)
			self.game_mode = mode
		if mode == Modes.GamePause:
			if self.game_mode is None:
				raise AttributeError("Cannot set pause game mode.")
		if mode == Modes.MainMenu:
			self.dots = None
			self.game_mode = None
		self.last_mode = self.mode
		self.mode = mode
		self.updateButtons()

	def updateButtons(self):
		if self.mode == Modes.MainMenu:
			self.buttons = {Button(QRect(self.width() // 2 - 128,
			                             self.height() // 2 - 256 + i * 112,
			                             256, 64),
			                       text=("SINGLEPLAYER",
			                             "LOCAL MULTIPLAYER",
			                             "MULTIPLAYER",
			                             "SETTINGS",
			                             "QUIT")[i],
			                       func=(lambda: self.setMode(Modes.SingleGame),
			                             lambda: self.setMode(Modes.LocalGame),
			                             lambda: self.setMode(Modes.MultiplayerGame),
			                             lambda: self.setMode(Modes.Settings),
			                             self.close)[i])
			                for i in range(5)}
		if self.mode == Modes.LocalGame:
			self.buttons = {
				Button(QRect(QPoint(self.geometry().width(), self.geometry().height()) - QPoint(70, 70), QSize(64, 64)),
			                image=Resources.gear,
				            func=lambda: self.setMode(Modes.Settings)
				       )
			}
		elif self.mode in Modes.Delevoping:
			self.buttons = {
				Button(QRect(self.geometry().width() // 2 - 64, self.geometry().height() // 2 + 50, 128, 48),
			                      text="EXIT",
			                      func=lambda: self.setMode(self.last_mode))
			                }
		if self.mode == Modes.GamePause:
			self.buttons = {
				Button(QRect(self.geometry().width() // 2 - 128,
				             self.geometry().height() // 2 - 200 + 112 * i,
				             256, 64),
				       text=("BACK TO GAME", "GAME RULES", "SETTINGS", "EXIT TO MAIN MENU")[i],
				       func=(lambda: self.setMode(self.game_mode),
				            lambda: self.setMode(Modes.Rules),
				            lambda: self.setMode(Modes.Settings),
				            lambda: self.setMode(Modes.MainMenu))[i])
				for i in range(4)
			}

	def closeEvent(self, _: QCloseEvent) -> None:
		self.draw_thread.cancel()

	def resizeEvent(self, _: QResizeEvent) -> None:
		self.updateButtons()

	def cursorPos(self) -> QPoint:
		"""Cursor position relative top left corner of window excluding the frame."""
		return self.cursor().pos() - self.geometry().topLeft()

	def dotCoordinatesOnMap(self, dot: QPoint) -> QPoint:
		"""Place, where dot is drawing."""
		return (dot * 16 + QPoint(8 - self.dots.cam_x + (self.width() / self.dots.scale) // 2,
		                          8 - self.dots.cam_y + (self.height() / self.dots.scale) // 2)) * self.dots.scale

	def paintEvent(self, _: QPaintEvent) -> None:
		painter = QPainter(self)
		if self.mode == Modes.LocalGame:
			project_dot = self.coordsOnMap(self.cursorPos())
			on_map = self.dotCoordinatesOnMap(project_dot)
			if not all(on_map not in button.rect and self.cursorPos() not in button.rect for button in self.buttons) or\
					on_map not in QRect(QPoint(), self.geometry().size()):
				project_dot = None
			self.dots.draw(self.geometry().size(), painter, project_dot)
		if self.mode == Modes.GamePause:
			self.dots.draw(self.geometry().size(), painter)
			painter.setOpacity(.5)
			painter.setBrush(Qt.black)
			painter.drawRect(QRect(QPoint(), self.geometry().size()))
			painter.setOpacity(1)
		elif self.mode in Modes.Delevoping:
			painter.setPen(Qt.green)
			painter.setFont(QFont('Times', 30))
			painter.drawText(self.geometry(), Qt.AlignCenter, "IN DEVELOPING")
		for button in self.buttons:
			button.draw(painter, self.cursorPos())
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
			self.dots.translate(QPoint(*translate) * self.dots.scale, self.size())

	def keyPressEvent(self, event: QKeyEvent) -> None:
		if event.key() == Qt.Key_Escape:
			if self.mode == Modes.LocalGame:
				self.setMode(Modes.GamePause)
			elif self.mode in Modes.Delevoping:
				self.setMode(self.last_mode)
			elif self.mode == Modes.GamePause:
				self.setMode(self.game_mode)

	def wheelEvent(self, event: QWheelEvent) -> None:
		if self.mode in Modes.Games:
			self.dots.changeScale(event.angleDelta().y() / 240, self.size())

	def coordsOnMap(self, point: QPoint) -> QPoint:
		real_point = point / self.dots.scale + QPoint(self.dots.cam_x, self.dots.cam_y) - \
		             QPoint(self.width() // 2, self.height() // 2) / self.dots.scale
		return QPoint(round(real_point.x() / 16 - .5),
		              round(real_point.y() / 16 - .5))

	def mouseReleaseEvent(self, event: QMouseEvent) -> None:
		for button in self.buttons:
			if button.event(event):
				return
				
		if event.button() == Qt.LeftButton:
			if self.mode in Modes.Games:
				on_map = self.dotCoordinatesOnMap(self.coordsOnMap(self.cursorPos()))
				if on_map in QRect(QPoint(), self.geometry().size()):
					self.dots.turn(self.coordsOnMap(event.pos()).x(), self.coordsOnMap(event.pos()).y())


if __name__ == '__main__':
	app = QApplication([])
	frame = Frame()
	frame.setMaximumSize(app.screens()[0].size())
	frame.showMaximized()
	app.exec_()
