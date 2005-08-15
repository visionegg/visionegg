#!/usr/bin/env python
"""2 viewports, one with a changing perspective."""

import math,os
from VisionEgg import *
start_default_logging(); watch_exceptions()

from VisionEgg.Core import *
from VisionEgg.FlowControl import Presentation, FunctionController
from VisionEgg.Textures import *
from OpenGL.GL import *

def angle_as_function_of_time(t):
    return 90.0*t # rotate at 90 degrees per second

def cam_matrix_f(t):
    projection = Projection()#SimplePerspectiveProjection(fov_x=55.0,aspect_ratio=(screen.size[0]/2.)/screen.size[1])
    eye = (0.0,t*0.3+1.0,-2.0)
    camera_look_at = (0.0,0.0,0.0)
    camera_up = (0.0,1.0,0.0)
    projection.look_at( eye, camera_look_at, camera_up)
    return projection.get_matrix()
    
screen = get_default_screen()
mid_x = screen.size[0]/2
mid_y = screen.size[1]/2
projection1 = SimplePerspectiveProjection(fov_x=90.0,
                                          aspect_ratio=(float(mid_x)/screen.size[1]))
projection2 = SimplePerspectiveProjection(fov_x=55.0,
                                          aspect_ratio=(float(mid_x)/screen.size[1]))

camera_matrix = ModelView() # Parameters set in realtime, so no need to specify here

# Get a texture
filename = os.path.join(config.VISIONEGG_SYSTEM_DIR,"data","panorama.jpg")
texture = Texture(filename)

stimulus = SpinningDrum(texture=texture,shrink_texture_ok=1)
viewport1 = Viewport(screen=screen,
                     position=(0,0),
                     anchor='lowerleft',
                     size=(mid_x,screen.size[1]),
                     projection=projection1,
                     stimuli=[stimulus])
viewport2 = Viewport(screen=screen,
                     position=(mid_x,0),
                     anchor='lowerleft',
                     size=(mid_x,screen.size[1]),
                     projection=projection2,
                     camera_matrix=camera_matrix,
                     stimuli=[stimulus])

p = Presentation(go_duration=(10.0,'seconds'),viewports=[viewport1,viewport2])

p.add_controller(stimulus,'angular_position', FunctionController(during_go_func=angle_as_function_of_time))
p.add_controller(camera_matrix,'matrix', FunctionController(during_go_func=cam_matrix_f))

p.go()
