#!/usr/bin/env python
"""Sinusoidal gratings calculated in realtime."""

############################
#  Import various modules  #
############################

import VisionEgg
VisionEgg.start_default_logging(); VisionEgg.watch_exceptions()

from VisionEgg.Core import *
from VisionEgg.FlowControl import Presentation
from VisionEgg.Gratings import *

#####################################
#  Initialize OpenGL window/screen  #
#####################################

screen = get_default_screen()

#######################################
#  Create sinusoidal grating objects  #
#######################################

size = (50,100)
grating_data_size = max(size)*2, max(size)*2 # make sure tilting it doesn't show edges

up = SinGrating2D(position         = ( size[0]/2.0, size[1]/2.0 ),
                  anchor           = 'center',
                  size             = grating_data_size,
                  spatial_freq     = 1.0/30.0, # units of cycles/pixel
                  temporal_freq_hz = 1.0,
                  orientation      = 80.0,
                  recalculate_phase_tolerance = 5.0, # speedup
                  )

down = SinGrating2D(position         = ( size[0]/2.0, size[1]/2.0 ),
                    anchor           = 'center',
                    size             = grating_data_size,
                    spatial_freq     = 1.0/30.0, # units of cycles/pixel
                    temporal_freq_hz = 1.0,
                    orientation      = -80.0,
                    recalculate_phase_tolerance = 5.0, # speedup
                    )

################################################################
#  Create viewports - intermediary between stimuli and screen  #
################################################################

x_space = 10
y_space = 10

viewports = []

for x in range(size[0]+x_space,screen.size[0],size[0]+x_space):
    even_row = 0
    for y in range(size[1]+y_space,screen.size[1],size[1]+y_space):
        even_row = not even_row
        if even_row:
            stimulus = up
        else:
            stimulus = down
            
        viewports.append( Viewport( screen=screen,
                                    stimuli=[stimulus],
                                    position=(x,y),
                                    anchor='top',
                                    size=size))

########################################
#  Create presentation object and go!  #
########################################

p = Presentation(go_duration=(10.0,'seconds'),viewports=viewports)
p.go()
