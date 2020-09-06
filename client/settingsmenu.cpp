#include "settingsmenu.h"
#include "frame.h"
#include "resources.h"

SettingsMenu::SettingsMenu(Frame *parent) : QFrame(parent)
{
    setupUi(this);
    connect(ok_button, SIGNAL(released()), this, SLOT(saveSettings()));
    connect(ok_button, SIGNAL(released()), parent, SLOT(openMenu()));
    connect(apply_button, SIGNAL(released()), this, SLOT(saveSettings()));
    connect(close_button, SIGNAL(released()), this, SLOT(syncWithDSettings()));
    connect(close_button, SIGNAL(released()), parent, SLOT(openMenu()));
}

void SettingsMenu::saveName(QLineEdit *name_edit, int player)
{
    QString name = name_edit->text();

    if (name.isEmpty())
    {
        name = "Player " + QString::number(player);
    }

    dsettings()->setPlayerName(player, name);
}

void SettingsMenu::saveColor(QComboBox *color_box, int player)
{
    int cur_index = color_box->currentIndex();
    QColor color = COLORS[cur_index];

    if (color == dsettings()->color((player + 1) % 2))
    {
        color = COLORS[(cur_index + 1) % 4];
        color_box->setCurrentIndex((cur_index + 1) % 4);
    }

    dsettings()->setPlayerColor(player, color);
}

void SettingsMenu::saveSettings()
{
    saveName(player_name_1, 0);
    saveName(player_name_2, 1);
    saveColor(color_1, 0);
    saveColor(color_2, 1);
}

void SettingsMenu::syncWithDSettings()
{
    player_name_1->setText(dsettings()->name(0));
    player_name_2->setText(dsettings()->name(1));
}
