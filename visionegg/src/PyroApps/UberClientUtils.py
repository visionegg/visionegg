#!/usr/bin/env python

# Copyright (c) 2002-2003 Andrew Straw.  Distributed under the terms
# of the GNU Lesser General Public License (LGPL).

import sys, os, string, time, types
import Tkinter
import Pyro.core

import VisionEgg.PyroClient

__version__ = VisionEgg.release_name
__cvs__ = string.split('$Revision$')[1]
__date__ = string.join(string.split('$Date$')[1:3], ' ')
__author__ = 'Andrew Straw <astraw@users.sourceforge.net>'

class StimulusControlFrame(Tkinter.Frame):
    def __init__(self,
                 master=None,
                 suppress_uber_buttons=0,
                 title="Stimulus Control",
                 meta_params_class=None,
                 **kw):
        apply(Tkinter.Frame.__init__,(self,master),kw)
        self.pyro_client = None
        self.entry_width = 10
        self.connected = 0
        self.meta_params = meta_params_class()
        self.loopable_variables = {}

        row = 0
        Tkinter.Label(self,
                      text=title,
                      font=("Helvetica",12,"bold")).grid(row=row,column=0,columnspan=2)
        
        if not suppress_uber_buttons:
            row += 1

            # let columns expand
            connected_frame = Tkinter.Frame(self)
            connected_frame.grid(row=row,column=0,columnspan=2,sticky=Tkinter.W+Tkinter.E)
            connected_frame.columnconfigure(0,weight=1)
            connected_frame.columnconfigure(1,weight=1)
            connected_frame.columnconfigure(2,weight=1)

            self.connected_label = Tkinter.Label(connected_frame,text="Server status: Not connected")
            self.connected_label.grid(row=0,column=0)
            Tkinter.Button(connected_frame,text="Connect",command=self.connect).grid(row=0,column=1)
            Tkinter.Button(connected_frame,text="Quit server",command=self.quit_server).grid(row=0,column=2)
        
        row += 1
        self.param_frame = Tkinter.Frame(self)
        self.param_frame.grid(row=row,column=0,sticky=Tkinter.N)
        
        if not suppress_uber_buttons:
            row += 1
            Tkinter.Button(self,text="Begin Trial",command=self.go).grid(row=row,column=0,columnspan=2)

    def make_callback_entry(self, master=None, **kw):
        if 'width' not in kw.keys():
            kw['width'] = self.entry_width
        if master==None:
            master=self.param_frame
        e = apply(Tkinter.Entry,(master,),kw)
        e.bind('<Return>',self.send_values)
        e.bind('<Tab>',self.send_values)
        return e
            
    def get_shortname(self):
        """Used as basename for saving parameter files and other ID purposes"""
        raise NotImplementedError("Must be overriden by derived class")

    def set_param_dict(self,new_param_dict):
        orig_params = dir(self.meta_params)
        for new_param_name in new_param_dict.keys():
            if new_param_name[:2] != '__' and new_param_name[-2:] != '__':
                if new_param_name not in orig_params:
                    raise ValueError('Gave parameter "%s", which I do not know about.'%(new_param_name,))
                setattr(self.meta_params,new_param_name,new_param_dict[new_param_name])
        self.update_tk_vars()
        self.update() # update screen with new tk_var value

    def update_tk_vars(self):
        """Update Tkinter variables with (new) values from meta_params"""
        raise NotImplementedError("Must be overriden by derived class")

    def get_parameters_dict(self):
        result = {}
        for param_name in dir(self.meta_params):
            if param_name[:2] != '__' and param_name[-2:] != '__':
                result[param_name] = getattr(self.meta_params,param_name)
        return result

    def get_parameters_as_py_strings(self):
        """Return parameter values as Python-executable strings"""
        result = []
        for param_name in dir(self.meta_params):
            if param_name[:2] != '__' and param_name[-2:] != '__':
                value = getattr(self.meta_params,param_name)
                value_string = str(value)
                result.append((param_name,value_string))
        return result

    def get_parameters_as_m_strings(self):
        """Return parameter values as Matlab-executable strings"""
        result = []
        for param_name in dir(self.meta_params):
            if param_name[:2] != '__' and param_name[-2:] != '__':
                value = getattr(self.meta_params,param_name)
                value_string = self.get_matlab_string(value)
                result.append((param_name,value_string))
        return result

    def get_matlab_string(self, value):
        # I'm no Matlab whiz, so you may have to modify this!!
        if type(value) in [types.IntType, types.FloatType]:
            return str(value)
        elif type(value) in [types.ListType, types.TupleType]:
            s = "[ "
            for v in value:
                s += str(v) + " "
            s += "]"
            return s
        elif type(value) == types.StringType:
            s = "'%s'"%value
            return s
        else:
            raise NotImplementedError("No support for converting %s to Matlab format."%str(type(value)))

    def set_parameters_dict(self, dict):
        for key in dict.keys():
            if not key in dir(self.meta_params):
                raise RuntimeError("Parameter %s not in %s"%(key, str(self.meta_params)))
            setattr(self.meta_params,key,dict[key])

    def get_loopable_variable_names(self):
        return self.loopable_variables.keys()

    def set_loopable_variable(self,easy_name,value):
        meta_param_var_name,tk_var = self.loopable_variables[easy_name]
        setattr(self.meta_params,meta_param_var_name,value)
        tk_var.set(value)
        self.update() # update screen with new tk_var value
        
    def send_values(self,dummy_arg=None):
        """Update meta_params variables with values from Tkinter fields"""
        raise NotImplementedError("Must be overriden by derived class")

    def get_duration_sec(self):
        """Calculate total duration in go loop"""
        raise NotImplementedError("Must be overriden by derived class")

    def go(self,dummy_arg=None):
        self.send_values()
        if not self.connected:
            raise RuntimeError("must be connected to run trial")

        root = self.winfo_toplevel()
        old_cursor = root["cursor"]

        root["cursor"] = "watch"
        root.update()
        self.meta_controller.go()
        root["cursor"] = old_cursor
        root.update()

    def connect(self):
        self.pyro_client = VisionEgg.PyroClient.PyroClient()

        shortname = self.get_shortname()
        meta_controller_name = shortname + "_server"
        timeout_seconds = 60.0
        retry_interval_seconds = 0.1
        start_time = time.time()
        if hasattr(self,"meta_controller"):
            del self.meta_controller # get rid of old meta_controller

        # get new meta_controller
        while not hasattr(self,"meta_controller"):
            try:
                self.meta_controller = self.pyro_client.get(meta_controller_name)
            except Pyro.errors.NamingError, x:
                if str(x) == "name not found":
                    if (time.time()-start_time) >= timeout_seconds:
                        raise # Couldn't find experiment controller on Pyro network
                    time.sleep(retry_interval_seconds)
                else:
                    raise # unknown error
        
        self.meta_params = self.meta_controller.get_parameters()

        self.connected = 1
        if hasattr(self,'connected_label'): # uber client suppresses this label
            self.connected_label.config(text="Server status: Connected")

    def quit_server(self,dummy=None):
        self.meta_controller.quit_server()
        self.connected = 0
        if hasattr(self,'connected_label'): # uber client suppresses this label
            self.connected_label.config(text="Server status: Not connected")

if __name__=='__main__':
    frame = StimulusControlFrame()
    frame.pack(expand=1,fill=Tkinter.BOTH)
    frame.winfo_toplevel().title("%s"%(os.path.basename(os.path.splitext(sys.argv[0])[0]),))
    frame.mainloop()
