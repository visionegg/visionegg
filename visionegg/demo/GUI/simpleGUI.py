#!/usr/bin/env python

from VisionEgg.Core import *
from VisionEgg.AppHelper import *

def angle_as_function_of_time(t):
    return 90.0*t # rotate at 90 degrees per second

VisionEgg.config.VISIONEGG_DEFAULT_INIT = 'GUI' # Naughty to force this way
screen = get_default_screen()
projection = SimplePerspectiveProjection(fov_x=45.0)
viewport = Viewport(screen,(0,0),screen.size,projection)
stimulus = Stimulus()
stimulus.init_gl()
viewport.add_stimulus(stimulus)
p = Presentation(duration_sec=5.0,viewports=[viewport])
p.add_parameter_controller(stimulus.parameters,'yrot', angle_as_function_of_time)
p.go()


