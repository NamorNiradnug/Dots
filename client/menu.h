#pragma once

#include "ui_menu.h"

class Frame;

class Menu : public QFrame, private Ui::Menu
{
    Q_OBJECT

public:
    explicit Menu(Frame *parent = nullptr);
private:
    friend class Frame;
};

