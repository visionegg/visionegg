#!/usr/bin/env python

import math, os
from VisionEgg.Core import *
from VisionEgg.AppHelper import *
from VisionEgg.MoreStimuli import *
from VisionEgg.MotionBlur import *

fps = 12.0 # frames per second

target_max_velocity = 10.0
drum_max_speed = 1000.0 # degrees per second

def x_as_function_of_time(t):
    return target_max_velocity*sin(0.2*2.0*math.pi*t)

def y_as_function_of_time(t):
    return target_max_velocity*sin(0.2*2.0*math.pi*t)

def orientation(dummy):
    return 135.0

def angle_as_function_of_time(t):
    return drum_max_speed*math.cos(0.1*2.0*math.pi*t)

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
viewport.add_overlay(target)
drum = BlurredDrum(max_speed=drum_max_speed,target_fps=fps)
drum.init_gl()
viewport.add_stimulus(drum)

p = Presentation(duration_sec=10.0,viewports=[viewport])

p.add_realtime_controller(target.parameters,'x', x_as_function_of_time)
p.add_realtime_controller(target.parameters,'y', y_as_function_of_time)
p.add_realtime_controller(drum.parameters,'angle', angle_as_function_of_time)
p.add_realtime_controller(drum.parameters,'cur_time', lambda t: t)
p.add_transitional_controller(target.parameters,'orientation', orientation)
p.add_transitional_controller(target.parameters,'on', one_during_experiment)
p.add_transitional_controller(drum.parameters,'contrast', one_during_experiment)

p.export_movie_go(frames_per_sec=fps,path=os.path.join(VisionEgg.config.VISIONEGG_STORAGE,'movie'))


