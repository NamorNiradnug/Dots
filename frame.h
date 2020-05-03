#pragma once

#include <QMainWindow>
#include <QFont>
#include <QTimer>
#include <string>
#include "dots.h"


class Frame;


class Button
{
public:
    Button(QRect rect, std::string text, void (*func)());
    Button(QRect rect, QImage image, void (*func)());
    bool event(QMouseEvent);
    void draw(QPainter painter, QPoint cursor_pos);
private:
    QRect rect;
    std::vector<std::string> lines;
    QImage image;
    QFont font = QFont("ubuntu", 20);
    void *func();
};


class Frame : public QMainWindow
{
public:
    Frame();
    ~Frame();
    void paintEvent(QPaintEvent *_);
    void keyReleaseEvent(QKeyEvent *event);
    void wheelEvent(QWheelEvent *event);
    void mousePressEvent(QMouseEvent *event);
    QPoint dotCoordinatesOnMap(QPoint dot);
    QPoint cursorPos();
    QPoint coordsOnMap(QPoint point);
private:
    enum Modes
    {
        SinglePlayer = -1
    };
    Dots dots;
    Modes mode;
    std::set<Button> buttons;
    QTimer *draw_timer;
};
