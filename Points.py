from tkinter import Tk, Canvas
from points_res import points_map, players_color_list


zoom_koef = 10

root = Tk()
paper = Canvas(root, width = 160 * 4, height = 4 * 160)
paper.pack()


def draw_point(point_type, x, y):
    if point_type != 0:
        paper.create_oval((x * 16 + 5) * zoom_koef, (y * 16 + 5) * zoom_koef, (x * 16 + 11) * zoom_koef, (y * 16 + 11) * zoom_koef, fill = players_color_list[point_type])


def draw_paper():
    for i in range(1, len(points_map) + 1):
        paper.create_line(0, (i * 16 - 8) * zoom_koef, 16 * len(points_map[0]) * zoom_koef, (i * 16 - 8) * zoom_koef, width = 1 * zoom_koef)
    for i in range(1, len(points_map[0]) + 1):
        paper.create_line((i * 16 - 8) * zoom_koef, 0, (i * 16 - 8) * zoom_koef, 16 * len(points_map) * zoom_koef, width = 1 * zoom_koef)
    for i in range(len(points_map)):
        for j in range(len(points_map[i])):
            draw_point(points_map[i][j], j, i)


draw_paper()
root.mainloop()