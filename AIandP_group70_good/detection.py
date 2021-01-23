import cv2
import keyboard
import pygame
from settings import *
import keyboard
import cv2


class Detection:
    def _init_(self):
        pass

    def detect_nose(self, img, faceCascade):

        # convert image to gray-scale
        gray_img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

        # detecting features in gray-scale image, returns coordinates, width and height of features
        features = faceCascade.detectMultiScale(gray_img, 1.1, 8)
        nose_cords = []

        # drawing rectangle around the feature and labeling it
        for (x, y, w, h) in features:
            cv2.circle(img, ((2 * x + w) // 2, (2 * y + h) // 2), 10, (255, 0, 0), 2)
            nose_cords = ((2 * x + w) // 2, (2 * y + h) // 2)
        return img, nose_cords

    def draw_controller(self, img, cords):
        size = 40
        x1 = cords[0] - size
        y1 = cords[1] - size
        x2 = cords[0] + size
        y2 = cords[1] + size
        cv2.circle(img, cords, size, (0, 0, 255), 2)
        return [(x1, y1), (x2, y2)]

    def keyboard_events(self, img, nose_cords, cords, cmd):
        try:
            [(x1, y1), (x2, y2)] = cords
            xc, yc = nose_cords
        except Exception as e:
            print(e)
            return
        if xc < x1:
            cmd = "left"

        elif (xc > x2):
            cmd = "right"

        elif (yc < y1):
            cmd = "up"

        elif (yc > y2):
            cmd = "down"

        if cmd:
            print("Detected movement: ", cmd, "\n")
            keyboard.press_and_release(cmd)
        return img, cmd

    def reset_press_flag(self, nose_cords, cords, cmd):
        try:
            [(x1, y1), (x2, y2)] = cords
            xc, yc = nose_cords
        except:
            return True, cmd
        if x1 < xc < x2 and y1 < yc < y2:
            return True, None
        return False, cmd