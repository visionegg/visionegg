#!/usr/bin/env python

from VisionEgg.Core import *
from VisionEgg.AppHelper import *
from VisionEgg.MoreStimuli import *

# Define several "controller" functions
def x_as_function_of_time(t):
    return 25.0*sin(0.1*2.0*math.pi*t)

def y_as_function_of_time(t):
    return 25.0*sin(0.1*2.0*math.pi*t)

def orientation(dummy_argument):
    return 135.0

def on_during_experiment(t):
    if t < 0.0:
        return 0 # off between stimuli
    else:
        return 1 # on during stimulus presentation
    
screen = get_default_screen()
screen.parameters.bgcolor = (1.0,1.0,1.0,1.0) # background white (RGBA)
viewport = Viewport(screen,(0,0),screen.size)
target = Target2D()
target.init_gl()
target.parameters.color = (0.0,0.0,0.0,1.0) # black target (RGBA)
viewport.add_stimulus(target)
p = Presentation(duration=(10.0,'seconds'),viewports=[viewport])
p.add_realtime_time_controller(target.parameters,'x', x_as_function_of_time)
p.add_realtime_time_controller(target.parameters,'y', y_as_function_of_time)
p.add_transitional_controller(target.parameters,'orientation', orientation)
p.add_transitional_controller(target.parameters,'on', on_during_experiment)
p.go()


