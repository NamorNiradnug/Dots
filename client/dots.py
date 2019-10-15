from tkinter import Tk, Canvas
from PIL import Image, ImageTk
from pathlib import Path

# TODO: Комментируй код! Я половину не понимаю, пиши комменты! Например (это пример, очевидное комментить не надо):
# Создаём окно.
root = Tk()
root.title('Dots')
canvas = Canvas()


class Resources:
    resources = Path('resources')
    settings_button = ImageTk.PhotoImage(Image.open(resources / 'settings.png'))
    singleplayer_button = ImageTk.PhotoImage(Image.open(resources / 'singleplayer.png'))
    multiplayer_button = ImageTk.PhotoImage(Image.open(resources / 'multiplayer.png'))
    home_button = ImageTk.PhotoImage(Image.open(resources / 'home.png'))
    local_multiplayer_button = ImageTk.PhotoImage(Image.open(resources / 'local_multiplayer.png'))
    quit_button = ImageTk.PhotoImage(Image.open(resources / 'quit.png'))
    logo_texture = ImageTk.PhotoImage(Image.open(resources / 'menu_logo.png'))


class Settings:
    def __init__(self):
        self.colors = ['#20D020', 'blue']
        self.fullscreen = False
        self.sound_voice = 100
        self.settings_canvas = Canvas(root, width=320, height=540)
        self.settings_canvas.place_forget()

    def open_settings(self, master, x, y):
        self.settings_canvas.master = master
        self.settings_canvas.place(x=x, y=y)

    def close_settings(self):
        self.settings_canvas.place_forget()

    def change_fullscreen(self):
        self.fullscreen = not self.fullscreen
        root.attributes('-fullscreen', self.fullscreen)


settings = Settings()


class MainMenu:
    def __init__(self):
        canvas.place_forget()

        self.start_canvas = Canvas(width=640, height=640, bg='grey')

        self.start_canvas.create_image(100, 10, image=Resources.logo_texture, anchor='nw')
        self.start_canvas.create_image(560, 560, image=Resources.settings_button,
                                       anchor='nw', tag='settings')
        self.start_canvas.create_image(192, 200, image=Resources.singleplayer_button,
                                       anchor='nw', tag='singleplayer')
        self.start_canvas.create_image(192, 300, image=Resources.local_multiplayer_button,
                                       anchor='nw', tag='local_multiplayer')
        self.start_canvas.create_image(192, 400, image=Resources.multiplayer_button,
                                       anchor='nw', tag='multiplayer')
        self.start_canvas.create_image(192, 500, image=Resources.quit_button,
                                       anchor='nw', tag='quit')
        self.start_canvas.tag_bind('singleplayer', '<Button-1>', lambda event: self.start_game())
        self.start_canvas.tag_bind('settings', '<Button-1>', lambda event: self.open_settings())
        self.start_canvas.tag_bind('quit', '<Button-1>', lambda event: MainMenu.quit())
        self.start_canvas.pack()

    def start_game(self):
        self.start_canvas.destroy()
        canvas.place(relx=0.5, rely=0, anchor='n')
        LocalMultiplayerDots('#20D020', 'blue')

    def open_settings(self):
        settings.open_settings(self.start_canvas, 0, 160)

    @staticmethod
    def quit():
        root.destroy()


class GameMenu:
    def __init__(self):
        self.game_menu_canvas = Canvas(width=320, height=540, bg='grey')
        self.game_menu_canvas.create_image(160, 500, image=Resources.quit_button, anchor='center',
                                           tag='game_quit')
        self.game_menu_canvas.tag_bind('game_quit', '<Button-1>', lambda event: MainMenu.quit())
        self.game_menu_button = canvas.create_image(0, 0, image=Resources.home_button, anchor='nw')
        canvas.tag_bind(self.game_menu_button, '<Button-1>', lambda event: self.open_game_menu())
        root.bind('<Escape>', lambda event: self.open_game_menu())

    def open_game_menu(self):
        self.game_menu_canvas.place(relx=0.5, rely=0.5, anchor='center')
        root.tag_bind(self.game_menu_button, '<Button-1>', lambda event: self.close_game_menu())
        root.bind('<Escape>', lambda event: self.close_game_menu())

    def close_game_menu(self):
        self.game_menu_canvas.place_forget()
        canvas.tag_bind(self.game_menu_button, '<Button-1>', lambda event: self.open_game_menu())
        root.bind('<Escape>', lambda event: self.open_game_menu())

    def redraw(self):
        canvas.delete(self.game_menu_button)
        self.game_menu_button = canvas.create_image(0, 0, image=Resources.home_button, anchor='nw')


class Dots:
    def __init__(self, color1: str = settings.colors[0], color2: str = settings.colors[1],
                 width: int = root.winfo_screenwidth(),
                 height: int = root.winfo_screenheight()):
        self.menu = GameMenu()
        self.height = height
        self.width = width
        canvas.config(width=self.width, height=self.height)
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

    @staticmethod
    def to_tracks(track: list):
        return {(track[i], track[i + 1]) for i in range(len(track) - 1)}

    def get_surrounding(self, point: (int, int)):
        return [i for i in ((point[0], point[1] - 1), (point[0] + 1, point[1] - 1),
                            (point[0] + 1, point[1]), (point[0] + 1, point[1] + 1),
                            (point[0], point[1] + 1), (point[0] - 1, point[1] + 1),
                            (point[0] - 1, point[1]), (point[0] - 1, point[1] - 1))
                if self.points[i[1]][i[0]] == self.points[point[1]][point[0]]]

    # TODO: ЭТУ ФУНКЦИЮ НУЖНО ПЕРЕДЕЛАТЬ. СНОВА.
    def do_connect(self, point: (int, int)):
        open_p = self.get_surrounding(point)
        used = []

        # TODO: КАКОГО ФИГА ЗДЕСЬ ПРОИСХОДИТ??? ЗАЧЕМ [point, i]???
        tracks = [[point, i] for i in open_p]
        while len(open_p):
            old_tracks = tracks.copy()
            tracks = []
            for i in old_tracks:

                # TODO: old_tracks[i] - list[(int, int), int], а не (int, int)!
                for new in self.get_surrounding(old_tracks[i]):
                    if new == point:

                        # TODO: old_tracks[i] - list[(int, int), int], а не (int, int)!
                        self.tracks.update(Dots.to_tracks(old_tracks[i] + [new]))
                    elif used.count(new):

                        # TODO: old_tracks[i] - list[(int, int), int], а не (int, int)!
                        tracks += old_tracks[i] + [new]
                        open_p.remove(new)
                        used.append(new)
                        open_p += [q for q in self.get_surrounding(new) if used.count(q)]

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
        w = self.width // (self.scale * 16) + 1
        h = self.height // (self.scale * 16)
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
                                   fill=self.colors[self.points[i[0][1]][i[0][0]]], width=2 * self.scale)
        self.menu.redraw()

    def set_scale(self, delta: int):
        scale = int(self.scale * (2 ** (delta // (abs(delta)))))
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

    def turn_start(self):
        pass

    def turn(self, x: int, y: int):
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
            self.turn_start()


class LocalMultiplayerDots(Dots):
    def turn_start(self):
        canvas.bind('<Button-1>', lambda event: self.turn(event.x, event.y))


MainMenu()
root.mainloop()
