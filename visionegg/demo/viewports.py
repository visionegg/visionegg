#!/usr/bin/env python

from VisionEgg.Core import *
from VisionEgg.AppHelper import *
from VisionEgg.MoreStimuli import *

def angle_as_function_of_time(t):
    return 90.0*t # rotate at 90 degrees per second

screen = get_default_screen()

mid_y = screen.size[1]/2

projection = SimplePerspectiveProjection(fov_x=45.0,aspect_ratio=float(screen.size[0]/mid_y))

viewport1 = Viewport(screen,(0,0),(screen.size[0],mid_y),projection)

viewport2 = Viewport(screen,(0,mid_y),(screen.size[0],mid_y),projection)

stimulus = Teapot()
stimulus.init_gl()
viewport1.add_stimulus(stimulus)
viewport2.add_stimulus(stimulus)
p = Presentation(duration=(5.0,'seconds'),viewports=[viewport1,viewport2])
p.add_realtime_time_controller(stimulus.parameters,'yrot', angle_as_function_of_time)
p.go()


