#!/usr/bin/env python
"""Sinusoidal grating in a gaussian mask"""

############################
#  Import various modules  #
############################

import VisionEgg
VisionEgg.start_default_logging(); VisionEgg.watch_exceptions()

from VisionEgg.Core import *
from VisionEgg.FlowControl import Presentation
from VisionEgg.Gratings import SinGrating2D
from VisionEgg.Textures import Mask2D

#####################################
#  Initialize OpenGL window/screen  #
#####################################

screen = get_default_screen()

##########################################################
#  Create sinusoidal grating object and gaussian window  #
##########################################################

mask = Mask2D(function='gaussian',   # also supports 'circle'
              radius_parameter=25,   # sigma for gaussian, radius for circle (units: num_samples)
              num_samples=(256,256)) # this many texture elements in mask (covers whole size specified below)

stimulus = SinGrating2D(mask             = mask,
                        position         = ( screen.size[0]/2.0, screen.size[1]/2.0 ),
                        size             = ( 300.0 , 300.0 ),
                        spatial_freq     = 10.0 / screen.size[0], # units of cycles/pixel
                        temporal_freq_hz = 1.0,
                        orientation      = 45.0 )

###############################################################
#  Create viewport - intermediary between stimuli and screen  #
###############################################################

viewport = Viewport( screen=screen, stimuli=[stimulus] )

########################################
#  Create presentation object and go!  #
########################################

p = Presentation(go_duration=(5.0,'seconds'),viewports=[viewport])
p.go()
