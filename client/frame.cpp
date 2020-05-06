#include "frame.h"
#include <iostream>


Frame::Frame()
{
    this->setMinimumSize(QSize(640, 480));
    dots = Dots();
    mode = Modes::SinglePlayer;
    draw_timer = new QTimer();
    draw_timer->setInterval(20); // 50 fps
    draw_timer->connect(draw_timer, SIGNAL(timeout()), this, SLOT(update()));
    draw_timer->start();
}

void Frame::paintEvent(QPaintEvent *_)
{
    QPainter *painter = new QPainter(this);
    if (mode == -1)
    {
        QPoint project_dot = coordsOnMap(cursorPos());
        QPoint on_map = dotCoordinatesOnMap(project_dot);
        if (not QRect(QPoint(), geometry().size()).contains(cursorPos()) or
            not QRect(QPoint(), geometry().size()).contains(on_map))
        {
            project_dot = QPoint();
        }
        dots.draw(geometry().size(), painter, project_dot);
    }
    painter->end();
}

QPoint Frame::dotCoordinatesOnMap(QPoint dot)
{
    return (dot * 16 + QPoint(8, 8) - dots.camPos() +
            QPoint(width(), height()) / (dots.getScale() * 2)) * dots.getScale();
}

void Frame::keyReleaseEvent(QKeyEvent *event)
{
    int key = event->key();
    QSize gsize =  geometry().size();
    if (mode < 0)
    {
        if (key == Qt::Key_Up)
        {
            dots.translate(QPoint(0, -10), gsize);
        }
        if (key == Qt::Key_Down)
        {
            dots.translate(QPoint(0, 10), gsize);
        }
        if (key == Qt::Key_Left)
        {
            dots.translate(QPoint(-10, 0), gsize);
        }
        if (key == Qt::Key_Right)
        {
            dots.translate(QPoint(10, 0), gsize);
        }
    }
}

void Frame::wheelEvent(QWheelEvent *event)
{
    if (mode < 0)
    {
        dots.changeScale(1.0 * event->angleDelta().y() / 240.0, geometry().size());
    }
}

void Frame::mousePressEvent(QMouseEvent *event)
{
    if (mode == -1)
    {
        if (event->button() == Qt::LeftButton)
        {
            QPoint on_map = dotCoordinatesOnMap(coordsOnMap(event->pos()));
            if (QRect(QPoint(), geometry().size()).contains(on_map))
            {
                dots.turn(coordsOnMap(event->pos()));
            }

        }
    }
}

QPoint Frame::coordsOnMap(QPoint point)
{
    QPoint real_point = point / dots.getScale() + dots.camPos() - \
            QPoint(width() / 2, height() / 2) / dots.getScale();
    return QPoint(round(real_point.x() / 16 - 0.5),
                  round(real_point.y() / 16 - 0.5));
}

QPoint Frame::cursorPos()
{
    return cursor().pos() - geometry().topLeft();
}

Frame::~Frame()
{
    draw_timer->stop();
    delete draw_timer;
}
