from typing import Tuple, Set, FrozenSet, Optional

from PyQt5.QtGui import QPainter, QPen, QColor, QBrush
from PyQt5.QtCore import QPoint, QSize, Qt


class DotsSettings:
	def __init__(self):
		self.colors = {
			0: Qt.red,
			1: Qt.blue,
			2: Qt.green,
			3: Qt.yellow
		}
		self.nicks = {
			0: 'red',
			1: 'blue',
			2: 'green',
			3: 'yellow'
		}


class DotsManager:
	empty = -1
	empty_eaten = -2
	
	def __init__(self, players_number: int):
		if not 0 < players_number < 5:
			raise AttributeError(f"Only from 1 to 4 player can play dots, not {players_number}.")
		self.players_number = players_number
		self.settings = DotsSettings()
	
	def _getPlayer(self, player: int) -> int:
		if not 0 <= player < self.players_number:
			raise AttributeError(f"It is only {self.players_number} players in {self}, player {player} does not exist.")
		return player
	
	def real(self, player: int) -> int:
		return self._getPlayer(player)
	
	def isEaten(self, dot: int) -> bool:
		return self.eaten(self.player(dot)) == dot

	def eaten(self, player: int) -> int:
		if player == self.empty:
			return self.empty_eaten
		return self._getPlayer(player) + self.players_number
	
	def color(self, dot: int) -> QColor:
		if dot in {self.empty, self.empty_eaten}:
			return Qt.transparent
		return self.settings.colors[self.player(dot)]
	
	def player(self, dot: int) -> int:
		if dot in {self.empty, self.empty_eaten}:
			return -1
		return dot % self.players_number


class Chunk:
	def __init__(self, x: int, y: int, dots_manager: DotsManager):
		self.x = x
		self.y = y
		self.dots_manager = dots_manager
		self.map = [[dots_manager.empty for _ in range(16)] for _ in range(16)]
		self.tracks: Set[FrozenSet[Tuple[int, int], Tuple[int, int]]] = set()
		self.eater = [[-1 for _ in range(16)] for _ in range(16)]
	
	def isEmpty(self):
		return self.map == [[self.dots_manager.empty for _ in range(16)] for _ in range(16)]
	
	def drawLines(self, painter: QPainter, tx: int, ty: int) -> None:
		line_pen = QPen(Qt.black)
		line_pen.setWidth(1)
		painter.setPen(line_pen)
		for i in range(16):
			painter.drawLine(self.x * 16 + tx, (self.y + i) * 16 + 8 + ty,  # \ horizontal line
			                 self.x * 16 + 256 + tx, (self.y + i) * 16 + 8 + ty)  # /
			painter.drawLine((self.x + i) * 16 + 8 + tx, self.y * 16 + ty,  # \ vertical line
			                 (self.x + i) * 16 + 8 + tx, self.y * 16 + 256 + ty)  # /
	
	def drawDots(self, painter: QPainter, tx: int, ty: int, dots: 'Dots') -> None:
		for track in self.tracks:
			track = tuple(track)
			max_dot = max(track)
			painter.setPen(self.dots_manager.color(self.map[max_dot[0] % 16][max_dot[1] % 16]))
			painter.drawLine(track[0][0] * 16 + 8 + tx, track[0][1] * 16 + 8 + ty,
	                 track[1][0] * 16 + 8 + tx, track[1][1] * 16 + 8 + ty)

		painter.setPen(Qt.transparent)
		for x in range(16):
			for y in range(16):
				painter.setBrush(
					self.dots_manager.color(self.map[x][y])
				)
				painter.drawEllipse((self.x + x) * 16 + 5 + tx, (self.y + y) * 16 + 5 + ty, 6, 6)
				if not self.dots_manager.isEaten(self.map[x][y]):
					continue
				fill_brush = QBrush(self.dots_manager.color(self.eater[x][y]))
				fill_brush.setStyle(Qt.BDiagPattern)
				painter.setBrush(fill_brush)
				before = {(0, -1): (-1, -1),
				          (1, 0): (1, -1),
				          (0, 1): (1, 1),
				          (-1, 0): (-1, 1)
				          }
				poly = [self.dotCoord(xx, yy) + QPoint(tx, ty)
				        for xx, yy in [(x, y - 1), (x + 1, y), (x, y + 1), (x - 1, y)]]
				for val in before:
					if dots.getDot(self.x + x + before[val][0], self.y + y + before[val][1]) == self.eater[x][y]:
						poly.insert(poly.index(self.dotCoord(val[0] + x, val[1] + y) + QPoint(tx, ty)),
						            self.dotCoord(before[val][0] + x, before[val][1] + y) + QPoint(tx, ty))
				painter.drawPolygon(*poly)
	
	def dotCoord(self, x: int, y: int) -> QPoint:
		return QPoint((self.x + x) * 16 + 8, (self.y + y) * 16 + 8)


class Dots:
	def __init__(self, players_number: int = 2):
		self.dots_manager = DotsManager(players_number)
		self.chunks = [[Chunk(x * 16, y * 16, self.dots_manager) for y in range(16)] for x in range(16)]
		self.tracks: Set[FrozenSet[Tuple[int, int], Tuple[int, int]]] = set()
		self.turning_player = 0
		self.cam_x: int = 2048
		self.cam_y: int = 2048
		self.scale: float = 2
		self.counters = [0] * players_number

	def addTrack(self, track: Tuple[Tuple[int, int], ...]) -> None:
		for i in range(len(track) - 1):
			max_dot = max(track[i], track[i + 1])
			self.chunks[max_dot[0] // 16][max_dot[1] // 16].tracks.add(frozenset((track[i], track[i + 1])))

	def changeScale(self, delta: float, size: QSize) -> None:
		self.scale += delta
		self.scale = max(self.scale, 2)
		self.scale = min(self.scale, 6)
		self.translate(QPoint(), size)
	
	@staticmethod
	def circle(dx: int, dy: int, radius: int) -> Set[Tuple[int, int]]:
		answer = set()
		for x in range(-radius, radius + 1):
			for y in (radius - abs(x), -radius + abs(x)):
				answer.add((x + dx, y + dy))
		return answer

	def draw(self, size: QSize, painter: QPainter, cursor: Optional[QPoint] = None) -> None:
		painter.save()
		painter.scale(self.scale, self.scale)
		size /= self.scale
		visible: Set[Chunk] = set()
		for chunks in self.chunks:
			for chunk in chunks:
				if (-256 < chunk.x * 16 + size.width() // 2 - self.cam_x <= size.width() and
					-256 < chunk.y * 16 + size.height() // 2 - self.cam_y <= size.height()):
					visible.add(chunk)
		print(len(visible))
		tx = -self.cam_x + size.width() // 2
		ty = -self.cam_y + size.height() // 2
		for chunk in visible:
			chunk.drawLines(painter, tx, ty)
		for chunk in visible:
			chunk.drawDots(painter, tx, ty, self)
		if cursor is not None and self.getDot(cursor.x(), cursor.y()) == self.dots_manager.empty and \
				0 < cursor.x() < 255 and 0 < cursor.y() < 255:
			painter.setOpacity(.5)
			painter.setBrush(self.dots_manager.color(self.turning_player))
			painter.drawEllipse(cursor.x() * 16 + 5 - self.cam_x + size.width() // 2,
			                    cursor.y() * 16 + 5 - self.cam_y + size.height() // 2, 6, 6)
		painter.restore()

	@staticmethod
	def getAdjacent(x: int, y: int) -> Set[Tuple[int, int]]:
		return Dots.circle(x, y, 1)
	
	def getDot(self, x: int, y: int) -> int:
		if 0 <= x < 256 and 0 <= y < 256:
			return self.chunks[x // 16][y // 16].map[x % 16][y % 16]
		return self.dots_manager.empty

	def getEater(self, x: int, y: int) -> int:
		if 0 <= x < 256 and 0 <= y < 256:
			return self.chunks[x // 16][y // 16].eater[x % 16][y % 16]
		return -1

	def getSurrounding(self, x: int, y: int, every: bool = False) -> Set[Tuple[int, int]]:
		return set([i for i in ((x, y - 1), (x + 1, y - 1),
		                        (x + 1, y), (x + 1, y + 1),
		                        (x, y + 1), (x - 1, y + 1),
		                        (x - 1, y), (x - 1, y - 1))
		            if self.getDot(x, y) == self.getDot(*i) or every])
	
	def _findEmpty(self, x: int, y: int) -> Tuple[int, int]:
		radius = 0
		x //= 16
		y //= 16
		while (radius < x and radius < y and radius < 15 - x and radius < 15 - y and
		       all(not self.chunks[i][j].isEmpty() for i, j in self.circle(x, y, radius))):
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
	
	def settings(self) -> DotsSettings:
		return self.dots_manager.settings
	
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
					if self.dotOwner(i, j) not in {-1, self.dots_manager.player(self.getDot(x, y))}:
						self.counters[self.dots_manager.player(self.getDot(x, y))] += 1
					self.chunks[i // 16][j // 16].map[i % 16][j % 16] = self.dots_manager.eaten(
						self.dots_manager.player(self.getDot(i, j)))
					self.chunks[i // 16][j // 16].eater[i % 16][j % 16] = self.dots_manager.player(self.getDot(x, y))

	def dotOwner(self, x: int, y: int):
		return self.getEater(x, y) if self.getEater(x, y) != -1 else self.dots_manager.player(self.getDot(x, y))

	def translate(self, delta: QPoint, size: QSize) -> None:
		size /= self.scale
		self.cam_x += delta.x()
		self.cam_y += delta.y()
		self.cam_x = max(self.cam_x, size.width() // 2 + self.scale * 16)
		self.cam_x = min(self.cam_x, len(self.chunks) * 256 - size.width() // 2 - self.scale * 16)
		self.cam_y = max(self.cam_y, size.height() // 2 + self.scale * 16)
		self.cam_y = min(self.cam_y, len(self.chunks[0]) * 256 - size.height() // 2 - self.scale * 16)

	def turn(self, x: int, y: int) -> None:
		if self.getDot(x, y) == self.dots_manager.empty and 0 < x < 255 and 0 < y < 255:
			self.chunks[x // 16][y // 16].map[x % 16][y % 16] = self.dots_manager.real(self.turning_player)
			self.findNewTracks(x, y)
			self.findNewEaten(x, y)
			self.turning_player = (self.turning_player + 1) % self.dots_manager.players_number
