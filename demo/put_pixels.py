#!/usr/bin/env python
import VisionEgg
VisionEgg.start_default_logging(); VisionEgg.watch_exceptions()

from VisionEgg.Core import *
import pygame
from pygame.locals import *

screen = get_default_screen()
screen.set( bgcolor = (0.0,0.0,0.0) ) # black (RGB)

white_data = (Numeric.ones((100,200,3))*255).astype(Numeric.UnsignedInt8)
red_data = white_data.copy()
red_data[:,:,1:] = 0 # zero non-red channels

blue_data = white_data.copy()
blue_data[:,:,:-1] = 0 # zero non-blue channels

frame_timer = FrameTimer() # start frame counter/timer
count = 0
quit_now = 0

# This style of main loop is an alternative to using the
# VisionEgg.FlowControl module.
while not quit_now:
    for event in pygame.event.get():
        if event.type in (QUIT,KEYDOWN,MOUSEBUTTONDOWN):
            quit_now = 1
    screen.clear()
    count = (count+1) % 3
    if count == 0:
        pixels = white_data
    elif count == 1:
        pixels = red_data
    elif count == 2:
        pixels = blue_data
    screen.put_pixels(pixels=pixels,
                      position=(screen.size[0]/2.0,screen.size[1]/2.0),
                      anchor="center")
    swap_buffers() # display what we've drawn
    frame_timer.tick() # register frame draw with timer
frame_timer.log_histogram()
