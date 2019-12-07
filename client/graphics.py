from PyQt5.QtWidgets import QLabel, QMainWindow, QApplication
from PyQt5.QtGui import QPixmap, QPainter, QPen, QColor, QImage
from PyQt5.QtCore import Qt, QLine, QPoint
from PIL import Image, ImageQt
from resources import Resources


class Line(QLine):
    def __init__(self, x1, y1, x2, y2, **kwargs):
        super().__init__(x1, y1, x2, y2)
        self.fill = kwargs.get('fill', 'black')
        self.width = kwargs.get('width', 1)

    def draw(self, master):
        painter = QPainter(master)
        pen = QPen(QColor(self.fill))
        pen.setWidth(self.width)
        painter.setPen(pen)
        painter.drawLine(self)
        painter.end()


class Point(QPoint):
    def __init__(self, x, y, **kwargs):
        super().__init__(x, y)
        self.radius = kwargs.get('radius', 1)
        self.fill = kwargs.get('fill', 'black')

    def draw(self, master):
        painter = QPainter(master)
        pen = QPen(QColor(self.fill))
        pen.setWidth(self.radius)
        painter.setPen(pen)
        painter.drawPoint(self)
        painter.end()


class DrawWindow(QMainWindow):
    def __init__(self, width=1920, height=1080):
        super().__init__()
        self.setWindowTitle('Dots')
        self.graphics_container = QLabel()
        self.setCentralWidget(self.graphics_container)
        self.canvas = Canvas(width=width, height=height, master_window=self)
        self.mouse_press_events = {}
        self.key_press_events = {}
        self.graphics_update()

    def toggle_full_screen(self):
        if self.isFullScreen():
            self.showNormal()
        else:
            self.showFullScreen()

    def delete_all(self):
        self.graphics_container.pixmap().fill(QColor('green'))
        self.graphics_container.update()

    def keyPressEvent(self, event):
        if event.key() in self.key_press_events.keys():
            data = self.key_press_events[event.key()]
            data[0](*data[1])

    def mousePressEvent(self, event):
        if (event.button(), event.x(), event.y()) in self.mouse_press_events.keys():
            data = self.mouse_press_events[(event.button(), event.x(), event.y())]
            data[0](*data[1])

    def key_bind(self, event_key, function, arg=()):
        self.key_press_events[event_key] = (function, arg)

    def mouse_bind(self, event_button, x, y, function, arg=()):
        self.mouse_press_events[(event_button, x, y)] = (function, arg)

    def graphics_update(self):
        self.graphics_container.setPixmap(self.canvas)
        self.update()

    def rect_mouse_bind(self, event_button, x1, y1, x2, y2, function, arg=()):
        arg = list(arg)
        x_parameter = []
        y_parameter = []
        for a in range(len(arg)):
            if arg[a] == '__x__':
                x_parameter.append(a)
            elif arg[a] == '__y__':
                y_parameter.append(a)
        for i in range(int(x1), int(x2) + 1):
            for j in range(int(y1), int(y2) + 1):
                for x in x_parameter:
                    arg[x] = i
                for y in y_parameter:
                    arg[y] = j
                self.mouse_bind(event_button, i, j, function, tuple(arg))
# TODO unbind methods


class Canvas(QPixmap):
    def __init__(self, **kwargs):
        if 'width' not in kwargs.keys() or 'height' not in kwargs.keys():
            raise AttributeError

        super().__init__(kwargs['width'], kwargs['height'])
        master_window = kwargs.get('master_window', None)
        if master_window is not None:
            self.master_window = master_window
        self.color = kwargs.get('color', 'white')
        self.fill(QColor(self.color))
        self.objects_tags = ['self']
        self.objects = {'self': (self, 0, 0)}

    def create_object(self, **kwargs):
        obj, x, y, master_tag, tag, relx, rely = kwargs['obj'], kwargs.get('x', 0),\
            kwargs.get('y', 0), kwargs.get('master_tag', 'self'),\
            kwargs['tag'], kwargs.get('relx', None), kwargs.get('rely', None)

        if tag == 'self':
            raise KeyError

        if relx is not None:
            x = self.objects[master_tag][0].size().width() * relx -\
                obj.size().width() * .5
        if rely is not None:
            y = self.objects[master_tag][0].size().height() * rely -\
                obj.size().height() * .5

        if master_tag == 'self':
            master_tag = self.objects_tags[-1]
            self.objects[tag] = obj, x, y
        else:
            self.objects_tags[tag] = obj, x + self.objects[master_tag][1],\
                y + self.objects[master_tag][2]

        self.objects_tags.insert(self.objects_tags.index(master_tag) + 1, tag)
        self.update()

    def draw_obj(self, *args):
        if type(args[0]) in {Line, Point}:
            func = Data.draw_functions[type(args[0])]
            func(args[0], self)
            return

        if len(args) != 3:
            raise AttributeError

        obj, x, y = args
        painter = QPainter(self)
        func = Data.draw_functions[type(obj)]
        func(painter, x, y, obj)
        painter.end()

    def update(self):
        self.fill(QColor(self.color))
        for tag in self.objects_tags[1:]:
            self.draw_obj(*self.objects[tag])

    def delete_object(self, obj_tag):
        if obj_tag in self.objects_tags[1:]:
            self.objects_tags.remove(obj_tag)
            self.objects.pop(obj_tag)
            self.update()
        else:
            raise KeyError

    def mouse_bind(self, event_button, x, y, function, arg=(), tag='self'):
        self.master_window.mouse_press_events[(event_button, self.objects[tag][1] + x, self.objects[tag][2] + y)] = (function, arg)

    # TODO unbind methods

    def rect_mouse_bind(self, event_button, x1, y1, x2, y2, function, arg=(), tag='self'):
        x1 += self.objects[tag][1]
        x2 += self.objects[tag][1]
        y1 += self.objects[tag][2]
        y2 += self.objects[tag][2]
        self.master_window.rect_mouse_bind(event_button, x1, y1, x2, y2, function, arg)


class Data:
    draw_functions = {QPixmap: QPainter.drawPixmap, Canvas: QPainter.drawPixmap,
                      QLine: QPainter.drawLine, Line: Line.draw,
                      QImage: QPainter.drawImage, Point: Point.draw}
    image = ImageQt.ImageQt(Image.open('resources/settings.png'))

    @staticmethod
    def main_menu_canvas():
        start_canvas = Canvas(width=640, height=640, color='grey')
        start_canvas.create_object(x=100, y=10, obj=QImage(Resources.logo_texture),
                                   tag='logo')
        start_canvas.create_object(x=560, y=560, obj=QImage(Resources.settings_button),
                                   tag='settings_button')
        start_canvas.create_object(x=192, y=200, obj=QImage(Resources.singleplayer_button),
                                   tag='singleplayer_button')
        start_canvas.create_object(x=192, y=300, obj=QImage(Resources.local_multiplayer_button),
                                   tag='local_multiplayer_button')
        start_canvas.create_object(x=192, y=400, obj=QImage(Resources.multiplayer_button),
                                   tag='multiplayer_button')
        start_canvas.create_object(x=192, y=500, obj=QImage(Resources.quit_button),
                                   tag='quit_button')
        return start_canvas

    @staticmethod
    def game_menu_canvas():
        game_menu_canvas = Canvas(width=320, height=540, color='grey')
        game_menu_canvas.create_object(x=160, y=500, image=QImage(Resources.quit_button),
                                       tag='game_quit')
        return game_menu_canvas
