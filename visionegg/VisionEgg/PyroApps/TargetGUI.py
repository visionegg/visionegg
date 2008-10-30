#!/usr/bin/env python
#
# The Vision Egg: TargetGUI
#
# Copyright (C) 2001-2003 Andrew Straw.
# Author: Andrew Straw <astraw@users.sourceforge.net>
# URL: <http://www.visionegg.org/>
#
# Distributed under the terms of the GNU Lesser General Public License
# (LGPL). See LICENSE.TXT that came with this file.
#
# $Id$

"""Handle small target stimulus (client-side)"""

import VisionEgg
__version__ = VisionEgg.release_name
__cvs__ = '$Revision$'.split()[1]
__date__ = ' '.join('$Date$'.split()[1:3])
__author__ = 'Andrew Straw <astraw@users.sourceforge.net>'

import sys, os, math
import Tkinter
import VisionEgg.PyroApps.EPhysGUIUtils as client_utils

def get_control_list():
    return [("target_server",TargetControlFrame,TargetControlFrame.title)]

class TargetMetaParameters:
    def __init__(self):
        # colors
        self.color = (0.0, 0.0, 0.0, 1.0)
        self.bgcolor = (1.0, 1.0, 1.0, 0.0)

        # motion parameters
        self.start_x = 10.0
        self.start_y = 50.0
        self.velocity_pps = 100.0 # pixels per second
        self.direction_deg = 0.0

        # size and orientation
        self.width = 10.0
        self.height = 30.0
        self.orientation_deg = 0.0

        self.pre_stim_sec = 1.0
        self.stim_sec = 2.0
        self.post_stim_sec = 1.0

class TargetControlFrame(client_utils.StimulusControlFrame):
    title = "Moving Target Experiment"
    def __init__(self, master=None, suppress_go_buttons=0,**kw):
        client_utils.StimulusControlFrame.__init__(self,
                                                   master,
                                                   suppress_go_buttons,
                                                   TargetControlFrame.title,
                                                   TargetMetaParameters,
                                                   **kw)

        param_frame = self.param_frame # shorthand for self.param_frame created in base class

        pf_row = 0
        Tkinter.Label(param_frame,text="Start X (pixels):").grid(row=pf_row,column=0,sticky=Tkinter.E)
        self.start_x_tk_var = Tkinter.DoubleVar()
        self.start_x_tk_var.set(self.meta_params.start_x)
        self.make_callback_entry(textvariable=self.start_x_tk_var).grid(row=pf_row,column=2)
        self.loopable_variables["Start X"] = ("start_x",self.start_x_tk_var)

        pf_row += 1
        Tkinter.Label(param_frame,text="Start Y (pixels):").grid(row=pf_row,column=0,sticky=Tkinter.E)
        self.start_y_tk_var = Tkinter.DoubleVar()
        self.start_y_tk_var.set(self.meta_params.start_y)
        self.make_callback_entry(textvariable=self.start_y_tk_var).grid(row=pf_row,column=2)
        self.loopable_variables["Start Y"] = ("start_y",self.start_y_tk_var)

        pf_row += 1
        Tkinter.Label(param_frame,text="Velocity (pixels/sec):").grid(row=pf_row,column=0,sticky=Tkinter.E)
        self.velocity_tk_var = Tkinter.DoubleVar()
        self.velocity_tk_var.set(self.meta_params.velocity_pps)
        self.make_callback_entry(textvariable=self.velocity_tk_var).grid(row=pf_row,column=2)
        self.loopable_variables["Velocity"] = ("velocity_pps",self.velocity_tk_var)

        pf_row += 1
        Tkinter.Label(param_frame,text="Direction (degrees):").grid(row=pf_row,column=0,sticky=Tkinter.E)
        self.direction_tk_var = Tkinter.DoubleVar()
        self.direction_tk_var.set(self.meta_params.direction_deg)
        self.make_callback_entry(textvariable=self.direction_tk_var).grid(row=pf_row,column=2)
        self.loopable_variables["Direction"] = ("direction_deg",self.direction_tk_var)

        pf_row += 1
        Tkinter.Label(param_frame,text="Color:").grid(row=pf_row,column=0,sticky=Tkinter.E)
        self.color_tk_var = Tkinter.StringVar()
        self.color_tk_var.set("black on white")
        bar = Tkinter.Menubutton(param_frame, textvariable=self.color_tk_var, relief=Tkinter.RAISED)
        bar.grid(row=pf_row, column=2, sticky=Tkinter.W+Tkinter.E, pady=2, padx=2)
        bar.menu = Tkinter.Menu(bar,tearoff=0)
        bar.menu.add_radiobutton(label="white on black",
                                 value="white on black",
                                 variable=self.color_tk_var,
                                 command=self.send_values)
        bar.menu.add_radiobutton(label="black on white",
                                 value="black on white",
                                 variable=self.color_tk_var,
                                 command=self.send_values)
        bar['menu'] = bar.menu

        pf_row += 1
        Tkinter.Label(param_frame,text="Orientation (degrees):").grid(row=pf_row,column=0,sticky=Tkinter.E)
        self.ortho_tk_var = Tkinter.StringVar()
        self.ortho_tk_var.set("ortho")

        manual = Tkinter.Radiobutton( param_frame, text="Manual",
                                      variable=self.ortho_tk_var, value="manual")
        manual.grid(row=pf_row,column=1)

        self.orient_tk_var = Tkinter.DoubleVar()
        self.orient_tk_var.set(self.meta_params.orientation_deg)

        manual_entry = Tkinter.Entry( param_frame,
                                      textvariable=self.orient_tk_var,
                                      width=self.entry_width )
        manual_entry.grid(row=pf_row,column=2)

        ortho = Tkinter.Radiobutton( param_frame, text="Orthogonal to motion",
                                     variable=self.ortho_tk_var, value="ortho")
        ortho.grid(row=pf_row,column=3)
        self.loopable_variables["Orientation"] = ("orientation_deg",self.orient_tk_var)

        pf_row += 1
        Tkinter.Label(param_frame,text="Width (pixels):").grid(row=pf_row,column=0,sticky=Tkinter.E)
        self.width_tk_var = Tkinter.DoubleVar()
        self.width_tk_var.set(self.meta_params.width)
        self.make_callback_entry(textvariable=self.width_tk_var).grid(row=pf_row,column=2)
        self.loopable_variables["Width"] = ("width",self.width_tk_var)

        pf_row += 1
        Tkinter.Label(param_frame,text="Height (pixels):").grid(row=pf_row,column=0,sticky=Tkinter.E)
        self.height_tk_var = Tkinter.DoubleVar()
        self.height_tk_var.set(self.meta_params.height)
        self.make_callback_entry(textvariable=self.height_tk_var).grid(row=pf_row,column=2)
        self.loopable_variables["Height"] = ("height",self.height_tk_var)

        pf_row += 1
        Tkinter.Label(param_frame,text="Pre stimulus duration (sec):").grid(row=pf_row,column=0,sticky=Tkinter.E)
        self.prestim_dur_tk_var = Tkinter.DoubleVar()
        self.prestim_dur_tk_var.set(self.meta_params.pre_stim_sec)
        self.make_callback_entry(textvariable=self.prestim_dur_tk_var).grid(row=pf_row,column=2)

        pf_row += 1
        Tkinter.Label(param_frame,text="Stimulus duration (sec):").grid(row=pf_row,column=0,sticky=Tkinter.E)
        self.stim_dur_tk_var = Tkinter.DoubleVar()
        self.stim_dur_tk_var.set(self.meta_params.stim_sec)
        self.make_callback_entry(textvariable=self.stim_dur_tk_var).grid(row=pf_row,column=2)
        self.loopable_variables["Duration"] = ("stim_sec",self.stim_dur_tk_var)

        pf_row += 1
        Tkinter.Label(param_frame,text="Post stimulus duration (sec):").grid(row=pf_row,column=0,sticky=Tkinter.E)
        self.poststim_dur_tk_var = Tkinter.DoubleVar()
        self.poststim_dur_tk_var.set(self.meta_params.post_stim_sec)
        self.make_callback_entry(textvariable=self.poststim_dur_tk_var).grid(row=pf_row,column=2)

    def get_shortname(self):
        return "target"

    def update_tk_vars(self):
        self.start_x_tk_var.set( self.meta_params.start_x )
        self.start_y_tk_var.set( self.meta_params.start_y )
        self.velocity_tk_var.set( self.meta_params.velocity_pps )
        self.direction_tk_var.set( self.meta_params.direction_deg )
        self.orient_tk_var.set( self.meta_params.orientation_deg )
        self.width_tk_var.set( self.meta_params.width )
        self.height_tk_var.set( self.meta_params.height )
        self.prestim_dur_tk_var.set( self.meta_params.pre_stim_sec )
        self.stim_dur_tk_var.set( self.meta_params.stim_sec )
        self.poststim_dur_tk_var.set( self.meta_params.post_stim_sec )

        if self.meta_params.color == (0.0,0.0,0.0,1.0) and self.meta_params.bgcolor == (1.0,1.0,1.0,0.0):
            self.color_tk_var.set( "black on white" )
        elif self.meta_params.color == (1.0,1.0,1.0,1.0) and self.meta_params.bgcolor == (0.0,0.0,0.0,0.0):
            self.color_tk_var.set( "white on black" )
        else:
            raise RuntimeError("Cannot set tk variable for color")

    def send_values(self,dummy_arg=None):
        self.meta_params.start_x = self.start_x_tk_var.get()
        self.meta_params.start_y = self.start_y_tk_var.get()
        self.meta_params.velocity_pps = self.velocity_tk_var.get()
        self.meta_params.direction_deg = self.direction_tk_var.get()
        if self.color_tk_var.get() == "black on white":
            self.meta_params.color = (0.0,0.0,0.0,1.0)
            self.meta_params.bgcolor = (1.0,1.0,1.0,0.0)
        elif self.color_tk_var.get() == "white on black":
            self.meta_params.color = (1.0,1.0,1.0,1.0)
            self.meta_params.bgcolor = (0.0,0.0,0.0,0.0)

        if self.ortho_tk_var.get() == "ortho":
            self.meta_params.orientation_deg = math.fmod(self.meta_params.direction_deg,360.0)
        else: # it's "manual"
            self.meta_params.orientation_deg = self.orient_tk_var.get()
        self.meta_params.width = self.width_tk_var.get()
        self.meta_params.height = self.height_tk_var.get()
        self.meta_params.pre_stim_sec = self.prestim_dur_tk_var.get()
        self.meta_params.stim_sec = self.stim_dur_tk_var.get()
        self.meta_params.post_stim_sec = self.poststim_dur_tk_var.get()
        if self.connected:
            self.meta_controller.set_parameters( self.meta_params )

    def get_duration_sec(self):
        self.meta_params.pre_stim_sec = self.prestim_dur_tk_var.get()
        self.meta_params.stim_sec = self.stim_dur_tk_var.get()
        self.meta_params.post_stim_sec = self.poststim_dur_tk_var.get()
        return self.meta_params.pre_stim_sec + self.meta_params.stim_sec + self.meta_params.post_stim_sec

if __name__=='__main__':
    frame = TargetControlFrame()
    frame.pack(expand=Tkinter.YES,fill=Tkinter.BOTH)
    frame.winfo_toplevel().title("%s"%(os.path.basename(os.path.splitext(sys.argv[0])[0]),))
    frame.mainloop()
