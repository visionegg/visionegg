#!/usr/bin/env python

"""Draw dots and save movie using your own event loop.

This bypasses the VisionEgg.FlowControl.Presentation class.  It may be easier
to create simple scripts this way."""

import VisionEgg
VisionEgg.start_default_logging(); VisionEgg.watch_exceptions()

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

VisionEgg.config.VISIONEGG_MONITOR_REFRESH_HZ = 60.0 # fake framerate
VisionEgg.set_time_func_to_frame_locked() # force VisionEgg to fake this framerate

num_frames = 5
for i in range(num_frames):
    screen.clear()
    viewport.draw()
    swap_buffers()
    im = screen.get_framebuffer_as_image(buffer='front',format=gl.GL_RGB)
    filename = "movie_%02d.jpg"%(i+1)
    im.save(filename)
    print 'saved',filename
    
