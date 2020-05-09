#pragma once

#include <QtGui>
#include <vector>
#include <set>
#include <map>
#include <QString>
#include "resources.h"


class Dots;


class Chunk
{
public:
    Chunk(int x, int y);
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
    void findNewTracks(int x, int y);
    inline void findNewEaten(int x, int y);
    inline void normalize(QSize size);
    std::set<QPoint> surrounding(int x, int y);
    void translate(QPoint delta, QSize size);
    void turn(QPoint pos);
    int winner();
private:
    int cam_x = 0, cam_y = 0, turning_player = 0;
    int min_x = 256, max_x = 256, min_y = 0, max_y = 0;
    double scale = 2.0;
    std::vector<std::vector<Chunk>> chunks;
    QPoint first1 = QPoint(-1, -1), second1 = QPoint(-1, -1); // the first dot of players
};
