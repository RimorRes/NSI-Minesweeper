import random
import tkinter as tk
from PIL import ImageTk, Image


def generate_mines(width, height, number_mines, excluded):
    mine_list = []

    while len(mine_list) < number_mines:
        x = random.randint(0, width - 1)
        y = random.randint(0, height - 1)
        pos = [x, y]
        if pos not in mine_list and pos not in excluded:
            mine_list.append(pos)

    return mine_list


def delimit_start_area(start_x, start_y, width, height, radius=1):
    area = []
    for vert in range(-radius, radius + 1):
        for horz in range(-radius, radius + 1):
            x = start_x + horz
            y = start_y + vert
            if (0 <= x < width) and (0 <= y < height):
                area.append([x, y])
    return area


class Game(tk.Frame):

    def __init__(self, master, width, height, tile_size, number_mines):
        super().__init__()
        self.master = master
        self.master.title("Minesweeper")
        self.pack(side=tk.BOTTOM)

        self.canvas = tk.Canvas(self, width=400 + 4, height=650 + 4)
        self.canvas.bind('<Button-1>', self.handle_left_click)
        self.canvas.bind('<Button-3>', self.handle_right_click)
        self.canvas.pack()

        self.move_counter = 0

        self.width, self.height = width, height
        self.tile_size = tile_size

        self.tile_states = [[0] * self.width for _ in range(self.height)]
        self.number_mines = number_mines
        self.mine_positions = []
        self.flag_positions = []
        self.discovered_tiles = []

        self.tile_images = {}
        tiles = ['tile', 'flag', 'bomb', 'hidden', 'wrong', '0', '1', '2', '3', '4']
        for t in tiles:
            self.tile_images[t] = ImageTk.PhotoImage(
                Image.open('textures/' + t + '.png')
                .resize((self.tile_size, self.tile_size))
            )

        self.init_grid()

    def handle_left_click(self, event):
        x = event.x // self.tile_size
        y = event.y // self.tile_size
        self.move_counter += 1

        if self.move_counter == 1:
            start_area = delimit_start_area(x, y, self.width, self.height)
            self.mine_positions = generate_mines(self.width, self.height, self.number_mines, excluded=start_area)
            self.count_adjacent_mines()

        if [x, y] not in self.flag_positions:
            if [x, y] in self.mine_positions:
                self.place_tile(x, y, self.tile_images['bomb'])
                print("You lose!")
            else:
                self.reveal_tiles(x, y)
                if (self.width * self.height) - len(self.discovered_tiles) == self.number_mines:
                    print("You win! Hooray!")

    def handle_right_click(self, event):
        x = event.x // self.tile_size
        y = event.y // self.tile_size

        if self.move_counter >= 1:
            self.toggle_flag(x, y)

    def toggle_flag(self, x, y):
        if [x, y] not in self.discovered_tiles:
            if [x, y] not in self.flag_positions:
                self.flag_positions.append([x, y])
                self.place_tile(x, y, self.tile_images['flag'])
            else:
                self.flag_positions.remove([x, y])
                self.place_tile(x, y, self.tile_images['tile'])

    def count_adjacent_mines(self):
        for m in self.mine_positions:
            x, y = m
            for vert in range(-1, 2):
                for horz in range(-1, 2):
                    if (0 <= x + horz < self.width) and (0 <= y + vert < self.height):
                        self.tile_states[y + vert][x + horz] += 1

    def reveal_tiles(self, x, y):
        i = str(self.tile_states[y][x])
        self.place_tile(x, y, self.tile_images[i])
        self.discovered_tiles.append([x, y])

        if self.tile_states[y][x] == 0:
            for vert in range(-1, 2):
                for horz in range(-1, 2):
                    if (0 <= x + horz < self.width) and (0 <= y + vert < self.height):
                        if [x + horz, y + vert] not in self.discovered_tiles:
                            self.reveal_tiles(x + horz, y + vert)

        return

    def init_grid(self):
        for y in range(self.height):
            for x in range(self.width):
                self.place_tile(x, y, self.tile_images['tile'])

    def place_tile(self, x, y, img):
        self.canvas.create_image(x * self.tile_size + 2, y * self.tile_size + 2, anchor=tk.NW, image=img)


if __name__ == "__main__":
    root = tk.Tk()
    root.geometry("480x720")
    game = Game(root, 8, 13, 50, 10)
    root.mainloop()
