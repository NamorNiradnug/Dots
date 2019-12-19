from PyQt5.QtWidgets import QLabel, QMainWindow
from PyQt5.QtGui import QPixmap, QPainter, QPen, QColor, QImage
from PyQt5.QtCore import QLine, QPoint


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


class Circle(QPoint):
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
        self.canvas = Canvas(width=width, height=height, master=self)
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

    def graphics_update(self):
        self.graphics_container.setPixmap(self.canvas)
        self.update()

    def keyPressEvent(self, event):
        if event.key() in self.key_press_events.keys():
            data = self.key_press_events[event.key()]
            data[0](*data[1])

    def mousePressEvent(self, event):
        for button in self.mouse_press_events.keys():
            if button[0] < event.x() < button[2] and \
               button[1] < event.y() < button[3] and \
               event.button() == button[4]:
                arg = self.mouse_press_events[button][1]
                for i in range(len(arg)):
                    if arg[i] == '__x__':
                        arg[i] = event.x()
                    if arg[i] == '__y__':
                        arg[i] = event.y()
                self.mouse_press_events[button][0](*arg)
                return

    def key_bind(self, event_name, function, arg=()):
        self.key_press_events[Data.events_strings[event_name]] = (function, arg)

    def key_unbind(self, event_name):
        if event_name == 'all':
            self.key_press_events = {}
        else:
            self.key_press_events.pop(Data.events_strings[event_name])

# I think this functions doesn't need:
    # def mouse_bind(self, event_button, x, y, function, arg=()):
    #     self.rect_mouse_bind(event_button, x, y, x, y, function, arg)

    # def rect_mouse_bind(self, event_button, x1, y1, x2, y2, function, arg=()):
        # self.mouse_press_events[(x1, y1, x2, y2, event_button)] = function, arg

    # def mouse_unbind(self, button, x=None, y=None):
        # if button == 'all':
            # if x is None and y is None:
                # self.mouse_press_events = {}
            # else:
                # if (x, y) in self.mouse_press_events.keys():
                    # self.mouse_press_events.pop((x, y))
        # else:
            # if (x, y) in self.mouse_press_events.keys():
                # if button in self.mouse_press_events[(x, y)]:
                    # self.key_press_events[(x, y)].pop(button)

    # def rect_mouse_unbind(self, button, x1, y1, x2, y2):
        # for i in range(int(x1), int(x2) + 1):
            # for j in range(int(y1), int(y2) + 1):
                # self.mouse_unbind(button, i, j)


class Canvas(QPixmap):
    def __init__(self, **kwargs):
        if 'width' not in kwargs.keys() or 'height' not in kwargs.keys():
            raise AttributeError

        super().__init__(kwargs['width'], kwargs['height'])
        self.master = kwargs.get('master', None)
        if self.master is None:
            raise AttributeError
        self.color = kwargs.get('color', 'white')
        self.fill(QColor(self.color))
        self.objects_tags = ['self']
        self.objects = {'self': (self, 0, 0),
                        None: (None, 0, 0)}

    def create_object(self, **kwargs):
        obj, x, y, master_tag, tag, relx, rely = kwargs['obj'], kwargs.get('x', 0),\
            kwargs.get('y', 0), kwargs.get('master_tag', None),\
            kwargs['tag'], kwargs.get('relx', None), kwargs.get('rely', None)

        if tag == 'self':
            raise KeyError

        master_tag_copy = master_tag
        if master_tag is None:
            master_tag = 'self'
        if relx is not None:
            x = self.objects[master_tag][0].size().width() * relx -\
                obj.size().width() * .5
        if rely is not None:
            y = self.objects[master_tag][0].size().height() * rely -\
                obj.size().height() * .5

        master_tag = master_tag_copy
        if master_tag is None:
            master_tag = self.objects_tags[-1]
            self.objects[tag] = obj, x, y
        else:
            self.objects_tags[tag] = obj, x + self.objects[master_tag][1],\
                y + self.objects[master_tag][2]

        self.objects_tags.insert(self.objects_tags.index(master_tag) + 1, tag)
        self.update()

    def draw_obj(self, *args):
        if type(args[0]) in {Line, Circle}:
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

    def rect_mouse_bind(self, event_button, x1, y1, x2, y2, function, arg=()):
        if type(self.master) == DrawWindow:
            for old_button in self.master.mouse_press_events.copy().keys():
                if Data.is_intersection(old_button[:4], (x1, y1, x2, y2)):
                    self.master.mouse_press_events.pop(old_button)
            self.master.mouse_press_events[x1, y1, x2, y2, event_button] = function, arg
        else:
            for obj in self.master.objects:
                if obj[0] is self:
                    self.master.rect_mouse_bind(event_button, x1 + obj[1], y1 + obj[2], x2 + obj[1], y2 + obj[2], function, arg)

    def rect_mouse_unbind(self, x1, y1, x2, y2, tag='self'):
        x1 += self.objects[tag][1]
        x2 += self.objects[tag][1]
        y1 += self.objects[tag][2]
        y2 += self.objects[tag][2]
        self.rect_mouse_bind(1, x1, y1, x2, y2, print, ())
        self.master.mouse_press_events.pop((x1, y1, x2, y2, 1))

    def create_button(self, event_button, button_tag, function, arg=()):
        button_obj = self.objects[button_tag]
        self.rect_mouse_bind(event_button, button_obj[1], button_obj[2],
                             button_obj[1] + button_obj[0].size().width(),
                             button_obj[2] + button_obj[0].size().height(),
                             function, arg)

    def delete_button(self, event_button, button_tag):
        button_obj = self.objects[button_tag]
        self.master.mouse_press_events.pop((button_obj[1], button_obj[2],
                                            button_obj[1] + button_obj[0].size().width(),
                                            button_obj[2] + button_obj[0].size().height(),
                                            event_button))


class Data:
    draw_functions = {QPixmap: QPainter.drawPixmap, Canvas: QPainter.drawPixmap,
                      QLine: QPainter.drawLine, Line: Line.draw,
                      QImage: QPainter.drawImage, Circle: Circle.draw}
    events_strings = {'Esc': 16777216, 'Alt': 16777251, 'Ctrl': 16777249, 'Shift': 16777248, 'Space': 32}

    @staticmethod
    def to_keyboard_event_key(event_name):
        if len(event_name) == 1:
            return ord(event_name)
        else:
            return Data.events_strings[event_name]

    @staticmethod
    def is_intersection(rect1: tuple, rect2: tuple):
        # if distance between centers of rects less then width1/2 + width2/2
        if abs((rect1[0] + rect1[2]) - (rect2[0] + rect2[2])) < \
           rect2[2] - rect2[0] + rect1[2] - rect1[0] and \
           abs((rect1[0] + rect1[2]) - (rect2[0] + rect2[2])) < \
           rect2[2] - rect2[0] + rect1[2] - rect1[0]:
            return True
        return False

