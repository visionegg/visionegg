#!/usr/bin/env python
"""Sinusoidal grating stimulus control (see metaPyroServer)
"""

# Copyright (c) 2002 Andrew Straw.  Distributed under the terms
# of the GNU Lesser General Public License (LGPL).

import sys, os
import Tkinter
import Pyro.core
import VisionEgg.PyroClient

class GratingMetaParameters:
    def __init__(self):
        self.contrast = 1.0
        self.orient = 0.0
        self.sf = 0.02
        self.tf = 1.0
        self.pre_stim_sec = 1.0
        self.stim_sec = 2.0
        self.post_stim_sec = 1.0
        
class CallbackEntry(Tkinter.Entry):
    def __init__(self,master=None,callback=None,**kw):
        Tkinter.Entry.__init__(self,master, **kw)
        self.bind('<Return>',callback)
        self.bind('<Tab>',callback)

class StimulusControlFrame(Tkinter.Frame):
    def __init__(self, master=None, suppress_begin_button=0,**kw):
        Tkinter.Frame.__init__(self,master,**kw)
        self.pyro_client = None
        self.entry_width = 10
        self.connected = 0
        self.meta_params = GratingMetaParameters()
        self.loopable_variables = {}

        row = 0
        Tkinter.Label(self,text="Grating Experiment").grid(row=row,column=0,columnspan=2)

        row += 1
        # let columns expand
        connected_frame = Tkinter.Frame(self)
        connected_frame.grid(row=row,column=0,columnspan=2,sticky=Tkinter.W+Tkinter.E)
        connected_frame.columnconfigure(0,weight=1)
        connected_frame.columnconfigure(1,weight=1)
        connected_frame.columnconfigure(2,weight=1)
        
        Tkinter.Label(connected_frame,text="Server hostname:").grid(row=0,column=0,sticky=Tkinter.E)
        self.server_hostname = Tkinter.StringVar()
        self.server_hostname.set( '' )
        Tkinter.Entry(connected_frame,textvariable=self.server_hostname).grid(row=0,
                                                                              column=1,
                                                                              columnspan=2,
                                                                              sticky=Tkinter.W+Tkinter.E)

        self.connected_label = Tkinter.Label(connected_frame,text="Server status: Not connected")
        self.connected_label.grid(row=1,column=0)
        Tkinter.Button(connected_frame,text="Connect",command=self.connect).grid(row=1,column=1)
        Tkinter.Button(connected_frame,text="Quit server",command=self.quit_server).grid(row=1,column=2)

        row += 1
        param_frame = Tkinter.Frame(self)
        param_frame.grid(row=row,column=0,sticky=Tkinter.N)
        param_frame.columnconfigure(0,weight=1)
        param_frame.columnconfigure(1,weight=1)

        pf_row = 0
        Tkinter.Label(param_frame,text="Contrast:").grid(row=pf_row,column=0)
        self.contrast_tk_var = Tkinter.DoubleVar()
        self.contrast_tk_var.set(1.0)
        CallbackEntry(param_frame,
                      self.send_values,
                      width=self.entry_width,
                      textvariable=self.contrast_tk_var).grid(row=pf_row,column=1)
        self.loopable_variables["Contrast"] = ("contrast",self.contrast_tk_var)

        pf_row += 1
        Tkinter.Label(param_frame,text="Spatial frequency:").grid(row=pf_row,column=0)
        self.sf_tk_var = Tkinter.DoubleVar()
        self.sf_tk_var.set(0.02)
        CallbackEntry(param_frame,
                      self.send_values,
                      width=self.entry_width,
                      textvariable=self.sf_tk_var).grid(row=pf_row,column=1)
        self.loopable_variables["Spatial frequency"] = ("sf",self.sf_tk_var)
        
        pf_row += 1
        Tkinter.Label(param_frame,text="Temporal frequency:").grid(row=pf_row,column=0)
        self.tf_tk_var = Tkinter.DoubleVar()
        self.tf_tk_var.set(5.0)
        CallbackEntry(param_frame,
                      self.send_values,
                      width=self.entry_width,
                      textvariable=self.tf_tk_var).grid(row=pf_row,column=1)
        self.loopable_variables["Temporal frequency"] = ("tf",self.tf_tk_var)
        
        pf_row += 1
        Tkinter.Label(param_frame,text="Orientation:").grid(row=pf_row,column=0)
        self.orient_tk_var = Tkinter.DoubleVar()
        self.orient_tk_var.set(0.0)
        CallbackEntry(param_frame,
                      self.send_values,
                      width=self.entry_width,
                      textvariable=self.orient_tk_var).grid(row=pf_row,column=1)
        self.loopable_variables["Orientation"] = ("orient",self.orient_tk_var)
        
        pf_row += 1
        Tkinter.Label(param_frame,text="Pre stimulus duration (sec):").grid(row=pf_row,column=0)
        self.prestim_dur_tk_var = Tkinter.DoubleVar()
        self.prestim_dur_tk_var.set(1.0)
        CallbackEntry(param_frame,
                      self.send_values,
                      width=self.entry_width,
                      textvariable=self.prestim_dur_tk_var).grid(row=pf_row,column=1)
        
        pf_row += 1
        Tkinter.Label(param_frame,text="Stimulus duration (sec):").grid(row=pf_row,column=0)
        self.stim_dur_tk_var = Tkinter.DoubleVar()
        self.stim_dur_tk_var.set(2.0)
        CallbackEntry(param_frame,
                      self.send_values,
                      width=self.entry_width,
                      textvariable=self.stim_dur_tk_var).grid(row=pf_row,column=1)
        
        pf_row += 1
        Tkinter.Label(param_frame,text="Post stimulus duration (sec):").grid(row=pf_row,column=0)
        self.poststim_dur_tk_var = Tkinter.DoubleVar()
        self.poststim_dur_tk_var.set(1.0)
        CallbackEntry(param_frame,
                      self.send_values,
                      width=self.entry_width,
                      textvariable=self.poststim_dur_tk_var).grid(row=pf_row,column=1)

        if not suppress_begin_button:
            row += 1
            Tkinter.Button(self,text="Begin Trial",command=self.go).grid(row=row,column=0,columnspan=2)

    def get_shortname(self):
        """Used as basename for saving parameter files"""
        return "simple_grating"

    def get_param_dict(self):
        result = {}
        for param_name in dir(self.meta_params):
            if param_name[:2] != '__' and param_name[-2:] != '__':
                result[param_name] = getattr(self.meta_params,param_name)
        return result

    def get_type(self):
        return "metaPyroGUI"
    
    def set_param_dict(self,new_param_dict):
        orig_params = dir(self.meta_params)
        for new_param_name in new_param_dict.keys():
            if new_param_name[:2] != '__' and new_param_name[-2:] != '__':
                if new_param_name not in orig_params:
                    raise ValueError('Gave parameter "%s", which I do not know about.'%(new_param_name,))
                setattr(self.meta_params,new_param_name,new_param_dict[new_param_name])
        self.contrast_tk_var.set( self.meta_params.contrast )
        self.sf_tk_var.set( self.meta_params.sf )
        self.tf_tk_var.set( self.meta_params.tf )
        self.orient_tk_var.set( self.meta_params.orient )
        self.prestim_dur_tk_var.set( self.meta_params.pre_stim_sec )
        self.stim_dur_tk_var.set( self.meta_params.stim_sec )
        self.poststim_dur_tk_var.set( self.meta_params.post_stim_sec )
    
    def get_parameters_as_strings(self):
        result = []
        for param_name in dir(self.meta_params):
            if param_name[:2] != '__' and param_name[-2:] != '__':
                value = getattr(self.meta_params,param_name)
                value_string = str(value)
                result.append((param_name,value_string))
        return result

    def get_loopable_variable_names(self):
        return self.loopable_variables.keys()

    def set_loopable_variable(self,easy_name,value):
        meta_param_var_name,tk_var = self.loopable_variables[easy_name]
        setattr(self.meta_params,meta_param_var_name,value)
        tk_var.set(value)
        self.update() # update screen with new tk_var value
        
    def send_values(self,dummy_arg=None):
        self.meta_params.contrast = self.contrast_tk_var.get()
        self.meta_params.sf = self.sf_tk_var.get()
        self.meta_params.tf = self.tf_tk_var.get()
        self.meta_params.orient = self.orient_tk_var.get()
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

    def go(self,dummy_arg=None):
        self.send_values()
        if not self.connected:
            raise RuntimeError("must be connected to metaPyroServer to run trial")
        self.meta_controller.go()
##        if self.connected:
##            self.meta_controller.go()

    def connect(self):
        self.pyro_client = VisionEgg.PyroClient.PyroClient(server_hostname=self.server_hostname.get(),
                                                           server_port=7766)

        self.meta_controller = self.pyro_client.get("meta_controller")
        self.meta_params = self.meta_controller.get_parameters()

        self.connected = 1
        self.meta_controller.turn_off()
        self.connected_label.config(text="Server status: Connected")

    def quit_server(self,dummy=None):
        self.meta_controller.quit_server()
        self.connected = 0
        self.connected_label.config(text="Server status: Not connected")

if __name__=='__main__':
    frame = StimulusControlFrame()
    frame.pack(expand=1,fill=Tkinter.BOTH)
    frame.winfo_toplevel().title("%s"%(os.path.basename(os.path.splitext(sys.argv[0])[0]),))
    frame.mainloop()  
