import random
import tkinter as tk
from PIL import ImageTk, Image
from time import sleep


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

# gui = tk.Tk()
# diff = tk.Label(gui, text = "Difficulty")
# diff.pack()
# easy = tk.Button(gui, text = "Easy", command = gui.destroy)
# easy.pack()
# medium = tk.Button(gui, text = "Medium", command = gui.destroy)
# medium.pack()
# hard = tk.Button(gui, text = "Hard", command = gui.destroy)
# hard.pack()
# gui.mainloop


class SplashScreen(tk.Toplevel):

    def __init__(self, master):
        super().__init__(master)
        self.title("Splash Screen Example")
        self.overrideredirect(True)

        screen_width = master.winfo_screenwidth()
        screen_height = master.winfo_screenheight()
        x = (screen_width/2) - (1280/2)
        y = (screen_height/2) - (640/2)
        self.geometry(f'1280x640+{int(x)}+{int(y)}')

        self.canvas = tk.Canvas(self, width=1280, height=640, bd=-2)
        self.canvas.pack()
        self.img = ImageTk.PhotoImage(
                Image.open('naval_mine6.png')
                .resize((1280, 640))
            )
        self.canvas.create_image(0, 0, anchor=tk.NW, image=self.img)

        self.update()


class Game(tk.Frame):

    def __init__(self, master, width, height, tile_size, number_mines):
        # Setting up the frame
        super().__init__(master)
        self.master = master
        self.pack(side=tk.BOTTOM)

        # Game/tile dimensions
        self.width, self.height = width, height  # columns and rows
        self.tile_size = tile_size

        # Setting up canvas
        self.canvas = tk.Canvas(  # Dimensions of actual game + remove thin border
            self,
            width=self.width*self.tile_size,
            height=self.height*self.tile_size,
            bd=-2)
        self.canvas.bind('<Button-1>', self.handle_left_click)  # Binding clicks to have functions
        self.canvas.bind('<Button-3>', self.handle_right_click)
        self.canvas.pack()

        # Move counter
        self.move_counter = 0

        # Setting up tile states
        self.tile_states = [[0] * self.width for _ in range(self.height)]  # matrix for number of adjacent mines
        self.number_mines = number_mines
        self.mine_positions = []
        self.flag_positions = []
        self.discovered_tiles = []

        # Handling game icon/images
        self.tile_images = {}
        tiles = ['tile', 'flag', 'bomb', 'hidden', 'wrong', '0', '1', '2', '3', '4', '5', '6', '7', '8']
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
        self.canvas.create_image(x * self.tile_size, y * self.tile_size, anchor=tk.NW, image=img)


def game_easy():  # Easy difficulty
    gui.destroy()
    root = tk.Tk()
    root.title("Minesweeper")
    # root.configure(background="gray")
    root.geometry("480x720")
    Game(
        master=root,
        width=8,
        height=13,
        tile_size=50,
        number_mines=10
    )


def game_normal():  # Normal difficulty
    gui.destroy()
    root = tk.Tk()
    root.title("Minesweeper")
    # root.configure(background="gray")
    root.geometry("580x820")
    Game(
        master=root,
        width=13,
        height=15,
        tile_size=50,
        number_mines=40
    )


def game_hard():  # Hard difficulty
    gui.destroy()
    root = tk.Tk()
    root.title("Minesweeper")
    # root.configure(background = "gray")
    root.geometry("1130x640")
    Game(
        master=root,
        width=30,
        height=16,
        tile_size=35,
        number_mines=99
    )

# TODO: Choose your own difficulty
# def game_choose(event):  # Choose your own difficulty
#     gui.destroy()
#     root = tk.Tk()
#     root.title("Minesweeper")
#     root.configure(background="gray")
#     Game(root)


if __name__ == "__main__":

    gui = tk.Tk()  # Creating GUI

    # Splash screen
    splash = SplashScreen(gui)
    gui.withdraw()
    sleep(2)
    splash.destroy()
    gui.deiconify()

    gui.title("Menu")
    gui.configure(background="#d2e3d0")
    gui.geometry("300x500")
    diff = tk.Label(gui, text="Difficulty")
    diff.pack(pady=5)
    easy = tk.Button(gui, text="Easy", command=game_easy)  # Easy mode button
    easy.pack(pady=5)
    medium = tk.Button(gui, text="Normal", command=game_normal)  # Normal mode button
    medium.pack(pady=5)
    hard = tk.Button(gui, text="Hard", command=game_hard)  # Hard mode button
    hard.pack(pady=5)

    canvas = tk.Canvas(width=100, height=100)  # Canvas for choose your own

    number = tk.Label(canvas, text="Enter a Number")
    number.pack(pady=20)
    box = tk.Entry(canvas)
    box.pack(pady=10)
    button = tk.Button(canvas, text="Confirm number")
    button.pack(pady=20)
    canvas_label = tk.Label(gui)

    canvas.pack()

    gui.mainloop()
