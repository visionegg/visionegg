#!/usr/bin/env python
"""Control a target with the mouse, using your own event loop."""

# Variables to store the mouse position
mouse_position = (320.0, 240.0)
last_mouse_position = (0.0,0.0)

############################
#  Import various modules  #
############################

import VisionEgg
VisionEgg.start_default_logging(); VisionEgg.watch_exceptions()

from VisionEgg.Core import *
from VisionEgg.MoreStimuli import *
from VisionEgg.Text import *
from math import *
import pygame

# Use Python's bool constants if available, make aliases if not
try:
    True
except NameError:
    True = 1==1
    False = 1==0

#################################
#  Initialize the various bits  #
#################################

# Initialize OpenGL graphics screen.
screen = get_default_screen()

# Set the background color to white (RGBA).
screen.parameters.bgcolor = (1.0,1.0,1.0,1.0)

# Create an instance of the Target2D class with appropriate parameters.
target = Target2D(size  = (25.0,10.0),
                  anchor = 'center',
                  color      = (0.0,0.0,0.0,1.0)) # Set the target color (RGBA) black

text = Text( text = "Press Esc to quit, arrow keys to change size of target.",
             position = (screen.size[0]/2.0,5),
             anchor='bottom',
             color = (0.0,0.0,0.0,1.0))

# Create a Viewport instance
viewport = Viewport(screen=screen, stimuli=[target,text])

################
#  Math stuff  #
################

def cross_product(b,c):
    """Cross product between vectors, represented as tuples of length 3."""
    det_i = b[1]*c[2] - b[2]*c[1]
    det_j = b[0]*c[2] - b[2]*c[0]
    det_k = b[0]*c[1] - b[1]*c[0]
    return (det_i,-det_j,det_k)

def mag(b):
    """Magnitude of a vector."""
    return b[0]**2.0 + b[1]**2.0 + b[2]**2.0
    
# target size
target_w = 50.0
target_h = 10.0

# key state
up = False
down = False
left = False
right = False

# The main loop below is an alternative to using the
# VisionEgg.FlowControl.Presentation class.

quit_now = False
frame_timer = FrameTimer()
while not quit_now:
    for event in pygame.event.get():
        if event.type == pygame.locals.QUIT:
            quit_now = True
        elif event.type == pygame.locals.KEYDOWN:
            if event.key == pygame.locals.K_ESCAPE:
                quit_now = True
            elif event.key == pygame.locals.K_UP:
                up = True
            elif event.key == pygame.locals.K_DOWN:
                down = True
            elif event.key == pygame.locals.K_RIGHT:
                right = True
            elif event.key == pygame.locals.K_LEFT:
                left = True
        elif event.type == pygame.locals.KEYUP:
            if event.key == pygame.locals.K_UP:
                up = False
            elif event.key == pygame.locals.K_DOWN:
                down = False
            elif event.key == pygame.locals.K_RIGHT:
                right = False
            elif event.key == pygame.locals.K_LEFT:
                left = False

    just_current_pos = mouse_position
    (x,y) = pygame.mouse.get_pos()
    y = screen.size[1]-y # convert to OpenGL coords
    mouse_position = (x,y)
    if just_current_pos != mouse_position:
        last_mouse_position = just_current_pos
        
    # Set target position
    target.parameters.position = mouse_position
    
    # Set target orientation
    b = (float(last_mouse_position[0]-mouse_position[0]),
         float(last_mouse_position[1]-mouse_position[1]),
         0.0)

    orientation_vector = cross_product(b,(0.0,0.0,1.0))
    target.parameters.orientation = atan2(orientation_vector[1],orientation_vector[0])/math.pi*180.0

    # Set target size
    amount = 0.02
    
    if up:
        target_w = target_w+(amount*target_w)
    elif down:
        target_w = target_w-(amount*target_w)
    elif right:
        target_h = target_h+(amount*target_h)
    elif left:
        target_h = target_h-(amount*target_h)
    target_w = max(target_w,0.0)
    target_h = max(target_h,0.0)

    target.parameters.size = (target_w, target_h)

    screen.clear()
    viewport.draw()
    swap_buffers()
    frame_timer.tick()
frame_timer.log_histogram()
