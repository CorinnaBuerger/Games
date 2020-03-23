import pygame as pg
import random
import sys
import tkinter as tk
from tkinter import messagebox
import time

print("Select the size:")
print("Small = 10 x 10 cells with 10 bombs")
print("Medium = 15 x 15 cells with 20 bombs")
print("Large = 20 x 20 cells with 35 bombs")
size = input()
if size == "small" or size == "Small":
    height = 400 # height and width of the screen
    grid = 10 # rows and columns
    start_num_mines = 10
if size == "medium" or size == "Medium":
    height = 650 # height and width of the screen
    grid = 15 # rows and columns
    start_num_mines = 20
if size == "large" or size == "Large":
    height = 800 # height and width of the screen
    grid = 20 # rows and columns
    start_num_mines = 35

square_size = height // grid
cells_around = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)] # contains the positions of the cells around my cell
matrix = []
cell_selected = []

pg.init()
clock = pg.time.Clock()
screen = pg.display.set_mode([height, height]) # creates the screen of the game

# loads all images into the game:
def load_images(adress, square_size = square_size):
    return pg.transform.scale(pg.image.load(adress), (square_size, square_size))


class Cell():
    def __init__(self, row, column):
        self.row : int = row
        self.column : int = column
        self.mine : bool = False
        self.selected : bool = False
        self.flagged : bool = False
        self.num_mines_around : int = 0
        self.cell_normal = load_images(r'C:\Users\Corinna\Documents\python_coding\minesweeper\normal_cell.gif')
        self.cell_marked = load_images(r'C:\Users\Corinna\Documents\python_coding\minesweeper\marked_cell.gif')
        self.cell_mine = load_images(r'C:\Users\Corinna\Documents\python_coding\minesweeper\mine_cell.gif')
    
    def show(self):
        global cell_selected
        global matrix
        for n in range(9):
            cell_selected.append(load_images('C:\\Users\\Corinna\\Documents\\python_coding\\minesweeper\\ms_cell_{}.gif'.format(n)))
        pos = (self.column*square_size, self.row*square_size)
        if self.selected:
            if self.mine:
                screen.blit(self.cell_mine, pos)
            else:
                screen.blit(cell_selected[self.num_mines_around], pos)
        else:
            if self.flagged:
                screen.blit(self.cell_marked, pos)
            else:
                screen.blit(self.cell_normal, pos)

    def get_num_of_mines_around(self):
        global matrix
        global cells_around
        for pos in cells_around:
            new_row, new_column = self.row + pos[0], self.column + pos[1]
            if new_row >= 0 and new_row < grid and new_column >= 0 and new_column < grid:
                if matrix[new_row*grid + new_column].mine == True:
                    self.num_mines_around += 1

    def reset(self):
        global matrix
        self.selected = False
        self.flagged = False
        self.mine = False
        self.num_mines_around = 0

                    
# fills the matrix of the screen with cells:
def fill_matrix(matrix):
    for n in range(grid*grid):
        matrix.append(Cell(n // grid, n % grid))
    return matrix

# distributes the bombs on the grid:
def distribute_bombs(num_mines, matrix):
    while num_mines > 0:
        x = random.randrange(grid*grid)
        if matrix[x].mine == False:
            matrix[x].mine = True
            num_mines -= 1

# gets the number of bombs surrounding a certain cell:
def counting_surrounding_bombs(matrix):
    for obj in matrix:
        if obj.mine == False:
            obj.get_num_of_mines_around()

def all_cells_selected(matrix):
    any_not_selected = True
    for obj in matrix:
        if not obj.mine and not obj.selected:
            any_not_selected = False

    return any_not_selected

# automatically selects all cells with no surrounding bombs surrounding a selected cell with no surrounding bombs
def floodfill(row, column, matrix):
    global cells_around
    for pos in cells_around:
        new_row = row + pos[0]
        new_column = column + pos[1]
        if new_row >= 0 and new_row < grid and new_column >= 0 and new_column < grid:
            if matrix[new_row*grid + new_column].num_mines_around == 0 and not matrix[new_row*grid + new_column].selected:
               matrix[new_row*grid + new_column].selected = True
               floodfill(new_row, new_column, matrix)
            else:
                matrix[new_row*grid + new_column].selected = True

def message_box(subject, content):
    root = tk.Tk()
    root.attributes("-topmost", True)
    root.withdraw()
    messagebox.showinfo(subject, content)
    try:
        root.destroy()
    except:
        pass

def restart(matrix):
    distribute_bombs(start_num_mines, matrix)
    counting_surrounding_bombs(matrix)
    play(matrix)

def update_screen(matrix):
    for obj in matrix:
        obj.show()
    pg.display.flip() # updates the full display surface to the screen

def convert_millis(millis):
    seconds =  round((millis / 1000) % 60)
    minutes = round((millis / (1000*60)) % 60)
    time = "{} minutes and {} seconds".format(minutes, seconds)
    print(millis)
    print(minutes)
    print(seconds)
    return time


def play(matrix):
    play = True
    start_time = pg.time.get_ticks()
    while play:
        for event in pg.event.get():
            if event.type == pg.QUIT:
                play = False
            if event.type == pg.MOUSEBUTTONDOWN:
                mouseX, mouseY = pg.mouse.get_pos()
                clicked_column = mouseX // square_size
                clicked_row = mouseY // square_size
                i = clicked_row*grid + clicked_column
                clicked_cell = matrix[i]
                if pg.mouse.get_pressed()[2]: # right click
                    clicked_cell.flagged = not clicked_cell.flagged # if clicked_cell.flagged == False (default), it will be Not-False -> True and the other way around
                if pg.mouse.get_pressed()[0]: # left click ([1] is the middle)
                    clicked_cell.selected = True
                    if clicked_cell.num_mines_around == 0 and clicked_cell.mine == False:
                        floodfill(clicked_row, clicked_column, matrix)
                    if clicked_cell.mine: # in case I lose
                        print("BOMB!")
                        for obj in matrix:
                            obj.selected = True # show all cells
                        update_screen(matrix)
                        millis_since_play = pg.time.get_ticks() - start_time
                        tk.messagebox.showinfo(message = "Oh no! You totally fucked up in {}.".format(convert_millis(millis_since_play)))
                        message_box("You lost!", "Play again")
                        update_screen(matrix)
                        for obj in matrix:
                            obj.reset()
                        restart(matrix)
                        break
                    if all_cells_selected(matrix): # in case I win
                        update_screen(matrix)
                        millis_since_play = pg.time.get_ticks() - start_time
                        tk.messagebox.showinfo(message = "Congrats! This little challenge only took you {}.".format(convert_millis(millis_since_play)))
                        message_box("You won!", "Play again")
                        for obj in matrix:
                            obj.reset()
                        restart(matrix)
        update_screen(matrix) 
    pg.quit()

def main(matrix):
    matrix = fill_matrix(matrix)
    distribute_bombs(start_num_mines, matrix)
    counting_surrounding_bombs(matrix)
    play(matrix)

if __name__ == "__main__":
    main(matrix)

# TODO(coco): save high score in a file (with name, time, field size, # of bombs)
