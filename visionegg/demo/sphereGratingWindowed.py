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
import OpenGL.GL as gl

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

shift_key = 0

def keyup(event):
    global shift_key
    if event.key in [pygame.locals.K_LSHIFT,pygame.locals.K_RSHIFT]:
        shift_key = 0

def keydown(event):
    global grating_stimulus, mask, text1_5, text1_75
    global shift_key
    if event.key == pygame.locals.K_ESCAPE:
        quit(event)
    elif event.key in [pygame.locals.K_LSHIFT,pygame.locals.K_RSHIFT]:
        shift_key = 1
    elif event.key == pygame.locals.K_KP1:
        grating_stimulus.parameters.orientation = 225.0
    elif event.key == pygame.locals.K_KP2:
        grating_stimulus.parameters.orientation = 270.0
    elif event.key == pygame.locals.K_KP3:
        grating_stimulus.parameters.orientation = 315.0
    elif event.key == pygame.locals.K_KP6:
        grating_stimulus.parameters.orientation = 0.0
    elif event.key == pygame.locals.K_KP9:
        grating_stimulus.parameters.orientation = 45.0
    elif event.key == pygame.locals.K_KP8:
        grating_stimulus.parameters.orientation = 90.0
    elif event.key == pygame.locals.K_KP7:
        grating_stimulus.parameters.orientation = 135.0
    elif event.key == pygame.locals.K_KP4:
        grating_stimulus.parameters.orientation = 180.0
    elif event.key == pygame.locals.K_s:
        if shift_key:
            grating_stimulus.parameters.spatial_freq_cpd *= (1.0/1.5)
        else:
            grating_stimulus.parameters.spatial_freq_cpd *= 1.5
        text1_5.parameters.text = "'-' shrinks window, '+' grows window, 's/S' changes SF (now %.2f cycles per degree)"%(grating_stimulus.parameters.spatial_freq_cpd)
    elif event.key == pygame.locals.K_t:
        if shift_key:
            grating_stimulus.parameters.temporal_freq_hz *= (1.0/1.5)
        else:
            grating_stimulus.parameters.temporal_freq_hz *= 1.5
        text1_6.parameters.text = "'t/T' changes TF (now %.2f hz)"%(grating_stimulus.parameters.temporal_freq_hz)
    elif event.key == pygame.locals.K_c:
        if shift_key:
            grating_stimulus.parameters.lowpass_cutoff_cycles_per_texel *= (1.0/1.5)
        else:
            grating_stimulus.parameters.lowpass_cutoff_cycles_per_texel *= 1.5
        text1_75.parameters.text = "'c/C' changes cutoff SF (now %.2f cycles per texel)"%(grating_stimulus.parameters.lowpass_cutoff_cycles_per_texel)
    elif event.key == pygame.locals.K_g:
        grid_stimulus.parameters.on = not grid_stimulus.parameters.on
        grating_stimulus.parameters.on = not grating_stimulus.parameters.on
    elif event.key == pygame.locals.K_f:
        global cur_min_filter_index
        cur_min_filter_index = (cur_min_filter_index+1) % len(min_filters)
        min_filter = min_filters[cur_min_filter_index]
        text2.parameters.text = "'g' toggles grid display, 'f' cycles min_filter (now %s)"%min_filter
        min_filter_int = eval("gl."+min_filter)
        grating_stimulus.parameters.min_filter = min_filter_int
    elif event.key == pygame.locals.K_MINUS:
        mask.parameters.window_shape_radius_parameter *= 0.8
    elif event.key == pygame.locals.K_EQUALS:
        mask.parameters.window_shape_radius_parameter *= (1.0/0.8)
        
handle_event_callbacks = [(pygame.locals.QUIT, quit),
                          (pygame.locals.MOUSEBUTTONDOWN, mouse_button_down),
                          (pygame.locals.MOUSEBUTTONUP, mouse_button_up),
                          (pygame.locals.KEYDOWN, keydown),
                          (pygame.locals.KEYUP, keyup)]

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

min_filters = ['GL_NEAREST_MIPMAP_NEAREST',
               'GL_NEAREST_MIPMAP_LINEAR',
               'GL_LINEAR_MIPMAP_LINEAR',
               'GL_LINEAR_MIPMAP_NEAREST',
               'GL_NEAREST',
               'GL_LINEAR']
        
cur_min_filter_index = None
filter_used = grating_stimulus.parameters.min_filter
for filter_test_index in range(len(min_filters)):
    filter_test = min_filters[filter_test_index]
    if filter_used == eval("gl."+filter_test):
        cur_min_filter_index = filter_test_index
        break
if cur_min_filter_index is None:
    raise RuntimeError("Couldn't find min filter used")
    
mask = SphereWindow(radius=1.0*0.90, # make sure window is inside sphere with grating
                    window_shape_radius_parameter=40.0,
                    slices=50,
                    stacks=50)

text_color = (0.0,0.0,1.0,0.0) # RGBA (light blue)
xpos = 10.0
yspace = 5
kw = {'anchor':'lowerleft','color':text_color,'font_size':20}
text4 = Text( text = "(Hold mouse button to prevent re-orienting stimulus with mask.)",
              position=(xpos,0),**kw)
ypos = text4.parameters.size[1] + yspace
text3 = Text( text = "Numeric keypad changes grating orientation.",
              position=(xpos,ypos),**kw)
ypos += text3.parameters.size[1] + yspace

text2 = Text( text = "'g' toggles grid display",
              position=(xpos,ypos),**kw)

min_filter = min_filters[cur_min_filter_index]
text2.parameters.text = "'g' toggles grid display, 'f' cycles min_filter (now %s)"%min_filter

ypos += text2.parameters.size[1] + yspace
text1_75 = Text(text='temp text',
               position=(xpos,ypos),**kw)
text1_75.parameters.text = "'c/C' changes cutoff SF (now %.2f cycles per texel)"%(grating_stimulus.parameters.lowpass_cutoff_cycles_per_texel)

ypos += text1_75.parameters.size[1] + yspace
text1_6 = Text(text='temp text',
               position=(xpos,ypos),**kw)
text1_6.parameters.text = "'t/T' changes TF (now %.2f hz)"%(grating_stimulus.parameters.temporal_freq_hz)

ypos += text1_6.parameters.size[1] + yspace
text1_5 = Text(text='temp text',
               position=(xpos,ypos),**kw)
text1_5.parameters.text = "'-' shrinks window, '+' grows window, 's/S' changes SF (now %.2f cycles per degree)"%(grating_stimulus.parameters.spatial_freq_cpd)

ypos += text1_5.parameters.size[1] + yspace
text1 = Text( text = "Mouse moves window, press Esc to quit. Az, El = (%05.1f, %05.1f)"%(azimuth,elevation),
              position=(xpos,ypos),**kw)
ypos += text1.parameters.size[1] + yspace
text0 = Text( text = "Demonstration of perspective distorted, windowed grating.",
              position=(xpos,ypos),**kw)
viewport = Viewport(screen=screen,
                    size=screen.size,
                    projection=projection,
                    stimuli=[grid_stimulus,
                             grating_stimulus,
                             mask]) # mask must be drawn after others
text_viewport = Viewport(screen=screen, # default (orthographic) viewport
                         stimuli=[text0,
                                  text1,
                                  text1_5,
                                  text1_6,
                                  text1_75,
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
