#!/usr/bin/env python

# Display a white target moving across a textured drum.

############################
#  Import various modules  #
############################

from VisionEgg.Core import *
from VisionEgg.AppHelper import *
from VisionEgg.MoreStimuli import *
from VisionEgg.Textures import *
import math

# Initialize an OpenGL window
screen = get_default_screen()

############################################
#  Setup the background - a spinning drum  #           
############################################

# Create a perspective projection for the spinning drum
perspective = SimplePerspectiveProjection(fov_x=90.0)

# Create a viewport with this projection
perspective_viewport = Viewport(screen=screen,
                                projection=perspective)

# Now create a spinning drum stimulus
try:
    texture = TextureFromFile("orig.bmp") # try to open a texture file
except:
    texture = Texture(size=(256,16)) # otherwise, generate one
drum = SpinningDrum(texture=texture)

# Add the spinning drum to the viewport
perspective_viewport.add_stimulus(drum)

############################################
#  Setup a small target in the foreground  #
############################################

# Use viewport with pixel coordinate system for projection
flat_viewport = Viewport(screen=screen)

# Create an instance of the Target2D class with appropriate parameters
target = Target2D(size  = (25.0,10.0),
                  color = (1.0,1.0,1.0,1.0), # Set the target color (RGBA) white
                  orientation = 135.0)

# Add the small target to the appropriate viewport
flat_viewport.add_stimulus(target)

##################################################
#  Create an instance of the Presentation class  #
##################################################

# Add flat_viewport last so its stimulus is drawn last. This way the
# target is drawn after the drum and is visible, without worrying
# about depth testing.
p = Presentation(duration=(10.0,'seconds'),
                 viewports=[perspective_viewport,flat_viewport])

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

# Control the small target:
def xy_as_function_of_time(t):
    return ( max_vel*math.sin(0.1*2.0*math.pi*t) + mid_x , # x
             max_vel*math.sin(0.1*2.0*math.pi*t) + mid_y ) # y

# Control the background:
def angle_as_function_of_time(t):
    return 50.0*math.cos(0.2*2*math.pi*t)

# Control anything that should be off between presentations:
def one_during_experiment(t):
    if t < 0.0:
        return 0.0
    else:
        return 1.0

#############################################################
#  Connect the controllers with the variables they control  #
#############################################################

p.add_realtime_time_controller(target,'center', xy_as_function_of_time)
p.add_realtime_time_controller(drum,'angular_position', angle_as_function_of_time)
p.add_transitional_controller(target,'on', one_during_experiment)
p.add_transitional_controller(drum,'contrast', one_during_experiment)

#######################
#  Run the stimulus!  #
#######################

p.go()


