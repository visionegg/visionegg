#!/usr/bin/env python

from math import *
from VisionEgg.Core import *
from VisionEgg.MotionBlur import *
from VisionEgg.AppHelper import *

max_speed = 1000.0 # degrees per second

def angle_as_function_of_time(t):
    return max_speed*math.cos(t) # rotate at 90 degrees per second

screen = get_default_screen()
projection = SimplePerspectiveProjection(fov_x=90.0)
viewport = Viewport(screen,(0,0),screen.size,projection)
try:
    texture = TextureFromFile("orig.bmp")
except:
    texture = Texture(size=(256,32))
stimulus = BlurredDrum(max_speed=max_speed,texture=texture)
stimulus.init_gl()
viewport.add_stimulus(stimulus)

p = Presentation(duration_sec=10.0,viewports=[viewport])

p.add_realtime_controller(stimulus.parameters,'angle', angle_as_function_of_time)
p.add_realtime_controller(stimulus.parameters,'cur_time', lambda t: t)

p.go()


