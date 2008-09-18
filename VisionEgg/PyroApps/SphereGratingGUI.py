#!/usr/bin/env python
"""Handle perspective-distorted sinusoidal gratings (client-side)"""

# Copyright (c) 2002-2003 Andrew Straw.  Distributed under the terms
# of the GNU Lesser General Public License (LGPL).

import VisionEgg, string
__version__ = VisionEgg.release_name
__cvs__ = string.split('$Revision$')[1]
__date__ = string.join(string.split('$Date$')[1:3], ' ')
__author__ = 'Andrew Straw <astraw@users.sourceforge.net>'

import sys, os
import Tkinter
import VisionEgg.PyroApps.EPhysGUIUtils as client_utils

def get_control_list():
    return [("sphere_grating_server",SphereGratingControlFrame,SphereGratingControlFrame.title)]

class SphereGratingMetaParameters:
    def __init__(self):
        self.contrast = 1.0
        self.orient = 0.0
        self.sf = 0.1 # cycles per degree
        self.tf = 1.0
        self.pre_stim_sec = 1.0
        self.stim_sec = 2.0
        self.post_stim_sec = 1.0
        self.window_func = 'gaussian'
        self.window_radius = 10.0
        self.window_az = 0.0
        self.window_el = 0.0

class SphereGratingControlFrame(client_utils.StimulusControlFrame):
    title = "Grating (Perspective-distorted) Experiment"
    def __init__(self, master=None, suppress_go_buttons=0,**kw):
        client_utils.StimulusControlFrame.__init__(self,
                                                   master,
                                                   suppress_go_buttons,
                                                   SphereGratingControlFrame.title,
                                                   SphereGratingMetaParameters,
                                                   **kw)

        param_frame = self.param_frame # shorthand for self.param_frame created in base class

        # Allow columns to expand
        param_frame.columnconfigure(0,weight=1)
        param_frame.columnconfigure(1,weight=1)

        pf_row = 0
        Tkinter.Label(param_frame,text="Contrast:").grid(row=pf_row,column=0)
        self.contrast_tk_var = Tkinter.DoubleVar()
        self.contrast_tk_var.set(self.meta_params.contrast)
        self.make_callback_entry(textvariable=self.contrast_tk_var).grid(row=pf_row,column=1)
        self.loopable_variables["Contrast"] = ("contrast",self.contrast_tk_var)

        pf_row += 1
        Tkinter.Label(param_frame,text="Orientation (deg):").grid(row=pf_row,column=0)
        self.orient_tk_var = Tkinter.DoubleVar()
        self.orient_tk_var.set(self.meta_params.orient)
        self.make_callback_entry(textvariable=self.orient_tk_var).grid(row=pf_row,column=1)
        self.loopable_variables["Orientation"] = ("orient",self.orient_tk_var)

        pf_row += 1
        Tkinter.Label(param_frame,text="Spatial frequency (Cpd):").grid(row=pf_row,column=0)
        self.sf_tk_var = Tkinter.DoubleVar()
        self.sf_tk_var.set(self.meta_params.sf)
        self.make_callback_entry(textvariable=self.sf_tk_var).grid(row=pf_row,column=1)
        self.loopable_variables["Spatial frequency"] = ("sf",self.sf_tk_var)

        pf_row += 1
        Tkinter.Label(param_frame,text="Temporal frequency (Hz):").grid(row=pf_row,column=0)
        self.tf_tk_var = Tkinter.DoubleVar()
        self.tf_tk_var.set(self.meta_params.tf)
        self.make_callback_entry(textvariable=self.tf_tk_var).grid(row=pf_row,column=1)
        self.loopable_variables["Temporal frequency"] = ("tf",self.tf_tk_var)

        pf_row += 1
        Tkinter.Label(param_frame,text="Pre stimulus duration (sec):").grid(row=pf_row,column=0)
        self.prestim_dur_tk_var = Tkinter.DoubleVar()
        self.prestim_dur_tk_var.set(self.meta_params.pre_stim_sec)
        self.make_callback_entry(textvariable=self.prestim_dur_tk_var).grid(row=pf_row,column=1)

        pf_row += 1
        Tkinter.Label(param_frame,text="Stimulus duration (sec):").grid(row=pf_row,column=0)
        self.stim_dur_tk_var = Tkinter.DoubleVar()
        self.stim_dur_tk_var.set(self.meta_params.stim_sec)
        self.make_callback_entry(textvariable=self.stim_dur_tk_var).grid(row=pf_row,column=1)

        pf_row += 1
        Tkinter.Label(param_frame,text="Post stimulus duration (sec):").grid(row=pf_row,column=0)
        self.poststim_dur_tk_var = Tkinter.DoubleVar()
        self.poststim_dur_tk_var.set(self.meta_params.post_stim_sec)
        self.make_callback_entry(textvariable=self.poststim_dur_tk_var).grid(row=pf_row,column=1)

        pf_row += 1
        Tkinter.Label(param_frame,text="Window function:").grid(row=pf_row,column=0)
        self.window_func_tk_var = Tkinter.StringVar()
        self.window_func_tk_var.set(self.meta_params.window_func)
        bar = Tkinter.Menubutton(param_frame, textvariable=self.window_func_tk_var, relief=Tkinter.RAISED)
        bar.grid(row=pf_row, column=1, sticky=Tkinter.W+Tkinter.E, pady=2, padx=2)
        bar.menu = Tkinter.Menu(bar,tearoff=0)
        bar.menu.add_radiobutton(label='circle',
                                 value='circle',
                                 variable=self.window_func_tk_var,
                                 command=self.send_values)
        bar.menu.add_radiobutton(label='gaussian',
                                 value='gaussian',
                                 variable=self.window_func_tk_var,
                                 command=self.send_values)
        bar['menu'] = bar.menu

        pf_row += 1
        Tkinter.Label(param_frame,text="Window radius/sigma (deg):").grid(row=pf_row,column=0)
        self.window_radius_tk_var = Tkinter.DoubleVar()
        self.window_radius_tk_var.set(self.meta_params.window_radius)
        self.make_callback_entry(textvariable=self.window_radius_tk_var).grid(row=pf_row,column=1)

        pf_row += 1
        Tkinter.Label(param_frame,text="Window azimuth (deg):").grid(row=pf_row,column=0)
        self.window_az_tk_var = Tkinter.DoubleVar()
        self.window_az_tk_var.set(self.meta_params.window_az)
        self.make_callback_entry(textvariable=self.window_az_tk_var).grid(row=pf_row,column=1)
        self.loopable_variables["Window azimuth"] = ("window_az",self.window_az_tk_var)

        pf_row += 1
        Tkinter.Label(param_frame,text="Window elevation (deg):").grid(row=pf_row,column=0)
        self.window_el_tk_var = Tkinter.DoubleVar()
        self.window_el_tk_var.set(self.meta_params.window_el)
        self.make_callback_entry(textvariable=self.window_el_tk_var).grid(row=pf_row,column=1)
        self.loopable_variables["Window elevation"] = ("window_el",self.window_el_tk_var)

    def get_shortname(self):
        return "sphere_grating"

    def update_tk_vars(self):
        self.contrast_tk_var.set( self.meta_params.contrast )
        self.orient_tk_var.set( self.meta_params.orient )
        self.sf_tk_var.set( self.meta_params.sf )
        self.tf_tk_var.set( self.meta_params.tf )
        self.prestim_dur_tk_var.set( self.meta_params.pre_stim_sec )
        self.stim_dur_tk_var.set( self.meta_params.stim_sec )
        self.poststim_dur_tk_var.set( self.meta_params.post_stim_sec )
        self.window_func_tk_var.set( self.meta_params.window_func )
        self.window_radius_tk_var.set( self.meta_params.window_radius )
        self.window_az_tk_var.set( self.meta_params.window_az )
        self.window_el_tk_var.set( self.meta_params.window_el )

    def send_values(self,dummy_arg=None):
        self.meta_params.contrast = self.contrast_tk_var.get()
        self.meta_params.orient = self.orient_tk_var.get()
        self.meta_params.sf = self.sf_tk_var.get()
        self.meta_params.tf = self.tf_tk_var.get()
        self.meta_params.pre_stim_sec = self.prestim_dur_tk_var.get()
        self.meta_params.stim_sec = self.stim_dur_tk_var.get()
        self.meta_params.post_stim_sec = self.poststim_dur_tk_var.get()
        self.meta_params.window_func = self.window_func_tk_var.get()
        self.meta_params.window_radius = self.window_radius_tk_var.get()
        self.meta_params.window_az = self.window_az_tk_var.get()
        self.meta_params.window_el = self.window_el_tk_var.get()
        if self.connected:
            self.meta_controller.set_parameters( self.meta_params )

    def get_duration_sec(self):
        self.meta_params.pre_stim_sec = self.prestim_dur_tk_var.get()
        self.meta_params.stim_sec = self.stim_dur_tk_var.get()
        self.meta_params.post_stim_sec = self.poststim_dur_tk_var.get()
        return self.meta_params.pre_stim_sec + self.meta_params.stim_sec + self.meta_params.post_stim_sec

if __name__=='__main__':
    frame = SphereGratingControlFrame()
    frame.pack(expand=1,fill=Tkinter.BOTH)
    frame.winfo_toplevel().title("%s"%(os.path.basename(os.path.splitext(sys.argv[0])[0]),))
    frame.mainloop()
