#!/usr/bin/env python

# Script to display a perspective distorted moving sinusoidal grating.

from VisionEgg.Core import *
from VisionEgg.Gratings import *
from VisionEgg.AppHelper import *

# Define a controller function to move the grating
def phase_as_function_of_time(t):
    temporal_frequency_hz = 2.0
    return temporal_frequency_hz*t*360.0

# Define a second controller to turn off grating between presentations
def on_during_experiment(t):
    if t < 0.0:
        return 0 # off between stimuli
    else:
        return 1 # on during stimulus presentation
    
# Initialize OpenGL graphics screen.
screen = get_default_screen()

# Create a perspective projection
monitor_width_degrees = 90.0
perspective = SimplePerspectiveProjection(fov_x=monitor_width_degrees)

# Create a viewport with this projection
viewport = Viewport(screen=screen,
                    projection=perspective)

# Create the instance SinGrating with appropriate parameters
spatial_frequency_cpd = 0.1 # cycles per degree
stimulus = SinGrating3D(wavelength  = 1.0/spatial_frequency_cpd, # specify wavelength in degrees
                        orientation = 0.0 )

# Add the stimulus to the viewport
viewport.add_stimulus(stimulus)

# Create an instance of the Presentation class
p = Presentation(duration=(10.0,'seconds'),viewports=[viewport])

# Register the controller functions
p.add_realtime_time_controller(stimulus,'phase', phase_as_function_of_time)
p.add_transitional_controller(stimulus,'on', on_during_experiment)

# Go!
p.go()
