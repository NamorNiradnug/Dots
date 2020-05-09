#include "frame.h"
#include <iostream>


//###################################
Button::Button(QRect rect, QString text, Frame *frame, Frame::Modes mode)
{
    this->rect = rect;
    this->frame = frame;
    this->mode = mode;
    QStringList stext = text.split(" ");
    QFontMetrics metrics = QFontMetrics(font);
    QVector<QString> vlines = {};
    if (stext.size() >= 1)
    {
        vlines.push_back(stext[0]);
        stext.erase(stext.begin());
        for (QString word: stext)
        {
            if (metrics.horizontalAdvance(vlines.back() + word) < rect.width() - 4)
            {
                vlines.back() += " " + word;
            }
            else
            {
                vlines.push_back(word);
            }
        }
    }
    for (QString line: vlines)
    {
        lines += line + "\n";
    }
    lines.remove(lines.size() - 1, 1);
}

Button::Button(QRect rect, QImage image, Frame *frame, Frame::Modes mode)
{
    this->rect = rect;
    this->image = image;
    this->frame = frame;
    this->mode = mode;
}

bool Button::event(QMouseEvent *event)
{
    if (rect.contains(event->pos()) && event->button() == Qt::LeftButton)
    {
        frame->setMode(mode);
        return true;
    }
    return false;
}

void Button::draw(QPainter *painter, QPoint cursor_pos)
{
    if (image.isNull())
    {
        QPen pen(Qt::black);
        if (rect.contains(cursor_pos))
        {
            pen.setColor(Qt::white);
        }
        pen.setWidth(2);
        painter->setPen(pen);
        painter->setBrush(QColor(255, 217, 168));
        painter->drawRoundedRect(rect, 15, 15);
    }
    else
    {
        if (rect.contains(cursor_pos))
        {
            painter->setOpacity(.6);
        }
        painter->drawImage(rect, image);
    }
    painter->setOpacity(1);
    painter->setFont(font);
    painter->setPen(QColor(10, 10, 20));
    painter->drawText(rect, Qt::AlignCenter, lines);
}

//###################################
Frame::Frame()
{
    this->setMinimumSize(QSize(640, 480));
    dots = Dots();
    mode = Modes::Game;
    draw_timer = new QTimer();
    draw_timer->setInterval(20); // 50 fps
    draw_timer->connect(draw_timer, SIGNAL(timeout()), this, SLOT(update()));
    draw_timer->start();
}

void Frame::paintEvent(QPaintEvent *_)
{
    QPainter *painter = new QPainter(this);
    if (mode == Modes::Game)
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
    else if (mode == Modes::GameMenu)
    {
        dots.draw(geometry().size(), painter, QPoint());
        painter->fillRect(rect(), QColor(0, 0, 0, 128));
        if (dots.winner() != 2)
        {
            painter->setFont(QFont("times", 40));
            painter->setPen(dsettings()->colors()[dots.winner()]);
            painter->drawText(QRect(rect().center() - QPoint(160, 70), QSize(320, 70)),
                              Qt::AlignCenter, dsettings()->name(dots.winner()) + " won!");
        }
    }
    for (Button button: buttons)
    {
        button.draw(painter, cursorPos());
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
    if (mode == Modes::Game)
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
        if (key == Qt::Key_Escape)
        {
            setMode(Modes::GameMenu);
        }
    }
    else if (mode == Modes::GameMenu)
    {
        if (key == Qt::Key_Escape and dots.winner() == 2)
        {
            setMode(Modes::Game);
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
    last_pos = event->pos();
}

void Frame::mouseMoveEvent(QMouseEvent *event)
{
    if (mode == Modes::Game)
    {
        if (event->buttons() == Qt::RightButton)
        {
            dots.translate((last_pos - event->pos()) / dots.getScale(), geometry().size());
        }
        last_pos = event->pos();
    }
}

void Frame::mouseReleaseEvent(QMouseEvent *event)
{
    for (Button button: buttons)
    {
        if (button.event(event))
        {
            return;
        }
    }
    if (mode == Modes::Game)
    {
        if (event->button() == Qt::LeftButton)
        {
            QPoint on_map = dotCoordinatesOnMap(coordsOnMap(event->pos()));
            if (QRect(QPoint(), geometry().size()).contains(on_map))
            {
                dots.turn(coordsOnMap(event->pos()));
                if (dots.winner() != 2)
                {
                    setMode(Modes::GameMenu);
                }
            }
        }
    }
}

void Frame::resizeEvent(QResizeEvent *event)
{
    QMainWindow::resizeEvent(event);
    updateButtons();
}

void Frame::setMode(Frame::Modes nmode)
{
    if (nmode == Modes::QuitMode)
    {
        close();
        return;
    }
    if (nmode == Modes::NewGame)
    {
        dots = Dots();
        nmode = Modes::Game;
    }
    mode = nmode;
    updateButtons();
}

void Frame::updateButtons()
{
    buttons.clear();
    std::vector<Button> new_buttons;
    if (mode == Modes::GameMenu)
    {
        new_buttons = {
            Button(QRect(rect().center() - QPoint(160, -40), QSize(150, 40)),
            "QUIT", this, Modes::QuitMode),
            Button(QRect(rect().center() - QPoint(-10, -40), QSize(150, 40)),
            "NEW GAME", this, Modes::NewGame)
        };
        if (dots.winner() == 2)
        {
            new_buttons.push_back(Button(QRect(rect().center() - QPoint(160, 70), QSize(320, 50)),
                                         "CONTINUE GAME", this, Modes::Game));
        }
    }
    for (Button btn: new_buttons)
    {
        buttons.push_back(btn);
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
