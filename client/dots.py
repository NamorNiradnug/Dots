from tkinter import Tk, Canvas


class App:
    def __init__(self):
        self.p_map = []
        for i in range(100):
            self.p_map.append([-1] * 100)
        self.colors = ["#20D020", "blue"]

        self.is_green_turn = False
        self.scale = 2
        self.position = (0, 0)
        self.origin = (0, 0)
        self.window = Tk()
        self.canvas = Canvas(self.window, width=160 * 4, height=4 * 160)
        self.canvas.pack()

        self.draw((1, 1))
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
        for point in ((p1[0], p1[1] - 1), (p1[0] - 1, p1[1] - 1), (p1[0] - 1, p1[1]), (p1[0] + 1, p1[1] - 1),
                      (p1[0] - 1, p1[1] + 1), (p1[0] + 1, p1[1]), (p1[0] + 1, p1[1] + 1), (p1[0], p1[1] + 1)):
            try:
                if self.p_map[point[1]][point[0]] == self.p_map[p1[1]][p1[0]] and not ((point, p1) in tracks):
                    print(tracks, (p1, p2))
                    variable = self.do_connect(point, p2, tracks and {(point, p2), (p2, point)}, length + 1)
                    result += variable[0]
                    tracks.update(variable[1])
            except IndexError:
                pass
        return bool(result), tracks

    def draw(self, point):
        self.position = point
        w = h = 640 // (self.scale * 16)
        for i in range(len(self.p_map[point[1]:point[1] + h])):
            for j in range(len(self.p_map[i][point[0]:point[0] + w])):
                self.canvas.create_line((i * 16 + 8) * self.scale, j * self.scale * 16,
                                        (i * 16 + 8) * self.scale, (j + 1) * self.scale * 16)
                self.canvas.create_line(i * self.scale * 16, (j * 16 + 8) * self.scale,
                                        (i + 1) * self.scale * 16, (j * 16 + 8) * self.scale)
                if self.p_map[j:j + h][i][i:i + w][j] != -1:
                    self.canvas.create_oval((i * 16 + 5) * self.scale, (j * 16 + 5) * self.scale,
                                            (i * 16 + 11) * self.scale, (j * 16 + 11) * self.scale,
                                            fill=self.colors[
                                                self.p_map[point[1]:point[1] + h][i][point[0]:point[0] + w][j]
                                            ])
        for i in range(len(self.p_map[point[1]:point[1] + h:])):
            for j in range(len(self.p_map[i][point[0]:point[0] + w:])):
                try:    
                    if self.p_map[point[1]:point[1] + h:][i][point[0]:point[0] + w:][j] == self.p_map[point[1]:point[1] + h:][i][point[0]:point[0] + w:][j + 1] > 0:
                        self.canvas.create_line((j * 16 + 8) * self.scale, (i * 16 + 8) * self.scale, (j * 16 + 24) * self.scale, (i * 16 + 8) * self.scale, fill = self.colors[self.p_map[point[1]:point[1] + h:][i][point[0]:point[0] + w:][j]], width = 2 * self.scale)
                except:
                    pass
                try:
                    if self.p_map[point[1]:point[1] + h:][i][point[0]:point[0] + w:][j] == self.p_map[point[1]:point[1] + h:][i + 1][point[0]:point[0] + w:][j] > 0:
                        self.canvas.create_line((j * 16 + 8) * self.scale, (i * 16 + 8) * self.scale, (j * 16 + 8) * self.scale, (i * 16 + 24) * self.scale, fill = self.colors[self.p_map[point[1]:point[1] + h:][i][point[0]:point[0] + w:][j]], width = 2 * self.scale)        
                except:
                    pass
            

    def to_scale(self, _scale):
        if _scale != 0 and _scale != 16:
            self.canvas.delete('all')
            self.scale = _scale
            self.draw(self.position)

    def translate(self, dx, dy):
        if self.position[1] <= -dy:
            self.p_map.insert(0, [-1] * len(self.p_map[0]))
            self.position = (self.position[0], self.position[1] + 1)
            self.origin = (self.origin[0], self.origin[1] + 1)
        if self.position[0] <= -dx:
            for i in range(len(self.p_map)):
                self.p_map[i].insert(0, -1)
            self.position = (self.position[0] + 1, self.position[1])
            self.origin = (self.origin[0] + 1, self.origin[1])
        self.canvas.delete('all')
        self.draw((self.position[0] + dx, self.position[1] + dy))

    def create_point(self, x, y):
        x, y = x // (16 * self.scale) + self.position[0], y // (16 * self.scale) + self.position[1]
        if self.p_map[y][x] == -1:
            self.p_map[y][x] = int(self.is_green_turn)
            print(self.do_connect((x, y), (x, y)))
            self.canvas.delete('all')
            self.draw((self.position[0], self.position[1]))
            self.is_green_turn = not self.is_green_turn


App()