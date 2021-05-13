import tkinter as tk
import tkinter.ttk as ttk
from ttkthemes import ThemedStyle
import random
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


def center_widget(widget, widget_width=None, widget_height=None):
    if widget_width is None:
        widget.update()
        widget_width = widget.winfo_width()
    if widget_height is None:
        widget.update()
        widget_height = widget.winfo_height()

    screen_width = widget.winfo_screenwidth()
    screen_height = widget.winfo_screenheight()
    x = (screen_width / 2) - (widget_width / 2)
    y = (screen_height / 2) - (widget_height / 2)

    widget.geometry(f'+{int(x)}+{int(y)}')


class SplashScreen(tk.Toplevel):

    def __init__(self, master):
        super().__init__(master)
        self.title("Minesweeper Splash Screen")
        self.overrideredirect(True)

        self.geometry('1280x640')
        center_widget(self, 1280, 640)

        self.canvas = tk.Canvas(self, width=1280, height=640, bd=-2)
        self.canvas.pack()
        self.img = ImageTk.PhotoImage(
                Image.open('textures/naval_mine6.png')
                .resize((1280, 640))
            )
        self.canvas.create_image(0, 0, anchor=tk.NW, image=self.img)

        self.update()


class MainMenuGUI(tk.Tk):

    def __init__(self):
        # Setting up the window
        super().__init__()
        self.title("Main Menu")
        icon_image = ImageTk.PhotoImage(Image.open('textures/title_bar_icon.png'))
        self.iconphoto(False, icon_image)

        # Setting up the style
        style = ThemedStyle(self)
        style.theme_use('arc')

        # Splash screen
        self.withdraw()
        splash = SplashScreen(self)

        self.geometry("300x500")
        center_widget(self, 300, 500)

        self.display_menu_content()

        sleep(1)
        splash.destroy()
        self.deiconify()

        self.mainloop()

    def display_menu_content(self):
        diff = ttk.Label(self, text="Difficulty")
        diff.pack(pady=5)

        easy = ttk.Button(self, text="Easy", command=lambda: self.start_game("easy"))  # Easy mode button
        easy.pack(pady=5)
        medium = ttk.Button(self, text="Normal", command=lambda: self.start_game("normal"))  # Normal mode button
        medium.pack(pady=5)
        hard = ttk.Button(self, text="Hard", command=lambda: self.start_game("hard"))  # Hard mode button
        hard.pack(pady=5)

        canvas = tk.Canvas(width=100, height=100)  # Canvas for custom difficulty

        # TODO: finish this
        number = ttk.Label(canvas, text="Enter a Number")
        number.pack(pady=20)
        box = ttk.Entry(canvas)
        box.pack(pady=10)
        button = ttk.Button(canvas, text="Confirm number")
        button.pack(pady=20)
        canvas_label = ttk.Label(self, text="Custom difficulty")
        canvas_label.pack()

        canvas.pack()

    def start_game(self, difficulty):
        self.destroy()

        if difficulty == "easy":  # Easy difficulty
            Game(
                width=8,
                height=13,
                tile_size=50,
                number_mines=10
            )
        elif difficulty == "normal":  # Normal difficulty
            Game(
                width=13,
                height=15,
                tile_size=50,
                number_mines=40
            )
        elif difficulty == "hard":  # Hard difficulty
            Game(
                width=30,
                height=16,
                tile_size=35,
                number_mines=99
            )

        elif difficulty == "custom":  # Custom difficulty
            pass  # TODO: Choose your own difficulty


class Game(tk.Tk):

    def __init__(self, width, height, tile_size, number_mines):
        # Setting up the window
        super().__init__()
        self.title("Minesweeper")
        icon_image = ImageTk.PhotoImage(Image.open('textures/title_bar_icon.png'))
        self.iconphoto(False, icon_image)

        # Game/tile dimensions
        self.width, self.height = width, height  # columns and rows
        self.tile_size = tile_size

        # Resizing game window
        w = self.width * self.tile_size + 50*2  # canvas width + extra padding
        h = self.height * self.tile_size + 50*2  # canvas width + extra padding
        self.geometry(f"{int(w)}x{int(h)}")
        center_widget(self)

        # Setting up canvas
        self.canvas = tk.Canvas(  # Dimensions of actual game + remove thin border
            self,
            width=self.width*self.tile_size,
            height=self.height*self.tile_size,
            bd=-2)
        self.canvas.bind('<Button-1>', self.handle_left_click)  # Binding clicks to have functions
        self.canvas.bind('<Button-3>', self.handle_right_click)
        self.canvas.place(relx=0.5, rely=0.5, anchor=tk.CENTER)  # pack canvas to center

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

        self.mainloop()  # redundant

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


if __name__ == "__main__":
    main_menu = MainMenuGUI()
