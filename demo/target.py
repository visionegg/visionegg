#!/usr/bin/env python

# Display a black target moving across a white background.

############################
#  Import various modules  #
############################

from VisionEgg.Core import *
from VisionEgg.AppHelper import *
from VisionEgg.MoreStimuli import *
from math import *
from types import *

#################################
#  Initialize the various bits  #
#################################

# Initialize OpenGL graphics screen.
screen = get_default_screen()

# Set the background color to white (RGBA).
screen.parameters.bgcolor = (1.0,1.0,1.0,1.0)

# Create an instance of the Target2D class with appropriate parameters.
target = Target2D(size  = (25.0,10.0),
                  color      = (0.0,0.0,0.0,1.0), # Set the target color (RGBA) black
                  orientation = 135.0)

# Create a Viewport instance
viewport = Viewport(screen=screen, stimuli=[target])

# Create an instance of the Presentation class.  This contains the
# the Vision Egg's runtime control abilities.
p = Presentation(duration=(10.0,'seconds'),viewports=[viewport])

#######################
#  Define controller  #
#######################

# Here is a bit of object-oriented programming.  The class Controller
# is an abstract interface for anything that controls
# parameters. Below is the definition of TargetPositionController,
# which we make a subclass of Controller. Later, we will create an
# instance of TargetPositionController to control the position of the
# target.

class TargetPositionController( Controller ):
    def __init__(self):
        Controller.__init__(self,
                            return_type=TupleType,
                            temporal_variable_type=Controller.TIME_SEC_SINCE_GO,
                            eval_frequency=Controller.EVERY_FRAME)
                           
        # A few variables used to calculate postion based on screen size
        self.mid_x = screen.size[0]/2.0
        self.mid_y = screen.size[1]/2.0
        if screen.size[0] < screen.size[1]:
            self.max_vel = screen.size[0] * 0.4
        else:
            self.max_vel = screen.size[1] * 0.4

    def during_go_eval(self):
        t = self.temporal_variable
        return ( self.max_vel*sin(0.1*2.0*pi*t) + self.mid_x , # x
                 self.max_vel*sin(0.1*2.0*pi*t) + self.mid_y ) # y

# Create an instance of the class we just defined
target_position_controller = TargetPositionController()

#############################################################
#  Connect the controllers with the variables they control  #
#############################################################

p.add_controller(target,'center', target_position_controller )

#######################
#  Run the stimulus!  #
#######################

p.go()

