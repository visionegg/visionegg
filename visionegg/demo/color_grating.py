#!/usr/bin/env python
"""Colored sine wave grating in circular mask"""

############################
#  Import various modules  #
############################

import VisionEgg
VisionEgg.start_default_logging(); VisionEgg.watch_exceptions()

from VisionEgg.Core import *
from VisionEgg.FlowControl import Presentation, FunctionController
from VisionEgg.Gratings import SinGrating2D
from VisionEgg.Textures import Mask2D
from math import *

#####################################
#  Initialize OpenGL window/screen  #
#####################################

screen = get_default_screen()

######################################
#  Create sinusoidal grating object  #
######################################

mask = Mask2D(function='circle',   # also supports 'circle'
              radius_parameter=100,   # sigma for gaussian, radius for circle (units: num_samples)
              num_samples=(256,256)) # this many texture elements in mask (covers whole size specified below)

# NOTE: I am not a color scientist, and I am not familiar with the
# needs of color scientists.  Color interpolation is currently done in
# RGB space, but I assume there are other interpolation methods that
# people may want.  Please submit any suggestions.

stimulus = SinGrating2D(color1           = (0.5, 0.25, 0.5), # RGB (alpha ignored if given)
                        color2           = (1.0, 0.5,  0.1), # RGB (alpha ignored if given)
                        contrast         = 0.2,
                        pedestal         = 0.1,
                        mask             = mask, # optional
                        position         = ( screen.size[0]/2.0, screen.size[1]/2.0 ),
                        anchor           = 'center',
                        size             = ( 300.0 , 300.0 ),
                        spatial_freq     = 20.0 / screen.size[0], # units of cycles/pixel
                        temporal_freq_hz = 1.0,
                        orientation      = 270.0 )

def pedestal_func(t):
    # Calculate pedestal over time. (Pedestal range [0.1,0.9] and
    # contrast = 0.2 limits total range to [0.0,1.0])
    temporal_freq_hz = 0.2
    return 0.4 * sin(t*2*pi * temporal_freq_hz) + 0.5

###############################################################
#  Create viewport - intermediary between stimuli and screen  #
###############################################################

viewport = Viewport( screen=screen, stimuli=[stimulus] )

########################################
#  Create presentation object and go!  #
########################################

p = Presentation(go_duration=(10.0,'seconds'),viewports=[viewport])
p.add_controller(stimulus,'pedestal',FunctionController(during_go_func=pedestal_func))
p.go()
