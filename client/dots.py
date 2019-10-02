from tkinter import Tk, Canvas


class App:
    def __init__(self):
        self.points_map = []
        for i in range(100):
            self.points_map.append([0] * 100)
        self.colors = [0, "#20D020", "blue"]

        self.is_green_turn = [False]
        self.scale = 2
        self.position = [0, 0]
        self.origin = [0, 0]
        self.window = Tk()
        self.canvas = Canvas(self.window, width=160 * 4, height=4 * 160)
        self.canvas.pack()

        self.draw(1, 1)
        self.window.bind('<Control-=>', lambda event: self.to_scale(self.scale * 2))
        self.window.bind('<MouseWheel>', lambda event: self.to_scale(self.scale // 2))
        self.window.bind('<Up>', lambda event: self.translate(0, -1))
        self.window.bind('<Down>', lambda event: self.translate(0, 1))
        self.window.bind('<Left>', lambda event: self.translate(-1, 0))
        self.window.bind('<Right>', lambda event: self.translate(1, 0))
        self.window.bind('<Button-1>', lambda event: self.create_point(event.x, event.y))
        self.window.mainloop()

    def do_connect(self, p1, p2, tracks=None, length=0):
        if tracks is None:
            tracks = {1}
        print(p1, p2)
        if p1 == p2 and length > 2:
            print(3)
            return True, tracks
        result = False
        for i in ((p1[0], p1[1] - 1), (p1[0] - 1, p1[1] - 1), (p1[0] - 1, p1[1]), (p1[0] + 1, p1[1] - 1),
                  (p1[0] - 1, p1[1] + 1), (p1[0] + 1, p1[1]), (p1[0] + 1, p1[1] + 1), (p1[0], p1[1] + 1)):
            try:
                if self.points_map[i[1]][i[0]] == self.points_map[p1[1]][p1[0]] and not ((i, p1) in tracks):
                    print(tracks, (p1, p2))
                    variable = self.do_connect(i, p2, tracks and {(i, p2), (p2, i)}, length + 1)
                    result += variable[0]
                    tracks.update(variable[1])
            except IndexError:
                pass
        return bool(result), tracks

    def draw(self, x, y):
        self.position[0] = x
        self.position[1] = y
        w = h = 640 // (self.scale * 16)
        for i in range(len(self.points_map[y:y + h:])):
            for j in range(len(self.points_map[i][x:x + w:])):
                self.canvas.create_line((i * 16 + 8) * self.scale, j * self.scale * 16,
                                        (i * 16 + 8) * self.scale, (j + 1) * self.scale * 16)
                self.canvas.create_line(i * self.scale * 16, (j * 16 + 8) * self.scale,
                                        (i + 1) * self.scale * 16, (j * 16 + 8) * self.scale)
                if self.points_map[j:j + h:][i][i:i + w:][j] != 0:
                    self.canvas.create_oval((i * 16 + 5) * self.scale, (j * 16 + 5) * self.scale,
                                            (i * 16 + 11) * self.scale, (j * 16 + 11) * self.scale,
                                            fill=self.colors[self.points_map[y:y + h:][i][x:x + w:][j]])
        for i in range(len(self.points_map[y:y + h - 1:])):
            for j in range(len(self.points_map[i][x:x + w - 1:])):
                if self.points_map[i][j] == self.points_map[i][j + 1] > 0:
                    self.canvas.create_line((j * 16 - 8) * self.scale, (i * 16 - 8) * self.scale,
                                            (j * 16 + 8) * self.scale, (i * 16 - 8) * self.scale,
                                            fill=self.colors[self.points_map[i][j]],
                                            width=2 * self.scale)
                if self.points_map[i][j] == self.points_map[i + 1][j] > 0:
                    self.canvas.create_line((j * 16 - 8) * self.scale, (i * 16 - 8) * self.scale,
                                            (j * 16 - 8) * self.scale, (i * 16 + 8) * self.scale,
                                            fill=self.colors[self.points_map[i][j]],
                                            width=2 * self.scale)

    def to_scale(self, _scale):
        if _scale != 0 and _scale != 16:
            self.canvas.delete('all')
            self.scale = _scale
            self.draw(self.position[0], self.position[1])

    def translate(self, dx, dy):
        if self.position[1] + dy <= 0:
            self.points_map.insert(0, [0] * len(self.points_map[0]))
            self.position[1] += 1
            self.origin[1] += 1
        if self.position[0] + dx <= 0:
            for i in range(len(self.points_map)):
                self.points_map[i].insert(0, 0)
            self.position[0] += 1
            self.origin[0] += 1
        self.canvas.delete('all')
        self.draw(self.position[0] + dx, self.position[1] + dy)

    def create_point(self, x, y):
        x, y = x // (16 * self.scale) + \
               self.position[0], y // (16 * self.scale) + self.position[1]
        if self.points_map[y][x] == 0:
            self.points_map[y][x] = int(self.is_green_turn[0])
            print(self.do_connect((x, y), (x, y)))
            self.canvas.delete('all')
            self.draw(self.position[0], self.position[1])
            self.is_green_turn[0] = not self.is_green_turn[0]


App()
