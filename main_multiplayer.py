#! /usr/bin/env python3

#################### IMPORTS ####################

import pygame
import sys
import os
from time import sleep
from random import randrange
import socketio
from common.gameobjects import Cloud, RangerShip, OpponentRangerShip


#################### INIT ####################
pygame.init()
clock = pygame.time.Clock()
screenwidth, screenheight = (1280, 720)
screen = pygame.display.set_mode((screenwidth, screenheight))

# Socket.io client connection
sock = socketio.Client()

# will change once deployed
# to environmental variable
sock.connect('http://localhost:8000')

# Socket implementations
# don't move these, for some reason stops working if moved down
@sock.on("WelcomeClient")
def on_welcome(data):
    print("Server: ", data['message'])
    sock.emit("joinRoom", {
        'roomID': 'room1'
    })

@sock.on("newRoomMemberJoined")
def send_message_to_room(data):
    print(data)
    sock.emit('sendMessageToRoom', {
        'roomID': 'room1',
        'message': 'Welcome, my opponent has arrived finally!!!'
    })

@sock.on('messageFromRoomMember')
def message_from_room_member(data):
    print("new message from a room member!")
    print(data)

@sock.on('updateOpponentCoordinates')
def update_opponent_coordinates(data):
    print(data['xCoord'], data['yCoord'])
    OpponentRanger.UpdateCoords(data['xCoord'], data['yCoord'])


# Load Assets
background_path = os.path.join("./static", "background2.jpeg")
background_image = pygame.image.load(background_path)
ranger_path = os.path.join("./static", "rangership_50.png")
inverted_ranger_path = os.path.join("./static", "inverted_rangership_50.png")
cloud_path = os.path.join("./static", "cloud1_transparent_30.png")
laser_path = os.path.join("./static", "laser.mp3")

pygame.mouse.set_visible(0)
pygame.display.set_caption('Sky Danger Ranger')

# initialize cloud object
cloud = Cloud(cloud_path, randrange(0,screenwidth, 1), 0)

# initialize ranger object
Ranger = RangerShip(screenheight, screenwidth, ranger_path, 0, 0)

OpponentRanger = OpponentRangerShip(screenheight, screenwidth, inverted_ranger_path, 0, 0)


# replace 200 with the actual height of the cloud
# so we can continue to spawn in the cloud when it
# goes out of view
BOUND = 200

# laser info
maxLineWidth = 20
lineWidth = maxLineWidth
minLineWidth = 0
isClicking = False # TODO move this into a screen class
laser_sound = pygame.mixer.Sound(laser_path)
isPlayingLaserSound = False

#################### MAIN LOOP ####################
while True:
    # loop clock
    clock.tick(60)

    # re render the background
    screen.blit(background_image, (0,0))

    # get coordinates of mouse
    x, y = pygame.mouse.get_pos()

    # send coordinates to opponent
    sock.emit('updateMyCoordinates', {
        'roomID': 'room1',
        'xCoord': x,
        'yCoord': y
    })

    # show cloud
    cloud.Show(screen)
    cloud.SetY(cloud.GetY()+10)
    if cloud.GetY() < -BOUND or cloud.GetY() > screenheight + BOUND:
        cloud.SetX(randrange(0, screenwidth,1))
        cloud.SetY(-100) # TODO change this to be variable based on the cloud size

    # display laser
    if isClicking:
        if lineWidth == maxLineWidth:
            pygame.mixer.Sound.play(laser_sound)
            sock.emit('laserShot', {
                'roomID': 'room1'
            })
        pygame.draw.line(screen, (255,0,0), (x,y), (x,0), lineWidth)
        lineWidth -= 1
        if lineWidth < minLineWidth:
            lineWidth = minLineWidth

    # show opponent ranger
    OpponentRanger.Show(screen)

    # show ranger
    Ranger.UpdateCoords(x, y)
    Ranger.Show(screen)

    # check for events
    for event in pygame.event.get():
        # check for window close
        if event.type == pygame.QUIT:
            sys.exit()
        # check for mouse clicks
        if event.type == pygame.MOUSEBUTTONDOWN:
            isClicking = True
        if event.type == pygame.MOUSEBUTTONUP:
            isClicking = False
            lineWidth = maxLineWidth

    pygame.display.update()
