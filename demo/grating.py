#!/usr/bin/env python

# Display a moving sinusoidal grating

from VisionEgg.Core import *
from VisionEgg.Gratings import *
from VisionEgg.AppHelper import *

temporal_frequency_hz = 5.0
phase_controller = EvalStringController(
    during_go_eval_string="%f*t*360.0"%(temporal_frequency_hz,)
    )
    
# Initialize OpenGL graphics screen.
screen = get_default_screen()

# Calculate where the lower left corner of the grating must be to be centered
grating_size = 256
grating_left   = (screen.size[0]/2) - (grating_size/2)
grating_bottom = (screen.size[1]/2) - (grating_size/2)

# Create the instance SinGrating with appropriate parameters
stimulus = SinGrating2D(lowerleft   = ( grating_left , grating_bottom ),
                        size        = ( grating_size , grating_size ),
                        wavelength  = grating_size / 10.0, # 10 cycles over this size
                        orientation = 90.0 )

# Create a viewport (with default pixel coordinate system)
# with stimulus
viewport = Viewport( screen=screen, stimuli=[stimulus] )

# Create an instance of the Presentation class
p = Presentation(duration=(5.0,'seconds'),viewports=[viewport])

# Register the controller functions
p.add_controller(stimulus,'phase', phase_controller)

# Go!
p.go()
