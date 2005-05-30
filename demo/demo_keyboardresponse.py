#!/usr/bin/env python
"""Demo for the keyboard response controller class."""

# Author(s): Hubertus Becker <hubertus.becker@uni-tuebingen.de>
# Copyright: (C) 2005 by Hertie Institute for Clinical Brain Research,
#            Department of Cognitive Neurology, University of Tuebingen
# URL:       http://www.hubertus-becker.de/resources/visionegg/
# $Revision$  $Date$

############################
#  Import various modules  #
############################

#import math
#import warnings
#import random
#import sys
#import time
import Numeric, RandomArray
import VisionEgg
VisionEgg.start_default_logging(); VisionEgg.watch_exceptions()

from VisionEgg.Core import *
from VisionEgg.FlowControl import Presentation
from VisionEgg.Dots import *
import pygame
import VisionEgg.Daq
from VisionEgg.ResponseControl import *

#####################################
#  Initialize OpenGL window/screen  #
#####################################

screen = get_default_screen()
screen.parameters.bgcolor = (0.0,0.0,0.0,0.0) # make black (RGBA)

######################################
#  Create random dot stimulus        #
######################################

stimulus = DotArea2D(
    position                = (screen.size[0]/2.0, screen.size[1]/2.0),
    anchor                  = 'center',
    size                    = (300.0 , 300.0),
    signal_fraction         = 0.1,
    signal_direction_deg    = 180.0,
    velocity_pixels_per_sec = 10.0,
    dot_lifespan_sec        = 5.0,
    dot_size                = 3.0,
    num_dots                = 100
)

###############################################################
#  Create viewport - intermediary between stimuli and screen  #
###############################################################

viewport = Viewport(screen=screen, stimuli=[stimulus])

########################################
#  Create presentation object and go!  #
########################################

p = Presentation(go_duration=(5.0,'seconds'), viewports=[viewport])

##############################################
#  Connect the controller with the stimulus  #
##############################################

keyboard_response = KeyboardResponseController()

# Add the keyboard controller to the presentation's list of controllers
p.add_controller(None, None, keyboard_response)

########
#  Go  #
########

for i in range(3):
    p.go()

    # Print responses collected during the presentation
#   print "all       =",keyboard_response.get_responses_since_go()
#   print "all_time  =",keyboard_response.get_time_responses_since_go()
    print "first     =",keyboard_response.get_first_response_since_go()
    print "first_time=",keyboard_response.get_time_first_response_since_go()
#   print "last      =",keyboard_response.get_last_response_since_go()
#   print "last_time =",keyboard_response.get_time_last_response_since_go()

#   sleep(1) # Sleep for 1 second
