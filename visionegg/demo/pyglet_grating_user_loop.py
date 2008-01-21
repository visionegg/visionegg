#!/usr/bin/env python
"""Sinusoidal grating calculated in realtime, displayed simultaneously
in as many pyglet windows as you have physical screens (see pyglet.org).

In pyglet 1.0b3, a given window might not appear on its associated physical
screen unless set to fullscreen (see VISIONEGG_FULLSCREEN in VisionEgg.cfg)

Hit ESC to exit.
If you want to create more windows, add more calls to get_default_window()"""

############################
#  Import various modules  #
############################

from __future__ import division

import VisionEgg
VisionEgg.start_default_logging(); VisionEgg.watch_exceptions()
import VisionEgg.Core
import pyglet.window
from VisionEgg.FlowControl import Presentation
from VisionEgg.Gratings import SinGrating2D

##################################################################
#  Init OpenGL graphics windows, one window per physical screen  #
##################################################################

platform = pyglet.window.get_platform()
display = platform.get_default_display() # a display might be 2 screens side by side
pyglet_screens = display.get_screens()
ve_screens = [] # list of Windows
for pyglet_screen in pyglet_screens:
    # create a VisionEgg.Window, based on settings in VisionEgg.cfg
    ve_screen = VisionEgg.Core.get_default_screen(pyglet_screen=pyglet_screen)
    ve_screens.append(ve_screen)

######################################
#  Create sinusoidal grating object  #
######################################

stimulus = SinGrating2D(position=(ve_screens[0].win.width/2, ve_screens[0].win.height/2),
                        anchor='center',
                        size=(300, 300),
                        spatial_freq=10/ve_screens[0].win.width, # units of cycles/pixel
                        temporal_freq_hz=1,
                        orientation=45)

##################################################################
#  Create viewports - intermediaries between stimuli and screen  #
##################################################################

viewports = [] # list of viewports, one per window
for ve_screen in ve_screens:
    viewport = VisionEgg.Core.Viewport(screen=ve_screen, stimuli=[stimulus])
    viewports.append(viewport)

##########################
#  Run custom user loop  #
##########################

def exit():
    quit = False
    for ve_screen in ve_screens:
        if ve_screen.win.has_exit:
            quit = True
    return quit


while not exit():
    for ve_screen in ve_screens:
        # dispatch each window's events to its event handlers
        ve_screen.dispatch_events()
    for ve_screen, viewport in zip(ve_screens, viewports):
        ve_screen.switch_to() # ve_screen.make_current() also works
        ve_screen.clear()
        viewport.draw() # draw to its viewport
        ve_screen.flip() # ve_screen.swap buffers() also works
