#!/usr/bin/env python
"""Test whether your video drivers support setting gamma ramps"""

import VisionEgg
VisionEgg.start_default_logging(); VisionEgg.watch_exceptions()

from VisionEgg.Core import *
from VisionEgg.FlowControl import Presentation
from VisionEgg.Gratings import *
from VisionEgg.Text import *
from Numeric import *
import pygame

if not hasattr(pygame.display,"set_gamma_ramp"):
    raise RuntimeError("Need pygame 1.5 or greater for set_gamma_ramp function.")

# Initialize OpenGL graphics screen.
screen = get_default_screen()

center_x = screen.size[0]/2.0

# Create the instance SinGrating with appropriate parameters
stimulus = SinGrating2D()
text2 = Text(text="set_gamma_ramp(r,g,b):",
             position=(center_x,0),anchor="bottom")
text1 = Text(text="Press - to decrease luminance range, + to increase.",
             position=(center_x,text2.parameters.size[1]+5),anchor="bottom")

# Use viewport with pixel coordinate system for projection
viewport = Viewport(screen=screen,stimuli=[stimulus,text1,text2])

def quit(event):
    global p # get presentation instance
    p.parameters.quit = 1

# set initial value
global gamma_scale
gamma_scale = 1.0
            
def keydown(event):
    global gamma_scale
    if event.key == pygame.locals.K_ESCAPE:
        quit(event)
    elif event.key in [pygame.locals.K_KP_PLUS,
                       pygame.locals.K_PLUS,
                       pygame.locals.K_EQUALS]:
        gamma_scale += 0.05
        do_gamma()
    elif event.key in [pygame.locals.K_KP_MINUS,
                       pygame.locals.K_MINUS]:
        gamma_scale -= 0.05
        do_gamma()
        
def do_gamma():
    global gamma_scale, text2
    r = (arange(256)*256*gamma_scale).astype('i')
    g = r
    b = r
    worked = pygame.display.set_gamma_ramp(r,g,b)
    if worked:
        text2.parameters.text = "set_gamma_ramp(r,g,b): success"
    else:
        text2.parameters.text = "set_gamma_ramp(r,g,b): failure"

do_gamma() # set gamma once initially

handle_event_callbacks = [(pygame.locals.QUIT, quit),
                          (pygame.locals.KEYDOWN, keydown)]

# Create an instance of the Presentation class
p = Presentation(viewports=[viewport],
                 handle_event_callbacks=handle_event_callbacks)

# Go!
p.run_forever()
