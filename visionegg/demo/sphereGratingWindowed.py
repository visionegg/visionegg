#!/usr/bin/env python

from VisionEgg import *
from VisionEgg.Core import *
from VisionEgg.SphereMap import *
from VisionEgg.Text import *
import math, os
import pygame

mouse_position = (320.0, 240.0)

class MousePositionController( Controller ):
    def __init__(self):
        #global mouse_position
        Controller.__init__(self,
                            return_type=type(None),
                            eval_frequency=Controller.EVERY_FRAME)
        
    def during_go_eval(self,t=None):
        # Convert pygame mouse position to OpenGL position
        global mouse_position
        (x,y) = pygame.mouse.get_pos()
        y = screen.size[1]-y
        mouse_position = (x,y)
        return None

    between_go_eval = during_go_eval

def elevation_func(t=None):
    global mouse_position, screen
    y = mouse_position[1]
    elevation = (float(y) / screen.size[1]) * 180 - 90
    return elevation

def azimuth_func(t=None):
    global mouse_position, screen
    x = mouse_position[0]
    azimuth = (float(x) / screen.size[0]) * 180 - 90
    return azimuth

def quit(event):
    global p # get presentation instance
    p.parameters.quit = 1

def keydown(event):
    global up, down, left, right
    if event.key == pygame.locals.K_ESCAPE:
        quit(event)
        
handle_event_callbacks = [(pygame.locals.QUIT, quit),
                          (pygame.locals.KEYDOWN, keydown)]

screen = get_default_screen()

projection = SimplePerspectiveProjection(fov_x=130.0)
stimulus = SphereGrating(radius=1.0,
                         spatial_freq_cpd=1.0/9.0,
                         temporal_freq_hz=1.0)
mask = SphereWindow(radius=1.0*0.95,
                    window_shape_radius_parameter=20.0)
text = BitmapText(text="Mouse moves window, press Esc to quit",lowerleft=(0,0))
viewport = Viewport(screen=screen,
                    size=screen.size,
                    projection=projection,
                    stimuli=[stimulus,mask]) # mask must be drawn after grating
text_viewport = Viewport(screen=screen, # default (orthographic) viewport
                         stimuli=[text])
p = Presentation(viewports=[viewport,text_viewport],
                 handle_event_callbacks=handle_event_callbacks)
p.add_controller(None, None, MousePositionController() )
elevation_controller = FunctionController(during_go_func=elevation_func,
                                          between_go_func=elevation_func)
azimuth_controller = FunctionController(during_go_func=azimuth_func,
                                        between_go_func=azimuth_func)
p.add_controller(mask,'window_center_elevation', elevation_controller)
p.add_controller(stimulus,'grating_center_elevation', elevation_controller)
p.add_controller(mask,'window_center_azimuth', azimuth_controller)
p.add_controller(stimulus,'grating_center_azimuth', azimuth_controller)
p.run_forever()
