#!/usr/bin/env python

from VisionEgg.Core import *
from VisionEgg.AppHelper import *
from VisionEgg.Textures import *

def angle_as_function_of_time(t):
    return 90.0*t # rotate at 90 degrees per second

screen = get_default_screen()
projection = SimplePerspectiveProjection(fov_x=90.0)
viewport = Viewport(screen,(0,0),screen.size,projection)
stimulus = SpinningDrum()
stimulus.init_gl()
viewport.add_stimulus(stimulus)
p = Presentation(duration_sec=5.0,viewports=[viewport])
p.add_realtime_controller(stimulus.parameters,'angle', angle_as_function_of_time)
p.go()


