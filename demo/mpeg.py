#!/usr/bin/env python
"""mpeg.py - play MPEG movies in the Vision Egg

This demo uses pygame.movie to draw movies.  See also the quicktime.py
demo."""

import os
import VisionEgg
from VisionEgg.Core import *
from VisionEgg.FlowControl import Presentation, Controller, FunctionController
from VisionEgg.Text import *
from VisionEgg.Textures import *
import sys
import pygame
import pygame.surface, pygame.locals
import pygame.movie
import OpenGL.GL as gl

if len(sys.argv) > 1:
    filename = sys.argv[1]
else:
    filename = os.path.join(VisionEgg.config.VISIONEGG_SYSTEM_DIR,"data","water.mpg")
    
movie = pygame.movie.Movie(filename)

screen = get_default_screen()

width, height = movie.get_size()
scale_x = screen.size[0]/float(width)
scale_y = screen.size[1]/float(height)
scale = min(scale_x,scale_y) # maintain aspect ratio

# create pygame surface (buffer to draw uncompressed movie data into)
pygame_surface = pygame.surface.Surface((width,height))

# tell the movie to render onto the surface
movie.set_display( pygame_surface )

# create a texture using this surface as the source of texel data
texture = Texture(pygame_surface)

text = Text( text = "Vision Egg MPEG demo - Press Esc to quit",
             position = (screen.size[0]/2,2),
             anchor = 'bottom',
             color = (1.0,1.0,1.0,1.0))

# Create the instance of TextureStimulus

stimulus = TextureStimulus(texture  = texture,
                           position = (screen.size[0]/2,screen.size[1]/2),
                           anchor = 'center',
                           size = (width*scale,height*scale),
                           mipmaps_enabled = 0,
                           texture_min_filter=gl.GL_LINEAR)

texture_object = stimulus.parameters.texture.get_texture_object()
def update_movie():
    # While movie.play() decompresses the movie to pygame surface
    # in a separate thread, this sends the data to OpenGL.
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
p.add_controller(None,None,FunctionController(during_go_func=update_movie,
                                              temporal_variables=Controller.TIME_INDEPENDENT))
movie.play()
p.go()
