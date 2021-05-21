from logic import GameCanvas
from gui import SplashScreen, center_window
import multiprocessing
import tkinter as tk
import tkinter.ttk as ttk

import playsound
from PIL import ImageTk, Image
from ttkthemes import ThemedStyle


def play():
    while True:
        playsound.playsound('audio/Bubbles_and_Submarines.mp3')

class AudioGameTheme:

    def __init__(self):
        self.process = multiprocessing.Process(target=play)
        self.process.start()

    def stop(self):
        self.process.terminate()




class MainMenuGUI(tk.Tk):

    def __init__(self):
        super().__init__()
        # Splash screen
        self.withdraw()
        splash = SplashScreen(self)

        # Setting up the window
        self.title("Main Menu")
        icon_image = ImageTk.PhotoImage(Image.open('textures/title_bar_icon.png'))
        self.iconphoto(False, icon_image)
        self.geometry("300x500")
        center_window(self, 300, 500)

        # Setting up the style
        style = ThemedStyle(self)
        style.theme_use('arc')

        self.display_menu_content()

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
            GameCanvas(
                width=8,
                height=13,
                tile_size=50,
                number_mines=10
            )
        elif difficulty == "normal":  # Normal difficulty
            GameCanvas(
                width=13,
                height=15,
                tile_size=50,
                number_mines=40
            )
        elif difficulty == "hard":  # Hard difficulty
            GameCanvas(
                width=30,
                height=16,
                tile_size=35,
                number_mines=99
            )

        elif difficulty == "custom":  # Custom difficulty
            pass  # TODO: Choose your own difficulty


if __name__ == "__main__":
    main_menu = MainMenuGUI()
