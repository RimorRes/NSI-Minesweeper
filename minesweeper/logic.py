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


class GameCanvas(tk.Canvas):

    def __init__(self, master, width, height, tile_size, number_mines):
        # Inheriting tk.Canvas properties and setting up the canvas
        super().__init__(
            master,
            width=self.width * self.tile_size,
            height=self.height * self.tile_size,
            bd=-2
        )
        self.bind('<Button-1>', self.handle_left_click)  # Binding clicks to have functions
        self.bind('<Button-3>', self.handle_right_click)
        self.place(relx=0.5, rely=0.5, anchor=tk.CENTER)  # pack canvas to center

        # Game/tile dimensions
        self.width, self.height = width, height  # columns and rows
        self.tile_size = tile_size

        # Move counter
        self.move_counter = 0

        # Setting up tile states
        self.tile_states = [[0] * self.width for _ in range(self.height)]  # matrix for number of adjacent mines
        self.number_mines = number_mines
        self.mine_positions = []
        self.flag_positions = []
        self.discovered_tiles = []
        self.tripped_mine = []

        # Handling game icon/images
        self.tile_images = {}
        tiles = ['tile', 'flag', 'mine', 'hidden', 'wrong', '0', '1', '2', '3', '4', '5', '6', '7', '8']
        for t in tiles:
            self.tile_images[t] = ImageTk.PhotoImage(
                Image.open('textures/' + t + '.png')
                .resize((self.tile_size, self.tile_size))
            )

        # Setting up the starting grid
        self.init_grid()

    def handle_left_click(self, event):
        x = event.x // self.tile_size
        y = event.y // self.tile_size
        self.move_counter += 1

        # First move and mine generation
        if self.move_counter == 1:
            start_area = delimit_start_area(x, y, self.width, self.height)
            self.mine_positions = generate_mines(self.width, self.height, self.number_mines, excluded=start_area)
            self.count_adjacent_mines()

        # Reveal tiles and victory/defeat condition
        if [x, y] not in self.flag_positions:
            if [x, y] in self.mine_positions:
                self.place_tile(x, y, self.tile_images['mine'])
                self.tripped_mine = [x, y]
            else:
                self.reveal_tiles(x, y)

    def handle_right_click(self, event):
        x = event.x // self.tile_size
        y = event.y // self.tile_size

        if self.move_counter >= 1:
            self.toggle_flag(x, y)

    def check_win(self):
        if self.tripped_mine:
            self.game_over('lose')  # Defeat

        # If all tiles which aren't mines are discovered
        elif len(self.discovered_tiles) + self.number_mines == self.width * self.height:
            self.game_over('win')  # Victory

    def game_over(self, outcome):
        if outcome == 'lose':
            # Showing hidden bombs
            for mine in self.mine_positions:
                if mine != self.tripped_mine and mine not in self.flag_positions:
                    x, y = mine
                    self.place_tile(x, y, self.tile_images['hidden'])

            # Showing wrong guesses
            for flag in self.flag_positions:
                if flag not in self.mine_positions:
                    x, y = flag
                    self.place_tile(x, y, self.tile_images['wrong'])

    def restart(self):
        # Resetting variables
        self.move_counter = 0
        self.tile_states = [[0] * self.width for _ in range(self.height)]  # matrix for number of adjacent mines
        self.mine_positions = []
        self.flag_positions = []
        self.discovered_tiles = []
        self.tripped_mine = []

        self.init_grid()

    def toggle_flag(self, x, y):

        if [x, y] not in self.discovered_tiles:  # If the tile clicked on not already discovered

            # If the tile already has a flag on it and isn't out of the canvas
            if [x, y] in self.flag_positions and (0 <= x < self.width) and (0 <= y < self.height):
                self.place_tile(x, y, self.tile_images['tile'])
                self.flag_positions.remove([x, y])  # Make the tile a regular 'tile' and remove from flag positions

            else:  # Otherwise, if the tile doesn't have a flag on it
                self.place_tile(x, y, self.tile_images['flag'])
                self.flag_positions.append([x, y])  # Place a flag and add to flag positions

    def count_adjacent_mines(self):
        for m in self.mine_positions:
            x, y = m
            for vert in range(-1, 2):
                for horz in range(-1, 2):
                    if (0 <= x + horz < self.width) and (0 <= y + vert < self.height):
                        self.tile_states[y + vert][x + horz] += 1

    def reveal_tiles(self, x, y):
        if not [x, y] in self.discovered_tiles:
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
        self.create_image(x * self.tile_size, y * self.tile_size, anchor=tk.NW, image=img)
