#!/usr/bin/env python
"""Demo for the fixation point stimulus."""

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
screen.parameters.bgcolor = (0.0,0.0,0.0,0.0) # make it black (RGBA)

######################################
#  Create fixation point stimulus    #
######################################

stimulus = FilledCircle(
  anchor   = 'center',
  position = (screen.size[0]/2.0, screen.size[1]/2.0),
  radius   = 5.0,
  color    = (255, 0, 0) # Draw it in red
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
