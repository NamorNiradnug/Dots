#include "frame.h"

#include <QApplication>

int main(int argc, char *argv[])
{
    QApplication a(argc, argv);
    Frame *frame = new Frame();
    frame->show();
    return a.exec();
}
