#pragma once

#include <QMainWindow> // for QMainWindow
#include <QFont> // for QFont
#include <QTimer> // for QTimer
#include <string> // for std::string
#include "dots.h" // for Dots


class Button;


class Frame : public QMainWindow
{
public:
    Frame();
    ~Frame();
    enum Modes
    {
        NewGame = -3,
        GameMenu = -2,
        Game = -1,
        QuitMode = 0
    };
    void paintEvent(QPaintEvent *_);
    void keyReleaseEvent(QKeyEvent *event);
    void wheelEvent(QWheelEvent *event);
    void mousePressEvent(QMouseEvent *event);
    void mouseMoveEvent(QMouseEvent *event);
    void mouseReleaseEvent(QMouseEvent *event);
    void resizeEvent(QResizeEvent *event);
    void setMode(Modes mode);
    void updateButtons();
    QPoint dotCoordinatesOnMap(QPoint dot);
    QPoint cursorPos();
    QPoint coordsOnMap(QPoint point);
private:
    Dots dots;
    Modes mode;
    QTimer *draw_timer;
    QPoint last_pos = QPoint();
    std::vector<Button> buttons = {};
};


class Button
{
public:
    Button(QRect rect, QString text, Frame *frame, Frame::Modes mode);
    Button(QRect rect, QImage image, Frame *frame, Frame::Modes mode);
    bool event(QMouseEvent *event);
    void draw(QPainter *painter, QPoint cursor_pos);
private:
    QRect rect;
    QString lines = "";
    QImage image = QImage();
    QFont font = QFont("ubuntu", 20);
    Frame *frame;
    Frame::Modes mode;
};
