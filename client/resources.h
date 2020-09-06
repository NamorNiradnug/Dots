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
    QColor color(int player);
    QString name(int player);
    void setPlayerName(int player, QString name);
    void setPlayerColor(int player, QColor color);
private:
    QColor colors[3] = {Qt::blue, Qt::red, Qt::transparent};
    QColor bad_color = QColor(200, 0, 230);
    QString names[3] = {"Player 1", "Player 2"};
    QString bad_name = "__$UndefPlayer$__";
};

Settings *dsettings();
