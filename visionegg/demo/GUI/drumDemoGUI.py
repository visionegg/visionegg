#!/usr/bin/env python
"""Spinning drum with a graphical user interface.

This demo is complex because there are two tasks which normally have
their own mainloop: the GUI and the Vision Egg drawing routines.
Here, the GUI mainloop is in charge between trials, and it is locked
out during trials."""

# This is the python source code for a demo application that uses the
# Vision Egg package.
#
# This program displays a spinning drum, with the inside of the drum
# texture-mapped with a panoramic image.
#
# This demo uses the GUI tookit "Tkinter", which may not be available on
# all platforms. Also, because this code also controls a GUI, it is much
# more complicated than the minimum needed to create a stimulus with the
# VisionEgg.

import VisionEgg
VisionEgg.start_default_logging(); VisionEgg.watch_exceptions()

from VisionEgg import *
from VisionEgg.Core import *
from VisionEgg.FlowControl import Presentation, Controller, FunctionController
from VisionEgg.GUI import *
from VisionEgg.Textures import *

import Tkinter
from math import *
import os
import time

default_max_speed = 400.0

class DrumGui(AppWindow):
    def __init__(self,master=None,**cnf):

        AppWindow.__init__(self,master,**cnf)
        self.winfo_toplevel().title('Vision Egg - spinning drum')
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
                                      label="Duration of go loop (seconds):")
        self.duration.set(10.0)
        self.duration.pack(expand=1,fill=Tkinter.X)

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

config.VISIONEGG_GUI_INIT=1
VisionEgg.config.VISIONEGG_HIDE_MOUSE = 0 # make sure mouse is visible
screen = get_default_screen() # initialize graphics
if config.VISIONEGG_FULLSCREEN==1:
    raise RuntimeError("Cannot enter fullscreen mode if you want to see GUI panel!")

# Get a texture
filename = os.path.join(config.VISIONEGG_SYSTEM_DIR,"data/panorama.jpg")
texture = Texture(filename)

drum = SpinningDrum(texture=texture,shrink_texture_ok=1)
fixation_spot = FixationSpot(position=(screen.size[0]/2,screen.size[1]/2),
                             anchor='center')

perspective = SimplePerspectiveProjection(fov_x=90.0)
perspective_viewport = Viewport(screen=screen,
                                projection=perspective,
                                stimuli=[drum])

flat_viewport = Viewport(screen=screen,
                         stimuli=[fixation_spot])

p = Presentation(viewports=[perspective_viewport,flat_viewport])
gui_window = DrumGui(idle_func=p.between_presentations)

p.add_controller(fixation_spot,'on',FunctionController(during_go_func=lambda t: gui_window.fixation_spot.get(),eval_frequency=Controller.TRANSITIONS))
p.add_controller(p,'go_duration',FunctionController(during_go_func=lambda t: (gui_window.duration.get(),'seconds'),eval_frequency=Controller.TRANSITIONS))
p.add_controller(drum,'angular_position',FunctionController(during_go_func=gui_window.positionFunction))
p.add_controller(drum,'contrast',FunctionController(during_go_func=gui_window.contrastFunction))

gui_window.mainloop()

