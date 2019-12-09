from graphics import *
from resources import Resources
from PyQt5.QtWidgets import QApplication
from PyQt5.QtGui import QImage


app = QApplication([])
screen_info = app.desktop().screenGeometry()
window = DrawWindow(900, 900)


class Canvases:
    @staticmethod
    def main_menu_canvas():
        start_canvas = Canvas(width=640, height=640, color='grey')
        start_canvas.create_object(x=.5, y=10, obj=QImage(Resources.logo_texture),
                                   tag='logo')
        start_canvas.create_object(x=560, y=560, obj=QImage(Resources.settings_button),
                                   tag='settings_button')
        start_canvas.create_object(relx=.5, y=200, obj=QImage(Resources.singleplayer_button),
                                   tag='singleplayer_button')
        start_canvas.create_object(relx=.5, y=300, obj=QImage(Resources.local_multiplayer_button),
                                   tag='local_multiplayer_button')
        start_canvas.create_object(relx=.5, y=400, obj=QImage(Resources.multiplayer_button),
                                   tag='multiplayer_button')
        start_canvas.create_object(relx=.5, y=500, obj=QImage(Resources.quit_button),
                                   tag='quit_button')
        return start_canvas

    @staticmethod
    def game_menu_canvas():
        game_menu_canvas = Canvas(width=320, height=540, color='grey')
        game_menu_canvas.create_object(x=160, y=500, image=QImage(Resources.quit_button),
                                       tag='game_quit')
        return game_menu_canvas

    @staticmethod
    def settings_canvas():
        settings_canvas = Canvas(width=320, height=540, color='red')
        # TODO draw on settings canvas
        return settings_canvas


class Canvases:
    @staticmethod
    def main_menu_canvas():
        start_canvas = Canvas(width=640, height=640, color='grey')
        start_canvas.create_object(x=.5, y=10, obj=QImage(Resources.logo_texture),
                                   tag='logo')
        start_canvas.create_object(x=560, y=560, obj=QImage(Resources.settings_button),
                                   tag='settings_button')
        start_canvas.create_object(relx=.5, y=200, obj=QImage(Resources.singleplayer_button),
                                   tag='singleplayer_button')
        start_canvas.create_object(relx=.5, y=300, obj=QImage(Resources.local_multiplayer_button),
                                   tag='local_multiplayer_button')
        start_canvas.create_object(relx=.5, y=400, obj=QImage(Resources.multiplayer_button),
                                   tag='multiplayer_button')
        start_canvas.create_object(relx=.5, y=500, obj=QImage(Resources.quit_button),
                                   tag='quit_button')
        return start_canvas

    @staticmethod
    def game_menu_canvas():
        game_menu_canvas = Canvas(width=320, height=540, color='grey')
        game_menu_canvas.create_object(x=160, y=500, image=QImage(Resources.quit_button),
                                       tag='game_quit')
        return game_menu_canvas

    @staticmethod
    def settings_canvas():
        settings_canvas = Canvas(width=320, height=540, color='red')
        # TODO draw on settings canvas
        return settings_canvas


def toggle_settings(x=0, y=0):
    print('You toggle settings')
    if 'settings' not in window.canvas.objects_tags:
        open_settings(40, 40)
    else:
        close_settings()
    window.graphics_update()


def open_settings(x, y):
    window.canvas.create_object(obj=Canvases.settings_canvas(), x=x, y=y, tag='settings')
    window.canvas.rect_mouse_unbind(x, y, x + 320, y + 540)
    #window.rect_mouse_bind(1, x, y, x+320, y+540)


def close_settings():
    window.canvas.delete_object('settings')


window.canvas.create_object(obj=QImage(Resources.quit_button), relx=.5, rely=.5, tag='img')
window.canvas.create_button(1, 'img', print, ('Hello, World!'))
window.graphics_update()
window.key_bind('Esc', toggle_settings)
window.show()
app.exec_()


#window.canvas.create_object(obj=QImage(Data.image), relx=.5, rely=.5, tag='img')
#window.canvas.rect_mouse_bind(1, 0, 0, 30, 30, foo, ('__x__', '__y__'), 'img')
# window.graphics_update()
# print(window.canvas.objects['img'][0].size().width())
window.key_bind('Esc', toggle_settings)
window.show()
app.exec_()
