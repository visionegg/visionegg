#!/usr/bin/env python

# Display a white target moving across a textured drum.

############################
#  Import various modules  #
############################

from VisionEgg.Core import *
from VisionEgg.AppHelper import *
from VisionEgg.MoreStimuli import *
from VisionEgg.Textures import *
from math import *
from types import *

# Initialize OpenGL graphics screen.
screen = get_default_screen()

#######################
#  Create the target  #
#######################

# Create an instance of the Target2D class with appropriate parameters
target = Target2D(size  = (25.0,10.0),
                  color      = (1.0,1.0,1.0,1.0), # Set the target color (RGBA) black
                  orientation = 135.0)

# Create a viewport for the target
target_viewport = Viewport(screen=screen, stimuli=[target])

#####################
#  Create the drum  #
#####################

# Get a texture
try:
    texture = TextureFromFile("orig.bmp") # try to open a texture file
except:
    texture = Texture(size=(256,16)) # otherwise, generate one

# Create an instance of SpinningDrum class
drum = SpinningDrum(texture=texture)

# Create a perspective projection for the spinning drum
perspective = SimplePerspectiveProjection(fov_x=90.0)

# Create a viewport with this projection
drum_viewport = Viewport(screen=screen,
                         projection=perspective,
                         stimuli=[drum])

##################################################
#  Create an instance of the Presentation class  #
##################################################

# Add target_viewport last so its stimulus is drawn last. This way the
# target is always drawn after (on top of) the drum and is therefore
# visible.
p = Presentation(duration=(10.0,'seconds'),viewports=[drum_viewport,target_viewport])

########################
#  Define controllers  #
########################

class TargetPositionController( Controller ):
    def __init__(self):
        Controller.__init__(self, return_type=TupleType)
                           
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

# create an instance of this controller class
target_position_controller = TargetPositionController()

class DrumAngleController( Controller ):
    def __init__(self):
        Controller.__init__(self, return_type=FloatType)

    def during_go_eval(self):
        t = self.temporal_variable
        return 50.0*math.cos(0.2*2*math.pi*t)

# create an instance of this controller class
drum_angle_controller = DrumAngleController()

#############################################################
#  Connect the controllers with the variables they control  #
#############################################################

p.add_controller(target,'center', target_position_controller )
p.add_controller(drum,'angular_position', drum_angle_controller )

#######################
#  Run the stimulus!  #
#######################

p.go()

