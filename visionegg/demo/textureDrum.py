#!/usr/bin/env python
"""A texture-mapped spinning drum."""

from VisionEgg import *
start_default_logging(); watch_exceptions()

from VisionEgg.Core import *
from VisionEgg.FlowControl import Presentation, FunctionController
from VisionEgg.Textures import *
import math, os

max_speed = 100.0 # degrees per second

def angle_as_function_of_time(t):
    return max_speed*math.cos(t)

def contrast_as_function_of_time(t):
    return abs(math.cos(2*math.pi*t*0.2))

filename = os.path.join(config.VISIONEGG_SYSTEM_DIR,"data","panorama.jpg")
texture = Texture(filename)

screen = get_default_screen()
projection = SimplePerspectiveProjection(fov_x=90.0)
stimulus = SpinningDrum(texture=texture,shrink_texture_ok=1)
viewport = Viewport(screen=screen,
                    size=screen.size,
                    projection=projection,
                    stimuli=[stimulus])
p = Presentation(go_duration=(10.0,'seconds'),viewports=[viewport])
p.add_controller(stimulus,'angular_position', FunctionController(during_go_func=angle_as_function_of_time))
p.add_controller(stimulus,'contrast', FunctionController(during_go_func=contrast_as_function_of_time))
p.go()


