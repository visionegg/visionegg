#!/usr/bin/env python

from VisionEgg.Core import *
from VisionEgg.AppHelper import *
from VisionEgg.Textures import *

max_speed = 1000.0 # degrees per second

def angle_as_function_of_time(t):
    return max_speed*math.cos(t)

try:
    texture = TextureFromFile("orig.bmp") # try to open a texture file
except:
    texture = Texture(size=(256,16)) # otherwise, generate one

screen = get_default_screen()
projection = SimplePerspectiveProjection(fov_x=90.0)
viewport = Viewport(screen,(0,0),screen.size,projection)
stimulus = SpinningDrum(texture=texture)
stimulus.init_gl()
viewport.add_stimulus(stimulus)
p = Presentation(duration=(5.0,'seconds'),viewports=[viewport])
p.add_realtime_time_controller(stimulus.parameters,'angle', angle_as_function_of_time)
p.go()


