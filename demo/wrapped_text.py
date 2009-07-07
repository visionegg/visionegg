#!/usr/bin/env python
"""Display text strings."""

import VisionEgg
VisionEgg.start_default_logging(); VisionEgg.watch_exceptions()

from VisionEgg.Core import get_default_screen, Viewport, swap_buffers, \
     FrameTimer
from VisionEgg.Text import Text
from VisionEgg.WrappedText import WrappedText
import pygame
from pygame.locals import QUIT,KEYDOWN,MOUSEBUTTONDOWN

screen = get_default_screen()
screen.parameters.bgcolor = (0.0,0.0,1.0) # background blue (RGB)

text = WrappedText(
    text="""Lorem ipsum dolor sit amet, consectetur adipiscing elit. Maecenas ac magna nibh. Cras ac volutpat purus. Suspendisse potenti. Vestibulum accumsan erat ac massa hendrerit semper. Ut a laoreet magna. Suspendisse risus odio, porttitor nec sodales nec, laoreet sit amet tellus. Maecenas condimentum orci id magna laoreet tincidunt. Sed porta velit a ligula ullamcorper accumsan. Fusce a felis tortor, vel hendrerit mauris.""",

    position=(0,screen.size[1]))

viewport = Viewport(screen=screen,
                    size=screen.size,
                    stimuli=[text])
frame_timer = FrameTimer()
quit_now = 0
print "press any key or click the mouse to stop"
while not quit_now:
    for event in pygame.event.get():
        if event.type in (QUIT,KEYDOWN,MOUSEBUTTONDOWN):
            quit_now = 1
    screen.clear()
    viewport.draw()
    swap_buffers()
    frame_timer.tick()
frame_timer.log_histogram()
