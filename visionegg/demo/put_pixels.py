#!/usr/bin/env python

import VisionEgg
from VisionEgg.Core import *
import pygame
from pygame.locals import *

screen = get_default_screen()
screen.parameters.bgcolor = (0.0,0.0,0.0,0.0) # black (RGBA)

# The main loop below is an alternative to using the
# VisionEgg.Core.Presentation class.

white_frame = (Numeric.ones((100,200,3))*255).astype(Numeric.UnsignedInt8)
red_frame = white_frame.copy()
red_frame[:,:,1:] = 0 # zero non-red channels

blue_frame = white_frame.copy()
blue_frame[:,:,:-1] = 0 # zero non-blue channels

frame_timer = FrameTimer()
count = 0
while not pygame.event.peek((QUIT,KEYDOWN,MOUSEBUTTONDOWN)):
    screen.clear()
    count = (count+1) % 3
    if count == 0:
        pixels = white_frame
    elif count == 1:
        pixels = red_frame
    elif count == 2:
        pixels = blue_frame
    screen.put_pixels(pixels=pixels,
                      position=(screen.size[0]/2.0,screen.size[1]/2.0),
                      anchor="center")
    swap_buffers()
    frame_timer.tick()
frame_timer.print_histogram()
