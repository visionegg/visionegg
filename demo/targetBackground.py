#!/usr/bin/env python

import math
from VisionEgg.Core import *
from VisionEgg.AppHelper import *
from VisionEgg.MoreStimuli import *
from VisionEgg.Textures import *

# Define several "controller" functions
def x_as_function_of_time(t):
    return 25.0*sin(0.1*2.0*math.pi*t)

def y_as_function_of_time(t):
    return 25.0*sin(0.1*2.0*math.pi*t)

def orientation(dummy):
    return 135.0

def angle_as_function_of_time(t):
    return 50.0*math.cos(0.2*2*math.pi*t)

def one_during_experiment(t):
    if t < 0.0:
        return 0.0
    else:
        return 1.0

screen = get_default_screen()
projection = SimplePerspectiveProjection(fov_x=90.0)
viewport = Viewport(screen,(0,0),screen.size,projection)
target = Target2D()
target.init_gl()
try:
    texture = TextureFromFile("orig.bmp") # try to open a texture file
except:
    texture = Texture(size=(256,16)) # otherwise, generate one

drum = SpinningDrum(texture=texture)
drum.init_gl()
viewport.add_stimulus(drum)
viewport.add_stimulus(target) # add target after drum so it is drawn on top

p = Presentation(duration=(10.0,'seconds'),viewports=[viewport])

p.add_realtime_time_controller(target.parameters,'x', x_as_function_of_time)
p.add_realtime_time_controller(target.parameters,'y', y_as_function_of_time)
p.add_realtime_time_controller(drum.parameters,'angle', angle_as_function_of_time)
p.add_transitional_controller(target.parameters,'orientation', orientation)
p.add_transitional_controller(target.parameters,'on', one_during_experiment)
p.add_transitional_controller(drum.parameters,'contrast', one_during_experiment)

p.go()


