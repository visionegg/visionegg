#!/usr/bin/env python

# Display a black target moving across a white background.

############################
#  Import various modules  #
############################

from VisionEgg.Core import *
from VisionEgg.AppHelper import *
from VisionEgg.MoreStimuli import *
import math

#################################
#  Initialize the various bits  #
#################################

# Initialize OpenGL graphics screen.
screen = get_default_screen()

# Set the background color to white (RGBA).
screen.parameters.bgcolor = (1.0,1.0,1.0,1.0)

# Use viewport with pixel coordinate system for projection
viewport = Viewport(screen=screen)

# Create an instance of the Target2D class with appropriate parameters.
target = Target2D(size  = (25.0,10.0),
                  color      = (0.0,0.0,0.0,1.0)) # Set the target color (RGBA) black

# Tell the viewport to draw the target.
viewport.add_stimulus(target)

# Create an instance of the Presentation class.  This contains the
# the Vision Egg's runtime control abilities.
p = Presentation(duration=(10.0,'seconds'),viewports=[viewport])

#################################
#  Define controller functions  #
#################################

# A few variables used to calculate postion based on screen size
mid_x = screen.size[0]/2.0
mid_y = screen.size[1]/2.0
if screen.size[0] < screen.size[1]:
    max_vel = screen.size[0] * 0.4
else:
    max_vel = screen.size[1] * 0.4

def xy_as_function_of_time(t):
    return ( max_vel*math.sin(0.1*2.0*math.pi*t) + mid_x , # x
             max_vel*math.sin(0.1*2.0*math.pi*t) + mid_y ) # y

def orientation(dummy_argument):
    return 135.0

def on_during_experiment(t):
    if t < 0.0:
        return 0 # off between stimuli
    else:
        return 1 # on during stimulus presentation

#############################################################
#  Connect the controllers with the variables they control  #
#############################################################

p.add_realtime_time_controller(target,'center', xy_as_function_of_time)
p.add_transitional_controller(target,'orientation', orientation)
p.add_transitional_controller(target,'on', on_during_experiment)

#######################
#  Run the stimulus!  #
#######################

p.go()

