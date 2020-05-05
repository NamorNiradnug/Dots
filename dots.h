#pragma once

#include <QtGui>
#include <vector>
#include <set>
#include <map>


class Dots;


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
private:
    std::map<int, QColor> colors_;
};

class Chunk
{
public:
    Chunk(int x, int y, Settings *settings);
    void addTrack(QLine track);
    std::set<QLine> getTracks();
    int dot(int x, int y);
    int dot(QPoint pos);
    void setDot(int x, int y, int dot);
    void drawLines(QPainter *painter);
    void drawDots(QPainter *painter, Dots* dots);
private:
    QPoint dotCoord(int x, int y);
    QPoint dotCoord(QPoint pos);
    int x, y;
    std::vector<std::vector<int>> map;
    std::set<QLine> tracks;
    Settings *settings;
};


class Dots
{
public:
    Dots();
    void addTrack(std::vector<QPoint> track);
    void changeScale(double delta, QSize size);
    Chunk* chunk(int x, int y);
    void draw(QSize size, QPainter *painter, QPoint cursor);
    int dot(int x, int y);
    int dot(QPoint pos);
    double getScale();
    QPoint camPos();
    bool isFirst(QPoint pos);
    void findNewTracksAndEaten(int x, int y);
    void normalize(QSize size);
    std::set<QPoint> surrounding(int x, int y);
    void translate(QPoint delta, QSize size);
    void turn(QPoint pos);
private:
    int cam_x = 0, cam_y = 0, turning_player = 0;
    int min_x = 256, max_x = 256, min_y = 0, max_y = 0;
    double scale = 2.0;
    std::vector<std::vector<Chunk>> chunks;
    Settings *settings = new Settings();
    QPoint first1 = QPoint(-1, -1), second1 = QPoint(-1, -1); // the first dot of players

};
