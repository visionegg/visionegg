#!/usr/bin/env python
"""Test for incomplete DC restoration."""

description = \
"""From Brainard, Pelli, Robson (2002):

    There are at least six causes for the failure of pixel independence.

    ...

    [See display_voltage_regulation.py for test 3.]

    4. Incomplete DC restoration. Unfortunately, the video amplifier
    in most CRT monitors is not DC coupled.  Instead it is AC coupled
    most of the time, and momentarily DC couple to make zero volts
    produce black at the end of the vertical blanking interval. (DC,
    "direct current,") refers to zero temporal frequency; AC,
    "alternating current," refers to all high frequencies.) This is
    called "DC restoration," which is slightly cheaper to design and
    build than a fully DC coupled video circuit. If the AC time
    constant were much longer than a frame, the DC restoration would
    be equivalent to DC coupling, but, in practice, the AC time
    constant is typically short relative to the duration of a frame,
    so that the same video voltage will produce different screen
    luminances depending on the average voltage since the last
    blanking interval. As for failure 3, this effect is negligible at
    the top of the screen and maximal at the bottom. However, this
    effect can be distinguished from failure 3 by using silent
    substitution. To test, say, the green primary, use a green test
    spot, and switch the background (the rest of the screen) back and
    forth between green and blue. The green and blue backgrounds are
    indistinguishable to the high-voltage power supply (it serves all
    three guns) but are distinct to the video amplifiers (one per
    gun).


Brainard, D.H., Pelli, D.G., & Robson, T. (2002). Display
  Characterization. In: J. Hornak (Ed.) Encyclopedia of Imaging Science
  and Technology (pp. 172-188): Wiley.
"""

import VisionEgg
from VisionEgg.Core import *
from VisionEgg.MoreStimuli import *
import pygame
import pygame.locals

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

current_channel = 'green'

quit_now = False
toggle = False # flip bit
while not quit_now:
    toggle = not toggle
    for event in pygame.event.get():
        if event.type == pygame.locals.QUIT:
            quit_now = True
        elif event.type == pygame.locals.KEYDOWN:
            if event.key == pygame.locals.K_ESCAPE:
                quit_now = True
            elif event.type == pygame.locals.KEYDOWN:
                if event.key == pygame.locals.K_r:
                    current_channel = 'red'
                elif event.key == pygame.locals.K_g:
                    current_channel = 'green'
                elif event.key == pygame.locals.K_b:
                    current_channel = 'blue'

    if current_channel == 'red':
        bar.parameters.color = (1.0,0.0,0.0)
        if toggle:
            screen.parameters.bgcolor = (0.0,1.0,0.0)
        else:
            screen.parameters.bgcolor = bar.parameters.color
    elif current_channel == 'green':
        bar.parameters.color = (0.0,1.0,0.0)
        if toggle:
            screen.parameters.bgcolor = (0.0,0.0,1.0)
        else:
            screen.parameters.bgcolor = bar.parameters.color
    elif current_channel == 'blue':
        bar.parameters.color = (0.0,0.0,1.0)
        if toggle:
            screen.parameters.bgcolor = (1.0,0.0,0.0)
        else:
            screen.parameters.bgcolor = bar.parameters.color
    screen.clear()
    viewport.draw()
    swap_buffers()
