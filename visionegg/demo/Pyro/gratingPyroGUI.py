#!/usr/bin/env python
"""GUI panel for control of gratingPyroServer"""

# Copyright (c) 2002-2003 Andrew Straw.  Distributed under the terms
# of the GNU Lesser General Public License (LGPL).

import sys, os
import Tkinter

import VisionEgg.PyroClient

class CallbackEntry(Tkinter.Entry):
    def __init__(self,master=None,callback=None,**kw):
        Tkinter.Entry.__init__(self,master,**kw)
        self.bind('<Return>',callback)
        self.bind('<Tab>',callback)

class StimulusControlFrame(Tkinter.Frame):
    def __init__(self, master=None, suppress_begin_button=0,**kw):
        Tkinter.Frame.__init__(self,master,**kw)
        self.entry_width = 10
        self.connected = 0

        # let columns expand
        self.columnconfigure(0,weight=1)
        self.columnconfigure(1,weight=1)
        
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
        between_go_frame = Tkinter.Frame(self)
        between_go_frame.grid(row=row,column=0,sticky=Tkinter.N)
        bgf_row = 0
        Tkinter.Label(between_go_frame,text="Between trials").grid(row=bgf_row,column=0,columnspan=2)

        bgf_row += 1
        Tkinter.Label(between_go_frame,text="Contrast:").grid(row=bgf_row,column=0)
        self.between_contrast = Tkinter.DoubleVar()
        self.between_contrast.set(1.0)
        CallbackEntry(between_go_frame,self.send_values,width=self.entry_width,textvariable=self.between_contrast).grid(row=bgf_row,column=1)

        bgf_row += 1
        Tkinter.Label(between_go_frame,text="Spatial Frequency:").grid(row=bgf_row,column=0)
        self.between_sf = Tkinter.DoubleVar()
        self.between_sf.set(0.02)
        CallbackEntry(between_go_frame,self.send_values,width=self.entry_width,textvariable=self.between_sf).grid(row=bgf_row,column=1)

        bgf_row += 1
        Tkinter.Label(between_go_frame,text="Temporal Frequency:").grid(row=bgf_row,column=0)
        self.between_tf = Tkinter.DoubleVar()
        self.between_tf.set(0.0)
        CallbackEntry(between_go_frame,self.send_values,width=self.entry_width,textvariable=self.between_tf).grid(row=bgf_row,column=1)

        bgf_row += 1
        Tkinter.Label(between_go_frame,text="Orientation:").grid(row=bgf_row,column=0)
        self.between_orient = Tkinter.DoubleVar()
        self.between_orient.set(0.0)
        CallbackEntry(between_go_frame,self.send_values,width=self.entry_width,textvariable=self.between_orient).grid(row=bgf_row,column=1)

        trial_frame = Tkinter.Frame(self)
        trial_frame.grid(row=row,column=1,sticky=Tkinter.N)
        tf_row = 0
        Tkinter.Label(trial_frame,text="Trial Parameters").grid(row=tf_row,column=0,columnspan=2)

        tf_row += 1
        Tkinter.Label(trial_frame,text="Contrast:").grid(row=tf_row,column=0)
        self.trial_contrast = Tkinter.DoubleVar()
        self.trial_contrast.set(1.0)
        CallbackEntry(trial_frame,self.send_values,width=self.entry_width,textvariable=self.trial_contrast).grid(row=tf_row,column=1)
      
        tf_row += 1
        Tkinter.Label(trial_frame,text="Spatial Frequency:").grid(row=tf_row,column=0)
        self.trial_sf = Tkinter.DoubleVar()
        self.trial_sf.set(0.02)
        CallbackEntry(trial_frame,self.send_values,width=self.entry_width,textvariable=self.trial_sf).grid(row=tf_row,column=1)

        tf_row += 1
        Tkinter.Label(trial_frame,text="Temporal Frequency:").grid(row=tf_row,column=0)
        self.trial_tf = Tkinter.DoubleVar()
        self.trial_tf.set(0.5)
        CallbackEntry(trial_frame,self.send_values,width=self.entry_width,textvariable=self.trial_tf).grid(row=tf_row,column=1)

        tf_row += 1
        Tkinter.Label(trial_frame,text="Orientation:").grid(row=tf_row,column=0)
        self.trial_orient = Tkinter.DoubleVar()
        self.trial_orient.set(0.0)
        CallbackEntry(trial_frame,self.send_values,width=self.entry_width,textvariable=self.trial_orient).grid(row=tf_row,column=1)

        tf_row += 1
        Tkinter.Label(trial_frame,text="Duration (sec):").grid(row=tf_row,column=0)
        self.trial_dur_sec = Tkinter.DoubleVar()
        self.trial_dur_sec.set(2.0)
        CallbackEntry(trial_frame,self.send_values,width=self.entry_width,textvariable=self.trial_dur_sec).grid(row=tf_row,column=1)

        if not suppress_begin_button:
            tf_row += 1
            Tkinter.Button(trial_frame,text="Begin Trial",command=self.go).grid(row=tf_row,column=0,columnspan=2)

    def get_stim_param_dict(self):
        dict = {}
        self_dict = dir(self)
        for attrname in self_dict:
            if isinstance( getattr(self,attrname), Tkinter.Variable):
                dict[attrname] = getattr(self,attrname)
        return dict
    
    def go(self):
        self.send_values()
        self.go_controller.set_between_go_value(1)
        self.go_controller.evaluate_now()

    def send_values(self,dummy=None):
        if self.connected:
            self.duration_controller.set_during_go_value( (self.trial_dur_sec.get(),'seconds') )

            self.contrast_controller.set_during_go_value( self.trial_contrast.get() )
            self.contrast_controller.set_between_go_value( self.between_contrast.get() )
            self.contrast_controller.evaluate_now()
            
            self.sf_controller.set_during_go_value( self.trial_sf.get() )
            self.sf_controller.set_between_go_value( self.between_sf.get() )
            self.sf_controller.evaluate_now()
            
            self.tf_controller.set_during_go_value( self.trial_tf.get() )
            self.tf_controller.set_between_go_value( self.between_tf.get() )
            self.tf_controller.evaluate_now()
            
            self.orient_controller.set_during_go_value( self.trial_orient.get() )
            self.orient_controller.set_between_go_value( self.between_orient.get() )
            self.orient_controller.evaluate_now()
            
    def connect(self,dummy=None):
        client = VisionEgg.PyroClient.PyroClient(server_hostname=self.server_hostname.get(),
                                                 server_port=7766)

        self.tf_controller = client.get('tf_controller')
        self.sf_controller = client.get('sf_controller')
        self.contrast_controller = client.get('contrast_controller')
        self.orient_controller = client.get('orient_controller')
        self.duration_controller = client.get('duration_controller')
        self.go_controller = client.get('go_controller')
        self.quit_controller = client.get('quit_controller')

        self.connected = 1
        self.send_values()
        
        self.connected_label.config(text="Server status: connected")
        
    def quit_server(self,dummy=None):
        self.quit_controller.set_during_go_value(1)
        self.quit_controller.set_between_go_value(1)
        self.quit_controller.evaluate_now()

        self.connected = 0
        
        del self.tf_controller
        del self.sf_controller
        del self.contrast_controller
        del self.orient_controller
        del self.duration_controller
        del self.go_controller
        del self.quit_controller

if __name__=='__main__':
    frame = StimulusControlFrame()
    frame.pack(expand=1,fill=Tkinter.BOTH)
    frame.winfo_toplevel().title("%s"%(os.path.basename(os.path.splitext(sys.argv[0])[0]),))
    frame.mainloop()
