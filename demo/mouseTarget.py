#!/usr/bin/env python
"""Control a target with the mouse, get SDL/pygame events."""

# Variables to store the mouse position
mouse_position = (320.0, 240.0)
last_mouse_position = (0.0,0.0)

############################
#  Import various modules  #
############################

from VisionEgg.Core import *
from VisionEgg.MoreStimuli import *
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
                  color      = (0.0,0.0,0.0,1.0)) # Set the target color (RGBA) black

# Create a Viewport instance
viewport = Viewport(screen=screen, stimuli=[target])

########################
#  Define controllers  #
########################

class MousePositionController( Controller ):
    def __init__(self):
        global mouse_position
        Controller.__init__(self,
                            return_type=type(None),
                            eval_frequency=Controller.EVERY_FRAME)

    def during_go_eval(self):
        # Convert pygame mouse position to OpenGL position
        global mouse_position, last_mouse_position
        just_current_pos = mouse_position
        (x,y) = pygame.mouse.get_pos()
        y = screen.size[1]-y
        mouse_position = (x,y)
        if just_current_pos != mouse_position:
            last_mouse_position = just_current_pos
        return None
    
class TargetPositionController( Controller ):
    def __init__(self):
        global mouse_position
        Controller.__init__(self,
                            return_type=type(mouse_position),
                            eval_frequency=Controller.EVERY_FRAME)

    def during_go_eval(self):
        global mouse_position
        return mouse_position

class TargetOrientationController( Controller ):
    def __init__(self):
        Controller.__init__(self,
                            return_type=type(90.0),
                            eval_frequency=Controller.EVERY_FRAME)

    def during_go_eval(self):
        global mouse_position, last_mouse_position
        # should use cross product!
        return 90.0

#############################################
#  Create event handler callback functions  #
#############################################

def quit(event):
    raise SystemExit

def keydown(event):
    if event.key is pygame.locals.K_ESCAPE:
        quit(event)

handle_event_callbacks = [(pygame.locals.QUIT, quit),(pygame.locals.KEYDOWN, keydown)]

# Create an instance of the Presentation class.  This contains the
# the Vision Egg's runtime control abilities.
p = Presentation(duration=('forever',),
                 viewports=[viewport],
                 check_events=1,
                 handle_event_callbacks=handle_event_callbacks)

#############################################################
#  Connect the controllers with the variables they control  #
#############################################################

p.add_controller(None, None, MousePositionController() )
p.add_controller(target,'center', TargetPositionController() )
p.add_controller(target,'orientation', TargetOrientationController() )

#######################
#  Run the stimulus!  #
#######################

p.go()

