from PIL import Image, ImageQt


class Resources:
    # This is the structure for storing images.
    resources = Path('resources')
    settings_button = ImageQt.ImageQt(Image.open(resources / 'settings.png'))
    singleplayer_button = ImageQt.ImageQt(Image.open(resources / 'singleplayer.png'))
    multiplayer_button = ImageQt.ImageQt(Image.open(resources / 'multiplayer.png'))
    home_button = ImageQt.ImageQt(Image.open(resources / 'home.png'))
    local_multiplayer_button = ImageQt.ImageQt(Image.open(resources / 'local_multiplayer.png'))
    quit_button = ImageQt.ImageQt(Image.open(resources / 'quit.png'))
    logo_texture = ImageQt.ImageQt(Image.open(resources / 'menu_logo.png'))
