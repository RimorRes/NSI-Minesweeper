"""
NSI-Minesweeper
Python Minesweeper game using Tkinter. This game is the final project for the NSI curriculum of 2020-2021.
Made by: Maxime Djmb, Ian McFarland

!!! To install the necessary modules use: pip install -r REQUIREMENTS.txt
"""

import threading
import tkinter as tk
import tkinter.ttk as ttk
from random import randint
import time
from tkinter import messagebox

import simpleaudio
from PIL import ImageTk, Image
from ttkthemes import ThemedStyle


def generate_mines(width, height, number_mines, excluded):
    mine_list = []  # init liste des mines

    while len(mine_list) < number_mines:
        x = randint(0, width - 1)
        y = randint(0, height - 1)
        pos = [x, y]  # position de la mine
        # on verifie que la position n'existe pas deja et qu'elle n'est pas dans la zone de depart protegee
        if pos not in mine_list and pos not in excluded:
            mine_list.append(pos)  # on enregistre la position

    return mine_list  # on renvoie la liste


def delimit_start_area(start_x, start_y, width, height, radius=1):
    area = []  # la zone de depart protegee (ou il n'y aura pas de mines)
    for vert in range(-radius, radius + 1):
        for horz in range(-radius, radius + 1):
            x = start_x + horz
            y = start_y + vert
            if (0 <= x < width) and (0 <= y < height):
                area.append([x, y])  # on explore toutes les positions dans un rayon autour de la pos de depart
    return area


def center_window(window, width, height):
    screen_width = window.winfo_screenwidth()
    screen_height = window.winfo_screenheight()
    x = (screen_width / 2) - (width / 2)
    y = (screen_height / 2) - (height / 2)

    window.geometry(f'+{int(x)}+{int(y)}')  # centrer la fenetre


def hide_frame(frame, sub_canvases=None):
    for widget in frame.winfo_children():
        widget.destroy()  # on supprime les enfants du cadre

    if sub_canvases:
        for canvas in sub_canvases:  # si le cadre a des canevas, on supprime tout ce qu'il y a dedans
            canvas.delete("all")

    frame.place_forget()  # pour cacher le cadre
    frame.pack_forget()  # pour cacher le cadre
    frame.grid_forget()  # pour cacher le cadre


class GameAudio:  # Controleur pour la musique

    def __init__(self):
        self.stop = False

        self.main_theme = simpleaudio.WaveObject.from_wave_file('audio/Waypoint_K.wav')
        self.sonar_ping = simpleaudio.WaveObject.from_wave_file('audio/sonar.wav')
        self.explosion = simpleaudio.WaveObject.from_wave_file('audio/explosion.wav')

        theme_thread = threading.Thread(target=self.theme_loop)
        theme_thread.name = "ThemeSFXThread"
        theme_thread.start()

        sonar_thread = threading.Thread(target=self.sonar_sfx)
        sonar_thread.name = "SonarSFXThread"
        sonar_thread.start()

    def theme_loop(self):
        while not self.stop:
            play = self.main_theme.play()
            play.wait_done()

    def sonar_sfx(self):
        while not self.stop:
            if randint(1, 20) == 1:
                play = self.sonar_ping.play()
                play.wait_done()
            else:
                time.sleep(1)

    def explosion_sfx(self):
        explo_thread = threading.Thread(target=self.explosion.play)
        explo_thread.name = 'ExplosionSFXThread'
        explo_thread.start()


class SplashScreen(tk.Toplevel):  # Ecran de chargement

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


class GameBoard(tk.Frame):

    def __init__(self, master, width, height, tile_size, number_mines):
        # Inheriting tk.Frame properties
        super().__init__(master, bd=40, relief='raised')

        # Init variables
        # TODO: Auto-scale board dimensions
        self.width, self.height = width, height  # game dimensions; columns and rows
        self.tile_size = tile_size  # tile dimensions
        self.number_mines = number_mines
        self.move_counter = 0
        
        # Setting up tile states
        self.tile_states = [[0] * self.width for _ in range(self.height)]  # matrix for number of adjacent mines
        self.mine_positions = []  # list of mine positions
        self.flag_positions = []  # list of flag positions
        self.discovered_tiles = []  # list of discovered tiles
        self.tripped_mine = []  # the mine the player exploded

        # Setting up the HUD on the top
        self.mine_label = tk.Label(self, text=f'Mines:{self.number_mines}') # display the number of mines
        self.mine_label.grid(row=0, column=0)

        self.restart_button = ttk.Button(self, text='Restart', command=self.restart)  # button for reset
        self.restart_button.grid(row=0, column=1)

        self.menu_button = ttk.Button(self, text='Menu', command=lambda: print('Lol. WIP'))  # return to menu
        self.menu_button.grid(row=2, column=1)

        self.stopwatch = 0  # time spent
        self.clock_label = tk.Label(self, text='') # to display the time spent
        self.clock_label.grid(row=0, column=2)
        self.update_clock() # update the clock

        # Setting up the canvas
        self.canvas = tk.Canvas(
            self,
            width=self.width * self.tile_size,
            height=self.height * self.tile_size,
            bd=-2
        )
        self.canvas.bind('<Button-1>', self.handle_left_click)  # Binding clicks to functions
        self.canvas.bind('<Button-3>', self.handle_right_click)
        self.canvas.grid(row=1, columnspan=3)

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

    def update_clock(self):
      t = round(self.stopwatch, 1)
      self.clock_label.configure(text=f'Time: {t}')
      self.stopwatch += 0.1
      self.clock_label.after(100, self.update_clock)

    def update_points(self):
      self.point_label.configure(text=self.points)
      self.point_label.after(100, self.update_points)

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

        self.check_win()

    def handle_right_click(self, event):
        x = event.x // self.tile_size
        y = event.y // self.tile_size

        if self.move_counter >= 1:
            self.toggle_flag(x, y)  # place/remove a flag

    def check_win(self):
        if self.tripped_mine:
            audio.explosion_sfx()
            self.game_over('lose')  # Defeat

        # If all tiles which aren't mines are discovered
        elif len(self.discovered_tiles) + self.number_mines == self.width * self.height:
            self.game_over('win')  # Victory

    def game_over(self, outcome):
        # game-over event according to outcome: either a win or a loss
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

        # Dialog box
        response = messagebox.askyesno('Game over!', f'You {outcome}! Do you want to try again?')
        # Restarting the game or quitting
        if response:
            self.restart()  # reset the game but keep the same settings
        else:
            on_closing()  # destroy the window

    def restart(self):
        # Resetting variables
        self.stopwatch = 0  # reset time spent
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
        # chaque case est initialise a 0. A chaque fois qu'une case a une mine adjacente, on incremente de 1
        for m in self.mine_positions:  # on itere toutes les mines
            x, y = m
            for vert in range(-1, 2):
                for horz in range(-1, 2):
                    if (0 <= x + horz < self.width) and (0 <= y + vert < self.height):  # verif coordonnees valides
                        self.tile_states[y + vert][x + horz] += 1  # on regarde dans un rayon de 1 autour de la mine

    def reveal_tiles(self, x, y):
        # Recursive function that allows the discovery of tiles
        if not [x, y] in self.discovered_tiles:  # si on a pas deja explore cette case...
            i = str(self.tile_states[y][x])
            self.place_tile(x, y, self.tile_images[i])  # ... on dessine sur le canevas
            self.discovered_tiles.append([x, y])  # ... et on ajoute la case aux cases decouvertes

            if self.tile_states[y][x] == 0:  # si la case n'a pas de mines a cote, on peut continuer d'ouvrir les cases
                for vert in range(-1, 2):
                    for horz in range(-1, 2):
                        if (0 <= x + horz < self.width) and (0 <= y + vert < self.height):  # verif coordonnees valides
                            if [x + horz, y + vert] not in self.discovered_tiles:  # verif case pas deja decouverte
                                self.reveal_tiles(x + horz, y + vert)  # on libere les cases dans un rayon de 1

        return

    def init_grid(self):
        # On initialise la grille
        for y in range(self.height):
            for x in range(self.width):
                self.place_tile(x, y, self.tile_images['tile'])

    def place_tile(self, x, y, img):
        # on transforme les x,y de la grille en coordonnees de pixel
        # on dessine au coordonnes l'image/la case que l'on souhaite
        self.canvas.create_image(x * self.tile_size, y * self.tile_size, anchor=tk.NW, image=img)


class MainMenu(tk.Frame):

    def __init__(self, master):
        # Inheriting tk.Frame properties
        super().__init__(master, height=500, width=500, bd=20, relief='raised')

        self.display_menu_content()

    def display_menu_content(self):
        play_label = tk.Label(self, text="Play", fg='green', font=('Terminal', 36, 'bold'))
        play_label.grid(padx=20, pady=20)

        # Defining the buttons and labels
        diff = tk.Label(self, text="Difficulty", font=('Terminal', 16))
        diff.grid(pady=5)

        easy = ttk.Button(self, text="Easy", command=lambda: set_difficulty("easy"))  # Easy mode button
        easy.grid(pady=5)
        medium = ttk.Button(self, text="Normal", command=lambda: set_difficulty("normal"))  # Normal mode button
        medium.grid(pady=5)
        hard = ttk.Button(self, text="Hard", command=lambda: set_difficulty("hard"))  # Hard mode button
        hard.grid(pady=5)

        # Custom difficulty
        # TODO: finish the custom difficulty
        label = tk.Label(self, text="Custom difficulty")
        label.grid(pady=20)
        number = tk.Label(self, text="Enter a Number between 10 and 100")
        number.grid()
        box = ttk.Entry(self)
        box.grid(pady=10)
        button = ttk.Button(self, text="Confirm number")
        button.grid(pady=20)


def start_up():
    root.withdraw()  # hide the main window when loading
    splash = SplashScreen(root)  # display splash screen

    # resize and center window
    root.geometry(f"{1280}x{720}")
    center_window(root, 1280, 720)

    # Setting up the main window
    root.protocol("WM_DELETE_WINDOW", on_closing)
    icon_image = ImageTk.PhotoImage(Image.open('textures/title_bar_icon.png'))
    root.iconphoto(False, icon_image)  # window icon

    # Tk Style
    style = ThemedStyle(root)
    style.theme_use('arc')

    # End of loading. Maximize main window
    splash.destroy()
    root.deiconify()


def on_closing():
    audio.stop = True
    simpleaudio.stop_all()
    root.destroy()


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
    hide_frame(main_menu)  # hide the menu frame

    root.title("Minesweeper")

    game = GameBoard(  # create a new game with the specified settings
        master=root,
        width=width,
        height=height,
        tile_size=tile_size,
        number_mines=number_mines
    )
    game.place(relx=0.5, rely=0.5, anchor=tk.CENTER)


if __name__ == "__main__":
    # init the main window
    root = tk.Tk()

    # import and place background image
    bg_img = ImageTk.PhotoImage(Image.open('textures/background.png'))
    background_label = tk.Label(root, image=bg_img)
    background_label.place(x=0, y=0, relwidth=1, relheight=1)

    start_up()  # booting up
    audio = GameAudio()  # start audio loop

    # display the menu
    root.title("Main Menu")
    main_menu = MainMenu(root)
    main_menu.place(relx=0.5, rely=0.5, anchor=tk.CENTER)

    root.mainloop()
