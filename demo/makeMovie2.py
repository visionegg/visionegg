#!/usr/bin/env python

"""Draw dots and save movie using your own event loop.

This bypasses the VisionEgg.Core.Presentation class.  It may be easier
to create simple experiments this way."""

import VisionEgg
from VisionEgg.Core import *
import pygame
from pygame.locals import *
from VisionEgg.Text import *
from VisionEgg.Dots import *

screen = get_default_screen()
screen.parameters.bgcolor = (0.0,0.0,0.0,0.0) # black (RGBA)

dots = DotArea2D( position                = ( screen.size[0]/2.0, screen.size[1]/2.0 ),
                  size                    = ( 300.0 , 300.0 ),
                  signal_fraction         = 0.1,
                  signal_direction_deg    = 180.0,
                  velocity_pixels_per_sec = 10.0,
                  dot_lifespan_sec        = 5.0,
                  dot_size                = 3.0,
                  num_dots                = 100)

text = Text( text = "Vision Egg makeMovie2 demo.",
             position = (screen.size[0]/2,2),
             anchor = 'bottom',
             color = (1.0,1.0,1.0))

viewport = Viewport( screen=screen, stimuli=[dots,text] )

# Switch function VisionEgg.time_func
fake_time_sec = VisionEgg.time_func() # Set for real once
def fake_time_func():
    return fake_time_sec
VisionEgg.time_func = fake_time_func

num_frames = 5
framerate = 60.0 # simulated frames per second
for i in range(num_frames):
    screen.clear()
    viewport.draw()
    swap_buffers()
    im = screen.get_framebuffer_as_image(buffer='front',format=gl.GL_RGB)
    filename = "movie_%02d.jpg"%(i+1)
    im.save(filename)
    fake_time_sec += 1.0/framerate
    
