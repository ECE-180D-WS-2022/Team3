#! /usr/bin/env python3

#################### IMPORTS ####################

import pygame
import sys
import os
from time import sleep
from random import randrange
import socketio

#################### TODOs ####################
'''
- [x] make cloud appear
- [x] make plane follow cursor
- [ ] make multiple clouds appear
- [ ] make enemies appear
- [ ] make enemies take damage
- [ ] make enemies deal damage
- [ ] make amo boxes appear
- [ ] make plane shoot
- [ ] make plane GIF render plane flying
- [ ] ...
'''
#################### CLASSES ####################
class Cloud:
    def __init__(self, imagefile, x, y):
        self.image = imagefile
        self.shape = pygame.image.load(imagefile)
        self.x = x
        self.y = y

    def Show(self, surface):
        surface.blit(self.shape, (self.x, self.y))

    def SetX(self, val):
        self.x = val

    def GetX(self):
        return self.x

    def SetY(self, val):
        self.y = val

    def GetY(self):
        return self.y

    def GetCoords(self):
        return (self.x, self.y)

class RangerShip:
    def __init__(self, screenheight, screenwidth, imagefile, x, y):
        self.image = imagefile
        self.shape = pygame.image.load(imagefile)
        self.top = screenheight/2 - self.shape.get_height()
        self.left = screenwidth/2 - self.shape.get_width()/2
        self.x = x
        self.y = y

    def Show(self, surface):
        surface.blit(self.shape, (self.left, self.top))

    def UpdateCoords(self, x, y):
        self.left = x-self.shape.get_width()/2
        self.top = y-self.shape.get_height()/2



class OpponentRangerShip:
    def __init__(self, screenheight, screenwidth, imagefile, x, y):
        self.image = imagefile
        self.shape = pygame.image.load(imagefile)
        self.top = screenheight/2 - self.shape.get_height()
        self.left = screenwidth/2 - self.shape.get_width()/2
        self.x = x
        self.y = y

    def Show(self, surface):
        surface.blit(self.shape, (self.left, self.top))

    def UpdateCoords(self, x, y):
        self.left = x-self.shape.get_width()/2
        self.top = y-self.shape.get_height()/2

    def FetchCoords(self):
        return (x, y)
