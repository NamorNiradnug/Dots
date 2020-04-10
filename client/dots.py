from PyQt5.QtGui import QPainter, QPen, QColor
from PyQt5.QtCore import QPoint, QSize, Qt

from typing import Tuple, Set, FrozenSet


class DotsSettings:
	def __init__(self):
		self.colors = {
			0: Qt.red,
			1: Qt.blue,
			2: Qt.green,
			3: Qt.yellow
		}


class DotsManager:
	empty = -1

	def __init__(self, players_number: int):
		self.players_number = players_number
		self.settings = DotsSettings()

	def projecting(self, player: int) -> int:
		if player > self.players_number - 1:
			raise AttributeError(f"It is only {self.players_number} players in {self}, player {player} does not exist.")
		return self.players_number + player

	def color(self, dot: int) -> QColor:
		return self.settings.colors[dot % self.players_number]

	def real(self, player: int) -> int:
		if player > self.players_number - 1:
			raise AttributeError(f"It is only {self.players_number} players in {self}, player {player} does not exist.")
		return player

	def isReal(self, dot: int) -> bool:
		return dot // self.players_number == 0

	def isProjecting(self, dot: int) -> bool:
		return dot // self.players_number == 1

	def player(self, dot: int) -> int:
		if dot == self.empty:
			return -1
		return dot // self.players_number

	def isEmpty(self, dot: int) -> bool:
		return not self.isReal(dot)


class Chunk:
	def __init__(self, x: int, y: int, dots_manager: DotsManager):
		self.x = x
		self.y = y
		self.dots_manager = dots_manager
		self.map = [[dots_manager.empty for _ in range(16)] for _ in range(16)]

	def draw(self, painter: QPainter, tx: int, ty: int) -> None:
		pen = QPen(Qt.black)
		pen.setWidth(1)
		painter.setPen(pen)
		for x in range(16):
			for y in range(16):
				painter.drawLine((self.x + x) * 16 + tx, (self.y + y) * 16 + 8 + ty,  # \ horizontal line
						     (self.x + x + 1) * 16 + tx, (self.y + y) * 16 + 8 + ty)  # |
				painter.drawLine((self.x + x) * 16 + 8 + tx, (self.y + y) * 16 + ty,  # \ vertical line
						     (self.x + x) * 16 + 8 + tx, (self.y + y + 1) * 16 + ty)  # |
				if self.dots_manager.empty != self.map[x][y]:
					painter.setBrush(
						self.dots_manager.settings.colors[self.map[x][y] % self.dots_manager.players_number]
					)
					if self.dots_manager.isProjecting(self.map[x][y]):
						painter.setOpacity(.5)
					painter.drawEllipse(QPoint((self.x + x) * 16 + 8 + tx,
											   (self.y + y) * 16 + 8 + ty),
										4, 4)
					painter.setOpacity(1)


class Dots:
	def __init__(self, players_number: int = 2):
		self.dots_manager = DotsManager(players_number)
		self.chunks = [[Chunk(x * 16, y * 16, self.dots_manager) for y in range(16)] for x in range(16)]
		self.tracks: Set[FrozenSet[Tuple[int, int], Tuple[int, int]]] = set()
		self.turning_player = 0
		self.cam_x: int = 128
		self.cam_y: int = 128
		self.last_cursor = QPoint(0, 0)

	def getDot(self, x: int, y: int) -> int:
		return self.chunks[x // 16][y // 16].map[x % 16][y % 16]

	def addDot(self, x: int, y: int, dot: int) -> None:
		if self.dots_manager.isEmpty(self.getDot(x, y)):
			self.chunks[x // 16][y // 16].map[x % 16][y % 16] = dot

	def getSurrounding(self, x: int, y: int) -> Set[Tuple[int, int]]:
		return set([i for i in ((x, y - 1), (x + 1, y - 1),
							(x + 1, y), (x + 1, y + 1),
							(x, y + 1), (x - 1, y + 1),
							(x - 1, y), (x - 1, y - 1))
				if self.getDot(x, y) == self.getDot(*i)])

	def findNewTracks(self, x: int, y: int) -> None:
		open_tracks: Set[Tuple[Tuple[int, int], ...]] = {((x, y), )}
		used = {(x, y)}
		while open_tracks:
			open_tracks_copy = open_tracks.copy()
			open_tracks.clear()
			for track in open_tracks_copy:
				for pos in self.getSurrounding(*track[-1]):
					if pos not in used:
						open_tracks.add(track + (pos, ))
						used.add(pos)
					elif len(track) >= 3 and pos == (x, y):
						self.addTrack(track + (pos, ))
					elif pos != (x, y):
						for other in open_tracks_copy.union(open_tracks):
							if other[1] != track[1] and pos == other[-1]:
								self.addTrack(track + other[::-1])

	def addTrack(self, track: Tuple[Tuple[int, int], ...]) -> None:
		for i in range(len(track) - 1):
			self.tracks.add(frozenset((track[i], track[i + 1])))

	def removeDot(self, x: int, y: int) -> None:
		self.chunks[x // 16][y // 16].map[x % 16][y % 16] = self.dots_manager.empty

	def turn(self, x: int, y: int) -> None:
		if self.dots_manager.isEmpty(self.getDot(x, y)):
			self.addDot(x, y, self.dots_manager.real(self.turning_player))
			self.findNewTracks(x, y)
			self.turning_player = (self.turning_player + 1) % self.dots_manager.players_number

	def draw(self, size: QSize, cursor: QPoint, painter: QPainter) -> None:
		if self.dots_manager.isEmpty(self.getDot(self.last_cursor.x(), self.last_cursor.y())):
			self.removeDot(self.last_cursor.x(), self.last_cursor.y())
		self.addDot(cursor.x(), cursor.y(), self.dots_manager.projecting(self.turning_player))
		self.last_cursor = cursor
		for chunks in self.chunks:
			for chunk in chunks:
				if (-256 < chunk.x * 16 + size.width() // 2 - self.cam_x <= size.width() and
						-256 < chunk.y * 16 + size.height() // 2 - self.cam_y <= size.height()):
					chunk.draw(painter, -self.cam_x + size.width() // 2, -self.cam_y + size.height() // 2)
		for t in self.tracks:
			t = list(t)
			painter.drawLine(t[0][0] * 16 + 8 - self.cam_x + size.width() // 2,
							 t[0][1] * 16 + 8 - self.cam_y + size.height() // 2,
							 t[1][0] * 16 + 8 - self.cam_x + size.width() // 2,
							 t[1][1] * 16 + 8 - self.cam_y + size.height() // 2)
			print(t)

	def translate(self, delta: QPoint, size: QSize):
		self.cam_x += delta.x()
		self.cam_y += delta.y()
		self.cam_x = max(self.cam_x, size.width() // 2)
		self.cam_x = min(self.cam_x, len(self.chunks) * 256 - size.width() // 2)
		self.cam_y = max(self.cam_y, size.height() // 2)
		self.cam_y = min(self.cam_y, len(self.chunks[0]) * 256 - size.height() // 2)
