#!/usr/bin/env python
#
# This is the python source code for a demo application that uses the
# Vision Egg package.
#
# This program displays a spinning drum, with the inside of the drum
# texture-mapped with a panoramic image.  This image is motion-blurred
# as appropriate for the rotational velocity of the drum and the frame
# rate of the display. (You must set the frame rate of your display.)
#
# By default, the original image is called 'orig.bmp'.  You'll get an
# error if the code cannot find this image.  You could create a BMP
# format image called 'orig.bmp', or you could change the code to look
# look for another image.
#
# This demo uses the GUI tookit "Tkinter", which may not be available on
# all platforms. Also, because this code also controls a GUI, it is much
# more complicated than the minimum needed to create a stimulus with the
# VisionEgg.
#
# If you run this demo in fullscreen mode, you won't be able to see the
# control window to tell the stimulus to "go" unless you're connected
# to the computer running the Vision Egg from a remote X window.
#
# Copyright (c) 2001 Andrew Straw.  Distributed under the terms of the
# GNU General Public License (GPL).

import string
__version__ = string.split('$Revision$')[1]
__date__ = string.join(string.split('$Date$')[1:3], ' ')
__author__ = 'Andrew Straw <astraw@users.sourceforge.net>'

from VisionEgg.Core import *
from VisionEgg.AppHelper import *
from VisionEgg.GUI import *
from VisionEgg.MotionBlur import *

import Tkinter
from math import *
import os
import time

class BlurDrumGui(AppWindow):
    def __init__(self,master=None,**cnf):

        apply(AppWindow.__init__,(self,master),cnf)
        self.winfo_toplevel().title('Vision Egg - Motion blurred drum')
        self.pack(expand=1,fill=Tkinter.BOTH)

        # Position formula
        Tkinter.Label(self,text="Position as a function of time:").pack()
        self.positionFormula = Tkinter.StringVar()
        self.validated_pos_string = "%.1f*cos(t)"%default_max_speed
        self.positionFormula.set(self.validated_pos_string)
        Tkinter.Entry(self,textvariable=self.positionFormula).pack(expand=1,fill=Tkinter.X)

        # Contrast formula
        Tkinter.Label(self,text="Contrast as a function of time:").pack()
        self.contrastFormula = Tkinter.StringVar()
        self.validated_c_string = '1.0'
        self.contrastFormula.set(self.validated_c_string)
        Tkinter.Entry(self,textvariable=self.contrastFormula).pack(expand=1,fill=Tkinter.X)

        # Duration
        self.duration = Tkinter.Scale(self,
                                      from_=0.5,
                                      to=60.0,
                                      resolution=0.5,
                                      orient=Tkinter.HORIZONTAL,
                                      label="Duration (seconds):")
        self.duration.set(10.0)
        self.duration.pack(expand=1,fill=Tkinter.X)

        # Blur on
        self.blur_on = Tkinter.BooleanVar()
        self.blur_on.set(1)
        Tkinter.Checkbutton(self,
                            text='Motion blur',
                            variable=self.blur_on,
                            relief=Tkinter.FLAT).pack()

        # Fixation spot
        self.fixation_spot = Tkinter.BooleanVar()
        self.fixation_spot.set(1)
        Tkinter.Checkbutton(self,
                            text='Fixation spot',
                            variable=self.fixation_spot,
                            relief=Tkinter.FLAT).pack()
        
        # Go button
        Tkinter.Button(self,text="go",command=self.go).pack()

        self.validate_pos_string()
        self.validate_c_string()
 
    def positionFunction(self,t):
        return eval(self.validated_pos_string)

    def contrastFunction(self,t):
        if t < 0.0:     # In between stimulus presentations
            return 0.0
        return eval(self.validated_c_string)

    def validate_pos_string(self):
        tmp = self.positionFormula.get()
        try:
            t = 1.2
            eval(tmp)
            self.validated_pos_string = tmp
        finally:
            self.positionFormula.set(self.validated_pos_string)
    
    def validate_c_string(self):
        tmp = self.contrastFormula.get()
        try:
            t = 1.2
            eval(tmp)
            self.validated_c_string = tmp
        finally:
            self.contrastFormula.set(self.validated_c_string)
    
    def go(self):
        self.validate_pos_string()
        self.validate_c_string()
        p.go()

default_max_speed = 500.0

screen = get_default_screen() # initialize graphics
projection = SimplePerspectiveProjection(fov_x=90.0)
viewport = Viewport(screen,(0,0),screen.size,projection)

drum = BlurredDrum(max_speed=default_max_speed)
drum.init_gl()

fixation_spot = FixationSpot()
fixation_spot.init_gl()

viewport.add_stimulus(drum)
viewport.add_overlay(fixation_spot)

p = Presentation(viewports=[viewport])
gui_window = BlurDrumGui(idle_func=p.between_presentations)

p.add_transitional_controller(fixation_spot.parameters,'on',lambda t: gui_window.fixation_spot.get())
p.add_transitional_controller(drum.parameters,'motion_blur_on',lambda t: gui_window.blur_on.get())
p.add_transitional_controller(p.parameters,'duration_sec',lambda t: gui_window.duration.get())
p.add_realtime_controller(drum.parameters,'angle',gui_window.positionFunction)
p.add_realtime_controller(drum.parameters,'contrast',gui_window.contrastFunction)

gui_window.mainloop()

