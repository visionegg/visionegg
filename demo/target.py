#!/usr/bin/env python

# Display a black target moving across a white background.

########################################################
#  Import various modules from the Vision Egg package  #
########################################################

from VisionEgg.Core import *
from VisionEgg.AppHelper import *
from VisionEgg.MoreStimuli import *

#################################
#  Define controller functions  #
#################################

def x_as_function_of_time(t):
    return 25.0*sin(0.1*2.0*math.pi*t)

def y_as_function_of_time(t):
    return 25.0*sin(0.1*2.0*math.pi*t)

def orientation(dummy_argument):
    return 135.0

def on_during_experiment(t):
    if t < 0.0:
        return 0 # off between stimuli
    else:
        return 1 # on during stimulus presentation

##################
#  Main program  #
##################

# Initialize OpenGL graphics screen
screen = get_default_screen()

# Set the background color (RGBA) white
screen.parameters.bgcolor = (1.0,1.0,1.0,1.0)

# Create a viewport on the screen
viewport = Viewport(screen,(0,0),screen.size)

# Create an instance of the Target2D class
target = Target2D()

# Initialize the target's OpenGL stuff
target.init_gl()

# Set the target color (RGBA) black
target.parameters.color = (0.0,0.0,0.0,1.0)

# Tell the viewport to draw the target
viewport.add_stimulus(target)

# Create an instance of the Presentation class
p = Presentation(duration=(10.0,'seconds'),viewports=[viewport])

# Register the controller functions
p.add_realtime_time_controller(target.parameters,'x', x_as_function_of_time)
p.add_realtime_time_controller(target.parameters,'y', y_as_function_of_time)
p.add_transitional_controller(target.parameters,'orientation', orientation)
p.add_transitional_controller(target.parameters,'on', on_during_experiment)
p.go()
