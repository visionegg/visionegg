#!/usr/bin/env python

# Display a moving sinusoidal grating

from VisionEgg.Core import *
from VisionEgg.Gratings import *
from VisionEgg.AppHelper import *

# Define a controller function to move the grating
def phase_as_function_of_time(t):
    temporal_frequency_hz = 5.0
    return temporal_frequency_hz*t*360.0

# Define a second controller to turn off grating between presentations
def on_during_experiment(t):
    if t < 0.0:
        return 0 # off between stimuli
    else:
        return 1 # on during stimulus presentation
    
# Initialize OpenGL graphics screen.
screen = get_default_screen()

# Use viewport with pixel coordinate system for projection
viewport = Viewport(screen=screen)

# Calculate where the lower left corner of the grating must be to be centered
grating_size = 256
grating_left   = (screen.size[0]/2) - (grating_size/2)
grating_bottom = (screen.size[1]/2) - (grating_size/2)

# Create the instance SinGrating with appropriate parameters
stimulus = SinGrating2D(lowerleft   = ( grating_left , grating_bottom ),
                        size        = ( grating_size , grating_size ),
                        wavelength  = grating_size / 10.0, # 10 cycles over this size
                        orientation = 90.0 )

# Add the stimulus to the viewport
viewport.add_stimulus(stimulus)

# Create an instance of the Presentation class
p = Presentation(duration=(5.0,'seconds'),viewports=[viewport])

# Register the controller functions
p.add_realtime_time_controller(stimulus,'phase', phase_as_function_of_time)
p.add_transitional_controller(stimulus,'on', on_during_experiment)

# Go!
p.go()
