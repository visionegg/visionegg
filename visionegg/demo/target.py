#!/usr/bin/env python

# Display a black target moving across a white background.

########################################################
#  Import various modules from the Vision Egg package  #
########################################################

from VisionEgg.Core import *
from VisionEgg.AppHelper import *
from VisionEgg.MoreStimuli import *

#################################
#  Initialize the various bits  #
#################################

# Initialize OpenGL graphics screen
screen = get_default_screen()

# Set the background color (RGBA) white
screen.parameters.bgcolor = (1.0,1.0,1.0,1.0)

# Create a viewport on the screen
viewport = Viewport(screen,(0,0),screen.size)

# Create an orthographic projection that so that OpenGL object
# coordinates are equal to window (pixel) coordinates.
pixel_coords = OrthographicProjection(left=0,right=screen.size[0],
                                      bottom=0,top=screen.size[1])

# Create an instance of the Target2D class with appropriate parameters
target = Target2D(projection = pixel_coords,
                  width      = 25.0,
                  height     = 10.0,
                  color      = (0.0,0.0,0.0,1.0)) # Set the target color (RGBA) black

# Initialize the target's OpenGL stuff
target.init_gl()

# Tell the viewport to draw the target
viewport.add_stimulus(target)

# Create an instance of the Presentation class
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

def x_as_function_of_time(t):
    return max_vel*sin(0.1*2.0*math.pi*t) + mid_x

def y_as_function_of_time(t):
    return max_vel*sin(0.1*2.0*math.pi*t) + mid_y

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

p.add_realtime_time_controller(target.parameters,'x', x_as_function_of_time)
p.add_realtime_time_controller(target.parameters,'y', y_as_function_of_time)
p.add_transitional_controller(target.parameters,'orientation', orientation)
p.add_transitional_controller(target.parameters,'on', on_during_experiment)

#######################
#  Run the stimulus!  #
#######################

p.go()

