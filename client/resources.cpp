#include "resources.h"
#include "QDebug"

std::set<QPoint> circle(int cx, int cy)
{
    std::set<QPoint> answer =
    {
        QPoint(cx - 1, cy),
        QPoint(cx + 1, cy),
        QPoint(cx, cy - 1),
        QPoint(cx, cy + 1)
    };
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

std::vector<QPoint> operator +(std::vector<QPoint> first, std::vector<QPoint> second)
{
    std::vector<QPoint> answer = first;
    answer.insert(answer.end(), second.begin(), second.end());
    return answer;
}

std::vector<QPoint> reversed(std::vector<QPoint> vec)
{
    std::reverse(vec.begin(), vec.end());
    return vec;
}

int player(int dot)
{
    return dot % 3;
}

int eater(int dot)
{
    int e = dot / 3;
    return e;
}

//#######################################
Settings::Settings() {}

QColor Settings::color(int player)
{
    if (0 <= player && player <= 2)
    {
        return colors[player];
    }

    return bad_color;
}

QString Settings::name(int player)
{
    if (0 <= player && player < 2)
    {
        return names[player];
    }

    return bad_name;
}

void Settings::setPlayerName(int player, QString name)
{
    if (0 <= player && player < 2)
    {
        names[player] = name;
    }
}

void Settings::setPlayerColor(int player, QColor color)
{
    if (0 <= player && player < 2)
    {
        colors[player] = color;
    }
}

static Settings *dsettings_ = new Settings();

Settings *dsettings()
{
    return dsettings_;
}
