#include "frame.h"


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
    if (mode < 0)
    {
        dots.draw(this->geometry().size(), painter);
    }
    painter->end();
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

Frame::~Frame()
{
    draw_timer->stop();
    delete draw_timer;
}
