#!/usr/bin/env python
"""sinusoidal grating in gaussian window"""

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

def get_mouse_position():
    # convert to OpenGL coordinates
    (x,y) = pygame.mouse.get_pos()
    y = screen.size[1]-y
    return x,y

screen = get_default_screen()

mask = Mask2D(function='gaussian',   # also supports 'circle'
              radius_parameter=25,   # sigma for gaussian, radius for circle (units: num_samples)
              num_samples=(512,512)) # this many texture elements in mask (covers whole size specified below)

grating_stimulus = SinGrating2D(mask             = mask,
                                position         = ( screen.size[0]/2.0, screen.size[1]/2.0 ),
                                size             = ( 800 , 800 ),
                                spatial_freq     = 10.0 / screen.size[0], # units of cycles/pixel
                                temporal_freq_hz = 1.0,
                                num_samples      = 1024,
                                orientation      = 45.0 )

text_color = (0.0,0.0,1.0) # RGB ( blue)
xpos = 10.0
yspace = 5
text_params = {'anchor':'lowerleft','color':text_color,'font_size':20}

text_stimuli = []
ypos = 0
text_stimuli.append( Text( text = "Numeric keypad changes grating orientation.",
                           position=(xpos,ypos),**text_params))
ypos += text_stimuli[-1].parameters.size[1] + yspace

tf_text = Text(text = "'t/T' changes TF (now %.2f hz)"%(grating_stimulus.parameters.temporal_freq_hz),
               position=(xpos,ypos),**text_params)
text_stimuli.append( tf_text )
ypos += text_stimuli[-1].parameters.size[1] + yspace

text_stimuli.append( Text( text = "'-' shrinks window, '+' grows window (slow)",
                           position=(xpos,ypos),**text_params))
ypos += text_stimuli[-1].parameters.size[1] + yspace

sf_text = Text(text = "'s/S' changes SF (now %.3f cycles/pixel = %.1f pixels/cycle)"%(grating_stimulus.parameters.spatial_freq,1.0/grating_stimulus.parameters.spatial_freq),
               position=(xpos,ypos),**text_params)
text_stimuli.append( sf_text )
ypos += text_stimuli[-1].parameters.size[1] + yspace

text_stimuli.append( Text( text = "Mouse moves gabor, press Esc to quit",
                   position=(xpos,ypos),**text_params))
ypos += text_stimuli[-1].parameters.size[1] + yspace

text_stimuli.append( Text( text = "Demonstration of mouse controlled gabor.",
                           position=(xpos,ypos),**text_params))

viewport = Viewport(screen=screen,
                    stimuli=[grating_stimulus] + text_stimuli)

quit_now = False
shift_key = False
frame_timer = FrameTimer()
while not quit_now:
    for event in pygame.event.get():
        if event.type == pygame.locals.QUIT:
            quit_now = True
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
                    grating_stimulus.parameters.spatial_freq *= (1.0/1.5)
                else:
                    grating_stimulus.parameters.spatial_freq *= 1.5
                sf_text.parameters.text = "'s/S' changes SF (now %.3f cycles per pixel = %.1f pixels per cycle)"%(grating_stimulus.parameters.spatial_freq,1.0/grating_stimulus.parameters.spatial_freq)
            elif event.key == pygame.locals.K_t:
                if shift_key:
                    grating_stimulus.parameters.temporal_freq_hz *= (1.0/1.5)
                else:
                    grating_stimulus.parameters.temporal_freq_hz *= 1.5
                tf_text.parameters.text = "'t/T' changes TF (now %.2f hz)"%(grating_stimulus.parameters.temporal_freq_hz)
            elif event.key == pygame.locals.K_MINUS:
                old_params = grating_stimulus.parameters.mask.constant_parameters
                new_radius = old_params.radius_parameter * 0.8
                new_mask = Mask2D(function=old_params.function,
                                  radius_parameter=old_params.radius_parameter*0.8,
                                  num_samples=old_params.num_samples)
                grating_stimulus.parameters.mask = new_mask
            elif event.key == pygame.locals.K_EQUALS:
                old_params = grating_stimulus.parameters.mask.constant_parameters
                new_radius = old_params.radius_parameter * 0.8
                new_mask = Mask2D(function=old_params.function,
                                  radius_parameter=old_params.radius_parameter/0.8,
                                  num_samples=old_params.num_samples)
                grating_stimulus.parameters.mask = new_mask

    screen.clear()
    x,y = get_mouse_position()
    grating_stimulus.parameters.position = x,y
    viewport.draw()
    swap_buffers()
    frame_timer.tick()
    
frame_timer.log_histogram()
