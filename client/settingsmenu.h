#pragma once

#include "ui_settingsmenu.h"

class Frame;

class SettingsMenu : public QFrame, private Ui::SettingsMenu
{
    Q_OBJECT

public:
    explicit SettingsMenu(Frame *parent = nullptr);
    void show();
public slots:
    void saveSettings();
    void syncWithDSettings();
private:
    const QColor COLORS[4] =
    {
        Qt::red,
        Qt::green,
        Qt::blue,
        Qt::yellow
    };
    void saveName(QLineEdit *name_edit, int player);
    void saveColor(QComboBox *color_box, int player);
};

