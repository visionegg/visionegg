#!/usr/bin/env python
"""A demonstration of 2 viewports.

The viewport on the right looks a little bit strange, I think
due to clipping of the projection."""
import math

import VisionEgg
from VisionEgg.Core import *
from VisionEgg.AppHelper import *
from VisionEgg.MotionBlur import *

from OpenGL.GL import *
from OpenGL.GLU import *

max_speed = 500.0 # degrees per second

def angle_as_function_of_time(t):
    return max_speed*math.cos(t) # rotate at 90 degrees per second

def projection_matrix_f(t):
    matrix_mode = glGetIntegerv(GL_MATRIX_MODE) # Save the GL of the matrix state
    glMatrixMode(GL_PROJECTION)
    glPushMatrix()
    glLoadIdentity()
    gluLookAt(0.0,t*0.1,0.0,
              0.0,0.0,1.0,
              0.0,1.0,0.0)
    results = glGetFloatv(GL_PROJECTION_MATRIX)
    glPopMatrix()
    if matrix_mode != GL_PROJECTION:
        glMatrixMode(matrix_mode) # Set the matrix mode back
    return results

screen = get_default_screen()
mid_x = screen.size[0]/2
mid_y = screen.size[1]/2
projection1 = SimplePerspectiveProjection(fov_x=90.0,aspect_ratio=(float(mid_x)/screen.size[1]))
projection2 = SimplePerspectiveProjection(fov_x=135.0,aspect_ratio=(float(mid_x)/screen.size[1]))
projection2.translate(0.0,0.9,0.0)
viewport1 = Viewport(screen,(0,0),(mid_x,screen.size[1]),projection1)
viewport2 = Viewport(screen,(mid_x,0),(mid_x,screen.size[1]),projection2)
stimulus = BlurredDrum(max_speed=max_speed)
stimulus.init_gl()
viewport1.add_stimulus(stimulus)
viewport2.add_stimulus(stimulus)

p = Presentation(duration=(10.0,'seconds'),viewports=[viewport1,viewport2])

p.add_realtime_time_controller(stimulus.parameters,'angle', angle_as_function_of_time)
p.add_realtime_time_controller(stimulus.parameters,'cur_time', lambda t: t)
p.add_realtime_time_controller(projection2.parameters,'matrix', projection_matrix_f)

p.go()


