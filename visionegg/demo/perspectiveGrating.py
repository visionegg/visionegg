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
stimulus = SinGrating3D(spatial_freq_cpd = 1.0/18.0,
                        temporal_freq_hz = 5.0,
                        orientation = 0.0 )

# Create a viewport with this projection
viewport = Viewport(screen=screen,
                    projection=perspective,
                    stimuli=[stimulus])

# Create an instance of the Presentation class
p = Presentation(duration=(10.0,'seconds'),viewports=[viewport])

# Go!
p.go()
