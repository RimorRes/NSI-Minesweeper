import random
import tkinter as tk
from PIL import ImageTk, Image


def generate_mines(excluded):
    mine_list = []

    while len(mine_list) < 10:
        x = random.randint(0, 7)
        y = random.randint(0, 12)
        pos = [x, y]
        if pos not in mine_list and pos != excluded:
            mine_list.append(pos)

    return mine_list


class Game(tk.Frame):

    def __init__(self, master):
        super().__init__()
        self.master = master
        self.master.title("Minesweeper")
        self.pack(side=tk.BOTTOM)

        self.canvas = tk.Canvas(self, width=400+4, height=650+4)
        self.canvas.bind('<Button-1>', self.handle_left_click)
        self.canvas.bind('<Button-3>', self.handle_right_click)
        self.canvas.pack()

        self.move_counter = 0

        self.tile_img = ImageTk.PhotoImage(Image.open("textures/Tile.png").resize((50, 50)))
        self.flag_img = ImageTk.PhotoImage(Image.open("textures/Flag.png").resize((50, 50)))
        self.bomb_img = ImageTk.PhotoImage(Image.open("textures/Bomb.png").resize((50, 50)))
        self.empty_img = ImageTk.PhotoImage(Image.open("textures/Empty.png").resize((50, 50)))
        self.init_grid()

    def handle_left_click(self, event):
        print("Left-click!", event.x // 50, event.y // 50)
        self.move_counter += 1

        if self.move_counter == 1:
            self.mine_positions = generate_mines([event.x // 50, event.y // 50])

        if [event.x // 50, event.y // 50] in self.mine_positions:
            self.place_tile(event.x // 50, event.y // 50, self.bomb_img)

        else:
            self.place_tile(event.x // 50, event.y // 50, self.empty_img)


    def handle_right_click(self, event):
        print("Right-click!", event.x // 50, event.y // 50)

        if self.move_counter >= 1:
            self.place_tile(event.x // 50, event.y // 50, self.flag_img)

    def init_grid(self):
        for y in range(13):
            for x in range(8):
                self.canvas.create_image(x * 50 + 2, y * 50 + 2, anchor=tk.NW, image=self.tile_img)

    def place_tile(self, x, y, img):
        self.canvas.create_image(x * 50 + 2, y * 50 + 2, anchor=tk.NW, image=img)


if __name__ == "__main__":
    root = tk.Tk()
    root.geometry("480x720")
    game = Game(root)
    root.mainloop()
