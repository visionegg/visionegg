#!/usr/bin/env python
"""Use the Vision Egg to trigger an external device."""

import VisionEgg
VisionEgg.start_default_logging(); VisionEgg.watch_exceptions()

from VisionEgg.Core import *
from VisionEgg.FlowControl import Presentation
from VisionEgg.Gratings import *
import VisionEgg.Daq
from VisionEgg.DaqLPT import *

# Normal stuff (from grating demo):
screen = get_default_screen()
stimulus = SinGrating2D(position         = ( screen.size[0]/2.0, screen.size[1]/2.0 ),
                        anchor           = 'center',
                        size             = ( 300.0 , 300.0 ),
                        spatial_freq     = 10.0 / screen.size[0], # units of cycles/pixel
                        temporal_freq_hz = 5.0,
                        orientation      = 45.0 )
viewport = Viewport( screen=screen, stimuli=[stimulus] )
p = Presentation(go_duration=(5.0,'seconds'),viewports=[viewport])

# Create a trigger output controller
trigger_out_controller = LPTTriggerOutController()

# Add the trigger output controller to the presentation's list of controllers
p.add_controller(None,None,trigger_out_controller)

# Go!
p.go()
