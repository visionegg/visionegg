#!/usr/bin/env python
"""Handle mouse controlled small target stimulus (client-side)"""

# Copyright (c) 2002-2003 Andrew Straw.  Distributed under the terms
# of the GNU Lesser General Public License (LGPL).

import VisionEgg, string
__version__ = VisionEgg.release_name
__cvs__ = string.split('$Revision$')[1]
__date__ = string.join(string.split('$Date$')[1:3], ' ')
__author__ = 'Andrew Straw <astraw@users.sourceforge.net>'

import sys, os
import Tkinter
import VisionEgg.PyroApps.UberClientUtils as client_utils

def get_control_list():
    return [("mouse_target_server",MouseTargetControlFrame,MouseTargetControlFrame.title)]

class MouseTargetMetaParameters:
    def __init__(self):
        # colors
        self.color = (0.0, 0.0, 0.0, 1.0)
        self.bgcolor = (1.0, 1.0, 1.0, 0.0)
        
class MouseTargetControlFrame(client_utils.StimulusControlFrame):
    title = "Mouse Controlled Moving Target"
    def __init__(self, master=None, suppress_uber_buttons=0,**kw):
        apply(client_utils.StimulusControlFrame.__init__,(self,
                                                          master,
                                                          suppress_uber_buttons,
                                                          MouseTargetControlFrame.title,
                                                          MouseTargetMetaParameters),kw)

        param_frame = self.param_frame # shorthand for self.param_frame created in base class

        # Allow columns to expand
        param_frame.columnconfigure(0,weight=1)
        param_frame.columnconfigure(1,weight=1)
        
        pf_row = 0
        if 0:
            Tkinter.Label(param_frame,text="Start X (pixels):").grid(row=pf_row,column=0)
            self.start_x_tk_var = Tkinter.DoubleVar()
            self.start_x_tk_var.set(self.meta_params.start_x)
            self.make_callback_entry(textvariable=self.start_x_tk_var).grid(row=pf_row,column=2)
            self.loopable_variables["Start X"] = ("start_x",self.start_x_tk_var)
            
            pf_row += 1
            Tkinter.Label(param_frame,text="Start Y (pixels):").grid(row=pf_row,column=0)
            self.start_y_tk_var = Tkinter.DoubleVar()
            self.start_y_tk_var.set(self.meta_params.start_y)
            self.make_callback_entry(textvariable=self.start_y_tk_var).grid(row=pf_row,column=2)
            self.loopable_variables["Start Y"] = ("start_y",self.start_y_tk_var)
            
            pf_row += 1
            Tkinter.Label(param_frame,text="Velocity (pixels/sec):").grid(row=pf_row,column=0)
            self.velocity_tk_var = Tkinter.DoubleVar()
            self.velocity_tk_var.set(self.meta_params.velocity_pps)
            self.make_callback_entry(textvariable=self.velocity_tk_var).grid(row=pf_row,column=2)
            self.loopable_variables["Velocity"] = ("velocity_pps",self.velocity_tk_var)
            
            pf_row += 1
            Tkinter.Label(param_frame,text="Direction (degrees):").grid(row=pf_row,column=0)
            self.direction_tk_var = Tkinter.DoubleVar()
            self.direction_tk_var.set(self.meta_params.direction_deg)
            self.make_callback_entry(textvariable=self.direction_tk_var).grid(row=pf_row,column=2)
            self.loopable_variables["Direction"] = ("direction_deg",self.direction_tk_var)
    
            pf_row += 1
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

        if 0:
            pf_row += 1
            Tkinter.Label(param_frame,text="Orientation (degrees):").grid(row=pf_row,column=0)
            self.ortho_tk_var = Tkinter.StringVar()
            self.ortho_tk_var.set("ortho")
    
            ortho = Tkinter.Radiobutton( param_frame, text="Orthogonal",
                                        variable=self.ortho_tk_var, value="ortho")
            ortho.grid(row=pf_row,column=3)
            manual = Tkinter.Radiobutton( param_frame, #text="Orthogonal",
                                        variable=self.ortho_tk_var, value="manual")
            manual.grid(row=pf_row,column=1)
            self.orient_tk_var = Tkinter.DoubleVar()
            self.orient_tk_var.set(self.meta_params.orientation_deg)
            manual_entry = Tkinter.Entry( param_frame,
                                        textvariable=self.orient_tk_var,
                                        width=self.entry_width )
            manual_entry.grid(row=pf_row,column=2)
            self.loopable_variables["Orientation"] = ("orientation_deg",self.orient_tk_var)
            
            pf_row += 1
            Tkinter.Label(param_frame,text="Width (pixels):").grid(row=pf_row,column=0)
            self.width_tk_var = Tkinter.DoubleVar()
            self.width_tk_var.set(self.meta_params.width)
            self.make_callback_entry(textvariable=self.width_tk_var).grid(row=pf_row,column=2)
            self.loopable_variables["Width"] = ("width",self.width_tk_var)
            
            pf_row += 1
            Tkinter.Label(param_frame,text="Height (pixels):").grid(row=pf_row,column=0)
            self.height_tk_var = Tkinter.DoubleVar()
            self.height_tk_var.set(self.meta_params.height)
            self.make_callback_entry(textvariable=self.height_tk_var).grid(row=pf_row,column=2)
            self.loopable_variables["Height"] = ("height",self.height_tk_var)
            
            pf_row += 1
            Tkinter.Label(param_frame,text="Pre stimulus duration (sec):").grid(row=pf_row,column=0)
            self.prestim_dur_tk_var = Tkinter.DoubleVar()
            self.prestim_dur_tk_var.set(self.meta_params.pre_stim_sec)
            self.make_callback_entry(textvariable=self.prestim_dur_tk_var).grid(row=pf_row,column=2)
            
            pf_row += 1
            Tkinter.Label(param_frame,text="Stimulus duration (sec):").grid(row=pf_row,column=0)
            self.stim_dur_tk_var = Tkinter.DoubleVar()
            self.stim_dur_tk_var.set(self.meta_params.stim_sec)
            self.make_callback_entry(textvariable=self.stim_dur_tk_var).grid(row=pf_row,column=2)
            self.loopable_variables["Duration"] = ("stim_sec",self.stim_dur_tk_var)
            
            pf_row += 1
            Tkinter.Label(param_frame,text="Post stimulus duration (sec):").grid(row=pf_row,column=0)
            self.poststim_dur_tk_var = Tkinter.DoubleVar()
            self.poststim_dur_tk_var.set(self.meta_params.post_stim_sec)
            self.make_callback_entry(textvariable=self.poststim_dur_tk_var).grid(row=pf_row,column=2)

    def get_shortname(self):
        return "mouse_target"

    def update_tk_vars(self):
        if 0:
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
        if self.color_tk_var.get() == "black on white":
            self.meta_params.color = (0.0,0.0,0.0,1.0)
            self.meta_params.bgcolor = (1.0,1.0,1.0,0.0)
        elif self.color_tk_var.get() == "white on black":
            self.meta_params.color = (1.0,1.0,1.0,1.0)
            self.meta_params.bgcolor = (0.0,0.0,0.0,0.0)

        if 0:
            self.meta_params.start_x = self.start_x_tk_var.get()
            self.meta_params.start_y = self.start_y_tk_var.get()
            self.meta_params.velocity_pps = self.velocity_tk_var.get()
            self.meta_params.direction_deg = self.direction_tk_var.get()
            
            if self.ortho_tk_var.get():
                self.meta_params.orientation_deg = self.meta_params.direction_deg
            else:
                self.meta_params.orientation_deg = self.orient_tk_var.get()
            self.meta_params.width = self.width_tk_var.get()
            self.meta_params.height = self.height_tk_var.get()
            self.meta_params.pre_stim_sec = self.prestim_dur_tk_var.get()
            self.meta_params.stim_sec = self.stim_dur_tk_var.get()
            self.meta_params.post_stim_sec = self.poststim_dur_tk_var.get()
        if self.connected:
            self.meta_controller.set_parameters( self.meta_params )

    def get_duration_sec(self):
        if 0:
            self.meta_params.pre_stim_sec = self.prestim_dur_tk_var.get()
            self.meta_params.stim_sec = self.stim_dur_tk_var.get()
            self.meta_params.post_stim_sec = self.poststim_dur_tk_var.get()
            return self.meta_params.pre_stim_sec + self.meta_params.stim_sec + self.meta_params.post_stim_sec
        return 0.0

if __name__=='__main__':
    frame = MouseTargetControlFrame()
    frame.pack(expand=1,fill=Tkinter.BOTH)
    frame.winfo_toplevel().title("%s"%(os.path.basename(os.path.splitext(sys.argv[0])[0]),))
    frame.mainloop()
