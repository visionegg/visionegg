#!/usr/bin/env python
"""Sinusoidal color grating calculated in realtime."""

############################
#  Import various modules  #
############################

from VisionEgg.Core import *
from VisionEgg.Gratings import *

#####################################
#  Initialize OpenGL window/screen  #
#####################################

screen = get_default_screen()

######################################
#  Create sinusoidal grating object  #
######################################

stimulus = SinGrating2DColor(color1 = (0.5, 0.25, 0.5, 0.0), # RGBA, Alpha ignored
                             color2 = (1.0, 0.5,  0.1, 0.0), # RGBA, Alpha ignored
                             center           = ( screen.size[0]/2.0, screen.size[1]/2.0 ),
                             size             = ( 300.0 , 300.0 ),
                             spatial_freq     = 20.0 / screen.size[0], # units of cycles/pixel
                             temporal_freq_hz = 1.0,
                             orientation      = 270.0 )

###############################################################
#  Create viewport - intermediary between stimuli and screen  #
###############################################################

viewport = Viewport( screen=screen, stimuli=[stimulus] )

########################################
#  Create presentation object and go!  #
########################################

p = Presentation(go_duration=(5.0,'seconds'),viewports=[viewport])
p.go()
