#!/usr/bin/env python
#
# The Vision Egg: ScreenPositionGUI
#
# Copyright (C) 2001-2003 Andrew Straw.
# Author: Andrew Straw <astraw@users.sourceforge.net>
# URL: <http://www.visionegg.org/>
#
# Distributed under the terms of the GNU Lesser General Public License
# (LGPL). See LICENSE.TXT that came with this file.

"""Handle 3D perspective projection (client-side)"""

import sys, os, pickle, math, string
import Tkinter, tkFileDialog
import Pyro.core
import VisionEgg.PyroClient
import StringIO

class ScreenPositionParameters:
    def __init__(self):

        # frustum (initial values - view portion of unit sphere)
        self.left = -0.2
        self.right = 0.2
        self.top = 0.2
        self.bottom = -0.2
        self.near = 0.2
        self.far = 20.0

        # position/orientation
        self.eye = (0.0, 0.0, 0.0) # observer position
        self.center = (0.0, 0.0, -1.0) # center of gaze
        self.up = (0.0, 1.0, 0.0) # up vector

class CallbackEntry(Tkinter.Entry):
    def __init__(self,master=None,callback=None,**kw):
        Tkinter.Entry.__init__(self,master, **kw)
        self.bind('<Return>',callback)
        self.bind('<Tab>',callback)

class ScreenPositionControlFrame(Tkinter.Frame):
    def __init__(self, master=None, auto_connect=0, server_hostname='', server_port=7766, **kw):
        Tkinter.Frame.__init__(self,master,**kw)
        self.pyro_client = None
        self.entry_width = 10
        self.connected = 0
        self.meta_params = ScreenPositionParameters()
        self.loopable_variables = {}

        row = 0
        Tkinter.Label(self,
                      text="3D Perspective Calibration",
                      font=("Helvetica",12,"bold")).grid(row=row,column=0,columnspan=2)

        row += 1
        Tkinter.Label(self,
                      text="This dialog allows you to enter acheive "+\
                      "the proper perspective distortion for 3D scenes."
                      ).grid(row=row,column=0,columnspan=2)

        if not auto_connect:
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
        param_frame = Tkinter.Frame(self)
        param_frame.grid(row=row,column=0,sticky=Tkinter.N)
        param_frame.columnconfigure(0,weight=1)
        param_frame.columnconfigure(1,weight=1)

        pf_row = 0
        frustum_frame = Tkinter.Frame(param_frame)
        frustum_frame.grid(row=pf_row,column=0,columnspan=2,ipady=5)

        ff_row = 0
        Tkinter.Label(frustum_frame,
                      text="Viewing volume size",
                      font=("Helvetica",12,"bold")).grid(row=ff_row,column=0,columnspan=3,ipady=5)

        ff_row += 1
        Tkinter.Label(frustum_frame,text="Left:").grid(row=ff_row,column=0)
        self.left_tk_var = Tkinter.DoubleVar()
        self.left_tk_var.set(self.meta_params.left)
        CallbackEntry(frustum_frame,
                      self.send_values,
                      width=self.entry_width,
                      textvariable=self.left_tk_var).grid(row=ff_row,column=1)

        ff_row += 1
        Tkinter.Label(frustum_frame,text="Right:").grid(row=ff_row,column=0)
        self.right_tk_var = Tkinter.DoubleVar()
        self.right_tk_var.set(self.meta_params.right)
        CallbackEntry(frustum_frame,
                      self.send_values,
                      width=self.entry_width,
                      textvariable=self.right_tk_var).grid(row=ff_row,column=1)

        ff_row += 1
        Tkinter.Label(frustum_frame,text="Top:").grid(row=ff_row,column=0)
        self.top_tk_var = Tkinter.DoubleVar()
        self.top_tk_var.set(self.meta_params.top)
        CallbackEntry(frustum_frame,
                      self.send_values,
                      width=self.entry_width,
                      textvariable=self.top_tk_var).grid(row=ff_row,column=1)

        ff_row += 1
        Tkinter.Label(frustum_frame,text="Bottom:").grid(row=ff_row,column=0)
        self.bottom_tk_var = Tkinter.DoubleVar()
        self.bottom_tk_var.set(self.meta_params.bottom)
        CallbackEntry(frustum_frame,
                      self.send_values,
                      width=self.entry_width,
                      textvariable=self.bottom_tk_var).grid(row=ff_row,column=1)

        ff_row += 1
        Tkinter.Label(frustum_frame,text="Near:").grid(row=ff_row,column=0)
        self.near_tk_var = Tkinter.DoubleVar()
        self.near_tk_var.set(self.meta_params.near)
        CallbackEntry(frustum_frame,
                      self.send_values,
                      width=self.entry_width,
                      textvariable=self.near_tk_var).grid(row=ff_row,column=1)

        ff_row += 1
        Tkinter.Label(frustum_frame,text="Far:").grid(row=ff_row,column=0)
        self.far_tk_var = Tkinter.DoubleVar()
        self.far_tk_var.set(self.meta_params.far)
        CallbackEntry(frustum_frame,
                      self.send_values,
                      width=self.entry_width,
                      textvariable=self.far_tk_var).grid(row=ff_row,column=1)

        # quick frustum frame
        qf_frame = Tkinter.Frame(frustum_frame)
        qf_frame.grid(row=1,column=2,rowspan=ff_row)

        qf_row = 0
        Tkinter.Button(qf_frame,text="Taller",command=self.frustum_taller).grid(row=qf_row,column=0,columnspan=2)
        qf_row += 1
        Tkinter.Button(qf_frame,text="Narrower",command=self.frustum_narrower).grid(row=qf_row,column=0)
        Tkinter.Button(qf_frame,text="Wider",command=self.frustum_wider).grid(row=qf_row,column=1)
        qf_row += 1
        Tkinter.Button(qf_frame,text="Shorter",command=self.frustum_shorter).grid(row=qf_row,column=0,columnspan=2)

        qf_row = 0
        Tkinter.Button(qf_frame,text="Up",command=self.frustum_up).grid(row=qf_row,column=2,columnspan=2)
        qf_row += 1
        Tkinter.Button(qf_frame,text="Left",command=self.frustum_left).grid(row=qf_row,column=2)
        Tkinter.Button(qf_frame,text="Right",command=self.frustum_right).grid(row=qf_row,column=3)
        qf_row += 1
        Tkinter.Button(qf_frame,text="Down",command=self.frustum_down).grid(row=qf_row,column=2,columnspan=2)

        pf_row += 1
        lookat_frame = Tkinter.Frame(param_frame)
        lookat_frame.grid(row=pf_row,column=0,columnspan=2,ipady=5)

        la_row = 0
        Tkinter.Label(lookat_frame,
                      text="Viewing volume orientation",
                      font=("Helvetica",12,"bold")).grid(row=la_row,column=0,columnspan=3,ipady=5)

        la_row += 1
        Tkinter.Label(lookat_frame,text="eye X:").grid(row=la_row,column=0)
        self.eye_x_tk_var = Tkinter.DoubleVar()
        self.eye_x_tk_var.set(self.meta_params.eye[0])
        CallbackEntry(lookat_frame,
                      self.send_values,
                      width=self.entry_width,
                      textvariable=self.eye_x_tk_var).grid(row=la_row,column=1)

        la_row += 1
        Tkinter.Label(lookat_frame,text="eye Y:").grid(row=la_row,column=0)
        self.eye_y_tk_var = Tkinter.DoubleVar()
        self.eye_y_tk_var.set(self.meta_params.eye[1])
        CallbackEntry(lookat_frame,
                      self.send_values,
                      width=self.entry_width,
                      textvariable=self.eye_y_tk_var).grid(row=la_row,column=1)

        la_row += 1
        Tkinter.Label(lookat_frame,text="eye Z:").grid(row=la_row,column=0)
        self.eye_z_tk_var = Tkinter.DoubleVar()
        self.eye_z_tk_var.set(self.meta_params.eye[2])
        CallbackEntry(lookat_frame,
                      self.send_values,
                      width=self.entry_width,
                      textvariable=self.eye_z_tk_var).grid(row=la_row,column=1)

        la_row += 1
        Tkinter.Label(lookat_frame,text="look at X:").grid(row=la_row,column=0)
        self.center_x_tk_var = Tkinter.DoubleVar()
        self.center_x_tk_var.set(self.meta_params.center[0])
        CallbackEntry(lookat_frame,
                      self.send_values,
                      width=self.entry_width,
                      textvariable=self.center_x_tk_var).grid(row=la_row,column=1)

        quick_la_frame = Tkinter.Frame(lookat_frame)
        quick_la_frame.grid(row=la_row,column=2,rowspan=3)
        qla_row = 0
        Tkinter.Button(quick_la_frame,text="Look at az -",command=self.az_decrease).grid(row=qla_row,column=0)
        Tkinter.Button(quick_la_frame,text="Look at az +",command=self.az_increase).grid(row=qla_row,column=1)
        self.look_at_az_str = Tkinter.StringVar()
        Tkinter.Label(quick_la_frame,textvariable=self.look_at_az_str).grid(row=qla_row,column=2)

        qla_row += 1
        Tkinter.Button(quick_la_frame,text="Look at el -",command=self.el_decrease).grid(row=qla_row,column=0)
        Tkinter.Button(quick_la_frame,text="Look at el +",command=self.el_increase).grid(row=qla_row,column=1)
        self.look_at_el_str = Tkinter.StringVar()
        Tkinter.Label(quick_la_frame,textvariable=self.look_at_el_str).grid(row=qla_row,column=2)

        az,el = self.get_az_el(self.meta_params.center)
        self.look_at_az_str.set("%.1f"%az)
        self.look_at_el_str.set("%.1f"%el)

        la_row += 1
        Tkinter.Label(lookat_frame,text="look at Y:").grid(row=la_row,column=0)
        self.center_y_tk_var = Tkinter.DoubleVar()
        self.center_y_tk_var.set(self.meta_params.center[1])
        CallbackEntry(lookat_frame,
                      self.send_values,
                      width=self.entry_width,
                      textvariable=self.center_y_tk_var).grid(row=la_row,column=1)

        la_row += 1
        Tkinter.Label(lookat_frame,text="look at Z:").grid(row=la_row,column=0)
        self.center_z_tk_var = Tkinter.DoubleVar()
        self.center_z_tk_var.set(self.meta_params.center[2])
        CallbackEntry(lookat_frame,
                      self.send_values,
                      width=self.entry_width,
                      textvariable=self.center_z_tk_var).grid(row=la_row,column=1)

        la_row += 1
        Tkinter.Label(lookat_frame,text="up X:").grid(row=la_row,column=0)
        self.up_x_tk_var = Tkinter.DoubleVar()
        self.up_x_tk_var.set(self.meta_params.up[0])
        CallbackEntry(lookat_frame,
                      self.send_values,
                      width=self.entry_width,
                      textvariable=self.up_x_tk_var).grid(row=la_row,column=1)

        quick_up_frame = Tkinter.Frame(lookat_frame)
        quick_up_frame.grid(row=la_row,column=2,rowspan=3)
        qup_row = 0
        Tkinter.Button(quick_up_frame,text="Up az -",command=self.up_az_decrease).grid(row=qup_row,column=0)
        Tkinter.Button(quick_up_frame,text="Up az +",command=self.up_az_increase).grid(row=qup_row,column=1)
        self.up_az_str = Tkinter.StringVar()
        Tkinter.Label(quick_up_frame,textvariable=self.up_az_str).grid(row=qup_row,column=2)
        qup_row += 1
        Tkinter.Button(quick_up_frame,text="Up el -",command=self.up_el_decrease).grid(row=qup_row,column=0)
        Tkinter.Button(quick_up_frame,text="Up el +",command=self.up_el_increase).grid(row=qup_row,column=1)
        self.up_el_str = Tkinter.StringVar()
        Tkinter.Label(quick_up_frame,textvariable=self.up_el_str).grid(row=qup_row,column=2)

        az,el = self.get_az_el(self.meta_params.up)
        self.up_az_str.set("%.1f"%az)
        self.up_el_str.set("%.1f"%el)

        la_row += 1
        Tkinter.Label(lookat_frame,text="up Y:").grid(row=la_row,column=0)
        self.up_y_tk_var = Tkinter.DoubleVar()
        self.up_y_tk_var.set(self.meta_params.up[1])
        CallbackEntry(lookat_frame,
                      self.send_values,
                      width=self.entry_width,
                      textvariable=self.up_y_tk_var).grid(row=la_row,column=1)

        la_row += 1
        Tkinter.Label(lookat_frame,text="up Z:").grid(row=la_row,column=0)
        self.up_z_tk_var = Tkinter.DoubleVar()
        self.up_z_tk_var.set(self.meta_params.up[2])
        CallbackEntry(lookat_frame,
                      self.send_values,
                      width=self.entry_width,
                      textvariable=self.up_z_tk_var).grid(row=la_row,column=1)

        row += 1
        button_row_frame = Tkinter.Frame(self)
        button_row_frame.grid(row=row,column=0,ipady=5)
        Tkinter.Label(button_row_frame,
                      text="File operations",
                      font=("Helvetica",12,"bold")).grid(row=0,column=0,columnspan=2,ipady=5)
        Tkinter.Button(button_row_frame,text="Save...",command=self.save).grid(row=1,column=0)
        Tkinter.Button(button_row_frame,text="Load...",command=self.load).grid(row=1,column=1)

        if auto_connect:
            self.connect(server_hostname,server_port)

    def frustum_narrower(self,dummy_arg=None): # callback
        self.left_tk_var.set(self.meta_params.left*(1.0/1.05))
        self.right_tk_var.set(self.meta_params.right*(1.0/1.05))
        self.send_values()

    def frustum_wider(self,dummy_arg=None): # callback
        self.left_tk_var.set(self.meta_params.left*1.05)
        self.right_tk_var.set(self.meta_params.right*1.05)
        self.send_values()

    def frustum_shorter(self,dummy_arg=None): # callback
        self.bottom_tk_var.set(self.meta_params.bottom*(1.0/1.05))
        self.top_tk_var.set(self.meta_params.top*(1.0/1.05))
        self.send_values()

    def frustum_taller(self,dummy_arg=None): # callback
        self.bottom_tk_var.set(self.meta_params.bottom*1.05)
        self.top_tk_var.set(self.meta_params.top*1.05)
        self.send_values()

    def frustum_left(self,dummy_arg=None): # callback
        self.left_tk_var.set(self.meta_params.left*1.025)
        self.right_tk_var.set(self.meta_params.right*(1.0/1.025))
        self.send_values()

    def frustum_right(self,dummy_arg=None): # callback
        self.left_tk_var.set(self.meta_params.left*(1.0/1.025))
        self.right_tk_var.set(self.meta_params.right*1.025)
        self.send_values()

    def frustum_down(self,dummy_arg=None): # callback
        self.bottom_tk_var.set(self.meta_params.bottom*1.025)
        self.top_tk_var.set(self.meta_params.top*(1.0/1.025))
        self.send_values()

    def frustum_up(self,dummy_arg=None): # callback
        self.bottom_tk_var.set(self.meta_params.bottom*(1.0/1.025))
        self.top_tk_var.set(self.meta_params.top*1.025)
        self.send_values()

    def get_az_el(self,xyz_tuple):
        x,y,z = xyz_tuple
        r = math.sqrt(x*x + y*y + z*z)
        theta = math.acos(-y/r)
        rh = r * math.sin(theta)
        phi = math.atan2(-z,x)
        az = -(phi * 180.0/math.pi - 90.0)
        el = theta * 180.0/math.pi - 90.0
        return az,el

    def get_xyz(self,az_el):
        az,el = az_el
        theta = (el + 90.0) / 180.0 * math.pi
        phi = (az + 90.0) / 180.0 * math.pi
        y = -math.cos(theta)
        rh = math.sin(theta)
        x = -rh * math.cos(phi)
        z = -rh * math.sin(phi)
        return x,y,z

    def az_increase(self,dummy_arg=None): # callback
        az,el = self.get_az_el(self.meta_params.center)
        az = az + 5.0
        self.look_at_az_str.set("%.1f"%az)
        x,y,z = self.get_xyz((az,el))
        self.center_x_tk_var.set("%.4f"%x)
        self.center_y_tk_var.set("%.4f"%y)
        self.center_z_tk_var.set("%.4f"%z)
        self.send_values()

    def az_decrease(self,dummy_arg=None): # callback
        az,el = self.get_az_el(self.meta_params.center)
        az = az - 5.0
        self.look_at_az_str.set("%.1f"%az)
        x,y,z = self.get_xyz((az,el))
        self.center_x_tk_var.set("%.4f"%x)
        self.center_y_tk_var.set("%.4f"%y)
        self.center_z_tk_var.set("%.4f"%z)
        self.send_values()

    def el_increase(self,dummy_arg=None): # callback
        az,el = self.get_az_el(self.meta_params.center)
        el = el + 5.0
        el = min(el,90.0)
        self.look_at_el_str.set("%.1f"%el)
        x,y,z = self.get_xyz((az,el))
        self.center_x_tk_var.set("%.4f"%x)
        self.center_y_tk_var.set("%.4f"%y)
        self.center_z_tk_var.set("%.4f"%z)
        self.send_values()

    def el_decrease(self,dummy_arg=None): # callback
        az,el = self.get_az_el(self.meta_params.center)
        el = el - 5.0
        el = max(el,-90.0)
        self.look_at_el_str.set("%.1f"%el)
        x,y,z = self.get_xyz((az,el))
        self.center_x_tk_var.set("%.4f"%x)
        self.center_y_tk_var.set("%.4f"%y)
        self.center_z_tk_var.set("%.4f"%z)
        self.send_values()

    def up_az_increase(self,dummy_arg=None): # callback
        az,el = self.get_az_el(self.meta_params.up)
        az = az + 5.0
        self.up_az_str.set("%.1f"%az)
        x,y,z = self.get_xyz((az,el))
        self.up_x_tk_var.set("%.4f"%x)
        self.up_y_tk_var.set("%.4f"%y)
        self.up_z_tk_var.set("%.4f"%z)
        self.send_values()

    def up_az_decrease(self,dummy_arg=None): # callback
        az,el = self.get_az_el(self.meta_params.up)
        az = az - 5.0
        self.up_az_str.set("%.1f"%az)
        x,y,z = self.get_xyz((az,el))
        self.up_x_tk_var.set("%.4f"%x)
        self.up_y_tk_var.set("%.4f"%y)
        self.up_z_tk_var.set("%.4f"%z)
        self.send_values()

    def up_el_increase(self,dummy_arg=None): # callback
        az,el = self.get_az_el(self.meta_params.up)
        el = el + 5.0
        el = min(el,90.0)
        self.up_el_str.set("%.1f"%el)
        x,y,z = self.get_xyz((az,el))
        self.up_x_tk_var.set("%.4f"%x)
        self.up_y_tk_var.set("%.4f"%y)
        self.up_z_tk_var.set("%.4f"%z)
        self.send_values()

    def up_el_decrease(self,dummy_arg=None): # callback
        az,el = self.get_az_el(self.meta_params.up)
        el = el - 5.0
        el = max(el,-90.0)
        self.up_el_str.set("%.1f"%el)
        x,y,z = self.get_xyz((az,el))
        self.up_x_tk_var.set("%.4f"%x)
        self.up_y_tk_var.set("%.4f"%y)
        self.up_z_tk_var.set("%.4f"%z)
        self.send_values()

    def save(self):
        filename = tkFileDialog.asksaveasfilename(defaultextension=".ve_3dproj",filetypes=[('Projection file','*.ve_3dproj')])
        fd = open(filename,"wb")
        save_dict = self.get_param_dict()
        pickle.dump( save_dict, fd )

    def load(self):
        filename = tkFileDialog.askopenfilename(defaultextension=".ve_3dproj",filetypes=[('Projection file','*.ve_3dproj')])
        if not filename:
            return
        fd = open(filename,"rb")
        file_contents = fd.read()
        file_contents = file_contents.replace('\r\n','\n') # deal with Windows newlines
        memory_file = StringIO.StringIO(file_contents)
        load_dict = pickle.load(memory_file)
        self.set_param_dict( load_dict )
        self.send_values()

    def get_shortname(self):
        """Used as basename for saving parameter files"""
        return "screen_position"

    def get_param_dict(self):
        result = {}
        for param_name in dir(self.meta_params):
            if param_name[:2] != '__' and param_name[-2:] != '__':
                result[param_name] = getattr(self.meta_params,param_name)
        return result

    def get_type(self):
        return "screenPositionGUI"

    def set_param_dict(self,new_param_dict):
        orig_params = dir(self.meta_params)
        for new_param_name in new_param_dict.keys():
            if new_param_name[:2] != '__' and new_param_name[-2:] != '__':
                if new_param_name not in orig_params:
                    raise ValueError('Gave parameter "%s", which I do not know about.'%(new_param_name,))
                setattr(self.meta_params,new_param_name,new_param_dict[new_param_name])
        self.left_tk_var.set( self.meta_params.left )
        self.right_tk_var.set( self.meta_params.right )
        self.top_tk_var.set( self.meta_params.top )
        self.bottom_tk_var.set( self.meta_params.bottom )
        self.near_tk_var.set( self.meta_params.near )
        self.far_tk_var.set( self.meta_params.far )
        self.eye_x_tk_var.set( self.meta_params.eye[0] )
        self.eye_y_tk_var.set( self.meta_params.eye[1] )
        self.eye_z_tk_var.set( self.meta_params.eye[2] )
        self.center_x_tk_var.set( self.meta_params.center[0] )
        self.center_y_tk_var.set( self.meta_params.center[1] )
        self.center_z_tk_var.set( self.meta_params.center[2] )
        self.up_x_tk_var.set( self.meta_params.up[0] )
        self.up_y_tk_var.set( self.meta_params.up[1] )
        self.up_z_tk_var.set( self.meta_params.up[2] )

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
        self.meta_params.left = self.left_tk_var.get()
        self.meta_params.right = self.right_tk_var.get()
        self.meta_params.top = self.top_tk_var.get()
        self.meta_params.bottom = self.bottom_tk_var.get()
        self.meta_params.near = self.near_tk_var.get()
        self.meta_params.far = self.far_tk_var.get()
        self.meta_params.eye = (self.eye_x_tk_var.get(),
                                self.eye_y_tk_var.get(),
                                self.eye_z_tk_var.get())
        self.meta_params.center = (self.center_x_tk_var.get(),
                                self.center_y_tk_var.get(),
                                self.center_z_tk_var.get())
        self.meta_params.up = (self.up_x_tk_var.get(),
                                self.up_y_tk_var.get(),
                                self.up_z_tk_var.get())

        if self.connected:
            self.projection_controller.set_parameters( self.meta_params )

    def connect(self,server_hostname='',server_port=7766):
        self.pyro_client = VisionEgg.PyroClient.PyroClient(server_hostname,server_port)

        self.projection_controller = self.pyro_client.get("projection_controller")

        self.connected = 1
        if hasattr(self, 'connected_label'):
            self.connected_label.config(text="Server status: Connected")
            self.send_values() # send values only when running this way, otherwise get values
        else:
            self.meta_params = self.projection_controller.get_parameters()
            self.set_param_dict( {} ) # updates screen values to self.meta_params

    def quit_server(self,dummy=None):
        self.projection_controller.quit_server()
        self.connected = 0
        self.connected_label.config(text="Server status: Not connected")

if __name__=='__main__':
    frame = ScreenPositionControlFrame()
    frame.pack(expand=1,fill=Tkinter.BOTH)
    frame.winfo_toplevel().title("%s"%(os.path.basename(os.path.splitext(sys.argv[0])[0]),))
    frame.mainloop()
