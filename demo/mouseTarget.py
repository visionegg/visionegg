#!/usr/bin/env python
"""Control a target with the mouse, get SDL/pygame events."""

# Variables to store the mouse position
mouse_position = (320.0, 240.0)
last_mouse_position = (0.0,0.0)

############################
#  Import various modules  #
############################

import VisionEgg
VisionEgg.start_default_logging(); VisionEgg.watch_exceptions()

from VisionEgg.Core import *
from VisionEgg.FlowControl import Presentation, FunctionController
from VisionEgg.MoreStimuli import *
from VisionEgg.Text import *
from math import *
import pygame

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
    
def every_frame_func(t=None):
    # Get mouse position
    global mouse_position, last_mouse_position
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
    global target_w, target_h
    global up, down, left, right

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

#############################################
#  Create event handler callback functions  #
#############################################

# target size global variables
target_w = 50.0
target_h = 10.0

# key state global variables
up = 0
down = 0
left = 0
right = 0

def keydown(event):
    global up, down, left, right
    if event.key == pygame.locals.K_ESCAPE:
        quit(event)
    elif event.key == pygame.locals.K_UP:
        up = 1
    elif event.key == pygame.locals.K_DOWN:
        down = 1
    elif event.key == pygame.locals.K_RIGHT:
        right = 1
    elif event.key == pygame.locals.K_LEFT:
        left = 1
        
def keyup(event):
    global up, down, left, right
    if event.key == pygame.locals.K_UP:
        up = 0
    elif event.key == pygame.locals.K_DOWN:
        down = 0
    elif event.key == pygame.locals.K_RIGHT:
        right = 0
    elif event.key == pygame.locals.K_LEFT:
        left = 0

# Create an instance of the Presentation class.  This contains the
# the Vision Egg's runtime control abilities.
p = Presentation(go_duration=('forever',),
                 viewports=[viewport])

def quit(event):
    p.parameters.go_duration = (0,'frames')

p.parameters.handle_event_callbacks = [(pygame.locals.QUIT, quit),
                                       (pygame.locals.KEYDOWN, keydown),
                                       (pygame.locals.KEYUP, keyup)]

#############################################################
#  Connect the controllers with the variables they control  #
#############################################################

p.add_controller(None, None, FunctionController(during_go_func=every_frame_func) )

#######################
#  Run the stimulus!  #
#######################

p.go()

