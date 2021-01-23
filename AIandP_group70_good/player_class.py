import pygame
from settings import *
vec = pygame.math.Vector2


class Player:
    def __init__(self, logic, pos, screen):
        self.logic = logic
        self.starting_pos = [pos.x, pos.y]              #list of starting pos for later resetting
        self.grid_pos = pos                             #for moving through cells
        #for fluent movement, move in pixels instead of cells
        self.pix_pos = self.get_pix_pos()               #for moving through pixels, relative to grid
        self.direction = vec(1, 0)
        self.stored_direction = None
        self.able_to_move = True                        #compare to can_move
        self.current_score = 0
        self.speed = 2
        self.lives = 3
        self.screen = screen

    def update(self):
        if self.able_to_move:                              #if you are able to move (can_move)
            self.pix_pos += self.direction*self.speed       #go in this directoin
        if self.time_to_move():                             #if you are in the center of cell
            if self.stored_direction != None:               #if you are moving
                self.direction = self.stored_direction      #store direction in self.direction
            self.able_to_move = self.can_move()
        # Setting grid position in reference to pix pos
        self.grid_pos[0] = (self.pix_pos[0]-TOP_BOTTOM_BUFFER +
                            self.logic.cell_width//2)//self.logic.cell_width+1
        self.grid_pos[1] = (self.pix_pos[1]-TOP_BOTTOM_BUFFER +
                            self.logic.cell_height//2)//self.logic.cell_height+1
        if self.grid_pos in self.logic.foods:       #if current position has food
            self.logic.foods.remove(self.grid_pos)  # from the foods list, remove the coin with corresponding vec
            self.current_score += 1                 # update score

    def draw(self):
        image = pygame.image.load('crab.png').convert_alpha()
        image = pygame.transform.scale(image, (20, 20))
        self.screen.blit(image, (int(self.pix_pos.x)-10, int(self.pix_pos.y)-10))

        # Drawing player lives
        for x in range(self.lives):
            self.screen.blit(image, (30 + 20*x, HEIGHT - 22))

    def move(self, direction):
        self.stored_direction = direction

    def get_pix_pos(self):
        return vec((self.grid_pos[0]*self.logic.cell_width)+TOP_BOTTOM_BUFFER//2+self.logic.cell_width//2,
                   (self.grid_pos[1]*self.logic.cell_height) +
                   TOP_BOTTOM_BUFFER//2+self.logic.cell_height//2)


    def time_to_move(self):
        if int(self.pix_pos.x+TOP_BOTTOM_BUFFER//2) % self.logic.cell_width == 0:
            if self.direction == vec(1, 0) or self.direction == vec(-1, 0) or self.direction == vec(0, 0):
                return True
        if int(self.pix_pos.y+TOP_BOTTOM_BUFFER//2) % self.logic.cell_height == 0:
            if self.direction == vec(0, 1) or self.direction == vec(0, -1) or self.direction == vec(0, 0):
                return True

    def can_move(self):                                             #checks if there is a wall
        for wall in self.logic.walls:
            if vec(self.grid_pos+self.direction) == wall:           #if the direction you are goint equals wall
                return False                                        #you cannot move
        return True
