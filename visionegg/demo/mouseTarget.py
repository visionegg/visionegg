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
                  color      = (0.0,0.0,0.0,1.0)) # Set the target color (RGBA) black

text = BitmapText( text = "Press Esc to quit, arrow keys to change size of target.", lowerleft = (0,5), color = (0.0,0.0,0.0,0.0))

# Create a Viewport instance
viewport = Viewport(screen=screen, stimuli=[target,text])

########################
#  Define controllers  #
########################

class MousePositionController( Controller ):
    def __init__(self):
        global mouse_position
        Controller.__init__(self,
                            return_type=type(None),
                            eval_frequency=Controller.EVERY_FRAME)

    def during_go_eval(self,t=None):
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

    def during_go_eval(self,t=None):
        global mouse_position
        return mouse_position

def cross_product(b,c):
    """Cross product between vectors, represented as tuples of length 3."""
    det_i = b[1]*c[2] - b[2]*c[1]
    det_j = b[0]*c[2] - b[2]*c[0]
    det_k = b[0]*c[1] - b[1]*c[0]
    return (det_i,-det_j,det_k)

def mag(b):
    """Magnitude of a vector."""
    return b[0]**2.0 + b[1]**2.0 + b[2]**2.0
    
class TargetOrientationController( Controller ):
    def __init__(self):
        Controller.__init__(self,
                            return_type=type(90.0),
                            eval_frequency=Controller.EVERY_FRAME)
        self.c = (0.0,0.0,1.0)
        self.last_orientation = 0.0

    def during_go_eval(self):
        global mouse_position, last_mouse_position

        b = (float(last_mouse_position[0]-mouse_position[0]),
             float(last_mouse_position[1]-mouse_position[1]),
             0.0)

        if mag(b) > 2.0: # Must mouse 10 pixels before changing orientation (rejects noise)
            # find cross product b x c. assume b and c are 3-vecs, b has
            # 3rd component 0.
            orientation_vector = cross_product(b,self.c)
            self.last_orientation = atan2(orientation_vector[1],orientation_vector[0])/math.pi*180.0
        return self.last_orientation

def get_target_size(t=None):
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
    
    return (target_w, target_h)

#############################################
#  Create event handler callback functions  #
#############################################

def quit(event):
    raise SystemExit

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
        
handle_event_callbacks = [(pygame.locals.QUIT, quit),
                          (pygame.locals.KEYDOWN, keydown),
                          (pygame.locals.KEYUP, keyup)]

# Create an instance of the Presentation class.  This contains the
# the Vision Egg's runtime control abilities.
p = Presentation(go_duration=('forever',),
                 viewports=[viewport],
                 check_events=1,
                 handle_event_callbacks=handle_event_callbacks)

#############################################################
#  Connect the controllers with the variables they control  #
#############################################################

p.add_controller(None, None, MousePositionController() )
p.add_controller(target,'center', TargetPositionController() )
p.add_controller(target,'size', FunctionController(during_go_func=get_target_size) )
p.add_controller(target,'orientation', TargetOrientationController() )

#######################
#  Run the stimulus!  #
#######################

p.go()

