#!/usr/bin/env python
"""Perspective-distorted sinusoidal grating."""

from VisionEgg.Core import *
from VisionEgg.Gratings import *

# Initialize OpenGL graphics screen.
screen = get_default_screen()

# Create a perspective projection
monitor_width_degrees = 90.0
perspective = SimplePerspectiveProjection(fov_x=monitor_width_degrees)

# Create the instance SinGrating with appropriate parameters
num_samples = 2048
success = 0
while not success:
    try:
        # The next line raises a NumSamplesTooLargeError exception if num_samples too large
        stimulus = SinGrating3D(spatial_freq_cpd = 1.0/18.0,
                                temporal_freq_hz = 5.0,
                                orientation = 0.0,
                                num_samples = num_samples)
        # Doesn't get here unless successful
        success = 1
    except NumSamplesTooLargeError:
        num_samples = num_samples / 2
        
# Create a viewport with the perspective projection and stimulus
viewport = Viewport(screen=screen,
                    projection=perspective,
                    stimuli=[stimulus])

# Create an instance of the Presentation class
p = Presentation(go_duration=(10.0,'seconds'),viewports=[viewport])

# Go!
p.go()
