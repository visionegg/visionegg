#!/usr/bin/env python

# Display a white target moving across a textured drum.

########################################################
#  Import various modules from the Vision Egg package  #
########################################################

import math
from VisionEgg.Core import *
from VisionEgg.AppHelper import *
from VisionEgg.MoreStimuli import *
from VisionEgg.Textures import *

#################################
#  Initialize the various bits  #
#################################

screen = get_default_screen()

# This projection controls any objects that don't set their own, which
# is the textured drum in this case.
projection = SimplePerspectiveProjection(fov_x=90.0)
viewport = Viewport(screen,(0,0),screen.size,projection)

# Create an orthographic projection for the target that so that OpenGL
# object coordinates are equal to window (pixel) coordinates.
pixel_coords = OrthographicProjection(left=0,right=screen.size[0],
                                      bottom=0,top=screen.size[1])

# Create an instance of the Target2D class with appropriate parameters
target = Target2D(projection = pixel_coords,
                  width      = 25.0,
                  height     = 10.0,
                  color      = (1.0,1.0,1.0,1.0)) # Set the target color (RGBA) white

target.init_gl()
try:
    texture = TextureFromFile("orig.bmp") # try to open a texture file
except:
    texture = Texture(size=(256,16)) # otherwise, generate one

drum = SpinningDrum(texture=texture)
drum.init_gl()
viewport.add_stimulus(drum)
viewport.add_stimulus(target) # add target after drum so it is drawn on top

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

def orientation(dummy):
    return 135.0

def angle_as_function_of_time(t):
    return 50.0*math.cos(0.2*2*math.pi*t)

def one_during_experiment(t):
    if t < 0.0:
        return 0.0
    else:
        return 1.0

#############################################################
#  Connect the controllers with the variables they control  #
#############################################################

p.add_realtime_time_controller(target.parameters,'x', x_as_function_of_time)
p.add_realtime_time_controller(target.parameters,'y', y_as_function_of_time)
p.add_realtime_time_controller(drum.parameters,'angle', angle_as_function_of_time)
p.add_transitional_controller(target.parameters,'orientation', orientation)
p.add_transitional_controller(target.parameters,'on', one_during_experiment)
p.add_transitional_controller(drum.parameters,'contrast', one_during_experiment)

#######################
#  Run the stimulus!  #
#######################

p.go()


