#!/usr/bin/env python
"""Demonstrate the loading of .3ds file using the lib3ds library."""

from math import *
import os
from VisionEgg import *
from VisionEgg.Core import *
from VisionEgg.Lib3DS import *

screen = get_default_screen()

filename = os.path.join("/3dmodels/insects","a3dwasp.3ds")

# Create the instance of Model3DS
stimulus = Model3DS(filename=filename)

projection = SimplePerspectiveProjection(fov_x=90.0)
viewport = Viewport(screen=screen,
                    size=screen.size,
                    projection=projection,
                    stimuli=[stimulus])

p = Presentation(go_duration=(5.0,'seconds'),viewports=[viewport])

def projection_matrix_f(t):
    projection = SimplePerspectiveProjection(fov_x=55.0)
    eye = (2.*sin(t),3.5,8.*cos(t))
    camera_look_at = (0.0,0.5,0.0)
    camera_up = (0.0,1.0,0.0)
    projection.look_at( eye, camera_look_at, camera_up)
    return projection.get_matrix()

p.add_controller(projection,'matrix', FunctionController(during_go_func=projection_matrix_f))

p.go()
