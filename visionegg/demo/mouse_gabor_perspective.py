#!/usr/bin/env python
"""Perspective-distorted sinusoidal grating in gaussian window"""

from VisionEgg import *
start_default_logging(); watch_exceptions()

from VisionEgg.Core import *
from VisionEgg.Gratings import *
from VisionEgg.SphereMap import *
from VisionEgg.Text import *
from VisionEgg.Textures import *
import VisionEgg.ParameterTypes as ve_types
import math, os
import pygame
import OpenGL.GL as gl

elevation = 0.0
azimuth = 0.0
fov_x = 90.0

def get_mouse_position():
    # convert to OpenGL coordinates
    (x,y) = pygame.mouse.get_pos()
    y = screen.size[1]-y
    return x,y

grating_orient_method = 'reorient stimulus' # start with this as default

def set_az_el(x,y):
    global screen, elevation
    global grid_stimulus_moving, grating_stimulus, mask
    global grating_orient_method
    azimuth = (float(x) / screen.size[0]) * 180 - 90
    elevation = (float(y) / screen.size[1]) * 180 - 90
    az_el_text.parameters.text = "Mouse moves window, press Esc to quit. Az, El = (%5.1f, %5.1f)"%(azimuth,elevation)
    mask.parameters.window_center_azimuth = azimuth
    mask.parameters.window_center_elevation = elevation
    if grating_orient_method == 'reorient stimulus': # normal
        grid_stimulus_moving.parameters.center_azimuth = azimuth
        grid_stimulus_moving.parameters.center_elevation = elevation
        grating_stimulus.parameters.grating_center_azimuth = azimuth
        grating_stimulus.parameters.grating_center_elevation = elevation
    elif grating_orient_method == 'mask only':
        grating_stimulus.parameters.grating_center_azimuth = 0.0
        grating_stimulus.parameters.grating_center_elevation = 0.0
        grid_stimulus_moving.parameters.center_azimuth = 0.0
        grid_stimulus_moving.parameters.center_elevation = 0.0

screen = get_default_screen()
projection_3d = SimplePerspectiveProjection(fov_x=fov_x)
grid_stimulus_moving = AzElGrid(use_text=False, # no text
                                minor_line_color=(0.9,0.5,0.5,.2),# set low alpha
                                major_line_color=(1.0,0.0,0.0,.4),# set low alpha
                                on=False) # start with grid off
grid_stimulus_fixed  = AzElGrid(on=False,
                                minor_line_color=(0.5,0.5,0.7),
                                ) # start with grid off

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

min_filters = ['GL_LINEAR',
               'GL_NEAREST',
               'GL_NEAREST_MIPMAP_LINEAR',
               'GL_NEAREST_MIPMAP_NEAREST',
               'GL_LINEAR_MIPMAP_LINEAR',
               'GL_LINEAR_MIPMAP_NEAREST',
               ]
cur_min_filter_index = 0

def set_filter_and_text():
    global grating_stimulus, filter_text, cur_min_filter_index, min_filters
    min_filter = min_filters[cur_min_filter_index]
    filter_text.parameters.text = "'g' toggles grid display, 'f' cycles min_filter (now %s)"%min_filter
    min_filter_int = eval("gl."+min_filter)
    grating_stimulus.parameters.min_filter = min_filter_int
    
mask = SphereWindow(radius=1.0*0.90, # make sure window is inside sphere with grating
                    window_shape_radius_parameter=40.0,
                    slices=50,
                    stacks=50)

text_color = (0.0,0.0,1.0) # RGB ( blue)
xpos = 10.0
yspace = 5
text_params = {'anchor':'lowerleft','color':text_color,'font_size':20}

text_stimuli = []
ypos = 0
text_stimuli.append( Text( text = "(Hold mouse button to prevent re-orienting stimulus with mask.)",
                           position=(xpos,ypos),**text_params))
ypos += text_stimuli[-1].parameters.size[1] + yspace

text_stimuli.append( Text( text = "Numeric keypad changes grating orientation.",
                           position=(xpos,ypos),**text_params))
ypos += text_stimuli[-1].parameters.size[1] + yspace

filter_text = Text( text = "temporary text",
                    position=(xpos,ypos),**text_params)
set_filter_and_text()
text_stimuli.append( filter_text )
ypos += text_stimuli[-1].parameters.size[1] + yspace

sf_cutoff_text = Text(text = "'c/C' changes cutoff SF (now %.2f cycles per texel)"%(grating_stimulus.parameters.lowpass_cutoff_cycles_per_texel),
               position=(xpos,ypos),**text_params)
text_stimuli.append( sf_cutoff_text )
ypos += text_stimuli[-1].parameters.size[1] + yspace

zoom_text = Text(text = "'z/Z' changes zoom (X field of view %.2f degrees)"%(fov_x),
                 position=(xpos,ypos),**text_params)
text_stimuli.append( zoom_text )
ypos += text_stimuli[-1].parameters.size[1] + yspace

tf_text = Text(text = "'t/T' changes TF (now %.2f hz)"%(grating_stimulus.parameters.temporal_freq_hz),
               position=(xpos,ypos),**text_params)
text_stimuli.append( tf_text )
ypos += text_stimuli[-1].parameters.size[1] + yspace

sf_text = Text(text = "'-' shrinks window, '+' grows window, 's/S' changes SF (now %.2f cycles per degree)"%(grating_stimulus.parameters.spatial_freq_cpd),
               position=(xpos,ypos),**text_params)
text_stimuli.append( sf_text )
ypos += text_stimuli[-1].parameters.size[1] + yspace

az_el_text = Text( text = "Mouse moves window, press Esc to quit. Az, El = (%05.1f, %05.1f)"%(azimuth,elevation),
                   position=(xpos,ypos),**text_params)
text_stimuli.append( az_el_text )
ypos += text_stimuli[-1].parameters.size[1] + yspace

text_stimuli.append( Text( text = "Demonstration of perspective distorted, windowed grating.",
                           position=(xpos,ypos),**text_params))

viewport = Viewport(screen=screen,
                    projection=projection_3d,
                    stimuli=[grating_stimulus,
                             grid_stimulus_moving,
                             mask, # mask must be drawn after grating
                             grid_stimulus_fixed,
                             ]) 
grid_stimulus_fixed.set(my_viewport=viewport) # must know viewport for proper positioning of text labels
grid_stimulus_moving.set(my_viewport=viewport) # must know viewport for proper positioning of text labels

text_viewport = Viewport(screen=screen, # default (orthographic) viewport
                         stimuli=text_stimuli)

quit_now = False
shift_key = False
frame_timer = FrameTimer()
while not quit_now:
    for event in pygame.event.get():
        if event.type == pygame.locals.QUIT:
            quit_now = True
        elif event.type == pygame.locals.MOUSEBUTTONDOWN:
            if event.button == 1:
                grating_orient_method = 'mask only'
        elif event.type == pygame.locals.MOUSEBUTTONUP:
            if event.button == 1:
                grating_orient_method = 'reorient stimulus'
        elif event.type == pygame.locals.KEYUP:
            if event.key in [pygame.locals.K_LSHIFT,pygame.locals.K_RSHIFT]:
                shift_key = False
        elif event.type == pygame.locals.KEYDOWN:
            if event.key == pygame.locals.K_ESCAPE:
                quit_now = True
            elif event.key in [pygame.locals.K_LSHIFT,pygame.locals.K_RSHIFT]:
                shift_key = True
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
                sf_text.parameters.text = "'-' shrinks window, '+' grows window, 's/S' changes SF (now %.2f cycles per degree)"%(grating_stimulus.parameters.spatial_freq_cpd)
            elif event.key == pygame.locals.K_t:
                if shift_key:
                    grating_stimulus.parameters.temporal_freq_hz *= (1.0/1.5)
                else:
                    grating_stimulus.parameters.temporal_freq_hz *= 1.5
                tf_text.parameters.text = "'t/T' changes TF (now %.2f hz)"%(grating_stimulus.parameters.temporal_freq_hz)
            elif event.key == pygame.locals.K_c:
                if shift_key:
                    grating_stimulus.parameters.lowpass_cutoff_cycles_per_texel *= (1.0/1.5)
                else:
                    grating_stimulus.parameters.lowpass_cutoff_cycles_per_texel *= 1.5
                sf_cutoff_text.parameters.text = "'c/C' changes cutoff SF (now %.2f cycles per texel)"%(grating_stimulus.parameters.lowpass_cutoff_cycles_per_texel)
            elif event.key == pygame.locals.K_g:
                grid_stimulus_fixed.parameters.on = not grid_stimulus_fixed.parameters.on
                grid_stimulus_moving.parameters.on = not grid_stimulus_moving.parameters.on
            elif event.key == pygame.locals.K_z:
                if shift_key:
                    fov_x  *= (1.0/1.1)
                else:
                    fov_x  *= 1.1
                viewport.parameters.projection = SimplePerspectiveProjection(fov_x=fov_x)
                zoom_text.parameters.text = "'z/Z' changes zoom (X field of view %.2f degrees)"%(fov_x)
            elif event.key == pygame.locals.K_f:
                cur_min_filter_index = (cur_min_filter_index+1) % len(min_filters)
                set_filter_and_text()
            elif event.key == pygame.locals.K_MINUS:
                mask.parameters.window_shape_radius_parameter *= 0.8
            elif event.key == pygame.locals.K_EQUALS:
                mask.parameters.window_shape_radius_parameter *= (1.0/0.8)

    screen.clear()
    x,y = get_mouse_position()
    set_az_el(x,y)
    viewport.draw()
    text_viewport.draw()
    swap_buffers()
    frame_timer.tick()
    
frame_timer.log_histogram()
