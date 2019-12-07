from graphics import *
from PyQt5.QtWidgets import QApplication
from PyQt5.QtGui import QImage


def foo(arg, arg2):
    print(arg + 2 * arg2)


app = QApplication([])
screen_info = app.desktop().screenGeometry()
window = DrawWindow(900, 900)
window.canvas.create_object(obj=QImage(Data.image), relx=.5, rely=.5, tag='img')
window.canvas.rect_mouse_bind(1, 0, 0, 30, 30, foo, ('__x__', '__y__'), 'img')
window.graphics_update()
print(window.canvas.objects['img'][0].size().width())
window.show()
app.exec_()
