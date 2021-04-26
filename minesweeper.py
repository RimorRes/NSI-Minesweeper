import tkinter 

def create_grid(event=None):
    width = c.winfo_width() # Getting current width of canvas
    height = c.winfo_height() # Getting current height of canvas
    c.delete('grid_line') # Will only remove the grid_line

    # Creates all vertical lines at intevals of 100
    for i in range(0, width, 80):
        c.create_line([(i, 0), (i, height)], tag='grid_line')

    # Creates all horizontal lines at intevals of 100
    for i in range(0, height, 80):
        c.create_line([(0, i), (width, i)], tag='grid_line')

#Initializing the window
window = tkinter.Tk()

#Giving the window a title
window.title('Minesweeper')

#Creating a window of size 600x1000 having yellow background color
c = tkinter.Canvas(window,bg='yellow')

#maximizing the window
window.state('zoomed')

c.pack(fill=tkinter.BOTH, expand=True)

c.bind('<Configure>', create_grid)

window.mainloop()
