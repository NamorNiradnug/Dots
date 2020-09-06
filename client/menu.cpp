#include "menu.h"
#include "frame.h"

Menu::Menu(Frame *parent) : QFrame(parent)
{
    setupUi(this);
    connect(quit_btn, SIGNAL(released()), parent, SLOT(close()));
    connect(continue_btn, SIGNAL(released()), parent, SLOT(continueGame()));
    connect(new_game_btn, SIGNAL(released()), parent, SLOT(startNewGame()));
    connect(settings_btn, SIGNAL(released()), parent, SLOT(openSettings()));
}
