#!/usr/bin/env python
"""flames_visionegg.py - a Vision Egg implementation of pygame flames.

This demo renders a pygame surface (drawn with the flames demo of the
PCR - pygame code repository) and then updates and OpenGL texture with
surface using the Vision Egg."""

import os
import VisionEgg
VisionEgg.start_default_logging(); VisionEgg.watch_exceptions()

from VisionEgg.Core import *
from VisionEgg.FlowControl import Presentation, FunctionController, TIME_INDEPENDENT
from VisionEgg.Text import *
from VisionEgg.Textures import *
import pygame.surface, pygame.locals
import pygame.surfarray
import OpenGL.GL as gl
import flames_pygame as flames # "flames" from the pygame code repository

screen = get_default_screen()

# create 8 bit pygame surface
pygame_surface = pygame.surface.Surface((256,128),0,8)
# set the colormap of the pygame surface
flames.setpalette(pygame_surface)
# create a texture using this surface as the source of texel data
texture = Texture(pygame_surface)

# create an empty array
flame = Numeric.zeros(texture.size)
# fill it
flames.randomflamebase(flame)

text = Text( text = "Vision Egg/pygame flames demo - Press Esc to quit",
             position = (screen.size[0]/2,2),
             anchor = 'bottom',
             color = (1.0,1.0,1.0,1.0))

# Create the instance of TextureStimulus

# (The bottom 3 pixels of the flames texture contains artifacts from
# the flame-drawing algorithm, so put them below the visible portion
# of the screen)

hide_fraction = 3.0/texture.size[1]
screen_hide_height = screen.size[1]*hide_fraction*2

stimulus = TextureStimulus(texture = texture,
                           position = (0,-screen_hide_height),
                           anchor = 'lowerleft',
                           size    = (screen.size[0],screen.size[1]+screen_hide_height), # scale to fit screen
                           mipmaps_enabled = 0,
                           texture_min_filter=gl.GL_LINEAR)

texture_object = stimulus.parameters.texture.get_texture_object()
def update_flames():
    # this does the work of updating the flames
    flames.modifyflamebase( flame )
    flames.processflame( flame )
    pygame.surfarray.blit_array(pygame_surface, flame)
    texture_object.put_sub_image( pygame_surface )
    
viewport = Viewport(screen=screen,
                    stimuli=[stimulus,text])

p = Presentation(go_duration=('forever',),viewports=[viewport])

def quit(dummy_arg=None):
    p.parameters.go_duration = (0,'frames')
    
def keydown(event):
    if event.key == pygame.locals.K_ESCAPE:
        quit()
        
p.parameters.handle_event_callbacks=[(pygame.locals.QUIT, quit),
                                     (pygame.locals.KEYDOWN, keydown)]
p.add_controller(None,None,FunctionController(during_go_func=update_flames,
                                              temporal_variables=TIME_INDEPENDENT))
p.go()
