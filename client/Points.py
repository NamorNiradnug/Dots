from tkinter import Tk, Canvas

points_map = [[0] * 100 for __ in range(100)]
first_player_color, second_player_color = "red", "green"
players_color_list = [0, first_player_color, second_player_color]

player_how_turn = [1]
zoom_koef = [2]
paper_coords = [0, 0]
zero_move = [0, 0]
root = Tk()
paper = Canvas(root, width = 160 * 4, height = 4 * 160)
paper.pack() 


def draw_point(point_type, x, y):
    paper.create_line((x * 16 + 8) * zoom_koef[0], y * zoom_koef[0] * 16, (x * 16 + 8) * zoom_koef[0], (y + 1) * zoom_koef[0] * 16)
    paper.create_line(x * zoom_koef[0] * 16, (y * 16 + 8) * zoom_koef[0], (x + 1) * zoom_koef[0] * 16,  (y * 16 + 8) * zoom_koef[0])
    if point_type != 0:
        paper.create_oval((x * 16 + 5) * zoom_koef[0], (y * 16 + 5) * zoom_koef[0], (x * 16 + 11) * zoom_koef[0], (y * 16 + 11) * zoom_koef[0], fill = players_color_list[point_type])


def draw_paper(x, y):
    paper_coords[0] = x
    paper_coords[1] = y
    w = h =  640 // (zoom_koef[0] * 16)
    for i in range(len(points_map[y:y + h:])):
        for j in range(len(points_map[i][x:x + w:])):
            draw_point(points_map[y:y + h:][i][x:x + w:][j], j, i)
    for i in range(len(points_map[y:y + h - 1:])):
        for j in range(len(points_map[i][x:x + w - 1:])):
            if points_map[i][j] == points_map[i][j + 1] > 0:
                paper.create_line((j * 16 - 8) * zoom_koef[0], (i * 16 - 8) * zoom_koef[0], (j * 16 + 8) * zoom_koef[0], (i * 16 - 8) * zoom_koef[0], fill = players_color_list[points_map[i][j]], width = 2 * zoom_koef[0])
            if points_map[i][j] == points_map[i + 1][j] > 0:
                paper.create_line((j * 16 - 8) * zoom_koef[0], (i * 16 - 8) * zoom_koef[0], (j * 16 - 8) * zoom_koef[0], (i * 16 + 8) * zoom_koef[0], fill = players_color_list[points_map[i][j]], width = 2 * zoom_koef[0])        


def to_zoom_koef(zoom_k):
    if zoom_k != 0 and zoom_k != 16:
        paper.delete('all')
        zoom_koef[0] = zoom_k
        draw_paper(paper_coords[0], paper_coords[1])    


def move_screen(x, y):
    if paper_coords[1] + y <= 0:
        points_map.insert(0, [0] * len(points_map[0]))
        paper_coords[1] += 1
        zero_move[1] += 1
    if paper_coords[0] + x <= 0:
        for i in range(len(points_map)):
            points_map[i].insert(0, 0)
        paper_coords[0] += 1
        zero_move[0] += 1
    paper.delete('all')
    draw_paper(paper_coords[0] + x, paper_coords[1] + y)


def create_point(x, y):
    x ,y = x // (16 * zoom_koef[0]) + paper_coords[0], y // (16 * zoom_koef[0]) + paper_coords[1]
    #send to server  x - zero_move[0], y - zero_move[1] - new point coords
    #if server answer == true:
    if points_map[y][x] == 0:
        points_map[y][x] = player_how_turn[0]
        paper.delete('all')
        draw_paper(paper_coords[0], paper_coords[1])
        if player_how_turn[0] == 1:
            player_how_turn[0] = 2
        else:
            player_how_turn[0] = 1


draw_paper(1, 1)
root.bind('<Control-=>', lambda event: to_zoom_koef(zoom_koef[0] * 2))
root.bind('<MouseWheel>', lambda event: to_zoom_koef(zoom_koef[0] // 2))
root.bind('<Up>', lambda event: move_screen(0, -1))
root.bind('<Down>', lambda event: move_screen(0, 1))
root.bind('<Left>', lambda event: move_screen(-1, 0))
root.bind('<Right>', lambda event: move_screen(1, 0))
root.bind('<Button-1>', lambda event: create_point(event.x, event.y))
root.mainloop()