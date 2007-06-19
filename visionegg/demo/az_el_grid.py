#!/usr/bin/env python
"""Azimuth and elevation grid"""

from VisionEgg import *
start_default_logging(); watch_exceptions()

from VisionEgg.Core import *
from VisionEgg.FlowControl import Presentation, FunctionController
from VisionEgg.SphereMap import *
from VisionEgg.Textures import *
import math, os

import numpy
numpy.seterr(all='raise')

def projection_matrix_f(t):
    # This bit of code is from the "movingPOV" demo and can be used to
    # gain a moving external view of the texture-mapped sphere by
    # uncommenting the appropriate line below.
    projection = SimplePerspectiveProjection(fov_x=55.0,aspect_ratio=(screen.size[0]/2.)/screen.size[1])
    eye = (0.0,t*0.3+1.0,-2.0)
    camera_look_at = (0.0,0.0,0.0)
    camera_up = (0.0,1.0,0.0)
    projection.look_at( eye, camera_look_at, camera_up)
    return projection.get_matrix()

screen = get_default_screen()
screen.parameters.bgcolor = (1.0,1.0,1.0,1.0)

projection = SimplePerspectiveProjection(fov_x=90.0)
text_viewport = Viewport(screen=screen)
stimulus = AzElGrid()
viewport = Viewport(screen=screen,
                    projection=projection,
                    stimuli=[stimulus])
stimulus.parameters.my_viewport = viewport # set afterwards
p = Presentation(go_duration=(10.0,'seconds'),viewports=[viewport])#,text_viewport])
#p.add_controller(projection,'matrix', FunctionController(during_go_func=projection_matrix_f))
p.go()
