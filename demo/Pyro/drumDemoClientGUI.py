#!/usr/bin/env python

#from VisionEgg.GUI import *
from VisionEgg.PyroHelpers import *

import Tkinter
from math import *

default_max_speed = 1000.0

client = PyroClient()

fixation_spot_on_controller = client.get('fixation_spot_on_controller')
drum_on_controller = client.get('drum_on_controller')
duration_controller = client.get('duration_controller')
angle_controller = client.get('angle_controller')
contrast_controller = client.get('contrast_controller')
projection_controller = client.get('projection_controller')
drum_flat_controller = client.get('drum_flat_controller')
interpolation_controller = client.get('interpolation_controller')
go_object = client.get('go_object')

class DrumGui(Tkinter.Frame):
    def __init__(self,master=None,**cnf):
        apply(Tkinter.Frame.__init__,(self,master),cnf)
        self.winfo_toplevel().title('Vision Egg - spinning drum')
        self.pack(expand=1,fill=Tkinter.BOTH)

        # Close server button
        Tkinter.Button(self,text="Close server",command=self.quit).pack()

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
        
        # On between stimulus presentations
        self.isi_on = Tkinter.BooleanVar()
        self.isi_on.set(0)
        Tkinter.Checkbutton(self,
                            text='Visible between stimuli',
                            command=self.push_values,
                            variable=self.isi_on,
                            relief=Tkinter.FLAT).pack()
        
        # Fixation spot
        self.fixation_spot = Tkinter.BooleanVar()
        self.fixation_spot.set(1)
        Tkinter.Checkbutton(self,
                            text='Fixation spot',
                            variable=self.fixation_spot,
                            command=self.push_values,
                            relief=Tkinter.FLAT).pack()

        # Drum type/projection type
        self.flat = Tkinter.BooleanVar()
        self.flat.set(0)
        Tkinter.Checkbutton(self,
                            text='Flat projection',
                            variable=self.flat,
                            command=self.push_values,
                            relief=Tkinter.FLAT).pack()

        # Interpolation mode
        self.linear_interp = Tkinter.BooleanVar()
        self.linear_interp.set(1)
        Tkinter.Checkbutton(self,
                            text='Linear interpolation',
                            variable=self.linear_interp,
                            command=self.push_values,
                            relief=Tkinter.FLAT).pack()
        
        # Go button
        Tkinter.Button(self,text="go",command=self.go).pack()

        self.validate_pos_string()
        self.validate_c_string()
 
    def validate_pos_string(self):
        tmp = self.positionFormula.get()
        try:
            angle_controller.set_value(tmp)
            # won't execute below here if line above raised exception
            self.validated_pos_string = tmp 
        finally:
            self.positionFormula.set(self.validated_pos_string)
    
    def validate_c_string(self):
        tmp = self.contrastFormula.get()
        try:
            contrast_controller.set_value(tmp)
            # won't execute below here if line above raised exception
            self.validated_c_string = tmp
        finally:
            self.contrastFormula.set(self.validated_c_string)
    
    def push_values(self):
        self.validate_pos_string()
        self.validate_c_string()
        
        drum_on_controller.set_value(1,self.isi_on.get())
        fixation_spot_on_controller.set_value(gui_window.fixation_spot.get())
        duration_controller.set_value((gui_window.duration.get(),'seconds'))
        angle_controller.set_value(self.validated_pos_string)
        contrast_controller.set_value(self.validated_c_string)
        interpolation_controller.set_value(self.linear_interp.get())
        if gui_window.flat.get():
            # Use orthographic projection
            projection_controller.set_value('ortho_proj')
            # Use flat drum
            drum_flat_controller.set_value(1)
        else:
            # Use perspective projection
            projection_controller.set_value('perspective_proj')
            # Use cylindrical drum
            drum_flat_controller.set_value(0)
            
    def go(self):
        self.push_values()
        go_object.go()

    def quit(self):
        go_object.quit()
        sys.exit()

gui_window = DrumGui()
gui_window.push_values() # make sure everything is in sync
gui_window.mainloop()

