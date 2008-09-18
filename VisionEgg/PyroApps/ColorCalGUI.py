#!/usr/bin/env python
#
# The Vision Egg: ColorCalGUI
#
# Copyright (C) 2001-2003 Andrew Straw.
# Author: Andrew Straw <astraw@users.sourceforge.net>
# URL: <http://www.visionegg.org/>
#
# Distributed under the terms of the GNU Lesser General Public License
# (LGPL). See LICENSE.TXT that came with this file.
#
# $Id$

"""Handle luminance and color calibration stimulus (client-side)"""

import VisionEgg, string
__version__ = VisionEgg.release_name
__cvs__ = string.split('$Revision$')[1]
__date__ = string.join(string.split('$Date$')[1:3], ' ')
__author__ = 'Andrew Straw <astraw@users.sourceforge.net>'

import sys, os
import Tkinter
import VisionEgg.PyroApps.EPhysGUIUtils as client_utils

def get_control_list():
    return [("color_cal_server",ColorCalControlFrame,ColorCalControlFrame.title)]

class ColorCalMetaParameters:
    def __init__(self):
        self.color = (1.0, 1.0, 1.0, 0.0)

class ColorCalControlFrame(client_utils.StimulusControlFrame):
    title = "Color Calibration"
    def __init__(self, master=None, suppress_go_buttons=0,**kw):
        client_utils.StimulusControlFrame.__init__(self,
                                                   master,
                                                   suppress_go_buttons,
                                                   ColorCalControlFrame.title,
                                                   ColorCalMetaParameters,
                                                   **kw)

        param_frame = self.param_frame # shorthand for self.param_frame created in base class

        # Allow columns to expand
        param_frame.columnconfigure(0,weight=1)
        param_frame.columnconfigure(1,weight=1)

        pf_row = 0
        Tkinter.Label(param_frame,text="Red:").grid(row=pf_row,column=0)
        self.red_tk_var = Tkinter.DoubleVar()
        self.red_tk_var.set(self.meta_params.color[0])
        self.make_callback_entry(textvariable=self.red_tk_var).grid(row=pf_row,column=1)

        pf_row += 1
        Tkinter.Label(param_frame,text="Green:").grid(row=pf_row,column=0)
        self.green_tk_var = Tkinter.DoubleVar()
        self.green_tk_var.set(self.meta_params.color[1])
        self.make_callback_entry(textvariable=self.green_tk_var).grid(row=pf_row,column=1)

        pf_row += 1
        Tkinter.Label(param_frame,text="Blue:").grid(row=pf_row,column=0)
        self.blue_tk_var = Tkinter.DoubleVar()
        self.blue_tk_var.set(self.meta_params.color[2])
        self.make_callback_entry(textvariable=self.blue_tk_var).grid(row=pf_row,column=1)

    def get_shortname(self):
        return "color_cal"

    def update_tk_vars(self):
        self.red_tk_var.set( self.meta_params.color[0] )
        self.green_tk_var.set( self.meta_params.color[1] )
        self.blue_tk_var.set( self.meta_params.color[2] )

    def send_values(self,dummy_arg=None):
        self.meta_params.color =  ( self.red_tk_var.get(),
                                    self.green_tk_var.get(),
                                    self.blue_tk_var.get(),
                                    0.0 )

        if self.connected:
            self.meta_controller.set_parameters( self.meta_params )

    def get_duration_sec(self):
        return 0.0

if __name__=='__main__':
    frame = ColorCalControlFrame()
    frame.pack(expand=1,fill=Tkinter.BOTH)
    frame.winfo_toplevel().title("%s"%(os.path.basename(os.path.splitext(sys.argv[0])[0]),))
    frame.mainloop()
