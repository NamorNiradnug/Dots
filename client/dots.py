from typing import Tuple, Set, FrozenSet

from PyQt5.QtGui import QPainter, QPen, QColor
from PyQt5.QtCore import QPoint, QSize, Qt


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
	empty_eaten = -2
	
	def __init__(self, players_number: int):
		self.players_number = players_number
		self.settings = DotsSettings()
	
	def _getPlayer(self, player: int) -> int:
		if not 0 <= player < self.players_number:
			raise AttributeError(f"It is only {self.players_number} players in {self}, player {player} does not exist.")
		return player
	
	def projecting(self, player: int) -> int:
		return self._getPlayer(player) + self.players_number
	
	def real(self, player: int) -> int:
		return self._getPlayer(player)
	
	def eaten(self, player: int) -> int:
		if player == -1:
			return self.empty_eaten
		return self._getPlayer(player) + self.players_number * 2
	
	def color(self, dot: int) -> QColor:
		if dot in {-1}:
			return Qt.transparent
		if self.isReal(dot) or self.isProjecting(dot):
			return self.settings.colors[self.player(dot)]
		return Qt.white
	
	def isReal(self, dot: int) -> bool:
		return dot // self.players_number == 0
	
	def isProjecting(self, dot: int) -> bool:
		return dot // self.players_number == 1
	
	def isEaten(self, dot: int) -> bool:
		return (dot // self.players_number == 2 and dot >= 0) or dot == self.empty_eaten
	
	def isEmpty(self, dot: int) -> bool:
		return not self.isReal(dot)
	
	def player(self, dot: int) -> int:
		if dot == self.empty:
			return -1
		return dot % self.players_number


class Chunk:
	def __init__(self, x: int, y: int, dots_manager: DotsManager):
		self.x = x
		self.y = y
		self.dots_manager = dots_manager
		self.map = [[dots_manager.empty for _ in range(16)] for _ in range(16)]
		self.tracks: Set[FrozenSet[Tuple[int, int], Tuple[int, int]]] = set()
	
	def isEmpty(self):
		return self.map == [[self.dots_manager.empty for _ in range(16)] for _ in range(16)]
	
	def draw(self, painter: QPainter, tx: int, ty: int) -> None:
		line_pen = QPen(Qt.black)
		line_pen.setWidth(1)
		for x in range(16):
			for y in range(16):
				painter.setPen(line_pen)
				painter.drawLine((self.x + x) * 16 + tx, (self.y + y) * 16 + 8 + ty,  # \ horizontal line
				                 (self.x + x + 1) * 16 + tx, (self.y + y) * 16 + 8 + ty)  # |
				painter.drawLine((self.x + x) * 16 + 8 + tx, (self.y + y) * 16 + ty,  # \ vertical line
				                 (self.x + x) * 16 + 8 + tx, (self.y + y + 1) * 16 + ty)  # |
				painter.setPen(Qt.transparent)
				painter.setBrush(
					self.dots_manager.color(self.map[x][y])
				)
				if self.dots_manager.isProjecting(self.map[x][y]):
					painter.setOpacity(.5)
				painter.drawEllipse(QPoint((self.x + x) * 16 + 8 + tx,
				                           (self.y + y) * 16 + 8 + ty),
				                    4, 4)
				painter.setOpacity(1)

		for track in self.tracks:
			track = tuple(track)
			min_dot = max(track)
			painter.setPen(self.dots_manager.color(self.map[min_dot[0] % 16][min_dot[1] % 16]))
			painter.drawLine(track[0][0] * 16 + 8 + tx, track[0][1] * 16 + 8 + ty,
			                 track[1][0] * 16 + 8 + tx, track[1][1] * 16 + 8 + ty)


class Dots:
	def __init__(self, players_number: int = 2):
		self.dots_manager = DotsManager(players_number)
		self.chunks = [[Chunk(x * 16, y * 16, self.dots_manager) for y in range(16)] for x in range(16)]
		self.tracks: Set[FrozenSet[Tuple[int, int], Tuple[int, int]]] = set()
		self.turning_player = 0
		self.cam_x: int = 0
		self.cam_y: int = 0
		self.last_cursor = QPoint(0, 0)
	
	def addDot(self, x: int, y: int, dot: int) -> None:
		if self.dots_manager.isEmpty(self.getDot(x, y)) and 0 < x < 255 and 0 < y < 255 and \
				not self.dots_manager.isEaten(self.getDot(x, y)):
			self.chunks[x // 16][y // 16].map[x % 16][y % 16] = dot
	
	def addTrack(self, track: Tuple[Tuple[int, int], ...]) -> None:
		for i in range(len(track) - 1):
			max_dot = max(track[i], track[i + 1])
			self.chunks[max_dot[0] // 16][max_dot[1] // 16].tracks.add(frozenset((track[i], track[i + 1])))
	
	def draw(self, size: QSize, cursor: QPoint, painter: QPainter) -> None:
		if self.dots_manager.isEmpty(self.getDot(self.last_cursor.x(), self.last_cursor.y())) and \
				not self.dots_manager.isEaten(self.getDot(self.last_cursor.x(), self.last_cursor.y())):
			self.removeDot(self.last_cursor.x(), self.last_cursor.y())
		self.addDot(cursor.x(), cursor.y(), self.dots_manager.projecting(self.turning_player))
		self.last_cursor = cursor
		for chunks in self.chunks:
			for chunk in chunks:
				if (-256 < chunk.x * 16 + size.width() // 2 - self.cam_x <= size.width() and
						-256 < chunk.y * 16 + size.height() // 2 - self.cam_y <= size.height()):
					chunk.draw(painter, -self.cam_x + size.width() // 2, -self.cam_y + size.height() // 2)
	
	@staticmethod
	def getAdjacent(x: int, y: int) -> Set[Tuple[int, int]]:
		return Dots.circle(x, y, 1)
	
	def getDot(self, x: int, y: int) -> int:
		return self.chunks[x // 16][y // 16].map[x % 16][y % 16]
	
	def getSurrounding(self, x: int, y: int) -> Set[Tuple[int, int]]:
		return set([i for i in ((x, y - 1), (x + 1, y - 1),
		                        (x + 1, y), (x + 1, y + 1),
		                        (x, y + 1), (x - 1, y + 1),
		                        (x - 1, y), (x - 1, y - 1))
		            if self.getDot(x, y) == self.getDot(*i)])
	
	def _findEmpty(self, x: int, y: int) -> Tuple[int, int]:
		radius = 1
		x //= 16
		y //= 16
		while (radius < x - 1 and radius < y - 1 and radius < 16 - x and radius < 16 and
		       all(not self.chunks[i][j].isEmpty for i, j in self.circle(x, y, radius))):
			radius += 1
		for i, j in self.circle(x, y, radius):
			if self.chunks[i][j].isEmpty():
				return i * 16 + 8, j * 16 + 8
			if i in {0, 15} or j in {0, 15}:
				return i * 16, j * 16
	
	def findNewTracks(self, x: int, y: int) -> None:
		# This is A* algorithm
		open_tracks: Set[Tuple[Tuple[int, int], ...]] = {((x, y),)}
		used = {(x, y)}
		while open_tracks:
			open_tracks_copy = open_tracks.copy()
			open_tracks.clear()
			for track in open_tracks_copy:
				for pos in self.getSurrounding(*track[-1]):
					if pos not in used:
						open_tracks.add(track + (pos,))
						used.add(pos)
					elif len(track) >= 3 and pos == (x, y):
						self.addTrack(track + (pos,))
					elif pos != (x, y):
						for other in open_tracks_copy.union(open_tracks):
							if other[1] != track[1] and pos == other[-1]:
								self.addTrack(track + other[::-1])
	
	def findNewEaten(self, x: int, y: int) -> None:
		empty_dot = self._findEmpty(x, y)
		for xx, yy in self.getAdjacent(x, y):
			if self.getDot(xx, yy) == self.getDot(x, y):
				continue
			
			used: Set[Tuple[int, int]] = set()
			open_pos: Set[Tuple[int, int]] = {(xx, yy)}
			while open_pos and empty_dot not in used:
				open_copy = open_pos.copy()
				open_pos.clear()
				for pos in open_copy:
					for new in self.getAdjacent(*pos):
						if new not in used and self.getDot(*new) != self.getDot(x, y):
							open_pos.add(new)
							if new[0] in {0, 255} or new[1] in {0, 255}:
								break
					used.add(pos)
			if not open_pos:
				for i, j in used:
					self.chunks[i // 16][j // 16].map[i % 16][j % 16] = self.dots_manager.eaten(self.getDot(i, j))
	
	def removeDot(self, x: int, y: int) -> None:
		self.chunks[x // 16][y // 16].map[x % 16][y % 16] = self.dots_manager.empty
	
	@staticmethod
	def circle(dx: int, dy: int, radius: int) -> Set[Tuple[int, int]]:
		answer = set()
		for x in range(-radius, radius + 1):
			for y in (radius - abs(x), -radius + abs(x)):
				answer.add((x + dx, y + dy))
		return answer
	
	def translate(self, delta: QPoint, size: QSize) -> None:
		self.cam_x += delta.x()
		self.cam_y += delta.y()
		self.cam_x = max(self.cam_x, size.width() // 2)
		self.cam_x = min(self.cam_x, len(self.chunks) * 256 - size.width() // 2)
		self.cam_y = max(self.cam_y, size.height() // 2)
		self.cam_y = min(self.cam_y, len(self.chunks[0]) * 256 - size.height() // 2)
	
	def turn(self, x: int, y: int) -> None:
		if self.dots_manager.isEmpty(self.getDot(x, y)):
			self.addDot(x, y, self.dots_manager.real(self.turning_player))
			self.findNewTracks(x, y)
			self.findNewEaten(x, y)
			self.turning_player = (self.turning_player + 1) % self.dots_manager.players_number
