import pygame
import random
from settings import *
import bisect
from grid_element import *
vec = pygame.math.Vector2


class Enemy:
    def __init__(self, logic, pos, number, screen):
        self.logic = logic
        self.grid_pos = pos                         #influences direction
        self.starting_pos = [pos.x, pos.y]          #list of start pos for later resetting
        self.pix_pos = self.get_pix_pos()
        self.number = number                        #influences personality
        self.direction = vec(0, 0)                  #influences pixpos
        self.personality = self.set_personality()   #gives enemy a personality which influences move function
        self.target = None
        self.speed = self.set_speed()               #gives enemy speed according to personality
        self.screen = screen

    def update(self):
        self.target = self.set_target()                     #set target per personality
        if self.target != self.grid_pos:                    #
            self.pix_pos += self.direction * self.speed     #position will move in a direction with a speed
            if self.time_to_move():                         #if you are in the center of a cell
                self.move()                                 #move

        self.grid_pos[0] = (self.pix_pos[0]-TOP_BOTTOM_BUFFER +
                            self.logic.cell_width//2)//self.logic.cell_width+1      #given pix pos set grid pos x
        self.grid_pos[1] = (self.pix_pos[1]-TOP_BOTTOM_BUFFER +
                            self.logic.cell_height//2)//self.logic.cell_height+1    #given pix pos set grid pos y

    def draw(self):
        image = pygame.image.load('sharky.png').convert_alpha()
        image = pygame.transform.scale(image, (20, 20))
        self.screen.blit(image, (int(self.pix_pos.x) - 10, int(self.pix_pos.y) - 10))

    def set_speed(self):
        if self.personality in ["speedy", "scared"]:
            speed = 2
        else:           #slow gets different speed
            speed = 1
        return speed

    def set_target(self):
        if self.personality == "speedy" or self.personality == "slow":      #different speed but same target
            return self.logic.player.grid_pos                               #vector of the players position
        else:                                                               # scared enemy should go exactly to opposite directoin
            if self.logic.player.grid_pos[0] > COLS//2 and self.logic.player.grid_pos[1] > ROWS//2:
                return vec(1, 1)        #if the player is on right side and below, target is left top of grid
            if self.logic.player.grid_pos[0] > COLS//2 and self.logic.player.grid_pos[1] < ROWS//2:
                return vec(1, ROWS-2)   #if the player is right and up, go to, target is top right
            if self.logic.player.grid_pos[0] < COLS//2 and self.logic.player.grid_pos[1] > ROWS//2:
                return vec(COLS-2, 1)   # if the player is left and below, target is bottom right
            else:                       #if the player is left and up, bottom right
                return vec(COLS-2, ROWS-2)

    def time_to_move(self):
        if int(self.pix_pos.x+TOP_BOTTOM_BUFFER//2) % self.logic.cell_width == 0:
            if self.direction == vec(1, 0) or self.direction == vec(-1, 0) or self.direction == vec(0, 0):
                return True     #if the x position is in the middle of the cell and  you are going left or right
        if int(self.pix_pos.y+TOP_BOTTOM_BUFFER//2) % self.logic.cell_height == 0:
            if self.direction == vec(0, 1) or self.direction == vec(0, -1) or self.direction == vec(0, 0):
                return True     #if the y position is in the middle of the cell and you are going up or down
        return False

    def move(self):
        if self.personality == "random":
            self.direction = self.get_random_direction()            #give it random direction
        if self.personality == "slow":
            self.direction = self.get_path_direction(self.target)
        if self.personality == "speedy":
            self.direction = self.get_path_direction(self.target)
        if self.personality == "scared":
            self.direction = self.get_path_direction(self.target)

    def get_path_direction(self, target):
        next_cell = self.find_next_cell_in_path(target)     #
        xdir = next_cell[0] - self.grid_pos[0]              #set x direction
        ydir = next_cell[1] - self.grid_pos[1]              #set y direction
        return vec(xdir, ydir)                              #return total direction


    def get_score(self, score):
        self.score = score

    def manhattan_distance(self, cell, other):
        x_distance = abs(cell[0] - other[0])
        y_distance = abs(cell[1] - other[1])
        return x_distance + y_distance

    # def find_next_cell_in_path(self, target):
    #     path = self.greedy_search([int(self.grid_pos.x), int(self.grid_pos.y)], [
    #                     int(target[0]), int(target[1])])
    #     return path[1]

    def greedy_search(self, start, target):
        grid = [[0 for x in range(28)] for x in range(30)]
        for cell in self.logic.walls:
            if cell.x < 28 and cell.y < 30:
                grid[int(cell.y)][int(cell.x)] = 1
        start = Gridelement(start, self.manhattan_distance(start, target))
        target = Gridelement(target, self.manhattan_distance(target, target))
        queue = [start]
        path = []
        visited = []

        while queue:
            current = queue[0]
            queue.remove(queue[0])
            visited.append(current)
            if current == target:
                break
            else:
                neighbours = [[0, -1], [1, 0], [0, 1], [-1, 0]]
                # if current not in visited:
                #     visited.append(current)
                for neighbour in neighbours:
                    if neighbour[0] + current.grid_pos[0] >= 0 and neighbour[0] + current.grid_pos[0] < len(grid[0]):
                        if neighbour[1] + current.grid_pos[1] >= 0 and neighbour[1] + current.grid_pos[1] < len(grid):
                            next_cell = [neighbour[0] + current.grid_pos[0], neighbour[1] + current.grid_pos[1]]
                            next_cell = Gridelement(next_cell, self.manhattan_distance(next_cell, target.grid_pos))
                            if next_cell not in visited:
                                if grid[next_cell.grid_pos[1]][next_cell.grid_pos[0]] != 1:
                                    queue.append(next_cell)
                                    path.append({"Current": current, "Next": next_cell})
                                    # gscore = self.manhattan_distance(next_cell, target)
                                    # next_cell.get_score(gscore)
                                    bisect.insort(queue, next_cell)

        # print("The number of visited nodes is: {}".format(len(visited)))
        shortest = [target]
        while target != start:
            for step in path:
                if step["Next"] == target:
                    target = step["Current"]
                    shortest.insert(0, step["Current"])
        return shortest


    def find_next_cell_in_path(self, target):
         path = self.greedy_search([int(self.grid_pos.x), int(self.grid_pos.y)], [
                         int(target[0]), int(target[1])]) #startingpoint is pos of player and target (pos of player)
         return path[1].grid_pos                                   # first cell is where we are, second is where we want to go

############################# FIRST BSF, NOW GREEDY  #############################################################

    # def BFS(self, start, target):
    #     grid = [[0 for x in range(28)] for x in range(30)] #grid to look through (maze grid)
    #     for cell in self.logic.walls:                      #look through all walls
    #         if cell.x < 28 and cell.y < 30:                #if it is in the grid
    #             grid[int(cell.y)][int(cell.x)] = 1         #then it is a wall
    #     queue = [start]                                     #list with start pos
    #     path = []                                           #path list
    #     visited = []                                        #visited list
    #     while queue:                                        #while queue isnt empty
    #         current = queue[0]                              #cell we want to look at is first in first out
    #         queue.remove(queue[0])                          #remove cell from queue
    #         visited.append(current)                         #add it to the visited queue
    #         if current == target:                           #if you have reached the target
    #             break
    #         else:
    #             neighbours = [[0, -1], [1, 0], [0, 1], [-1, 0]]     #these are the neighbours of the current node
    #             for neighbour in neighbours:                        #for each neigbour in this list
    #                 if neighbour[0]+current[0] >= 0 and neighbour[0] + current[0] < len(grid[0]): #if nextcell pos is not out of bounds
    #                     if neighbour[1]+current[1] >= 0 and neighbour[1] + current[1] < len(grid):
    #                         next_cell = [neighbour[0] + current[0], neighbour[1] + current[1]]      #nextcell gets these coordinates
    #                         if next_cell not in visited:    #if it hasn not been visited yet
    #                             if grid[next_cell[1]][next_cell[0]] != 1:   #check if it is not a wall
    #                                 queue.append(next_cell)                 #put the cell in the queue
    #                                 path.append({"Current": current, "Next": next_cell}) #path is appended with cell
    #     shortest = [target]     #equals list with target in it
    #     while target != start:  #if the target is not equal to the start (still not discovered everything)
    #         for step in path:   #loop through the whole path
    #             if step["Next"] == target:  #if the next cell is the target
    #                 target = step["Current"]  #then the target equals the step current
    #                 shortest.insert(0, step["Current"]) #insert it in the correct order
    #     return shortest

    def get_random_direction(self):
        while True:                         #if we hit a wall we still need new random direction
            number = random.randint(-2, 1)
            if number == -2:
                x_dir, y_dir = 1, 0         #go left
            elif number == -1:
                x_dir, y_dir = 0, 1         #
            elif number == 0:
                x_dir, y_dir = -1, 0        #
            else:
                x_dir, y_dir = 0, -1
            next_pos = vec(self.grid_pos.x + x_dir, self.grid_pos.y + y_dir)    #look what it's next position will be
            if next_pos not in self.logic.walls:                                #if it is not a wall
                break
        return vec(x_dir, y_dir)                                                #pass this direction

    def get_pix_pos(self):          #returns vector with pixel position
        return vec((self.grid_pos.x*self.logic.cell_width)+TOP_BOTTOM_BUFFER//2+self.logic.cell_width//2,
                   (self.grid_pos.y*self.logic.cell_height)+TOP_BOTTOM_BUFFER//2 +
                   self.logic.cell_height//2)

    def set_personality(self):      #look at idx number
        if self.number == 0:
            return "speedy"
        elif self.number == 1:
            return "slow"
        elif self.number == 2:
            return "random"
        else:
            return "scared"
