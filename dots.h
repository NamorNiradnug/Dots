#pragma once

#include <QtGui>
#include <vector>
#include <set>
#include <map>


class Dots;


bool operator <(QPoint point1, QPoint point2);
bool operator <(QLine line1, QLine line2);


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
    int dot(int x, int y);
    void setDot(int x, int y, int dot);
    bool isEmpty();
    void draw(QPainter *painter);
private:
    QPoint dotCoord(int x, int y);
    int x, y;
    std::vector<std::vector<int>> map;
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
    double getScale();
    QPoint camPos();
    void findNewTracksAndEaten(int x, int y);
    void normalize(QSize size);
    std::set<QPoint> surrounding(int x, int y);
    void translate(QPoint delta, QSize size);
    void turn(QPoint pos);
private:
    int cam_x = 0, cam_y = 0, turning_player = 0;
    std::set<QLine> tracks;
    double scale = 2.0;
    std::vector<std::vector<Chunk>> chunks;
    Settings *settings = new Settings();
};
