from PyQt5.QtWidgets import QLabel, QMainWindow, QApplication
from PyQt5.QtGui import QPixmap, QPainter, QPen, QColor, QImage
from PyQt5.QtCore import Qt, QLine, QPoint


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
        if (event.x(), event.y()) in self.mouse_press_events.keys():
            data = self.mouse_press_events[event.x(), event.y()][event.button()]
            data[0](*data[1])

    def key_bind(self, event_name, function, arg=()):
        self.key_press_events[Data.events_strings[event_name]] = (function, arg)

    def mouse_bind(self, event_button, x, y, function, arg=()):
        self.mouse_press_events[(x, y)] = {event_button: (function, arg)}

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

    def key_unbind(self, event_name):
        if event_name == 'all':
            self.key_press_events = {}
        else:
            self.key_press_events.pop(Data.events_strings[event_name])

    def mouse_unbind(self, button, x=None, y=None):
        if button == 'all':
            if x is None and y is None:
                self.mouse_press_events = {}
            else:
                if (x, y) in self.mouse_press_events.keys():
                    self.mouse_press_events.pop((x, y))                        
        else:
            if (x, y) in self.mouse_press_events.keys():
                if button in self.mouse_press_events[(x, y)]:
                    self.key_press_events[(x, y)].pop(button)

    def rect_mouse_unbind(self, button, x1, y1, x2, y2):
        for i in range(int(x1), int(x2) + 1):
            for j in range(int(y1), int(y2) + 1):
                self.mouse_unbind(button, i, j)
    #TODO save data about events in rect else rect_mouse_event work very slow.
 

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
        self.objects = {'self': (self, 0, 0), \
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

    def mouse_bind(self, event_button, x, y, function, arg=(), tag='self'):        
        self.master_window.mouse_bind(event_button, x + self.objects[tag][1], \
                                      y + self.objects[tag][2], function, arg)

    def rect_mouse_bind(self, event_button, x1, y1, x2, y2, function, arg=(), tag='self'):
        x1 += self.objects[tag][1]
        x2 += self.objects[tag][1]
        y1 += self.objects[tag][2]
        y2 += self.objects[tag][2]
        self.master_window.rect_mouse_bind(event_button, x1, y1, x2, y2, function, arg)

    def mouse_unbind(self, event_button, x, y, tag='self'):
        self.master_window.mouse_unbind(event_button, x + self.objects[tag][1], \
                                      y + self.objects[tag][2])
        
    def rect_mouse_unbind(self, event_button, x1, y1, x2, y2, tag='self'):
        x1 += self.objects[tag][1]
        x2 += self.objects[tag][1]
        y1 += self.objects[tag][2]
        y2 += self.objects[tag][2]
        self.master_window.rect_mouse_unbind(event_button, x1, y1, x2, y2)        


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
        