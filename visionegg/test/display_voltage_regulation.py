#!/usr/bin/env python
"""Test for poor high-voltage regulation."""

description = \
"""From Brainard, Pelli, Robson (2002):

    There are at least six causes for the failure of pixel independence.

    ...

    3. Poor high-voltage regulation. The electron beam current is
    accelerated by a high voltage (15 to 50 kV) power supply, and on
    cheaper monitors, the voltage may slowly drop when the average
    beam current is high. This has the effect of making the intensity
    of each pixel dependent on the average intensity of all the pixels
    that preceded it. (The high-voltage supply will generally
    recuperate between frames.)  You can test for such long-distance
    effects by displaying a steady white bar in the center of your
    display surrounded by a uniform field of variable
    luminance. Changing the surround from white to black ideally would
    have no effect on the luminance of the bar.  To try this
    informally without a photometer, create a cardboard shield with a
    hole smaller than the bar to occlude a flickering surround, and
    observe whether the bar is steady.  This effect depends on
    position. The effect is negligible at the top of the screen and
    maximal at the bottom. A single high-voltage supply generally
    provides the current for all three channels (R, G, and B), so that
    the effect on a particular test spot is independent of the channel
    used for background modulation.  When the high voltage is very
    poorly regulated, the whole screen image expands as the image is
    made brighter, because as the increased current pulls the high
    voltage down, the electrons take longer to reach the screen and
    deflect more.

    [See display_dc_restoration.py for test 4.]

Brainard, D.H., Pelli, D.G., & Robson, T. (2002). Display
  Characterization. In: J. Hornak (Ed.) Encyclopedia of Imaging Science
  and Technology (pp. 172-188): Wiley.
"""

import VisionEgg
from VisionEgg.Core import *
from VisionEgg.MoreStimuli import *
import pygame
from pygame.locals import *

# Use Python's bool constants if available, make aliases if not
try:
    True
except NameError:
    True = 1==1
    False = 1==0
   
bpps = [32, 24, 16, 0]
sizes = [ (640,480), (800,600), (1024,768), (1280,1024) ]
for bpp in bpps:
    success = False
    for size in sizes:
        print 'trying to initialize fullscreen %d x %d, %d bpp'%(
            size[0], size[1], bpp)
        try:
            screen = VisionEgg.Core.Screen( size          = size,
                                            fullscreen    = True,
                                            preferred_bpp = bpp,
                                            maxpriority   = False,
                                            hide_mouse    = True,
                                            sync_swap     = True,
                                            )
            success = True
        except:
            pass
        if success:
            break # we don't need to try other resolutions
    if success:
        break

if not success:
    raise RuntimeError('ERROR: could not initialize fullscreen mode.')

if not screen.constant_parameters.sync_swap:
    raise RuntimeError('This test requires sync_swap to work')

screen.set(bgcolor = (0.0,0.0,0.0)) # black (RGB)

bar = Target2D( size     = (screen.size[0]/10, screen.size[1]),
                position = (screen.size[0]/2, screen.size[1]/2),
                anchor   = 'center',
                )

viewport = Viewport( screen  = screen,
                     stimuli = [bar],
                     )

black = True
while not pygame.event.peek((QUIT,KEYDOWN,MOUSEBUTTONDOWN)):
    black = not black
    if black:
        screen.parameters.bgcolor = (0.0,0.0,0.0) # black (RGB)
    else:
        screen.parameters.bgcolor = (1.0,1.0,1.0) # white (RGB)
    screen.clear()
    viewport.draw()
    swap_buffers()
