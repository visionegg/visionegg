#!/usr/bin/env python
#
# The Vision Egg: SpinningDrumGUI
#
# Copyright (C) 2001-2003 Andrew Straw.
# Author: Andrew Straw <astraw@users.sourceforge.net>
# URL: <http://www.visionegg.org/>
#
# Distributed under the terms of the GNU Lesser General Public License
# (LGPL). See LICENSE.TXT that came with this file.
#
# $Id$

import VisionEgg, string
__version__ = VisionEgg.release_name
__cvs__ = string.split('$Revision$')[1]
__date__ = string.join(string.split('$Date$')[1:3], ' ')
__author__ = 'Andrew Straw <astraw@users.sourceforge.net>'

import sys, os
import Tkinter
import VisionEgg.PyroApps.EPhysGUIUtils as client_utils

def get_control_list():
    return [("spinning_drum_server",SpinningDrumControlFrame,SpinningDrumControlFrame.title)]

class SpinningDrumMetaParameters:
    def __init__(self):
        self.contrast = 1.0
        self.velocity_dps = 100.0
        self.startpos_deg = 0.0
        self.pre_stim_sec = 1.0
        self.stim_sec = 5.0
        self.post_stim_sec = 1.0

class SpinningDrumControlFrame(client_utils.StimulusControlFrame):
    title = "Spinning Drum Experiment"
    def __init__(self, master=None, suppress_go_buttons=0,**kw):
        client_utils.StimulusControlFrame.__init__(self,
                                                   master,
                                                   suppress_go_buttons,
                                                   SpinningDrumControlFrame.title,
                                                   SpinningDrumMetaParameters,
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
        Tkinter.Label(param_frame,text="Velocity (dps):").grid(row=pf_row,column=0)
        self.velocity_tk_var = Tkinter.DoubleVar()
        self.velocity_tk_var.set(self.meta_params.velocity_dps)
        self.make_callback_entry(textvariable=self.velocity_tk_var).grid(row=pf_row,column=1)
        self.loopable_variables["Velocity"] = ("velocity_dps",self.velocity_tk_var)

        pf_row += 1
        Tkinter.Label(param_frame,text="Start position (deg):").grid(row=pf_row,column=0)
        self.startpos_tk_var = Tkinter.DoubleVar()
        self.startpos_tk_var.set(self.meta_params.startpos_deg)
        self.make_callback_entry(textvariable=self.startpos_tk_var).grid(row=pf_row,column=1)
        self.loopable_variables["Start position"] = ("startpos_deg",self.startpos_tk_var)

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

    def get_shortname(self):
        """Used as basename for saving parameter files"""
        return "spinning_drum"

    def update_tk_vars(self):
        self.contrast_tk_var.set( self.meta_params.contrast )
        self.velocity_tk_var.set( self.meta_params.velocity_dps )
        self.startpos_tk_var.set( self.meta_params.startpos_deg )
        self.stim_dur_tk_var.set( self.meta_params.stim_sec )
        self.poststim_dur_tk_var.set( self.meta_params.post_stim_sec )

    def send_values(self,dummy_arg=None):
        self.meta_params.contrast = self.contrast_tk_var.get()
        self.meta_params.velocity_dps = self.velocity_tk_var.get()
        self.meta_params.startpos_deg = self.startpos_tk_var.get()
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
    frame = SpinningDrumControlFrame()
    frame.pack(expand=1,fill=Tkinter.BOTH)
    frame.winfo_toplevel().title("%s"%(os.path.basename(os.path.splitext(sys.argv[0])[0]),))
    frame.mainloop()
