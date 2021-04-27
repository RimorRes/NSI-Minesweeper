import random
import tkinter as tk


class GameFrame(tk.Frame):

    def __init__(self, master):
        super().__init__()
        self.master = master
        self.master.title("Minesweeper")
        self.pack()

        self.canvas = tk.Canvas(self, width=400, height=650)
        self.canvas.pack()

        self.draw_grid()

    def draw_grid(self):
        for vert in range(9):
            self.canvas.create_line(vert*50, 0, vert*50, 13*50)
        for horz in range(14):
            self.canvas.create_line(0, horz*50, 8*50, horz*50)

def mines():
    minelist = []
    counter = 0

    while len(minelist) < 10:
        x = random.randint(0, 7)
        y = random.randint(0, 12)
        pos = [x, y]
        minelist.append(pos)
        counter += 1
        print(minelist)

        for i in range(len(minelist)-1):
            if pos == minelist[i]:
                minelist.remove[i]


if __name__ == "__main__":
    root = tk.Tk()
    game = GameFrame(root)
    root.mainloop()
