#!/usr/bin/env python

from VisionEgg.Core import *
from VisionEgg.AppHelper import *
from VisionEgg.Textures import *

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
viewport = Viewport(screen,
                    size=screen.size,
                    projection=projection)
stimulus = SpinningDrum(texture=texture)
viewport.add_stimulus(stimulus)
p = Presentation(duration=(5.0,'seconds'),viewports=[viewport])
p.add_realtime_time_controller(stimulus,'angular_position', angle_as_function_of_time)
p.add_realtime_time_controller(stimulus,'contrast', contrast_as_function_of_time)
p.go()


