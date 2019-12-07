import sys
from PyQt5.QtWidgets import QLabel, QMainWindow, QApplication
from PyQt5.QtGui import QPixmap, QPainter, QPen, QColor, QImage
from PyQt5.QtCore import Qt, QLine, QPoint
from PIL import Image, ImageQt


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
    def __init__(self, width=1980, height=1280):
        super().__init__()
        self.setWindowTitle('Dots')
        self.graphics_container = QLabel()
        self.setCentralWidget(self.graphics_container)
        self.canvas = Canvas(width=width, height=height)
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

    def key_bind(self, event_key, function, arg):
        self.key_press_events[event_key] = (function, arg)

    def mouse_bind(self, event_button, x, y, function, arg=()):
        self.mouse_press_events[(event_button, x, y)] = (function, arg)

    def graphics_update(self):
        self.graphics_container.setPixmap(self.canvas)
        self.update()


class Canvas(QPixmap):
    def __init__(self, **kwargs):
        if 'width' not in kwargs.keys() or 'height' not in kwargs.keys():
            raise AttributeError

        super().__init__(kwargs['width'], kwargs['height'])

        self.color = kwargs.get('color', 'white')
        self.fill(QColor(self.color))
        self.objects_tags = ['self']
        self.objects = {'self': self}

    def create_object(self, **kwargs):
        obj, x, y, master_tag, tag = kwargs['obj'], kwargs.get('x', 0),\
            kwargs.get('y', 0), kwargs.get('master_tag', self.objects_tags[-1]), \
            kwargs['tag']
        self.objects_tags.insert(self.objects_tags.index(master_tag) + 1, tag)
        self.objects[tag] = obj, x, y
        print(1)
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

class Data:
    draw_functions = {QPixmap: QPainter.drawPixmap, Canvas: QPainter.drawPixmap,
                      QLine: QPainter.drawLine, Line: Line.draw,
                      QImage: QPainter.drawImage, Point: Point.draw}
    image = ImageQt.ImageQt(Image.open('resources/settings.png'))

    @staticmethod
    def something(window):
        try:
            for i in range(10):
                window.canvas.delete_object('pin_code' + str(i))            
        except:
            for i in range(10):
                window.canvas.create_object(obj=Point(10 * i, 10, radius=5), tag='pin_code' + str(i))
        window.graphics_update()
