from dots import Canvases
from graphics import *
from PyQt5.QtWidgets import QApplication
from PyQt5.QtGui import QImage


app = QApplication([])
screen_info = app.desktop().screenGeometry()
window = DrawWindow(900, 900)

def toggle_settings(x=0, y=0):
    print('You toggle settings')
    if 'settings' not in window.canvas.objects_tags:
        open_settings(x, y)
    else:
        close_settings()
    window.graphics_update()

def open_settings(x, y):
    window.canvas.create_object(obj=Canvases.settings_canvas(), x=x, y=y, tag='settings')
    window.rect_mouse_unbind('all', x, y, x+320, y+540)
    #window.rect_mouse_bind(1, x, y, x+320, y+540)

def close_settings():
    window.canvas.delete_object('settings')    

#window.canvas.create_object(obj=QImage(Data.image), relx=.5, rely=.5, tag='img')
#window.canvas.rect_mouse_bind(1, 0, 0, 30, 30, foo, ('__x__', '__y__'), 'img')
#window.graphics_update()
#print(window.canvas.objects['img'][0].size().width())
window.key_bind('Esc', toggle_settings)
window.show()
app.exec_()
