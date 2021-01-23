# this class has all the logic of the game, calls player and enemy

import pygame
import sys
import copy
from settings import *
from player_class import *
from enemy_class import *
from detection import *
import cv2
import keyboard
from detection import *


pygame.init()

#vector for speed en direction
vec = pygame.math.Vector2


class Logic:
    def __init__(self):
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        #to time the intro
        self.clock = pygame.time.Clock()
        self.running = True
        self.state = 'start'
        self.cell_width = MAZE_WIDTH//COLS
        self.cell_height = MAZE_HEIGHT//ROWS
        self.walls = []
        self.foods = []
        self.enemies = []                                           #holds enemies
        self.e_pos = []                                             #position for different enemies
        self.p_pos = None                                           #player start position defined in load
        self.load()
        self.player = Player(self, vec(self.p_pos), self.screen)
        self.make_enemies()
        self.detection = Detection
        self.faceCascade = cv2.CascadeClassifier('haarcascade_frontalface_default.xml')
        self.video_capture = cv2.VideoCapture(0)
        self.width = self.video_capture.get(3)  # float
        self.height = self.video_capture.get(4)  # float
        self.press_flag = False
        self.cmd = ""
        self.detection = Detection()
        self.side = None


    def get_nose(self):
        #while True:
        # Reading image from video stream
        _, img = self.video_capture.read()
        img = cv2.flip(img, 1)

        # detect nose and draw
        img, nose_cords = self.detection.detect_nose(img, self.faceCascade)
        cv2.putText(img, self.cmd, (10, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, RED, 1, cv2.LINE_AA)

        # draw boundary circle
        cords = self.detection.draw_controller(img, (int(self.width / 2), int(self.height // 2)))
        if self.press_flag and len(nose_cords):
            img, cmd = self.detection.keyboard_events(img, nose_cords, cords, self.cmd)
            self.side = cmd
        self.press_flag, cmd = self.detection.reset_press_flag(nose_cords, cords, self.cmd)

        # Writing processed image in a new window
        cv2.imshow("face detection", img)
        # if cv2.waitKey(1) & 0xFF == ord('q'):
        #     break

        # releasing web-cam
        # self.video_capture.release()
        # # Destroying output window
        # cv2.destroyAllWindows()
        return self.side


    def run(self):
        while self.running:
            if self.state == 'start':
                self.start_events()
                self.start_update()
                self.start_draw()
            elif self.state == 'playing':
                self.playing_events()
                self.playing_update()
                self.playing_draw()
                self.get_nose()
            elif self.state == 'game over':
                self.game_over_events()
                self.game_over_update()
                self.game_over_draw()
            else:
                self.running = False
            self.clock.tick(FPS)
        pygame.quit()
        sys.exit()

############################ HELPER FUNCTIONS ##################################

    def draw_text(self, words, screen, pos, size, colour, font_name):
        font = pygame.font.SysFont(font_name, size)
        text = font.render(words, False, colour)
        text_size = text.get_size()
        #to center the text

        pos[0] = pos[0]-text_size[0]//2
        pos[1] = pos[1]-text_size[1]//2
        screen.blit(text, pos)

    #load in background in here so that it doesnt slow the program down
    def load(self):
        self.background = pygame.image.load('watermaze.png')
        #scale it to the size of the screen
        self.background = pygame.transform.scale(self.background, (MAZE_WIDTH, MAZE_HEIGHT))

        # Opening walls file
        # Creating walls list with co-ords of walls
        # stored as  a vector
        with open("walls.txt", 'r') as file:
            for yidx, line in enumerate(file):
                for xidx, char in enumerate(line):
                    if char == "1":                             #if there is a wall
                        self.walls.append(vec(xidx, yidx))      #store pos in walls list
                    elif char == "C":                           #if there is food
                        self.foods.append(vec(xidx, yidx))      #store pos in food list
                    elif char == "P":                           #if it is the startposition for crab
                        self.p_pos = [xidx, yidx]               #give the p_pos this position
                    elif char in ["2", "3", "4", "5"]:          #if it is in one of the enemy positions
                        self.e_pos.append([xidx, yidx])         #store this in enemy start position
                    elif char == "B":                           #entrance for the enemies
                        pygame.draw.rect(self.background, BACKCOL, (xidx * self.cell_width, yidx * self.cell_height,
                                                                    self.cell_width, self.cell_height))

    def make_enemies(self):                                                 #idx sets personality of enemy
        for idx, pos in enumerate(self.e_pos):                              #for each position in start positions
            self.enemies.append(Enemy(self, vec(pos), idx, self.screen))     #make enemy with this position

    def reset(self):
        self.player.lives = 3                                       #reset lives
        self.player.current_score = 0
        self.player.grid_pos = vec(self.player.starting_pos)        #reset player
        self.player.pix_pos = self.player.get_pix_pos()
        self.player.direction *= 0
        for enemy in self.enemies:                                  #reset enemies
            enemy.grid_pos = vec(enemy.starting_pos)
            enemy.pix_pos = enemy.get_pix_pos()
            enemy.direction *= 0

        self.foods = []
        with open("walls.txt", 'r') as file:                        #reset food
            for yidx, line in enumerate(file):
                for xidx, char in enumerate(line):
                    if char == 'C':
                        self.foods.append(vec(xidx, yidx))
        self.state = "playing"                                      #go back to playing state


########################### INTRO FUNCTIONS ####################################

    def start_events(self):
        for event in pygame.event.get():
            #if cross is pressed
            if event.type == pygame.QUIT:
                self.running = False #stop running
            if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE: #when space button pressed start game
                self.state = 'playing'

    def start_update(self):
        pass

    def start_draw(self):
        self.screen.fill(BACKCOL)
        self.draw_text('PUSH SPACE BAR', self.screen, [
                       WIDTH//2, HEIGHT//2-50], START_TEXT_SIZE, (170, 132, 58), START_FONT)
        self.draw_text('1 PLAYER ONLY', self.screen, [
                       WIDTH//2, HEIGHT//2+50], START_TEXT_SIZE, (44, 167, 198), START_FONT)
        pygame.display.update()

########################### PLAYING FUNCTIONS ##################################


    def playing_events(self): #move player
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            if event.type == pygame.KEYDOWN:
                self.callcv()
                if event.key == pygame.K_LEFT:
                    self.player.move(vec(-1, 0))
                if event.key == pygame.K_RIGHT:
                    self.player.move(vec(1, 0))
                if event.key == pygame.K_UP:
                    self.player.move(vec(0, -1))
                if event.key == pygame.K_DOWN:
                    self.player.move(vec(0, 1))

    def playing_update(self):
        self.player.update()
        for enemy in self.enemies:                      #update enemies
            enemy.update()

        for enemy in self.enemies:
            if enemy.grid_pos == self.player.grid_pos:   #update lives
                self.remove_life()

    def playing_draw(self):
        self.screen.fill(BACKCOL)
        self.screen.blit(self.background, (TOP_BOTTOM_BUFFER//2, TOP_BOTTOM_BUFFER//2))     #draw bakground within a buffer
        self.draw_foods()           #draw the foods
        self.draw_text('CURRENT SCORE: {}'.format(self.player.current_score),
                       self.screen, [WIDTH//2, 10], 18, WHITE, START_FONT)                  #draw the text in the buffer
        self.player.draw()          #draw player
        for enemy in self.enemies:  #for each enemy in list
            enemy.draw()            #draw it
        pygame.display.update()

    def remove_life(self):
        self.player.lives -= 1                                      #remove a life
        if self.player.lives == 0:
            self.state = "game over"                                #go to game over state
        else:                                                       #reset game
            self.player.grid_pos = vec(self.player.starting_pos)    #go back to start position
            self.player.pix_pos = self.player.get_pix_pos()         #also for grid
            self.player.direction *= 0                              #player wont be moving in same direction
            for enemy in self.enemies:                              #same for enemies
                enemy.grid_pos = vec(enemy.starting_pos)
                enemy.pix_pos = enemy.get_pix_pos()
                enemy.direction *= 0

    def draw_foods(self):
        for food in self.foods:     #for all foods in the food list (made in load)
            pygame.draw.circle(self.screen, FOODCOL,
                               (int(food.x*self.cell_width)+self.cell_width//2+TOP_BOTTOM_BUFFER//2,
                                int(food.y*self.cell_height)+self.cell_height//2+TOP_BOTTOM_BUFFER//2), 5) #//2 widht to center position


########################### GAME OVER FUNCTIONS ################################

    def game_over_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                self.reset()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                self.running = False

    def game_over_update(self):
        pass

    def game_over_draw(self):
        self.screen.fill(BACKCOL)
        quit_text = "Press the escape button to QUIT"
        again_text = "Press SPACE bar to PLAY AGAIN"
        self.draw_text("GAME OVER", self.screen, [WIDTH//2, 100],  52, RED, START_FONT)
        self.draw_text(again_text, self.screen, [
                       WIDTH//2, HEIGHT//2],  25, (190, 190, 190), START_FONT)
        self.draw_text(quit_text, self.screen, [
                       WIDTH//2, HEIGHT//1.5],  25, (190, 190, 190), START_FONT)
        pygame.display.update()
