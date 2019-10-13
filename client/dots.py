import os
from tkinter import Tk, Canvas
from PIL import Image, ImageTk
from pathlib import Path

root = Tk()
root.title('Dots')
canvas = Canvas()

class Resources:
    resources = Path('resources')
    colors = [ImageTk.PhotoImage(Image.open(i)) for i in os.listdir(resources / 'settings_colors')]
    settings_texture = ImageTk.PhotoImage(Image.open(resources / 'settings.png'))
    singleplayer_texture = ImageTk.PhotoImage(Image.open(resources / 'singleplayer.png'))
    multiplayer_texture = ImageTk.PhotoImage(Image.open(resources / 'multiplayer.png'))
    game_menu_texture = ImageTk.PhotoImage(Image.open(resources / 'menu_icon.png'))
    local_multiplayer_texture = ImageTk.PhotoImage(Image.open(resources / 'local_multiplayer.png'))
    quit_texture = ImageTk.PhotoImage(Image.open(resources / 'quit.png'))
    item_texture = ImageTk.PhotoImage(Image.open(resources / 'dots_item.png'))

class Settings:
    def __init__(self):
        self.colors = ['#20D020', 'blue']
        self.fullscreen = False
        self.sound_voice = 100
       # self.music - random music
       # self.turn_voice - random voice playing when players turn 
        self.settings_canvas = Canvas(width=320, height=540)
       # self.
        self.settings_canvas.place_forget()
        
    def open_settings(self, master, x, y):
        self.settings_canvas['master'] = master
        self.settings_canvas.place(x, y)
        
    def close_settings(self):
        self.settings_canvas.place_forget()
    
    def change_fullscreen(self):
        self.fuulscreen = not self.fullscreen
        root.atributes('-fullscreen', self.fullscreen)

settings = Settings()

class StartMenu:
    def __init__(self):
        canvas.place_forget()
        self.start_canvas = Canvas(width=640, height=640, bg='grey')
        self.start_canvas.create_image(0, 10, image=Resources.item_texture, anchor='nw')
        self.start_canvas.create_image(560, 560, image=Resources.settings_texture, anchor='nw',
                                       tag='settings')
        self.start_canvas.create_image(192, 200, image=Resources.singleplayer_texture, anchor='nw',
                                       tag='singleplayer')
        self.start_canvas.create_image(192, 300, image=Resources.local_multiplayer_texture, anchor='nw',
                                       tag='local_multiplayer')        
        self.start_canvas.create_image(192, 400, image=Resources.multiplayer_texture, anchor='nw',
                                       tag='multiplayer')
        self.start_canvas.create_image(192, 500, image=Resources.quit_texture, anchor='nw',
                                       tag='quit')
        self.start_canvas.tag_bind('singleplayer', '<Button-1>', lambda event: self.start_game())
        self.start_canvas.tag_bind('settings', '<Button-1>', lambda event: self.open_settings())
        self.start_canvas.tag_bind('quit', '<Button-1>', lambda event: StartMenu.quit())        
        self.start_canvas.pack()

    def start_game(self):
        self.start_canvas.destroy()
        canvas.place(relx=0.5, rely=0, anchor='n')
        LocalMultiplayerDots('#20D020', 'blue')

    def open_settings(self):
        pass
        
    @staticmethod
    def quit():
        root.destroy()


class GameMenu:
    def __init__(self):
        self.game_menu_canvas = Canvas(width=320, height=540, bg='grey')
        self.game_menu_canvas.create_image(160, 500, image=Resources.quit_texture, anchor='center',
                                           tag='game_quit')
        self.game_menu_canvas.tag_bind('game_quit', '<Button-1>', lambda event: StartMenu.quit())  
        self.game_menu_button = canvas.create_image(0, 0, image=Resources.game_menu_texture, anchor='nw')
        canvas.tag_bind(self.game_menu_button, '<Button-1>', lambda event: self.open_game_menu())
        root.bind('<Escape>', lambda event: self.open_game_menu())

    def open_game_menu(self):
        self.game_menu_canvas.place(relx=0.5, rely=0.5, anchor='center')
        canvas.tag_bind(self.game_menu_button, '<Button-1>', lambda event: self.close_game_menu())
        root.bind('<Escape>', lambda event: self.close_game_menu())

    def close_game_menu(self):
        self.game_menu_canvas.place_forget()
        canvas.tag_bind(self.game_menu_button, '<Button-1>', lambda event: self.open_game_menu())
        root.bind('<Escape>', lambda event: self.open_game_menu())

    def redraw(self):
        canvas.delete(self.game_menu_button)
        self.game_menu_button = canvas.create_image(0, 0, image=Resources.game_menu_texture, anchor='nw')


class Dots:
    def __init__(self, color1: str = settings.colors[0], color2: str = settings.colors[1], width: int = root.winfo_screenwidth(),
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
        print(scale)
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
        
#class MultiplayerDots(Dots):

#class SingleplayerDots(Dots):

StartMenu()
root.mainloop()
