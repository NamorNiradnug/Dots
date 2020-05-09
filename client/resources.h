#pragma once

#include <QPoint>
#include <QLine>
#include <QColor>
#include <map>
#include <set>
#include <vector>


std::set<QPoint> circle(int cx, int cy);
bool operator <(QPoint point1, QPoint point2);
bool operator <(QLine line1, QLine line2);
std::vector<QPoint> operator +(std::vector<QPoint> first, std::vector<QPoint> second);
std::vector<QPoint> reversed(std::vector<QPoint> vec);
QPoint max(QPoint p1, QPoint p2);
int player(int dot);
int eater(int dot);


class Settings
{
public:
    Settings();
    std::map<int, QColor> colors();
    QString name(int player);
private:
    std::map<int, QColor> colors_;
    QString name1 = "Player 1", name2 = "Player 2";
};

Settings* dsettings();
