#!/usr/bin/env python
"""Perspective-distorted sin grating in gaussian window"""

show_grid = 0 # show grid on which grating is defined

from VisionEgg import *
from VisionEgg.Core import *
from VisionEgg.Gratings import *
from VisionEgg.SphereMap import *
from VisionEgg.Text import *
from VisionEgg.Textures import *
import VisionEgg.ParameterTypes as ve_types
import math, os
import pygame

if show_grid:
    from VisionEgg.Textures import *

mouse_position = (320.0, 240.0)
elevation = 0.0
azimuth = 0.0

class MousePositionController( Controller ):
    def __init__(self):
        global mouse_position
        Controller.__init__(self,
                            return_type=ve_types.get_type(None),
                            eval_frequency=Controller.EVERY_FRAME)
        self.between_go_eval = self.during_go_eval # duplicate reference to function
        
    def during_go_eval(self,t=None):
        # Convert pygame mouse position to OpenGL position
        global mouse_position
        (x,y) = pygame.mouse.get_pos()
        y = screen.size[1]-y
        mouse_position = (x,y)
        return None

grating_orient_method = 'reorient stimulus' # start with this as default

def az_el_controller(t=None):
    global mouse_position, screen, elevation
    global grid_stimulus, grating_stimulus, mask
    global grating_orient_method
    x,y = mouse_position
    azimuth = (float(x) / screen.size[0]) * 180 - 90
    elevation = (float(y) / screen.size[1]) * 180 - 90
    text1.parameters.text = "Mouse moves window, press Esc to quit. Az, El = (%5.1f, %5.1f)"%(azimuth,elevation)
    mask.parameters.window_center_azimuth = azimuth
    mask.parameters.window_center_elevation = elevation
    if grating_orient_method == 'reorient stimulus': # normal
        grid_stimulus.parameters.center_azimuth = azimuth
        grid_stimulus.parameters.center_elevation = elevation
        grating_stimulus.parameters.grating_center_azimuth = azimuth
        grating_stimulus.parameters.grating_center_elevation = elevation
    elif grating_orient_method == 'mask only':
        grating_stimulus.parameters.grating_center_azimuth = 0.0
        grating_stimulus.parameters.grating_center_elevation = 0.0
        grid_stimulus.parameters.center_azimuth = 0.0
        grid_stimulus.parameters.center_elevation = 0.0
    
def quit(event):
    global p # get presentation instance
    p.parameters.go_duration = (0,'frames')

def mouse_button_down(event):
    if event.button == 1:
        global grating_orient_method
        grating_orient_method = 'mask only'

def mouse_button_up(event):
    if event.button == 1:
        global grating_orient_method
        grating_orient_method = 'reorient stimulus'

def keydown(event):
    global grating_stimulus
    if event.key == pygame.locals.K_ESCAPE:
        quit(event)
    elif event.key == pygame.locals.K_KP1:
        grating_stimulus.parameters.orientation = 135.0
    elif event.key == pygame.locals.K_KP2:
        grating_stimulus.parameters.orientation = 90.0
    elif event.key == pygame.locals.K_KP3:
        grating_stimulus.parameters.orientation = 45.0
    elif event.key == pygame.locals.K_KP6:
        grating_stimulus.parameters.orientation = 0.0
    elif event.key == pygame.locals.K_KP9:
        grating_stimulus.parameters.orientation = 315.0
    elif event.key == pygame.locals.K_KP8:
        grating_stimulus.parameters.orientation = 270.0
    elif event.key == pygame.locals.K_KP7:
        grating_stimulus.parameters.orientation = 235.0
    elif event.key == pygame.locals.K_KP4:
        grating_stimulus.parameters.orientation = 180.0
    elif event.key == pygame.locals.K_g:
        grid_stimulus.parameters.on = 1
        grating_stimulus.parameters.on = 0
    elif event.key == pygame.locals.K_s:
        grid_stimulus.parameters.on = 0
        grating_stimulus.parameters.on = 1
        
handle_event_callbacks = [(pygame.locals.QUIT, quit),
                          (pygame.locals.MOUSEBUTTONDOWN, mouse_button_down),
                          (pygame.locals.MOUSEBUTTONUP, mouse_button_up),
                          (pygame.locals.KEYDOWN, keydown)]

screen = get_default_screen()

projection = SimplePerspectiveProjection(fov_x=130.0)

filename = os.path.join(config.VISIONEGG_SYSTEM_DIR,"data/az_el.png")
texture = Texture(filename)
grid_stimulus = SphereMap(texture = texture,
                          shrink_texture_ok = 1,
                          stacks = 100,
                          slices = 100,
                          on=0)
try:
    # We want the maximum number of samples possible, hopefully 2048
    grating_stimulus = SphereGrating(num_samples=2048,
                                     radius = 1.0,
                                     spatial_freq_cpd = 1.0/9.0,
                                     temporal_freq_hz = 1.0,
                                     slices = 50,
                                     stacks = 50)
except NumSamplesTooLargeError:
    grating_stimulus = SphereGrating(num_samples=1024,
                                     radius = 1.0,
                                     spatial_freq_cpd = 1.0/9.0,
                                     temporal_freq_hz = 1.0,
                                     slices = 50,
                                     stacks = 50)
    
mask = SphereWindow(radius=1.0*0.90, # make sure window is inside sphere with grating
                    window_shape_radius_parameter=40.0,
                    slices=50,
                    stacks=50)

text_color = (0.0,0.0,1.0,0.0) # RGBA (light blue)
center_x = screen.size[0]/2.0
kw = {'anchor':'bottom','color':text_color,'font_size':30}
text4 = Text( text = "(Hold mouse button to prevent re-orienting stimulus with mask.)",
              position=(center_x,0),**kw)
ypos = text4.parameters.size[1] + 10
text3 = Text( text = "Numeric keypad changes grating orientation.",
              position=(center_x,ypos),**kw)
ypos += text3.parameters.size[1] + 10
text2 = Text( text = "'s' displays sinusoidal grating, 'g' displays (az, el) grid.",
              position=(center_x,ypos),**kw)
ypos += text2.parameters.size[1] + 10
text1 = Text( text = "Mouse moves mask, press Esc to quit. Az, El = (%05.1f, %05.1f)"%(azimuth,elevation),
              position=(center_x,ypos),**kw)
ypos += text1.parameters.size[1] + 10
text0 = Text( text = "Demonstration of perspective distorted, windowed grating.",
              position=(center_x,ypos),**kw)
viewport = Viewport(screen=screen,
                    size=screen.size,
                    projection=projection,
                    stimuli=[grid_stimulus,
                             grating_stimulus,
                             mask]) # mask must be drawn after others
text_viewport = Viewport(screen=screen, # default (orthographic) viewport
                         stimuli=[text0,
                                  text1,
                                  text2,
                                  text3,
                                  text4])
p = Presentation(go_duration=('forever',),
                 viewports=[viewport,text_viewport],
                 handle_event_callbacks=handle_event_callbacks)

p.add_controller(None, None, MousePositionController() )

p.add_controller(None,None,FunctionController(during_go_func=az_el_controller,
                                              between_go_func=az_el_controller))

p.go()
