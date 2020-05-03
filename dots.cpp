#include "dots.h"
#include "math.h"
#include <QtCore>
#include <iostream>


std::set<QPoint> circle(int cx, int cy, int radius = 1)
{
    std::set<QPoint> answer;
    for (int x = -radius; x < radius + 1; x++)
    {
        for (int y = radius - std::abs(x); y < -radius + std::abs(x); y++)
        {
            answer.insert(QPoint(x + cx, y + cy));
        }
    }
    return answer;
}

bool operator <(QPoint point1, QPoint point2)
{
    if (point1.y() != point2.y())
    {
        return point1.y() < point2.y();
    }
    return point1.x() < point2.x();
}

bool operator <(QLine line1, QLine line2)
{
    if (line1.p1() != line2.p1())
    {
        return line1.p1() < line2.p1();
    }
    return line1.p2() < line2.p2();
}

//#######################################
Settings::Settings()
{
    colors_ = {
        {0, Qt::red},
        {1, Qt::blue},
        {2, Qt::transparent}
    };
}

std::map<int, QColor> Settings::colors()
{
    return colors_;
}

//#######################################
Chunk::Chunk(int x, int y, Settings *settings)
{
    map = std::vector<std::vector<int>>(16, std::vector<int>(16));
    for (int i = 0; i < 16; i++)
    {
        for (int j = 0; j < 16; j++)
        {
            map[i][j] = 8;
        }
    }
    this->settings = settings;
    this->x = x;
    this->y = y;
}

int Chunk::dot(int x, int y)
{
    return map[x][y];
}

void Chunk::setDot(int x, int y, int dot)
{
    map[x][y] = dot;
}

bool Chunk::isEmpty()
{
    for (auto line: map)
    {
        for (auto dot: line)
        {
            if (dot != 8)
            {
                return false;
            }
        }
    }
    return true;
}

void Chunk::draw(QPainter *painter)
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
    painter->setPen(Qt::transparent);
    for (int x = 0; x < 16; x++)
    {
        for (int y = 0; y < 16; y++)
        {
//            std::cout << x << " " << y  << " " << dot(x, y) << std::endl;
//            if (dot(x, y) != 8)
//            {
//                std::cout << dot(x, y) << std::endl;
//            }
            painter->setBrush(settings->colors()[dot(x, y) % 3]);
            painter->drawEllipse(dotCoord(x, y), 3, 3);
        }
    }
}

QPoint Chunk::dotCoord(int x, int y)
{
    return QPoint((this->x + x) * 16 + 8, (this->y + y) * 16 + 8);
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
            chunks[i].push_back(Chunk(i * 16, j * 16, settings));
        }
    }
}

void Dots::addTrack(std::vector<QPoint> track)
{
    for (unsigned i = 0; i < track.size() - 1; i++)
    {
        tracks.insert(QLine(track[i], track[i + 1]));
    }
}

std::set<QPoint> Dots::surrounding(int x, int y)
{
    std::set<QPoint> answer;
    for (int dx: {-1, 0, 1})
    {
        for (int dy: {-1, 0, 1})
        {
            if (not (dx == 0 and dy == 0) and this->dot(x + dx, y + dy) == this->dot(x, y))
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

void Dots::changeScale(double delta, QSize size)
{
    scale += delta;
    scale = std::min(scale, 6.0);
    scale = std::max(scale, 2.0);
    size /= scale;
    normalize(size);
}

Chunk* Dots::chunk(int x, int y)
{
    int cx = x / 16, cy = y / 16;
    return &chunks[cx][cy];
}

int Dots::dot(int x, int y)
{
    return chunk(x, y)->dot(x % 16, y % 16);
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

void Dots::findNewTracksAndEaten(int x, int y){}

void Dots::turn(QPoint pos)
{
    if (QRect(1, 1, 255, 255).contains(pos.x(), pos.y()) and dot(pos.x(), pos.y()) == 8)
    {
        chunk(pos.x(), pos.y())->setDot(pos.x() % 16, pos.y() % 16, turning_player);
        std::cout << pos.x() << " " << pos.y() << std::endl;
        this->findNewTracksAndEaten(pos.x(), pos.y());
        turning_player = (turning_player + 1) % 2;
    }
}

void Dots::draw(QSize size, QPainter *painter, QPoint cursor)
{
    painter->scale(scale, scale);
    size /= scale;
    normalize(size);
    int tx = size.width() / 2 - cam_x, ty = size.height() / 2 - cam_y;
    painter->translate(tx, ty);
    for (int x = 0; x < 256; x += 16)
    {
        for (int y = 0; y < 256; y += 16)
        {
            if (-256 < x * 16 + tx && x * 16 + tx <= size.width() and
                -256 < y * 16 + ty && y * 16 + ty <= size.height())
            {
                chunk(x, y)->draw(painter);
            }
        }
    }
    if (QRect(1, 1, 255, 255).contains(cursor) and
            dot(cursor.x(), cursor.y()) == 8)
    {
        painter->setBrush(settings->colors()[turning_player]);
        painter->setOpacity(0.5);
        painter->drawEllipse(cursor * 16 + QPoint(8, 8), 3, 3);

    }
}
