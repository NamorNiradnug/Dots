from tkinter import Tk, Canvas


class Dots:
    def __init__(self):
        self.points = [[0] * 100 for __ in range(100)]
        self.colors = [0, '#2D2', 'blue']
        self.all_tracks = []

        self.is_greens_turn = 1
        self.scale = 2
        self.position = [0, 0]
        self.origin = [0, 0]
        self.root = Tk()
        self.canvas = Canvas(self.root, width=160 * 4, height=4 * 160)
        self.canvas.pack()

        self.draw(1, 1)
        self.root.bind('<Control-=>', lambda event: self.set_scale(self.scale * 2))
        self.root.bind('<MouseWheel>', lambda event: self.set_scale(self.scale // 2))
        self.root.bind('<Up>', lambda event: self.translate(0, -1))
        self.root.bind('<Down>', lambda event: self.translate(0, 1))
        self.root.bind('<Left>', lambda event: self.translate(-1, 0))
        self.root.bind('<Right>', lambda event: self.translate(1, 0))
        self.root.bind('<Button-1>', lambda event: self.create_point(event.x, event.y))
        self.root.mainloop()

    def do_connect(self, point1, point2, used_tracks=None, track_len=0):
        if used_tracks is None:
            used_tracks = {1}
        result = False
        print(point1, point2)
        if point1 == point2 and track_len > 2:
            print(3)
            return True, used_tracks
        for point in ((point1[0], point1[1] - 1), (point1[0] - 1, point1[1] - 1),
                      (point1[0] - 1, point1[1]), (point1[0] + 1, point1[1] - 1),
                      (point1[0] - 1, point1[1] + 1), (point1[0] + 1, point1[1]),
                      (point1[0] + 1, point1[1] + 1), (point1[0], point1[1] + 1)):
            if 0 < point[1] < len(self.points) and 0 < point[0] < len(self.points[point[1]]) and 0 < point1[1] < len(
                    self.points) and 0 < point1[0] < len(self.points[point1[1]]) and self.points[point[1]][point[0]] ==\
                    self.points[point1[1]][point1[0]] and not (((point,), point1) in used_tracks):
                _next = self.do_connect((point,), point2, used_tracks and {((point,), point2), (point2, (point,))},
                                        track_len + 1)
                result += _next[0]
                used_tracks.update(_next[1])
        return bool(result), used_tracks

    def draw_point(self, point_type, x, y):
        self.canvas.create_line((x * 16 + 8) * self.scale, y * self.scale * 16,
                                (x * 16 + 8) * self.scale, (y + 1) * self.scale * 16)
        self.canvas.create_line(x * self.scale * 16, (y * 16 + 8) * self.scale,
                                (x + 1) * self.scale * 16, (y * 16 + 8) * self.scale)
        if point_type != 0:
            self.canvas.create_oval((x * 16 + 5) * self.scale, (y * 16 + 5) * self.scale,
                                    (x * 16 + 11) * self.scale, (y * 16 + 11) * self.scale,
                                    fill=self.colors[point_type])

    def draw(self, x, y):
        self.position[0] = x
        self.position[1] = y
        w = h = 640 // (self.scale * 16)
        for i in range(len(self.points[y:y + h])):
            for j in range(len(self.points[i][x:x + w])):
                self.draw_point(self.points[y:y + h][i][x:x + w][j], j, i)
        for i in range(len(self.points[y:y + h])):
            for j in range(len(self.points[i][x:x + w])):
                if 0 < y and y + h < len(self.points) and 0 < i < len(self.points[y:y + h]) and 0 < x and x + w < len(
                        self.points[y:y + h][i]) and 0 < j < len(self.points[y:y + h][i][x:x + w]):
                    if j + 1 < len(self.points[y:y + h][i][x:x + w]) and self.points[y:y + h][i][x:x + w][j] == \
                            self.points[y:y + h][i][x:x + w][j + 1] > 0:
                        self.canvas.create_line((j * 16 + 8) * self.scale, (i * 16 + 8) * self.scale,
                                                (j * 16 + 24) * self.scale, (i * 16 + 8) * self.scale,
                                                fill=self.colors[self.points[y:y + h][i][x:x + w][j]],
                                                width=2 * self.scale)
                    if i + 1 < len(self.points[y:y + h]) and self.points[y:y + h][i][x:x + w][j] == \
                            self.points[y:y + h][i + 1][x:x + w][j] > 0:
                        self.canvas.create_line((j * 16 + 8) * self.scale, (i * 16 + 8) * self.scale,
                                                (j * 16 + 8) * self.scale, (i * 16 + 24) * self.scale,
                                                fill=self.colors[self.points[y:y + h][i][x:x + w][j]],
                                                width=2 * self.scale)

    def set_scale(self, scale):
        if scale != 0 and scale != 16:
            self.canvas.delete('all')
            self.scale = scale
            self.draw(self.position[0], self.position[1])

    def translate(self, x, y):
        while self.position[1] + y <= 0:
            self.points.insert(0, [0] * len(self.points[0]))
            self.position[1] += 1
            self.origin[1] += 1
        while self.position[0] + x <= 0:
            for i in range(len(self.points)):
                self.points[i].insert(0, 0)
            self.position[0] += 1
            self.origin[0] += 1
        while self.position[1] + y + 80 // self.scale >= len(self.points):
            self.points.append([0] * len(self.points[0]))
        while self.position[0] + x + 80 // self.scale >= len(self.points[0]):
            for i in range(len(self.points)):
                self.points[i].append(0)
        self.canvas.delete('all')
        self.draw(self.position[0] + x, self.position[1] + y)

    def create_point(self, x, y):
        x, y = x // (16 * self.scale) + self.position[0], y // (16 * self.scale) + self.position[1]
        if self.points[y][x] == 0:
            self.points[y][x] = self.is_greens_turn
            self.canvas.delete('all')
            self.draw(self.position[0], self.position[1])
            if self.is_greens_turn == 1:
                self.is_greens_turn = 2
            else:
                self.is_greens_turn = 1


Dots()
