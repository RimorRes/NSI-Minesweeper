import random
import tkinter as tk
import tkinter.ttk as ttk

from PIL import ImageTk, Image
from ttkthemes import ThemedStyle


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


def center_window(window, width=None, height=None):
    if width is None:
        window.update()
        width = window.winfo_width()
    if height is None:
        window.update()
        height = window.winfo_height()

    screen_width = window.winfo_screenwidth()
    screen_height = window.winfo_screenheight()
    x = (screen_width / 2) - (width / 2)
    y = (screen_height / 2) - (height / 2)

    window.geometry(f'+{int(x)}+{int(y)}')


def hide_frame(frame, sub_canvases=()):
    for widget in frame.winfo_children():
        print(widget)
        widget.destroy()

    if sub_canvases:
        for canvas in sub_canvases:
            canvas.delete("all")

    frame.pack_forget()


class SplashScreen(tk.Toplevel):

    def __init__(self, master):
        super().__init__(master)

        # Setting up the window
        self.title("Minesweeper Splash Screen")
        self.overrideredirect(True)
        self.geometry('640x360')
        center_window(self, 640, 360)

        # Importing each frame of the .gif
        file_name = 'textures/splash_screen.gif'
        n_frames = Image.open(file_name).n_frames
        self.frames = [tk.PhotoImage(file=file_name, format=f'gif -index {i}') for i in range(n_frames)]

        # Displaying the .gif
        self.gif_label = tk.Label(self, image='')
        self.gif_label.pack()
        self.frame_index = 0
        self.animation()

        self.update()

    def animation(self):
        if self.frame_index < len(self.frames):
            self.gif_label.configure(image=self.frames[self.frame_index])
            self.update()
            self.frame_index += 1
            self.gif_label.after(ms=25)
            self.animation()


class Game(tk.Frame):

    def __init__(self, master, width, height, tile_size, number_mines):
        # Inheriting tk.Frame properties
        super().__init__(master)

        # Init variables
        self.width, self.height = width, height  # dimensions; columns and rows
        self.tile_size = tile_size  # tile dimensions
        self.number_mines = number_mines
        self.move_counter = 0

        # Setting up tile states
        self.tile_states = [[0] * self.width for _ in range(self.height)]  # matrix for number of adjacent mines
        self.mine_positions = []
        self.flag_positions = []
        self.discovered_tiles = []
        self.tripped_mine = []

        # Setting up the canvas
        self.canvas = tk.Canvas(
            self,
            width=self.width * self.tile_size,
            height=self.height * self.tile_size,
            bd=-2
        )
        self.canvas.bind('<Button-1>', self.handle_left_click)  # Binding clicks to functions
        self.canvas.bind('<Button-3>', self.handle_right_click)
        self.canvas.pack()

        # Handling game icon/images
        self.tile_images = {}
        tiles = ['tile', 'flag', 'mine', 'hidden', 'wrong', '0', '1', '2', '3', '4', '5', '6', '7', '8']
        for t in tiles:
            self.tile_images[t] = ImageTk.PhotoImage(
                Image.open('textures/' + t + '.png')
                .resize((self.tile_size, self.tile_size))
            )

        # Resizing game window
        w = self.width * self.tile_size + 50 * 2  # canvas width + extra padding
        h = self.height * self.tile_size + 50 * 2  # canvas width + extra padding
        master.geometry(f"{int(w)}x{int(h)}")
        center_window(master)

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
        self.canvas.create_image(x * self.tile_size, y * self.tile_size, anchor=tk.NW, image=img)


class MainMenu(tk.Frame):

    def __init__(self, master):
        # Inheriting tk.Frame properties
        super().__init__(master)

        self.display_menu_content()

    def display_menu_content(self):
        diff = ttk.Label(self, text="Difficulty")
        diff.grid(pady=5)

        easy = ttk.Button(self, text="Easy", command=lambda: set_difficulty("easy"))  # Easy mode button
        easy.grid(pady=5)
        medium = ttk.Button(self, text="Normal", command=lambda: set_difficulty("normal"))  # Normal mode button
        medium.grid(pady=5)
        hard = ttk.Button(self, text="Hard", command=lambda: set_difficulty("hard"))  # Hard mode button
        hard.grid(pady=5)

        # TODO: finish this
        canvas_label = ttk.Label(self, text="Custom difficulty")
        canvas_label.grid(pady=20)
        number = ttk.Label(self, text="Enter a Number")
        number.grid()
        box = ttk.Entry(self)
        box.grid(pady=10)
        button = ttk.Button(self, text="Confirm number")
        button.grid(pady=20)


def start_up():
    root.withdraw()
    splash = SplashScreen(root)

    icon_image = ImageTk.PhotoImage(Image.open('textures/title_bar_icon.png'))
    root.iconphoto(False, icon_image)

    style = ThemedStyle(root)
    style.theme_use('arc')

    splash.destroy()
    root.deiconify()


def set_difficulty(difficulty):

    if difficulty == "easy":  # Easy difficulty
        new_game(8, 13, 50, 10)

    elif difficulty == "normal":  # Normal difficulty
        new_game(13, 15, 50, 40)

    elif difficulty == "hard":  # Hard difficulty
        new_game(30, 16, 35, 99)

    elif difficulty == "custom":  # Custom difficulty
        pass  # TODO: Choose your own difficulty


def new_game(width, height, tile_size, number_mines):
    hide_frame(main_menu)

    root.title("Minesweeper")

    game = Game(
        master=root,
        width=width,
        height=height,
        tile_size=tile_size,
        number_mines=number_mines
    )
    game.pack()


if __name__ == "__main__":
    root = tk.Tk()

    start_up()

    root.title("Main Menu")
    root.geometry("300x500")
    center_window(root, 300, 500)
    main_menu = MainMenu(root)
    main_menu.pack()

    root.mainloop()
