#!/usr/bin/env python

from VisionEgg.Core import *
from VisionEgg.Gratings import *
from VisionEgg.AppHelper import *

def phase_as_function_of_time(t):
    return 10.0*t # advance 10 degrees of phase per second

screen = get_default_screen()

width,height = screen.size

# Set the projection so that eye coordinates are window coordinates
projection = OrthographicProjection(right=width,top=height)

# Create the instance of TextureStimulus
stimulus = SinGrating(projection=projection,
                      width=256,
                      height=256,
                      wavelength=25.6,
                      orientation=90.0)

# Set the stimulus to have 1:1 scaling (requires projection as set above)
# This may result in clipping if texture is bigger than screen
stimulus.init_gl()

# Because the stimulus has a projection, we don't care what the
# default is that the viewport uses.
viewport = Viewport(screen,(0,0),screen.size)

viewport.add_stimulus(stimulus)
p = Presentation(duration=(5.0,'seconds'),viewports=[viewport])
p.add_realtime_time_controller(stimulus.parameters,'phase', phase_as_function_of_time)
p.go()
