#!/usr/bin/env python
"""Demonstrate the loading of .3ds file using the lib3ds library."""

from math import *
import os
from VisionEgg import *
start_default_logging(); watch_exceptions()

from VisionEgg.Core import *
from VisionEgg.FlowControl import Presentation, FunctionController
from VisionEgg.Lib3DS import *
from VisionEgg.MoreStimuli import *
from Numeric import *

model_path = os.path.join(config.VISIONEGG_USER_DIR,"3dmodels")

building_file = os.path.join(model_path,"bldskyl1.3ds")
fly_file = os.path.join(model_path,"a3dwasp.3ds")
truck_file = os.path.join(model_path,"a3dsemi.3ds")
car_file = os.path.join(model_path,"autshdm1.3DS")

# Because we can't include the .3ds files with the Vision Egg
# (licensing issues), check to see if they are there and give warning
# if not.  If someone wants to donate some .3ds file to the Vision Egg
# project, that would be great!

error_string = (".3ds file \"%s\" not found.\nDownload from " +
    "http://www.amazing3d.com/free/free.html and try again.")

if not os.access(building_file,os.R_OK):
    raise RuntimeError(error_string%(building_file,))
if not os.access(fly_file,os.R_OK):
    raise RuntimeError(error_string%(fly_file,))
if not os.access(truck_file,os.R_OK):
    raise RuntimeError(error_string%(truck_file,))
if not os.access(car_file,os.R_OK):
    raise RuntimeError(error_string%(car_file,))
    
screen = get_default_screen()
screen.parameters.bgcolor = (0.0,0.0,0.3,0.0)

aspect = float(screen.size[0]) / (screen.size[1] / 2.0)

buildings = Model3DS(filename=building_file,
                     shrink_texture_ok=1)
truck = Model3DS(filename=truck_file,
                 position=array((-2000.0,0.0,-1000.0)),
                 orient_angle=90.0,
                 orient_axis=array((0.0,1.0,0.0)),
                 shrink_texture_ok=1)
car = Model3DS(filename=car_file,
               position=array((-2000.0,0.0,-1100.0)),
               orient_angle=90.0,
               orient_axis=array((0.0,1.0,0.0)),
               shrink_texture_ok=1)
fly = Model3DS(filename=fly_file,
               scale=array((10.0,10.0,10.0)),
               orient_angle=90.0,
               orient_axis=array((0.0,1.0,0.0)),
               shrink_texture_ok=1)
ground = Rectangle3D(color=(0.0,0.6,0.0,0.0),
                     vertex1=array(( -10000.0, 0.0, -10000.0)),
                     vertex2=array(( -10000.0, 0.0,  10000.0)),
                     vertex3=array((  10000.0, 0.0,  10000.0)),
                     vertex4=array((  10000.0, 0.0, -10000.0)),
                     )

# The top viewport shows tracks the fly from a circling POV above the
# buildings

projection1 = SimplePerspectiveProjection(fov_x=90.0,aspect_ratio=aspect)
viewport1 = Viewport(screen=screen,
                     position=(0,screen.size[1]/2),
                     anchor='lowerleft',
                     size=(screen.size[0],screen.size[1]/2),
                     projection=projection1,
                     stimuli=[ground,buildings,car,truck,fly])

# The bottom viewport is the fly eye view of the world

projection2 = SimplePerspectiveProjection(fov_x=90.0,aspect_ratio=aspect)
viewport2 = Viewport(screen=screen,
                     position=(0,0),
                     anchor='lowerleft',
                     size=(screen.size[0],screen.size[1]/2),
                     projection=projection2,
                     stimuli=[ground,buildings,car,truck])

p = Presentation(go_duration=(15.0,'seconds'),viewports=[viewport1,viewport2])

# This defines the fly's position in space as a function of time
def fly_pos_f(t):
    if t <=10.0:
        return array((1000.0-t*300.0,50.0,-1000.0))
    else:
        t = 10.0
        return array((1000.0-t*300.0,50.0,-1000.0))

def car_pos_f(t):
    return Numeric.array((-3000.0+t*330.0,0.0,-1100.0))

# This defines the perspective projection of the top viewport
def projection_matrix1_f(t):
    # Create a projection that we use to manipulate a projection matrix.
    projection = SimplePerspectiveProjection( fov_x=85.0,
                                              z_clip_near=1.,
                                              z_clip_far=100000.,
                                              aspect_ratio=aspect)
    eye = fly_pos_f(t)
    eye += (100.0*cos(0.5*t),10.0,30.0*sin(0.5*t))
    camera_look_at = fly_pos_f(t)
    camera_up = (0.0,1.0,0.0)
    projection.look_at( eye, camera_look_at, camera_up)
    return Numeric.array(projection.get_matrix())

# This defines the perspective projection of the bottom viewport
def projection_matrix2_f(t):
    # Create a projection that we use to manipulate a projection matrix.
    projection = SimplePerspectiveProjection( fov_x=135.0,
                                              z_clip_near=10.,
                                              z_clip_far=100000.,
                                              aspect_ratio=aspect)
    eye = fly_pos_f(t)
    camera_look_at = fly_pos_f(t) + array((-1.0,0.0,0.0)) # look ahead
    camera_up = (0.0,1.0,0.0)
    projection.look_at( eye, camera_look_at, camera_up)
    return Numeric.array(projection.get_matrix())

p.add_controller(projection1,'matrix',
                 FunctionController(during_go_func=projection_matrix1_f))
p.add_controller(projection2,'matrix',
                 FunctionController(during_go_func=projection_matrix2_f))
p.add_controller(fly,'position', FunctionController(during_go_func=fly_pos_f))
p.add_controller(car,'position', FunctionController(during_go_func=car_pos_f))

p.go()
