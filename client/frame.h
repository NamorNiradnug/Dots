#pragma once

#include <QMainWindow> // for QMainWindow
#include <QFont> // for QFont
#include <QTimer> // for QTimer
#include <string> // for std::string
#include "dots.h" // for Dots
#include "menu.h"
#include "settingsmenu.h"

class Frame : public QMainWindow
{
    Q_OBJECT

public:
    Frame();
    ~Frame();
    enum Mode
    {
        NewGame = -3,
        GameMenu = -2,
        Game = -1,
        Setting = 1
    };
    void paintEvent(QPaintEvent *_);
    void keyReleaseEvent(QKeyEvent *event);
    void wheelEvent(QWheelEvent *event);
    void mousePressEvent(QMouseEvent *event);
    void mouseMoveEvent(QMouseEvent *event);
    void mouseReleaseEvent(QMouseEvent *event);
    void resizeEvent(QResizeEvent *event);
    void updateMenuPos();
    QPoint dotCoordinatesOnMap(QPoint dot);
    QPoint cursorPos();
    QPoint coordsOnMap(QPoint point);
public slots:
    void startNewGame();
    void continueGame();
    void openSettings();
    void openMenu();
private:
    void setMode(Mode mode);
    void setWidget(QWidget *widget);
    void centredWidget(QWidget *widget);
    Dots dots;
    Mode mode;
    QTimer *draw_timer;
    QPoint last_pos = QPoint();
    Menu *menu = new Menu(this);
    SettingsMenu *settings_menu = new SettingsMenu(this);
    QWidget *current_widget = 0;
};
