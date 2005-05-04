#!/usr/bin/env python
"""Demo for the arrow stimulus."""

# Author(s): Hubertus Becker <hubertus.becker@uni-tuebingen.de>
# Copyright: (C) 2004-2005 by Hertie Institute for Clinical Brain Research,
#            Department of Cognitive Neurology, University of Tuebingen
# URL:       http://www.hubertus-becker.de/resources/visionegg/
# $Revision$  $Date$


############################
#  Import various modules  #
############################

import VisionEgg
VisionEgg.start_default_logging();
VisionEgg.watch_exceptions()

from VisionEgg.Core import *
from VisionEgg.FlowControl import Presentation

from VisionEgg.MoreStimuli import *

#####################################
#  Initialize OpenGL window/screen  #
#####################################

screen = get_default_screen()
screen.parameters.bgcolor = (0.0,0.0,0.0,0.0) # Make it black (RGBA)

######################################
#  Arrow stimulus                    #
######################################

stimulus = Arrow(
    anchor      = 'center',
    position    = (screen.size[0]/2.0, screen.size[1]/2.0),
    size        = (64.0, 16.0),
    color       = (1.0, 1.0, 1.0, 1.0), # Draw it in white (RGBA)
    orientation = 0.0 # Right
)

###############################################################
#  Create viewport - intermediary between stimuli and screen  #
###############################################################

viewport = Viewport( screen=screen, stimuli=[stimulus] )

########################################
#  Create presentation object and go!  #
########################################

p = Presentation(go_duration=(5.0, 'seconds'), viewports=[viewport])
p.go()
