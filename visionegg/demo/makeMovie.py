#!/usr/bin/env python

import math, os
from VisionEgg.Core import *
from VisionEgg.AppHelper import *
from VisionEgg.MoreStimuli import *

fps = 12.0 # frames per second

def x_as_function_of_frame(frame):
    t = float(frame) / fps
    return 10.0*sin(0.2*2.0*math.pi*t)

def y_as_function_of_frame(frame):
    t = float(frame) / fps
    return 10.0*sin(0.2*2.0*math.pi*t)

def orientation(dummy):
    return 135.0

def one_during_experiment(t):
    if t < 0.0:
        return 0.0
    else:
        return 1.0

screen = get_default_screen()
projection = SimplePerspectiveProjection(fov_x=45.0)
viewport = Viewport(screen,(0,0),screen.size,projection)
target = Target2D()
target.init_gl()
viewport.add_stimulus(target)

p = Presentation(duration=(60,'frames'),viewports=[viewport])

p.add_realtime_frame_controller(target.parameters,'x', x_as_function_of_frame)
p.add_realtime_frame_controller(target.parameters,'y', y_as_function_of_frame)
p.add_transitional_controller(target.parameters,'orientation', orientation)
p.add_transitional_controller(target.parameters,'on', one_during_experiment)

save_directory = os.path.join(VisionEgg.config.VISIONEGG_STORAGE,'movie')
if not os.path.isdir(save_directory):
    print "Error: cannot save movie, because directory '%s' does not exist."%save_directory
else:
    p.export_movie_go(frames_per_sec=fps,path=save_directory)


