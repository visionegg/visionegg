#!/usr/bin/env python
"""Moving target over a 2D spinning drum."""

############################
#  Import various modules  #
############################

from VisionEgg import *
start_default_logging(); watch_exceptions()

from VisionEgg.Core import *
from VisionEgg.FlowControl import Presentation, Controller, FunctionController
from VisionEgg.MoreStimuli import *
from VisionEgg.Textures import *
import os
from math import *

# Initialize OpenGL graphics screen.
screen = get_default_screen()

#######################
#  Create the target  #
#######################

# Create an instance of the Target2D class with appropriate parameters
target = Target2D(size  = (25.0,10.0),
                  color      = (1.0,1.0,1.0,0.5), # Set the target color (RGBA) black
                  orientation = -45.0)

##########################
#  Create the flat drum  #
##########################

# Get a texture
filename = os.path.join(config.VISIONEGG_SYSTEM_DIR,"data","panorama.jpg")
texture = Texture(filename)

# Create an instance of SpinningDrum class
drum = SpinningDrum(texture=texture,
                    shrink_texture_ok=1,
                    flat=1,
                    anchor='center',
                    position=(screen.size[0]/2,screen.size[1]/2),
                    )

#########################
#  Create the viewport  #
#########################

# Create a viewport for the target
viewport = Viewport(screen=screen, stimuli=[drum,target])

##################################################
#  Create an instance of the Presentation class  #
##################################################

# Add target_viewport last so its stimulus is drawn last. This way the
# target is always drawn after (on top of) the drum and is therefore
# visible.
p = Presentation(go_duration=(10.0,'seconds'),viewports=[viewport])

########################
#  Define controllers  #
########################

# calculate a few variables we need
mid_x = screen.size[0]/2.0
mid_y = screen.size[1]/2.0
max_vel = min(screen.size[0],screen.size[1]) * 0.4

# define target position as a function of time
def get_target_position(t):
    global mid_x, mid_y, max_vel
    return ( max_vel*sin(0.1*2.0*pi*t) + mid_x , # x
             max_vel*sin(0.1*2.0*pi*t) + mid_y ) # y

def get_drum_angle(t):
    return 10.0*t

# Create instances of the Controller class
target_position_controller = FunctionController(during_go_func=get_target_position)
drum_angle_controller = FunctionController(during_go_func=get_drum_angle)

#############################################################
#  Connect the controllers with the variables they control  #
#############################################################

p.add_controller(target,'position', target_position_controller )
p.add_controller(drum,'angular_position', drum_angle_controller )

#######################
#  Run the stimulus!  #
#######################

p.go()

