import math
import random
import pygame
import tkinter as tk
from tkinter import messagebox

class Cube(object):
    def __init__(self, start, rows = 20, width = 500, dirnx = 1, dirny = 0, color = (255, 0, 0)):
        self.pos = start
        self.dirnx = 1 # snake starts moving from beginning without needing a key to be clicked
        self.dirny = 0
        self.color = color
        self.rows = rows
        self.width = width

    def move(self, dirnx, dirny):
        self.dirnx = dirnx
        self.dirny = dirny
        self.pos = (self.pos[0] + self.dirnx, self.pos[1] + self.dirny)

    def draw(self, surface, eyes = False):
        dis = self.width // self.rows # gives us the size of the squares in the grid
        i = self.pos[0] # row
        j = self.pos[1] # column

        pygame.draw.rect(surface, self.color, (i*dis + 1, j*dis + 1, dis-2, dis-2)) # we need -2 for not drawing over the boundaries of the square
        if eyes:
            centre = dis//2
            radius = 3
            circleMiddle = (i*dis + centre - radius, j*dis + 8)
            circleMiddle2 = (i*dis + dis - radius*2, j*dis + 8)
            pygame.draw.circle(surface, (0,0,0), circleMiddle, radius)
            pygame.draw.circle(surface, (0,0,0), circleMiddle2, radius)

class Snake(object):
    body = []
    turns = {}
    def __init__(self, color, pos, rows, width):
        # initialize game music (.mp3 files must be loaded individually before playing them)
        pygame.mixer.init()

        # initialize class attributes
        self.color = color
        self.head = Cube(pos, 20, 500)
        self.body.append(self.head)
        # gives the direction the snake is moving; if x = 1/-1 then y = 0 (!) and the other way around
        self.dirnx = 0
        self.dirny = 1
        self.rows = rows
        self.width = width
        

    def move(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()

            keys = pygame.key.get_pressed()
        
            for key in keys:
                if keys[pygame.K_LEFT]:
                    self.dirnx = -1
                    self.dirny = 0
                    self.turns[self.head.pos[:]] = [self.dirnx, self.dirny] # adds the new position (self.dirnx, self.dirny) of our head to turns

                elif keys[pygame.K_RIGHT]:
                    self.dirnx = 1
                    self.dirny = 0
                    self.turns[self.head.pos[:]] = [self.dirnx, self.dirny]

                elif keys[pygame.K_UP]:
                    self.dirnx = 0
                    self.dirny = -1 # in pygame y = -1 means that you go up
                    self.turns[self.head.pos[:]] = [self.dirnx, self.dirny]

                elif keys[pygame.K_DOWN]:
                    self.dirnx = 0
                    self.dirny = 1
                    self.turns[self.head.pos[:]] = [self.dirnx, self.dirny]

        # moves our cube:
        for i, c in enumerate(self.body):
            position = c.pos[ : ]
            if position in self.turns:
                turn = self.turns[position]
                c.move(turn[0], turn[1])
                if i == len(self.body) - 1:
                    self.turns.pop(position)
            else:
                # if the snake leaves the left screen, it enters from the right screen
                if c.dirnx == -1 and c.pos[0] <= 0:
                    c.pos = (c.rows-1, c.pos[1])
                elif c.dirnx == 1 and c.pos[0] >= c.rows-1:
                    c.pos = (0, c.pos[1])
                elif c.dirny == 1 and c.pos[1] >= c.rows-1:
                    c.pos = (c.pos[0], 0)
                elif c.dirny == -1 and c.pos[1] <= 0:
                    c.pos = (c.pos[0], c.rows-1)
                else:
                    c.move(c.dirnx, c.dirny)

    def slurp(self):
        pygame.mixer.music.load("slurp.mp3")
        pygame.mixer.music.play()

    def fail(self):
        pygame.mixer.music.load("fail.mp3")
        pygame.mixer.music.play()
            
    def reset(self, pos):
        self.head = Cube(pos)
        self.body = []
        self.body.append(self.head)
        self.turns = {}
        self.dirnx = 0
        self.dirny = 1
        

    def addCube(self):
        tail = self.body[-1] # the tail is the last item in our list
        dx, dy = tail.dirnx, tail.dirny

        # checks where the tail is moving and adds the new cube at its end:
        if dx == 1 and dy == 0:
            self.body.append(Cube((tail.pos[0]-1, tail.pos[1]))) # adds the cube on the left
        elif dx == -1 and dy == 0:
            self.body.append(Cube((tail.pos[0]+1, tail.pos[1]))) # adds the cube on the right
        elif dx == 0 and dy == 1:
            self.body.append(Cube((tail.pos[0], tail.pos[1]-1))) # adds the cube above
        elif dx == 0 and dy == -1:
            self.body.append(Cube((tail.pos[0], tail.pos[1]+1))) # adds the cube below

        # makes sure that the new tail moves in the same direction
        self.body[-1].dirnx = dx
        self.body[-1].dirny = dy

    def draw(self, surface):
        for i, c in enumerate(self.body):
            if i == 0:
                # adding some eyes to the head of the snake
                c.draw(surface, True)
            else:
                # for the rest of the cubes eyes is False by default
                c.draw(surface)


def draw_grid(width, surface):
    rows = 20
    size_between = width // rows 

    x = 0
    y = 0
    for l in range(rows):
        x = x + size_between
        y = y + size_between

        pygame.draw.line(surface, (255, 255, 255), (x, 0), (x, width)) # draws a white vertical line starting at (x, 0) and ending at (x, w)
        pygame.draw.line(surface, (255, 255, 255), (0, y), (width, y)) # draws a white horizontal line
    

def redraw_window(surface):
    global s, snack
    width = 500
    surface.fill((0, 0, 0))
    s.draw(surface)
    snack.draw(surface)
    draw_grid(width, surface)
    pygame.display.update()
    

def random_snack(rows, item):
    positions = item.body

    while True:
        x = random.randrange(rows)
        y = random.randrange(rows)
        # makes sure that we don't put a snack on top of the snake:
        if len(list(filter(lambda z: z.pos == (x,y) , positions ))) > 0:
            continue # if the snack is generated on the snake, we do this again
        else:
            break

    return (x,y)



def message_box(subject, content):
    root = tk.Tk()
    root.attributes("-topmost", True)
    root.withdraw()
    messagebox.showinfo(subject, content)
    try:
        root.destroy()
    except:
        pass

def main():
    global s, snack
    w = 500
    win = pygame.display.set_mode(size = (w, w))

    # creates a red snake, which starts at the position 10, 10:
    s = Snake((255, 0, 0), (10, 10), 20, 500) 
    # generates a new snack
    snack = Cube(random_snack(20, s), color = (0, 255, 0))
    # creates our main loop:
    flag = True

    clock = pygame.time.Clock()

    while flag:
        pygame.time.delay(40) # slows down our snake (the higher, the slower our snake will be)
        clock.tick(10)        # the higher, the faster our snake will be
        s.move()
        if s.body[0].pos == snack.pos:
            s.slurp() # play slurping sound
            s.addCube()
            snack = Cube(random_snack(20, s), color = (0, 255, 0))
        
        # checks if there is a collision
        for x in range(len(s.body)):
            if s.body[x].pos in list(map(lambda z: z.pos, s.body[x+1:])):
                print("Score: " + str(len(s.body)))
                s.fail()
                message_box("You Lost!", "Play again!")
                s.reset((10, 10))
                break

        redraw_window(win)
    pass

if __name__ == "__main__":

    main()