#!/usr/bin/env python
#
# The Vision Egg: MouseTargetGUI
#
# Copyright (C) 2001-2003 Andrew Straw.
# Author: Andrew Straw <astraw@users.sourceforge.net>
# URL: <http://www.visionegg.org/>
#
# Distributed under the terms of the GNU Lesser General Public License
# (LGPL). See LICENSE.TXT that came with this file.

"""Handle mouse controlled small target stimulus (client-side)"""

import VisionEgg, string

import sys, os
import Tkinter
import VisionEgg.PyroApps.EPhysGUIUtils as client_utils

def get_control_list():
    return [("mouse_target_server",MouseTargetControlFrame,MouseTargetControlFrame.title)]

class MouseTargetMetaParameters:
    def __init__(self):
        # colors
        self.color = (0.0, 0.0, 0.0, 1.0)
        self.bgcolor = (1.0, 1.0, 1.0, 0.0)

class MouseTargetControlFrame(client_utils.StimulusControlFrame):
    title = "Mouse Controlled Moving Target"
    def __init__(self, master=None, suppress_go_buttons=0,**kw):
        client_utils.StimulusControlFrame.__init__(self,
                                                   master,
                                                   suppress_go_buttons,
                                                   MouseTargetControlFrame.title,
                                                   MouseTargetMetaParameters,
                                                   **kw)

        param_frame = self.param_frame # shorthand for self.param_frame created in base class

        # Allow columns to expand
        param_frame.columnconfigure(0,weight=1)
        param_frame.columnconfigure(1,weight=1)

        pf_row = 0
        Tkinter.Label(param_frame,text="Color:").grid(row=pf_row,column=0)
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

    def get_shortname(self):
        return "mouse_target"

    def update_tk_vars(self):
        if self.meta_params.color == (0.0,0.0,0.0,1.0) and self.meta_params.bgcolor == (1.0,1.0,1.0,0.0):
            self.color_tk_var.set( "black on white" )
        elif self.meta_params.color == (1.0,1.0,1.0,1.0) and self.meta_params.bgcolor == (0.0,0.0,0.0,0.0):
            self.color_tk_var.set( "white on black" )
        else:
            raise RuntimeError("Cannot set tk variable for color")

    def send_values(self,dummy_arg=None):
        if self.color_tk_var.get() == "black on white":
            self.meta_params.color = (0.0,0.0,0.0,1.0)
            self.meta_params.bgcolor = (1.0,1.0,1.0,0.0)
        elif self.color_tk_var.get() == "white on black":
            self.meta_params.color = (1.0,1.0,1.0,1.0)
            self.meta_params.bgcolor = (0.0,0.0,0.0,0.0)

        if self.connected:
            self.meta_controller.set_parameters( self.meta_params )

    def get_duration_sec(self):
        return 0.0

if __name__=='__main__':
    frame = MouseTargetControlFrame()
    frame.pack(expand=1,fill=Tkinter.BOTH)
    frame.winfo_toplevel().title("%s"%(os.path.basename(os.path.splitext(sys.argv[0])[0]),))
    frame.mainloop()
