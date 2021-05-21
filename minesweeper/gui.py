import tkinter as tk
from PIL import Image


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


class SplashScreen(tk.Toplevel):

    def __init__(self, master):
        super().__init__(master)

        # Setting up the window
        self.title("Minesweeper Splash Screen")
        self.overrideredirect(True)
        self.geometry('640x360')
        center_window(self, 640, 360)

        # Importing each frame of the .gif
        file_name = '../textures/splash_screen.gif'
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
