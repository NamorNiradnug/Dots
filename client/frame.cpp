#include "frame.h"
#include "QPainter"
#include "QtEvents"
#include "QDebug"
#include "cmath"

Frame::Frame()
{
    menu->hide();
    settings_menu->hide();
    settings_menu->syncWithDSettings();
    this->setMinimumSize(QSize(640, 480));
    dots = Dots();
    mode = Mode::Game;
    draw_timer = new QTimer();
    draw_timer->setInterval(20); // 50 fps
    draw_timer->connect(draw_timer, SIGNAL(timeout()), this, SLOT(update()));
    draw_timer->start();
}

void Frame::paintEvent(QPaintEvent *_)
{
    QPainter *painter = new QPainter(this);

    if (mode == Mode::Game)
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
    else
    {
        dots.draw(geometry().size(), painter, QPoint());
        painter->fillRect(rect(), QColor(0, 0, 0, 128));
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
    QSize gsize = geometry().size();

    if (mode == Mode::Game)
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
            setMode(Mode::GameMenu);
        }
    }
    else if (mode == Mode::GameMenu)
    {
        if (key == Qt::Key_Escape and dots.winner() == 2)
        {
            setMode(Mode::Game);
        }
    }
    else if (mode == Mode::Setting)
    {
        if (key == Qt::Key_Escape)
        {
            setMode(Mode::GameMenu);
        }
    }
}

void Frame::wheelEvent(QWheelEvent *event)
{
    if (mode == Mode::Game)
    {
        qDebug() << event->angleDelta().y();
        dots.changeScale(1.0 * event->angleDelta().y() / 240.0, geometry().size());
    }
}

void Frame::mousePressEvent(QMouseEvent *event)
{
    last_pos = event->pos();
}

void Frame::mouseMoveEvent(QMouseEvent *event)
{
    if (mode == Mode::Game)
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
    if (mode == Mode::Game)
    {
        if (event->button() == Qt::LeftButton)
        {
            QPoint on_map = dotCoordinatesOnMap(coordsOnMap(event->pos()));

            if (QRect(QPoint(), geometry().size()).contains(on_map))
            {
                dots.turn(coordsOnMap(event->pos()));

                if (dots.winner() != 2)
                {
                    setMode(Mode::GameMenu);
                }
            }
        }
    }
}

void Frame::resizeEvent(QResizeEvent *event)
{
    QMainWindow::resizeEvent(event);
    updateMenuPos();
}

void Frame::setMode(Frame::Mode nmode)
{
    if (nmode == Mode::NewGame)
    {
        dots = Dots();
        nmode = Mode::Game;
    }

    if (nmode == Mode::Game)
    {
        setWidget(0);
    }

    if (nmode == Mode::GameMenu)
    {
        if (dots.winner() != 2)
        {
            menu->win_label->setText(dsettings()->name(dots.winner()) + " won!");
            QPalette win_label_palette = menu->win_label->palette();
            win_label_palette.setColor(QPalette::WindowText, dsettings()->color(dots.winner()));
            menu->win_label->setPalette(win_label_palette);
            menu->continue_btn->hide();
        }
        else
        {
            menu->win_label->setText("");
            menu->continue_btn->show();
        }

        setWidget(menu);
    }

    if (nmode == Mode::Setting)
    {
        setWidget(settings_menu);
    }

    mode = nmode;
    updateMenuPos();
}

void Frame::centredWidget(QWidget *widget)
{
    widget->setGeometry((geometry().width() - widget->width()) / 2,
                        (geometry().height() - widget->height()) / 2,
                        widget->width(), widget->height());
}

void Frame::updateMenuPos()
{
    if (current_widget != 0)
    {
        centredWidget(current_widget);
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

void Frame::setWidget(QWidget *widget)
{
    if (current_widget != 0)
    {
        current_widget->hide();
    }

    current_widget = widget;

    if (current_widget != 0)
    {
        current_widget->show();
    }

    updateMenuPos();
}
/* Frame slots */

void Frame::startNewGame()
{
    setMode(Mode::NewGame);
}

void Frame::continueGame()
{
    setMode(Mode::Game);
}

void Frame::openSettings()
{
    setMode(Mode::Setting);
}

void Frame::openMenu()
{
    setMode(Mode::GameMenu);
}
