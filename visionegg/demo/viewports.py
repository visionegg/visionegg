#!/usr/bin/env python

from VisionEgg.Core import *
from VisionEgg.AppHelper import *
from VisionEgg.MoreStimuli import *

def angle_as_function_of_time(t):
    return 90.0*t # rotate at 90 degrees per second

screen = get_default_screen()
projection = SimplePerspectiveProjection(fov_x=45.0)

midscreen = (screen.size[0]/2,screen.size[1]/2)

viewport1 = Viewport(screen,(0,0),midscreen,projection)
viewport2 = Viewport(screen,midscreen,midscreen,projection)
stimulus = Teapot()
stimulus.init_gl()
viewport1.add_stimulus(stimulus)
viewport2.add_stimulus(stimulus)
p = Presentation(duration_sec=5.0,viewports=[viewport1,viewport2])
p.add_realtime_controller(stimulus.parameters,'yrot', angle_as_function_of_time)
p.go()


