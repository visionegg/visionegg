#!/usr/bin/env python

from VisionEgg.Core import *
from VisionEgg.MoreStimuli import *
from VisionEgg.AppHelper import *

def angle_as_function_of_time(t):
    return 90.0*t # rotate at 90 degrees per second

screen = get_default_screen()
projection = SimplePerspectiveProjection(fov_x=45.0)
viewport = Viewport(screen,(0,0),screen.size,projection)
stimulus = Teapot()
stimulus.init_gl()
viewport.add_stimulus(stimulus)
p = Presentation(duration=(5.0,'seconds'),viewports=[viewport])
p.add_realtime_time_controller(stimulus.parameters,'yrot', angle_as_function_of_time)
p.go()


