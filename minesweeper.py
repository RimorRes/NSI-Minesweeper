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

#gui = tk.Tk()
#diff = tk.Label(gui, text = "Difficulty")
#diff.pack()
#easy = tk.Button(gui, text = "Easy", command = gui.destroy)
#easy.pack()
#medium = tk.Button(gui, text = "Medium", command = gui.destroy)
#medium.pack()
#hard = tk.Button(gui, text = "Hard", command = gui.destroy)
#hard.pack()
#gui.mainloop


class Game(tk.Frame):

    def __init__(self, master, width, height, geometry_width, geometry_height, tile_size, number_mines):
        super().__init__()
        self.master = master
        self.master.title("Minesweeper")
        self.pack(side=tk.BOTTOM)

        self.gwidth, self.gheight = geometry_width, geometry_height

        self.canvas = tk.Canvas(self, width= self.gwidth - 76, height= self.gheight - 76)
        self.canvas.bind('<Button-1>', self.handle_left_click)
        self.canvas.bind('<Button-3>', self.handle_right_click)
        self.canvas.pack()

        self.move_counter = 0

        self.width, self.height = width, height
        self.tile_size = tile_size

        # Matrix which contains the number of adjacent mines
        self.tile_states = [[0] * self.width for _ in range(self.height)]
        self.number_mines = number_mines
        self.mine_positions = []
        self.flag_positions = []
        self.discovered_tiles = []

        self.tile_images = {}
        tiles = ['tile', 'flag', 'bomb', 'hidden', 'wrong', '0', '1', '2', '3', '4', '5', '6', '7', '8']
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
                # If all tiles which aren't mines are discovered
                if len(self.discovered_tiles) + self.number_mines == self.width * self.height:
                    print("You win!")

    def handle_right_click(self, event):
        x = event.x // self.tile_size
        y = event.y // self.tile_size

        if self.move_counter >= 1:
            self.toggle_flag(x, y)

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
        self.canvas.create_image(x * self.tile_size + 2, y * self.tile_size + 2, anchor=tk.NW, image=img)

def GameEasy():
  gui.destroy()
  root = tk.Tk()
  root.title("MINESWEEPER")
  #root.configure(background = "gray")
  root.geometry("480x720")
  game = Game(root, 8, 13, 480, 720, 50, 10)

def GameNormal():
  gui.destroy()
  root = tk.Tk()
  root.title("MINESWEEPER")
  #root.configure(background = "gray")
  root.geometry("580x820")
  game = Game(root, 13, 15, 580, 820, 50, 40)

def GameHard():
  gui.destroy()
  root = tk.Tk()
  root.title("MINESWEEPER")
  #root.configure(background = "gray")
  root.geometry("1130x640")
  game = Game(root, 30, 16, 1130, 640, 35, 99)

def GameChoose(event):
  gui.destroy()
  root = tk.Tk()
  root.title("MINESWEEPER")
  #root.configure(background = "gray")
  game = Game(root)



if __name__ == "__main__":
    gui = tk.Tk()
    gui.title("gui")
    gui.configure(background = "#d2e3d0")
    gui.geometry("300x500")
    diff = tk.Label(gui, text = "Difficulty")
    diff.pack(pady=5)
    easy = tk.Button(gui, text = "Easy", command = GameEasy)
    easy.pack(pady=5)
    medium = tk.Button(gui, text = "Medium", command = GameNormal)
    medium.pack(pady=5)
    hard = tk.Button(gui, text = "Hard", command = GameHard)
    hard.pack(pady=5)

    canvas = tk.Canvas(width = 100, height = 100)
    
    def number():
      pass

    number = tk.Label(canvas, text = "Enter a Number")
    number.pack(pady=20)
    box = tk.Entry(canvas)
    box.pack(pady = 20)
    button = tk.Button(canvas, text = "Confirm number", command = number)
    canvaslabel = tk.Label(gui)
    
    canvas.pack()
    


    #gui.mainloop

    gui.mainloop()


