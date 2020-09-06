#include "dots.h"
#include <QDebug>
#include <QPainter>
#include <QSize>


Chunk::Chunk(int x, int y)
{
    map = std::vector<std::vector<int>>(16, std::vector<int>(16));

    for (int i = 0; i < 16; i++)
    {
        for (int j = 0; j < 16; j++)
        {
            map[i][j] = 8;
        }
    }

    this->x = x;
    this->y = y;
}

void Chunk::addTrack(QLine track)
{
    if (!tracks.count(QLine(track.p2(), track.p1())))
    {
        tracks.insert(track);
    }
}

std::set<QLine> Chunk::getTracks()
{
    return tracks;
}

int Chunk::dot(int x, int y)
{
    return map[x][y];
}

int Chunk::dot(QPoint pos)
{
    return map[pos.x()][pos.y()];
}

void Chunk::setDot(int x, int y, int dot)
{
    map[x][y] = dot;
}

void Chunk::drawLines(QPainter *painter)
{
    QPen black_pen(Qt::black);
    QPen red_pen(Qt::red);
    black_pen.setWidth(1);
    red_pen.setWidth(1);
    painter->setPen(black_pen);

    for (int i = 0; i < 16; i++)
    {
        painter->drawLine(x * 16, (y + i) * 16 + 8,  // horizontal line
                          x * 16 + 256, (y + i) * 16 + 8);
        painter->drawLine((x + i) * 16 + 8, y * 16,  // vertical line
                          (x + i) * 16 + 8, y * 16 + 256);
    }

    painter->setPen(red_pen);

    if (y == 0)
    {
        painter->drawLine(x * 16, 8, x * 16 + 256, 8);
    }

    if (x == 0)
    {
        painter->drawLine(8, y * 16, 8, y * 16 + 256);
    }

    if (y == 16 * 15)
    {
        painter->drawLine(x * 16, 8 + (y + 15) * 16, x * 16 + 256, 8 + (y + 15) * 16);
    }

    if (x == 16 * 15)
    {
        painter->drawLine(8 + (x + 15) * 16, y * 16, 8 + (x + 15) * 16, y * 16 + 256);
    }
}

void Chunk::drawDots(QPainter *painter, Dots *dots)
{
    for (QLine track : tracks)
    {
        painter->setPen(dsettings()->color(player(dot(track.p1().x() % 16,
                                           track.p1().y() % 16))));
        painter->drawLine(track.p1() * 16 + QPoint(8, 8), track.p2() * 16 + QPoint(8, 8));
    }

    QBrush fill_brush = QBrush(Qt::transparent);
    fill_brush.setStyle(Qt::Dense6Pattern);
    painter->setPen(Qt::transparent);

    for (int x = 0; x < 16; x++)
    {
        for (int y = 0; y < 16; y++)
        {
            painter->setBrush(dsettings()->color(player(dot(x, y))));
            painter->drawEllipse(dotCoord(x, y), 3, 3);

            if (dot(x, y) == 8)
            {
                continue;
            }

            if (dots->isFirst(QPoint(x + this->x, y + this->y)))
            {
                painter->setBrush(Qt::transparent);
                painter->setPen(dsettings()->color(player(dot(x, y))));
                painter->drawEllipse(dotCoord(x, y), 6, 6);
                painter->setPen(Qt::transparent);
            }

            fill_brush.setColor(dsettings()->color(player(dot(x, y))));
            painter->setBrush(fill_brush);
            std::vector<QPoint> circle_ =
            {
                QPoint(x, y - 1),
                QPoint(x + 1, y),
                QPoint(x, y + 1),
                QPoint(x - 1, y)
            };

            for (int i = 0; i < 4; i++)
            {
                if (dots->dot(circle_[i] + QPoint(this->x, this->y)) == dot(x, y) &&
                        dot(x, y) == dots->dot(circle_[(i + 1) % 4] + QPoint(this->x, this->y)))
                {
                    QPoint mono_triang[3] =
                    {
                        dotCoord(x, y),
                        dotCoord(circle_[i]),
                        dotCoord(circle_[(i + 1) % 4])
                    };
                    painter->drawPolygon(mono_triang, 3);
                }
            }

            fill_brush.setColor(dsettings()->color(eater(dot(x, y))));
            painter->setBrush(fill_brush);
            QPoint poly[4] =
            {
                dotCoord(x, y - 1),
                dotCoord(x + 1, y),
                dotCoord(x, y + 1),
                dotCoord(x - 1, y)
            };
            painter->drawPolygon(poly, 4);
            QPoint some_points[4] =
            {
                QPoint(x - 1, y - 1),
                QPoint(x - 1, y + 1),
                QPoint(x + 1, y - 1),
                QPoint(x + 1, y + 1)
            };

            for (QPoint pos : some_points)
            {
                if (player(dots->dot(pos.x() + this->x, pos.y() + this->y)) == eater(dot(x, y)))
                {
                    QPoint triang[3] =
                    {
                        dotCoord(pos),
                        dotCoord(pos.x(), y),
                        dotCoord(x, pos.y())
                    };
                    painter->drawPolygon(triang, 3);
                }
            }
        }
    }
}

QPoint Chunk::dotCoord(int x, int y)
{
    return QPoint((this->x + x) * 16 + 8, (this->y + y) * 16 + 8);
}

QPoint Chunk::dotCoord(QPoint pos)
{
    return dotCoord(pos.x(), pos.y());
}

//#######################################
Dots::Dots()
{
    chunks = {};

    for (int i = 0; i < 16; i++)
    {
        chunks.push_back({});

        for (int j = 0; j < 16; j++)
        {
            chunks[i].push_back(Chunk(i * 16, j * 16));
        }
    }
}

void Dots::addTrack(std::vector<QPoint> track)
{
    QPoint max_dot, min_dot;

    for (unsigned i = 0; i < track.size() - 1; i++)
    {
        max_dot = track[i];
        min_dot = track[i + 1];

        if (max_dot < min_dot)
        {
            std::swap(min_dot, max_dot);
        }

        if (max_dot.x() != min_dot.x() and max_dot.y() != min_dot.y())
        {
            QLine intersec = QLine(max_dot.x(), min_dot.y(), min_dot.x(), max_dot.y());

            if (chunk(intersec.x1(), intersec.y1())->getTracks().count(intersec))
            {
                continue;
            }
        }

        chunk(max_dot.x(), max_dot.y())->addTrack(QLine(min_dot, max_dot));
        chunk(min_dot.x(), min_dot.y())->addTrack(QLine(min_dot, max_dot));
    }
}

std::set<QPoint> Dots::surrounding(int x, int y)
{
    std::set<QPoint> answer;

    for (int dx = -1; dx <= 1; dx++)
    {
        for (int dy = -1; dy <= 1; dy++)
        {
            if (!(dx == 0 and dy == 0) and dot(x + dx, y + dy) == dot(x, y))
            {
                answer.insert(QPoint(x + dx, y + dy));
            }
        }
    }

    return answer;
}

double Dots::getScale()
{
    return scale;
}

QPoint Dots::camPos()
{
    return QPoint(cam_x, cam_y);
}

bool Dots::isFirst(QPoint pos)
{
    return pos == first1 or pos == second1;
}

void Dots::changeScale(double delta, QSize size)
{
    scale += delta;
    scale = std::min(scale, 6.0);
    scale = std::max(scale, 1.5);
    size /= scale;
    normalize(size);
}

Chunk *Dots::chunk(int x, int y)
{
    int cx = x / 16, cy = y / 16;
    return &chunks[cx][cy];
}

int Dots::dot(int x, int y)
{
    return chunk(x, y)->dot(x % 16, y % 16);
}

int Dots::dot(QPoint pos)
{
    return dot(pos.x(), pos.y());
}

void Dots::translate(QPoint delta, QSize size)
{
    size /= scale;
    cam_x += delta.x();
    cam_y += delta.y();
    normalize(size);
}

void Dots::normalize(QSize size)
{
    cam_x = std::max(cam_x, size.width() / 2);
    cam_x = std::min(cam_x, 4096 - size.width() / 2);
    cam_y = std::max(cam_y, size.height() / 2);
    cam_y = std::min(cam_y, 4096 - size.height() / 2);
}

void Dots::findNewTracks(int x, int y)
{
    std::set<std::vector<QPoint>> open_tracks = {{QPoint(x, y)}}, open_tracks_copy;
    std::set<QPoint> used = {QPoint(x, y)};
    std::vector<QPoint> new_track;

    while (!open_tracks.empty())
    {
        open_tracks_copy = open_tracks;
        open_tracks = {};

        for (std::vector<QPoint> track : open_tracks_copy)
        {
            for (QPoint pos : surrounding(track.back().x(), track.back().y()))
            {
                if (!used.count(pos))
                {
                    new_track = track;
                    new_track.push_back(pos);
                    open_tracks.insert(new_track);
                    used.insert(pos);
                }
                else if (track.size() >= 3 and pos == QPoint(x, y))
                {
                    addTrack(track + std::vector<QPoint>(1, pos));
                }
                else if (pos != QPoint(x, y))
                {
                    for (std::vector<QPoint> other : open_tracks_copy)
                    {
                        if (other[1] != track[1] and pos == other.back())
                        {
                            addTrack(track + reversed(other));
                        }
                    }

                    for (std::vector<QPoint> other : open_tracks)
                    {
                        if (other[1] != track[1] and pos == other.back())
                        {
                            addTrack(track + reversed(other));
                        }
                    }
                }
            }
        }
    }
}

void Dots::findNewEaten(int x, int y)
{
    std::set<QPoint> open, open_copy, used;
    bool not_eaten;

    for (QPoint start : circle(x, y))
    {
        used = {};
        open = {start};
        not_eaten = false;

        while (!open.empty() and !not_eaten)
        {
            open_copy = open;
            open = {};

            for (QPoint pos : open_copy)
            {
                if (!QRect(min_x, min_y, max_x - min_x, max_y - min_y).contains(pos))
                {
                    not_eaten = true;
                    break;
                }

                for (QPoint p : circle(pos.x(), pos.y()))
                {
                    if (!used.count(p) and !open.count(p) and dot(p.x(), p.y()) != dot(x, y))
                    {
                        open.insert(p);
                    }
                }

                used.insert(pos);
            }
        }

        if (!not_eaten)
        {
            for (QPoint pos : used)
            {
                chunk(pos.x(), pos.y())->setDot(pos.x() % 16, pos.y() % 16,
                                                player(dot(pos)) + 3 * player(dot(x, y)));
            }
        }
    }
}

void Dots::turn(QPoint pos)
{
    if (winner() != 2)
    {
        return;
    }

    if (QRect(1, 1, 255, 255).contains(pos.x(), pos.y()) and dot(pos.x(), pos.y()) == 8)
    {
        chunk(pos.x(), pos.y())->setDot(pos.x() % 16, pos.y() % 16, turning_player + 6);
        max_x = std::max(max_x, pos.x());
        max_y = std::max(max_y, pos.y());
        min_x = std::min(min_x, pos.x());
        min_y = std::min(min_y, pos.y());
        findNewTracks(pos.x(), pos.y());
        findNewEaten(pos.x(), pos.y());

        if (first1 == QPoint(-1, -1) and turning_player == 0)
        {
            first1 = pos;
        }

        if (second1 == QPoint(-1, -1) and turning_player == 1)
        {
            second1 = pos;
        }

        turning_player = (turning_player + 1) % 2;
    }
}

int Dots::winner()
{
    if (first1 != QPoint(-1, -1) and eater(dot(first1)) == 1)
    {
        return 1;
    }

    if (second1 != QPoint(-1, -1) and eater(dot(second1)) == 0)
    {
        return 0;
    }

    return 2;
}

void Dots::draw(QSize size, QPainter *painter, QPoint cursor)
{
    painter->save();
    painter->scale(scale, scale);
    size /= scale;
    normalize(size);
    int tx = size.width() / 2 - cam_x, ty = size.height() / 2 - cam_y;
    painter->translate(tx, ty);
    std::set<Chunk *> visible = {};

    for (int x = 0; x < 256; x += 16)
    {
        for (int y = 0; y < 256; y += 16)
        {
            if (-256 < x * 16 + tx and x * 16 + tx <= size.width() and
                    - 256 < y * 16 + ty and y * 16 + ty <= size.height())
            {
                visible.insert(chunk(x, y));
                chunk(x, y)->drawLines(painter);
            }
        }
    }

    for (Chunk *chunk : visible)
    {
        chunk->drawDots(painter, this);
    }

    painter->setPen(Qt::transparent);

    if (QRect(1, 1, 255, 255).contains(cursor) and
            dot(cursor.x(), cursor.y()) == 8)
    {
        painter->setBrush(dsettings()->color(turning_player));
        painter->setOpacity(0.5);
        painter->drawEllipse(cursor * 16 + QPoint(8, 8), 3, 3);

        if (first1 == QPoint(-1, -1) or second1 == QPoint(-1, -1))
        {
            painter->setBrush(Qt::transparent);
            painter->setPen(dsettings()->color(turning_player));
            painter->drawEllipse(cursor * 16 + QPoint(8, 8), 6, 6);
        }
    }

    painter->restore();
}
