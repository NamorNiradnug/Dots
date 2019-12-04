import sys
from PyQt5.QtWidgets import QLabel, QMainWindow, QApplication
from PyQt5.QtGui import QPixmap, QPainter, QPen, QColor, QImage
from PyQt5.QtCore import Qt, QLine


class Line(QLine):
    def __init__(self, x1, y1, x2, y2, **kwargs):
        super().__init__(x1, y1, x2, y2)
        self.fill = kwargs.get('fill', 'black')
        self.width = kwargs.get('width', 1)

    def draw(self, master):
        painter = QPainter(master)
        pen = QPen()
        pen.setColor(QColor(self.fill))
        pen.setWidth(self.width)
        painter.setPen(pen)
        painter.drawLine(self)
        painter.end()


class DrawWindow(QMainWindow):
    def __init__(self, width=1980, height=1280):
        super().__init__()
        self.setWindowTitle('Dots')
        self.graphics_container = QLabel()
        canvas = Canvas(width=width, height=height)
        canvas.draw_obj(obj=Line(0, 0, 200, 200, fill='red', width=6), tag='line1')
        canvas.draw_obj(x=200, y=200, obj=Canvas(width=200, height=300, color='black'), tag='thing')
        canvas.draw_obj(obj=Line(0, 0, 20, 20, fill='white'), master_tag='thing')
        self.mouse_press_events = {}
        self.key_press_events = {}
        self.graphics_container.setPixmap(canvas)
        self.setCentralWidget(self.graphics_container)

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


class Canvas(QPixmap):
    def __init__(self, **kwargs):
        if 'width' not in kwargs.keys() or 'height' not in kwargs.keys():
            raise AttributeError

        super().__init__(kwargs['width'], kwargs['height'])

        self.fill(QColor(kwargs.get('color', 'white')))
        self.objects_tags = []
        self.objects = {'self': self}

    def create_image(self, x, y, image, tag):
        painter = QPainter()
        self.setPainter(painter)
        painter.drawImage(x, y, image)
        self.new_object(tag, image)
        painter.end()

    def create_canvas(self, x, y, canvas, tag):
        painter = QPainter(self)
        painter.drawPixmap(canvas)
        self.new_object(tag, canvas)
        painter.end()

    def draw_line(self, line, tag, master_tag=None):
        if master_tag == None:
            master_tag = 'self'
        painter = QPainter(self.objects_tags[master_tag])
        pen = QPen()
        pen.setColor(QColor(line.fill))
        pen.setWidth(line.width)
        painter.setPen(pen)
        painter.drawLine(line)
        self.new_object(tag, line, )
        painter.end()

    def new_object(self, tag, obj):
        self.objects_tags.append(tag)
        self.objects[tag] = obj

    def draw_obj(self, **kwargs):
        if 'obj' not in kwargs.keys():
            raise AttributeError

        x, y, obj, master, tag = kwargs.get('x', 0), kwargs.get('y', 0), kwargs['obj'], \
            self.objects[kwargs.get('master_tag', 'self')], kwargs.get('tag', None)

        if not tag is None:
            self.new_object(tag, obj)

        if type(master) not in {QPixmap, Canvas}:
           raise TypeError(tag)

        if type(obj) == Line:
            obj.draw(self)
        else:
            painter = QPainter(master)
            func = Data.draw_functions[type(obj)]
            func(painter, x, y, obj)
            painter.end()

    def update(self, )


class Data:
    draw_functions = {QPixmap: QPainter.drawPixmap, Canvas: QPainter.drawPixmap,
                      QLine: QPainter.drawLine, Line: Line.draw,
                      QImage: QPainter.drawImage}


app = QApplication(sys.argv)
window = DrawWindow(900, 900)
for i in range(800):
    for j in range(800):
        window.mouse_bind(1, i, j, print, (i, j))
window.key_bind(65, print, ('Hello!', "You pressed 'A'."))

window.show()
app.exec_()
