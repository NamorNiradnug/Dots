from tkinter import Tk, Canvas

def point_up(point):
    return [point[0], point[1] - 1]

def point_up_left(point):
    return [point[0] - 1, point[1] - 1]

def point_left(point):
    return [point[0] - 1, point[1]]

def point_up_right(point):
    return [point[0] + 1, point[1] - 1]

def point_right(point):
    return [point[0] + 1, point[1]]

def point_down(point):
    return [point[0], point[1] + 1]

def point_down_left(point):
    return [point[0] - 1, point[1] + 1]

def point_down_right(point):
    return [point[0] + 1, point[1] + 1]

nigh_points_func = [point_up, point_up_left, point_left, point_up_right, point_down_left, point_right, point_down_right, point_down]
npf = nigh_points_func


class Dots:
    def __init__(self):
        self.point_map = [[0] * 100 for __ in range(100)]
        self.players_colors = [0, 'red', 'blue']
        self.all_tracks = []
        #all_draw_trakcs = [[]]
        
        self.player_how_turn = 1
        self.scale = 2
        self.paper_coords = [0, 0]
        self.zero_move = [0, 0]
        self.root = Tk()
        self.paper = Canvas(self.root, width = 160 * 4, height = 4 * 160)
        self.paper.pack() 
        
        self.draw_paper(1, 1)
        self.root.bind('<Control-=>', lambda event: self.to_scale(self.scale * 2))
        self.root.bind('<MouseWheel>', lambda event: self.to_scale(self.scale // 2))
        self.root.bind('<Up>', lambda event: self.move_screen(0, -1))
        self.root.bind('<Down>', lambda event: self.move_screen(0, 1))
        self.root.bind('<Left>', lambda event: self.move_screen(-1, 0))
        self.root.bind('<Right>', lambda event: self.move_screen(1, 0))
        self.root.bind('<Button-1>', lambda event: self.create_point(event.x, event.y))
        self.root.mainloop()        
    
    def have_points_connect(self, point1, point2, used_tracks = {1}, track_len = 0):
        result = False
        print(point1, point2)
        if point1 == point2 and track_len > 2:
            print(3)
            return True, used_tracks
        for i in npf:
            try:
                if self.point_map[(i(point1))[1]][(i(point1))[0]] == self.point_map[point1[1]][point1[0]] and not ((tuple(i(point1)), point1) in used_tracks):
                    print(used_tracks, (point1, point2))
                    variable = self.have_points_connect(tuple(i(point1)), point2, used_tracks and {(tuple(i(point1)), point2), (point2, tuple(i(point1)))}, track_len + 1)
                    result += variable[0]
                    used_tracks.update(variable[1])
            except:
                pass
        return bool(result), used_tracks
    
    
    def draw_point(self, point_type, x, y):
        self.paper.create_line((x * 16 + 8) * self.scale, y * self.scale * 16, (x * 16 + 8) * self.scale, (y + 1) * self.scale * 16)
        self.paper.create_line(x * self.scale * 16, (y * 16 + 8) * self.scale, (x + 1) * self.scale * 16,  (y * 16 + 8) * self.scale)
        if point_type != 0:
            self.paper.create_oval((x * 16 + 5) * self.scale, (y * 16 + 5) * self.scale, (x * 16 + 11) * self.scale, (y * 16 + 11) * self.scale, fill = self.players_colors[point_type])
    
    
    def draw_paper(self, x, y):
        self.paper_coords[0] = x
        self.paper_coords[1] = y
        w = h =  640 // (self.scale * 16)
        for i in range(len(self.point_map[y:y + h:])):
            for j in range(len(self.point_map[i][x:x + w:])):
                self.draw_point(self.point_map[y:y + h:][i][x:x + w:][j], j, i)
        for i in range(len(self.point_map[y:y + h:])):
            for j in range(len(self.point_map[i][x:x + w:])):                        
                try:
                    if self.point_map[y:y + h:][i][x:x + w:][j] == self.point_map[y:y + h:][i][x:x + w:][j + 1] > 0:
                        self.paper.create_line((j * 16 + 8) * self.scale, (i * 16 + 8) * self.scale, (j * 16 + 24) * self.scale, (i * 16 + 8) * self.scale, fill = self.players_colors[self.point_map[y:y + h:][i][x:x + w:][j]], width = 2 * self.scale)
                except:
                    pass
                try:
                    if self.point_map[y:y + h:][i][x:x + w:][j] == self.point_map[y:y + h:][i + 1][x:x + w:][j] > 0:
                        self.paper.create_line((j * 16 + 8) * self.scale, (i * 16 + 8) * self.scale, (j * 16 + 8) * self.scale, (i * 16 + 24) * self.scale, fill = self.players_colors[self.point_map[y:y + h:][i][x:x + w:][j]], width = 2 * self.scale)        
                except:
                    pass                
                
    
    
    def to_scale(self, zoom_k):
        if zoom_k != 0 and zoom_k != 16:
            self.paper.delete('all')
            self.scale = zoom_k
            self.draw_paper(self.paper_coords[0], self.paper_coords[1])    
    
    
    def move_screen(self, x, y):
        if self.paper_coords[1] + y <= 0:
            self.point_map.insert(0, [0] * len(self.point_map[0]))
            self.paper_coords[1] += 1
            self.zero_move[1] += 1
        if self.paper_coords[0] + x <= 0:
            for i in range(len(self.point_map)):
                self.point_map[i].insert(0, 0)
            self.paper_coords[0] += 1
            self.zero_move[0] += 1
        self.paper.delete('all')
        self.draw_paper(self.paper_coords[0] + x, self.paper_coords[1] + y)
    
    
    def create_point(self, x, y):
        x ,y = x // (16 * self.scale) + self.paper_coords[0], y // (16 * self.scale) + self.paper_coords[1]
        if self.point_map[y][x] == 0:
            self.point_map[y][x] = self.player_how_turn
           # print(have_points_connect((x, y), (x, y)))
            self.paper.delete('all')
            self.draw_paper(self.paper_coords[0], self.paper_coords[1])
            if self.player_how_turn == 1:
                self.player_how_turn = 2
            else:
                self.player_how_turn = 1

Dots()