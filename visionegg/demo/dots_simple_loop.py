#!/usr/bin/env python

"""Draw dots, using your own event loop.

This bypasses the VisionEgg.FlowControl.Presentation class.  It may be easier
to create simple experiments this way."""

import VisionEgg
VisionEgg.start_default_logging(); VisionEgg.watch_exceptions()


from VisionEgg.Core import Screen, Viewport, swap_buffers, FrameTimer, \
     get_default_screen
import pygame
from pygame.locals import QUIT,KEYDOWN,MOUSEBUTTONDOWN
from VisionEgg.Text import Text
from VisionEgg.Dots import DotArea2D

screen = get_default_screen()
screen.parameters.bgcolor = (0.0,0.0,0.0) # black (RGB)

dots = DotArea2D( position                = ( screen.size[0]/2.0,
                                              screen.size[1]/2.0 ),
                  size                    = ( 300.0 , 300.0 ),
                  signal_fraction         = 0.1,
                  signal_direction_deg    = 180.0,
                  velocity_pixels_per_sec = 10.0,
                  dot_lifespan_sec        = 5.0,
                  dot_size                = 3.0,
                  num_dots                = 100)

text = Text( text = "Vision Egg dot_simple_loop demo.",
             position = (screen.size[0]/2,2),
             anchor = 'bottom',
             color = (1.0,1.0,1.0))

viewport = Viewport( screen=screen, stimuli=[dots,text] )

# The main loop below is an alternative to using the
# VisionEgg.FlowControl.Presentation class.

frame_timer = FrameTimer()
quit_now = 0
while not quit_now:
    for event in pygame.event.get():
        if event.type in (QUIT,KEYDOWN,MOUSEBUTTONDOWN):
            quit_now = 1
    screen.clear()
    viewport.draw()
    swap_buffers()
    frame_timer.tick()
frame_timer.log_histogram()
