#!/usr/bin/env python
"""Multiple sinusoidal gratings (with mask)."""

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

######################################
#  Create sinusoidal grating object  #
######################################

mask = Mask2D(function='circle',     # also supports 'gaussian'
              radius_parameter=100,  # radius for circle, sigma for gaussian (units: num_samples)
              num_samples=(256,256)) # this many texture elements in mask (covers whole size specified below)

# NOTE: I have never worked with plaids before, and I'm not sure the
# arithmetic used when combining these gratings is what people want.
# Please submit any suggestions.

sin1 = SinGrating2D(position         = ( screen.size[0]/2.0, screen.size[1]/2.0 ),
                    mask             = mask,
                    size             = ( 500.0 , 500.0 ),
                    spatial_freq     = 10.0 / screen.size[0], # units of cycles/pixel
                    temporal_freq_hz = 0.5,
                    orientation      = 45.0,
                    max_alpha        = 0.5) # controls "opacity": 1.0 = completely opaque, 0.0 = completely transparent

sin2 = SinGrating2D(position         = ( screen.size[0]/2.0, screen.size[1]/2.0 ),
                    mask             = mask,
                    size             = ( 500.0 , 500.0 ),
                    spatial_freq     = 10.0 / screen.size[0], # units of cycles/pixel
                    temporal_freq_hz = 0.5,
                    orientation      = 135.0,
                    max_alpha        = 0.5) # controls "opacity": 1.0 = completely opaque, 0.0 = completely transparent

###############################################################
#  Create viewport - intermediary between stimuli and screen  #
###############################################################

viewport = Viewport( screen=screen, stimuli=[sin1,sin2] )

########################################
#  Create presentation object and go!  #
########################################

p = Presentation(go_duration=(10.0,'seconds'),viewports=[viewport])
p.go()
