from tkinter import Tk, Canvas, Button
from PIL import Image, ImageTk

root = Tk()
root.title('Dots')
canvas = Canvas(width=640, height=640)


class Resources:
    settings = ImageTk.PhotoImage(Image.open('resources/settings.png'))
    singleplayer = ImageTk.PhotoImage(Image.open('resources/singleplayer.png'))
    multiplayer = ImageTk.PhotoImage(Image.open('resources/multiplayer.png'))


class StartMenu:
    def __init__(self):
        canvas.place_forget()
        self.start_canvas = Canvas(root, width=640, height=640, bg='#20B2AA')

        self.start_canvas.create_image(96, 220, image=Resources.singleplayer,
                                           anchor='center', tag='singleplayer')
        self.start_canvas.create_image(320, 220, image=Resources.multiplayer,
                                           anchor='center', tag='multiplayer')        
        Button(self.start_canvas, text='QUIT', command=StartMenu.quit).place(x=320, y=600)
        self.start_canvas.pack()
        self.start_canvas.tag_bind('singleplayer', '<Button-1>', lambda event: self.start_game())
        

    def start_game(self):
        self.start_canvas.destroy()
        canvas.place(relx=0.5, rely=0, anchor='n')
        Dots('#20D020', 'blue')

    @staticmethod
    def quit():
        root.destroy()


class Dots:
    def __init__(self, color1: str, color2: str):
        self.points = [[0] * 100 for _ in range(100)]
        self.colors = ["magenta", color1, color2]
        self.tracks = set()

        self.is_greens_turn = 1
        self.scale = 2
        self.position = [0, 0]
        self.origin = [0, 0]

        self.draw(1, 1)
        root.bind('<Control-=>', lambda event: self.set_scale(self.scale * 2))
        root.bind('<MouseWheel>', lambda event: self.set_scale(self.scale // 2))
        root.bind('<Up>', lambda event: self.translate(0, -1))
        root.bind('<Down>', lambda event: self.translate(0, 1))
        root.bind('<Left>', lambda event: self.translate(-1, 0))
        root.bind('<Right>', lambda event: self.translate(1, 0))
        canvas.bind('<Button-1>', lambda event: self.create_point(event.x, event.y))

    @staticmethod
    def get_adjacent(point: (int, int)):
        return ((point[0], point[1] - 1), (point[0] + 1, point[1]),
                (point[0], point[1] + 1), (point[0] - 1, point[1]))

    @staticmethod
    def get_surrounding(point: (int, int)):
        return ((point[0], point[1] - 1), (point[0] + 1, point[1] - 1),
                (point[0] + 1, point[1]), (point[0] + 1, point[1] + 1),
                (point[0], point[1] + 1), (point[0] - 1, point[1] + 1),
                (point[0] - 1, point[1]), (point[0] - 1, point[1] - 1))

    def do_connect(self, point: (int, int)):
        open_p = []
        used = []
        for i in Dots.get_surrounding(point):
            if self.points[i[1]][i[0]] == self.points[point[1]][point[0]]:
                open_p += [(point, i)]
        while len(open_p) > 0:
            position = open_p[-1][1]
            used += open_p[-1:]
            open_p.pop()
            if position == point:
                self.tracks.update(set(used))
            else:
                for i in Dots.get_surrounding(position):
                    if self.points[i[1]][i[0]] == self.points[position[1]][position[0]] and used.count(
                            (position, i)) == 0 and \
                            used.count((i, position)) == 0 \
                            and open_p.count((position, i)) == 0:
                        open_p += [(position, i)]
        for i in Dots.get_adjacent(point):
            if self.points[i[1]][i[0]] == self.points[point[1]][point[0]]:
                self.tracks.update({(point, i)})

    def draw_point(self, point_type: int, x: int, y: int):
        canvas.create_line((x * 16 + 8) * self.scale, y * self.scale * 16,
                           (x * 16 + 8) * self.scale, (y + 1) * self.scale * 16)
        canvas.create_line(x * self.scale * 16, (y * 16 + 8) * self.scale,
                           (x + 1) * self.scale * 16, (y * 16 + 8) * self.scale)
        if point_type != 0:
            canvas.create_oval((x * 16 + 5) * self.scale, (y * 16 + 5) * self.scale,
                               (x * 16 + 11) * self.scale, (y * 16 + 11) * self.scale,
                               fill=self.colors[point_type])

    def draw(self, x: int, y: int):
        self.position[0] = x
        self.position[1] = y
        w = h = 640 // (self.scale * 16)
        for i in range(len(self.points[y:y + h])):
            for j in range(len(self.points[i][x:x + w])):
                self.draw_point(self.points[y:y + h][i][x:x + w][j], j, i)
        for i in self.tracks:
            if x - 1 <= i[0][0] <= x + w + 1 and y - 1 <= i[0][1] <= y + h + 1 and x - 1 <= i[1][0] \
                    <= x + w + 1 and y - 1 <= i[1][1] <= y + h + 1:
                canvas.create_line(((i[0][0] - self.position[0]) * 16 + 8) * self.scale,
                                   ((i[0][1] - self.position[1]) * 16 + 8) * self.scale,
                                   ((i[1][0] - self.position[0]) * 16 + 8) * self.scale,
                                   ((i[1][1] - self.position[1]) * 16 + 8) * self.scale,
                                   fill=self.colors[self.points[i[0][1]][i[0][0]]],
                                   width=2 * self.scale)

    def set_scale(self, scale: float):
        if scale != 0 and scale != 16:
            canvas.delete('all')
            self.scale = scale
            self.draw(self.position[0], self.position[1])

    def translate(self, x: int, y: int):
        while self.position[1] + y <= 0:
            self.points.insert(0, [0] * len(self.points[0]))
            self.position[1] += 1
            self.origin[1] += 1
            self.tracks = set([((i[0][0], i[0][1] + 1), (i[1][0], i[1][1] + 1)) for i in self.tracks])
        while self.position[0] + x <= 0:
            for i in range(len(self.points)):
                self.points[i].insert(0, 0)
            self.position[0] += 1
            self.origin[0] += 1
            self.tracks = set([((i[0][0] + 1, i[0][1]), (i[1][0] + 1, i[1][1])) for i in self.tracks])
        while self.position[1] + y + 80 // self.scale >= len(self.points):
            self.points.append([0] * len(self.points[0]))
        while self.position[0] + x + 80 // self.scale >= len(self.points[0]):
            for i in range(len(self.points)):
                self.points[i].append(0)
        canvas.delete('all')
        self.draw(self.position[0] + x, self.position[1] + y)

    def create_point(self, x: int, y: int):
        x, y = x // (16 * self.scale) + self.position[0], y // (16 * self.scale) + self.position[1]
        if self.points[y][x] == 0:
            self.points[y][x] = self.is_greens_turn
            self.do_connect((x, y))
            canvas.delete('all')
            self.draw(self.position[0], self.position[1])
            if self.is_greens_turn == 1:
                self.is_greens_turn = 2
            else:
                self.is_greens_turn = 1


StartMenu()
root.attributes('-fullscreen', True)
root.mainloop()
