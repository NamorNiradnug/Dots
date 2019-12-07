from graphics import *
from resources import *
from PIL import Image, ImageQt
from PyQt5.QtWidgets import QApplication
from PyQt5.QtGui import QColor, QImage
from PyQt5.QtCore import Qt
from pathlib import Path

app = QApplication([])
screen_size = app.desktop().screenGeometry()
screen_width = screen_size.width()
screen_height = screen_size.height()
#window = DrawWindow(screen_width, screen_height)
window = DrawWindow(900, 900)
window.show()


class Settings:
    def __init__(self):
        self.colors = ['#20D020', 'blue']
        self.fullscreen = False
        self.sound_voice = 100
        self.draw_line_tracks = True
        self.dots_canvas_color = 'white'
        self.settings_canvas = Canvas(width=320, height=540, color='red')

    def toggle_settings(self, x=0, y=0):
        if 'settings' not in window.canvas.objects_tags:
            self.open_settings(x, y)
        else:
            self.close_settings()

    def open_settings(self, x, y):
        window.canvas.create_object(x=x, y=y, tag='settings')
        window.graphics_update()

    def close_settings(self):
        window.canvas.delete_object('settings')
        window.graphics_update()

    def change_fullscreen(self):
        self.fullscreen = not self.fullscreen
        window.toggle_full_screen()


settings = Settings()


class MainMenu:
    def __init__(self):
        self.start_canvas = Data.main_menu_canvas()
        window.canvas.create_object(obj=self.start_canvas, x=400, y=40, tag='MainMenu')
        window.canvas.rect_mouse_bind(1, 560, 560, 624, 624, toggle_settings, arg=(0, 0), 'MainMenu')
        window.graphics_update()

    def start_game(self):
        window.canvas.delete_object('MainMenu')
        LocalMultiplayerDots('#20D020', 'blue')

    @staticmethod
    def quit():
        app.quit()


class GameMenu:
    def __init__(self):
        self.game_menu_canvas = Data.game_menu_canvas()
        self.game_menu_canvas.tag_bind('game_quit', '<Button-1>', lambda event: MainMenu.quit())
        self.master.tag_bind(self.game_menu_button, '<Button-1>', lambda event: self.toggle_game_menu())
        root.bind('<Escape>', lambda event: self.toggle_game_menu())

    def toggle_game_menu(self):
        if self.game_menu_canvas.place_info() == {}:
            self.open_game_menu()
        else:
            self.close_game_menu()

    def open_game_menu(self):
        self.game_menu_canvas.place(relx=0.5, rely=0.5, anchor='center')

    def close_game_menu(self):
        self.game_menu_canvas.place_forget()

    # This function is required to redraw dots to canvas, when player makes a turn, and dots are drawn in front of
    # this button.
    def redraw(self):
        self.master.delete(self.game_menu_button)
        self.game_menu_button = self.master.create_image(0, 0, image=Resources.home_button, anchor='nw')


class Dots:
    def __init__(self, color1: str = settings.colors[0], color2: str = settings.colors[1],
                 width: int = screen_width, height: int = screen_height):
        self.height = height
        self.width = width
        self.dots_canvas = Canvas(root, bg=settings.dots_canvas_bg, bd=0)
        self.dots_canvas.config(width=self.width, height=self.height)
        self.dots_canvas.pack()
        self.menu = GameMenu(self.dots_canvas)
        self.points = [[0] * 100 for _ in range(100)]
        self.colors = ["magenta", color1, color2]
        self.tracks = set()

        self.is_greens_turn = 1
        self.scale = 2
        self.position = [0, 0]
        self.origin = [0, 0]

        self.draw(1, 1)
        root.bind('<MouseWheel>', lambda event: self.set_scale(event.delta))
        root.bind('<Up>', lambda event: self.translate(0, -1))
        root.bind('<Down>', lambda event: self.translate(0, 1))
        root.bind('<Left>', lambda event: self.translate(-1, 0))
        root.bind('<Right>', lambda event: self.translate(1, 0))
        self.turn_start()

    @staticmethod
    def get_adjacent(point: (int, int)):
        return ((point[0], point[1] - 1), (point[0] + 1, point[1]),
                (point[0], point[1] + 1), (point[0] - 1, point[1]))

    def get_surrounding(self, point: (int, int)):
        return [i for i in ((point[0], point[1] - 1), (point[0] + 1, point[1] - 1),
                            (point[0] + 1, point[1]), (point[0] + 1, point[1] + 1),
                            (point[0], point[1] + 1), (point[0] - 1, point[1] + 1),
                            (point[0] - 1, point[1]), (point[0] - 1, point[1] - 1))
                if self.points[i[1]][i[0]] == self.points[point[1]][point[0]]]

    def optim_clear(self, tracks):
        if len(tracks) != 0:
            deleting = [tracks[0]]
            for __ in range(len(tracks)):
                for i in tracks:
                    if set(self.get_surrounding(i[1])).intersection(set([p[1] for p in deleting])) != set():
                        self.tracks.add(i)
                        tracks.remove(i)
                        deleting.append(i)
        return tracks

    def find_triangulars(self, point):
        self_adjacent = [i for i in Dots.get_adjacent(point) if i in self.get_surrounding(point)]
        for p in range(len(self_adjacent)):
            if self_adjacent[p] in self.get_surrounding(self_adjacent[(p + 1) % len(self_adjacent)]):
                self.tracks.add((self_adjacent[p], self_adjacent[(p + 1) % len(self_adjacent)]))

    def do_connect(self, point: (int, int)):
        if settings.draw_line_tracks:
            self.tracks.update(set([(point, i) for i in Dots.get_adjacent(point)
                                    if self.points[i[1]][i[0]] == self.points[point[1]][point[0]]]))
        self.find_triangulars(point)
        connected = {point}
        used = []
        tracks = []
        open_t = [(point, i) for i in self.get_surrounding(point)]
        open_t = self.optim_clear(open_t)
        while len(open_t) != 0:
            position = open_t[-1][1]
            used += [open_t[-1], open_t[-1][::-1]]
            open_t.pop()
            for i in range(len(tracks)):
                if tracks[i][-1][1] == used[-2][0]:
                    tracks.append(tracks[i] + [used[-2]])
            if used[-1][1] in connected:
                tracks.append([(used[-1][1], position)])
            if position != point:
                open_t += [(position, i) for i in self.get_surrounding(position)
                           if not ((position, i) in used)]
            else:
                for i in tracks:
                    if i[-1][1] in connected:
                        self.tracks.update(set(i))
                        for t in i:
                             connected.add(t[1])

    def draw_point(self, point_type: int, x: int, y: int):
        if point_type != 0:
            self.dots_canvas.create_oval((x * 16 + 5) * self.scale, (y * 16 + 5) * self.scale,
                                         (x * 16 + 11) * self.scale, (y * 16 + 11) * self.scale,
                                         fill=self.colors[point_type])

    def find_eaten(self, point):
        pass

    def draw(self, x: int, y: int):
        self.position[0] = x
        self.position[1] = y
        w = self.width // (self.scale * 16) + 1
        h = self.height // (self.scale * 16) + 1
        for i in range(w):
            self.dots_canvas.create_line(((16 * i) + 8) * self.scale, 0,
                                         ((i * 16) + 8) * self.scale, self.height,
                                         fill='black')
        for i in range(h):
            self.dots_canvas.create_line(0, ((16 * i) + 8) * self.scale,
                                         self.width, ((16 * i) + 8) * self.scale,
                                         fill='black')
            for j in range(len(self.points[i][x:x + w])):
                self.draw_point(self.points[y:y + h][i][x:x + w][j], j, i)
        for i in self.tracks:
            if x - 1 <= i[0][0] <= x + w + 1 and y - 1 <= i[0][1] <= y + h + 1 and x - 1 <= i[1][0] \
                    <= x + w + 1 and y - 1 <= i[1][1] <= y + h + 1:
                self.dots_canvas.create_line(((i[0][0] - self.position[0]) * 16 + 8) * self.scale,
                                             ((i[0][1] - self.position[1]) * 16 + 8) * self.scale,
                                             ((i[1][0] - self.position[0]) * 16 + 8) * self.scale,
                                             ((i[1][1] - self.position[1]) * 16 + 8) * self.scale,
                                             fill=self.colors[self.points[i[0][1]][i[0][0]]], width=2 * self.scale)
        self.menu.redraw()

 # TODO set_scale

    def set_scale(self, delta: int):
        scale = int(self.scale * (2 ** (delta // (abs(delta)))))
        if scale != 1 and scale != 16:
            self.dots_canvas.delete('all')
            self.scale = scale
            if delta > 0:
                self.position[0] += int(self.width / (64 * self.scale))
                self.position[1] += int(self.height / (64 * self.scale))
            self.draw(self.position[0], self.position[1])

    def translate(self, x: int, y: int):
        # Update self.points for draw function in Dots.
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
        while self.position[1] + y + 200 // self.scale >= len(self.points):
            self.points.append([0] * len(self.points[0]))
        while self.position[0] + x + 200 // self.scale >= len(self.points[0]):
            for i in range(len(self.points)):
                self.points[i].append(0)
        self.dots_canvas.delete('all')
        self.draw(self.position[0] + x, self.position[1] + y)

    def turn_start(self):
        pass

    def turn(self, x: int, y: int):
        if x <= 64 and y <= 64:
            self.menu.toggle_game_menu()
        else:
            x, y = x // (16 * self.scale) + self.position[0], y // (16 * self.scale) + self.position[1]
            if self.points[y][x] == 0:
                self.points[y][x] = self.is_greens_turn
                self.do_connect((x, y))
                self.dots_canvas.delete('all')
                self.draw(self.position[0], self.position[1])
                if self.is_greens_turn == 1:
                    self.is_greens_turn = 2
                else:
                    self.is_greens_turn = 1
                self.turn_start()


class LocalMultiplayerDots(Dots):
    def turn_start(self):
        self.dots_canvas.bind('<Button-1>', lambda event: self.turn(event.x, event.y))


main = MainMenu()
app.exec_()
