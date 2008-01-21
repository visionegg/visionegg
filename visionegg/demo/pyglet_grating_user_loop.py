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

import VisionEgg.Core
import pyglet.window
from VisionEgg.FlowControl import Presentation
from VisionEgg.Gratings import SinGrating2D

##################################################################
#  Init OpenGL graphics windows, one window per physical screen  #
##################################################################

platform = pyglet.window.get_platform()
display = platform.get_default_display() # a display might be 2 screens side by side
screens = display.get_screens()
wins = [] # list of Windows
for screen in screens:
    # create a VisionEgg.Window, based on settings in VisionEgg.cfg
    win = VisionEgg.Core.get_default_window(screen=screen)
    wins.append(win)

######################################
#  Create sinusoidal grating object  #
######################################

stimulus = SinGrating2D(position=(wins[0].win.width/2, wins[0].win.height/2),
                        anchor='center',
                        size=(300, 300),
                        spatial_freq=10/wins[0].win.width, # units of cycles/pixel
                        temporal_freq_hz=1,
                        orientation=45)

##################################################################
#  Create viewports - intermediaries between stimuli and screen  #
##################################################################

viewports = [] # list of viewports, one per window
for win in wins:
    viewport = VisionEgg.Core.pyglet_Viewport(window=win, stimuli=[stimulus])
    viewports.append(viewport)

##########################
#  Run custom user loop  #
##########################

def exit():
    quit = False
    for win in wins:
        if win.win.has_exit:
            quit = True
    return quit


while not exit():
    for win in wins:
        # dispatch each window's events to its event handlers
        win.dispatch_events()
    for win, viewport in zip(wins, viewports):
        win.switch_to() # win.make_current() also works
        win.clear()
        viewport.draw() # draw to its viewport
        win.flip() # win.swap buffers() also works
