#!/usr/bin/env python
"""A texture-mapped spinning drum."""

from VisionEgg.Core import *
from VisionEgg.Textures import *
import math

max_speed = 500.0 # degrees per second

def angle_as_function_of_time(t):
    return max_speed*math.cos(t)

def contrast_as_function_of_time(t):
    return abs(math.cos(2*math.pi*t))

try:
    texture = TextureFromFile("orig.bmp") # try to open a texture file
except:
    texture = Texture(size=(256,16)) # otherwise, generate one

screen = get_default_screen()
projection = SimplePerspectiveProjection(fov_x=90.0)
stimulus = SpinningDrum(texture=texture)
viewport = Viewport(screen=screen,
                    size=screen.size,
                    projection=projection,
                    stimuli=[stimulus])
p = Presentation(duration=(5.0,'seconds'),viewports=[viewport])
p.add_realtime_time_controller(stimulus,'angular_position', angle_as_function_of_time)
p.add_realtime_time_controller(stimulus,'contrast', contrast_as_function_of_time)
p.go()


