#!/usr/bin/env python
"""Save movie of a black target moving across a white background."""

fps = 12.0

############################
#  Import various modules  #
############################

import VisionEgg
VisionEgg.start_default_logging(); VisionEgg.watch_exceptions()

from VisionEgg.Core import *
from VisionEgg.FlowControl import Presentation, Controller, FunctionController
from VisionEgg.MoreStimuli import *
from math import *
from types import *
import os

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
                  color      = (0.0,0.0,0.0,1.0), # Set the target color (RGBA) black
                  orientation = -45.0)

# Create a Viewport instance
viewport = Viewport(screen=screen, stimuli=[target])

# Create an instance of the Presentation class.  This contains the
# the Vision Egg's runtime control abilities.
p = Presentation(go_duration=(10.0,'seconds'),viewports=[viewport])

#######################
#  Define controller  #
#######################

# calculate a few variables we need
mid_x = screen.size[0]/2.0
mid_y = screen.size[1]/2.0
max_vel = min(screen.size[0],screen.size[1]) * 0.4

# define position as a function of time
def get_target_position(t):
    global mid_x, mid_y, max_vel
    return ( max_vel*sin(0.1*2.0*pi*t) + mid_x , # x
             max_vel*sin(0.1*2.0*pi*t) + mid_y ) # y

# Create an instance of the Controller class
target_position_controller = FunctionController(during_go_func=get_target_position)

#############################################################
#  Connect the controllers with the variables they control  #
#############################################################

p.add_controller(target,'position', target_position_controller )

#######################
#  Run the stimulus!  #
#######################

base_dir = VisionEgg.config.VISIONEGG_USER_DIR
if not os.path.isdir(base_dir):
    base_dir = VisionEgg.config.VISIONEGG_SYSTEM_DIR
save_directory = os.path.join(base_dir,'movie')
if not os.path.isdir(save_directory):
    os.mkdir(save_directory)
    if not os.path.isdir(save_directory):
        print "Error: cannot make movie directory '%s'."%save_directory
print "Saving movie to directory '%s'."%save_directory
basename = "movie_"+os.path.splitext(os.path.basename(sys.argv[0]))[0]
p.export_movie_go(frames_per_sec=fps,filename_base=basename,path=save_directory)


