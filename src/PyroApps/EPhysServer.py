#!/usr/bin/env python

# Copyright (c) 2002-2003 Andrew Straw.  Distributed under the terms
# of the GNU Lesser General Public License (LGPL).

import VisionEgg, string
__version__ = VisionEgg.release_name
__cvs__ = string.split('$Revision$')[1]
__date__ = string.join(string.split('$Date$')[1:3], ' ')
__author__ = 'Andrew Straw <astraw@users.sourceforge.net>'

import sys, os, math
import tkMessageBox
import pygame.display
import VisionEgg.Core
import VisionEgg.FlowControl
import VisionEgg.SphereMap
import VisionEgg.Text
import VisionEgg.Textures
import VisionEgg.PyroHelpers
import Pyro, Pyro.core

# Add your stimulus modules here
import VisionEgg.PyroApps.TargetServer
import VisionEgg.PyroApps.MouseTargetServer
import VisionEgg.PyroApps.FlatGratingServer
import VisionEgg.PyroApps.SphereGratingServer
import VisionEgg.PyroApps.SpinningDrumServer
import VisionEgg.PyroApps.GridServer
import VisionEgg.PyroApps.ColorCalServer

server_modules = [ VisionEgg.PyroApps.TargetServer,
                   VisionEgg.PyroApps.MouseTargetServer,
                   VisionEgg.PyroApps.FlatGratingServer,
                   VisionEgg.PyroApps.SphereGratingServer,
                   VisionEgg.PyroApps.SpinningDrumServer,
                   VisionEgg.PyroApps.GridServer,
                   VisionEgg.PyroApps.ColorCalServer,
                   ]

# 3D screen positioning parameters
from VisionEgg.PyroApps.ScreenPositionServer import ScreenPositionMetaController
from VisionEgg.PyroApps.ScreenPositionGUI import ScreenPositionParameters

class EPhysServer(  Pyro.core.ObjBase ):
    def __init__(self, presentation, server_modules ):
        Pyro.core.ObjBase.__init__(self)
        self.stimdict = {}
        self.stimkey = server_modules[0].get_meta_controller_stimkey() # first stimulus will be this
        self.quit_status = 0
        self.presentation = presentation
        # target for stimulus onset calibration
        self.onset_cal_bg = VisionEgg.MoreStimuli.Target2D(color=(0.0,0.0,0.0,1.0),
                                                           center=(30.0,30.0),
                                                           size=(50.0,50.0))
        self.onset_cal_fg = VisionEgg.MoreStimuli.Target2D(on=0,
                                                           color=(1.0,1.0,1.0,1.0),
                                                           center=(30.0,30.0),
                                                           size=(50.0,50.0))
        self.presentation.add_controller(self.onset_cal_fg,'on',VisionEgg.FlowControl.ConstantController(during_go_value=1,
                                                                                                  between_go_value=0))
        # get screen (hack)
        self.onset_cal_screen = self.presentation.parameters.viewports[0].parameters.screen
        self.onset_cal_viewport = VisionEgg.Core.Viewport(screen=self.onset_cal_screen,
                                                          stimuli=[self.onset_cal_bg,
                                                                   self.onset_cal_fg]
                                                          )
        
        for server_module in server_modules:
            stimkey = server_module.get_meta_controller_stimkey()
            klass = server_module.get_meta_controller_class()
            make_stimuli = server_module.make_stimuli
            self.stimdict[stimkey] = (klass, make_stimuli)

    def __del__(self):
        self.presentation.remove_controller(self.onset_cal_fg,'on')
        Pyro.core.ObjBase.__del__(self)
            
    def get_quit_status(self):
        return self.quit_status
    
    def set_quit_status(self,quit_status):
        self.quit_status = quit_status
        self.presentation.parameters.quit = quit_status

    def first_connection(self):
        # break out of initial run_forever loop        
        self.presentation.parameters.quit = 1

    def set_stim_onset_cal(self, on):
        if on:
            if self.onset_cal_viewport not in self.presentation.parameters.viewports:
                self.presentation.parameters.viewports.append(self.onset_cal_viewport)
        else:
            if self.onset_cal_viewport in self.presentation.parameters.viewports:
                self.presentation.parameters.viewports.remove(self.onset_cal_viewport)

    def set_stim_onset_cal_location(self, center, size):
        self.onset_cal_bg.parameters.center = center
        self.onset_cal_fg.parameters.center = center
        self.onset_cal_bg.parameters.size = size
        self.onset_cal_fg.parameters.size = size[0]-2,size[1]-2
        
    def get_stim_onset_cal_location(self):
        x,y = self.onset_cal_bg.parameters.center
        width,height = self.onset_cal_bg.parameters.size
        return x,y,width,height

    def set_gamma_ramp(self, red, blue, green):
        return pygame.display.set_gamma_ramp(red,green,blue)

    def is_in_go_loop(self):
        return self.presentation.is_in_go_loop()

    def were_frames_dropped_in_last_go_loop(self):
        return self.presentation.were_frames_dropped_in_last_go_loop()
    
    def get_last_go_loop_start_time_absolute_sec(self):
        return self.presentation.get_last_go_loop_start_time_absolute_sec()

    def set_override_t_abs_sec(self, value_sec_string):
        value_sec = float(value_sec_string) # Pyro loses precision
        self.presentation.parameters.override_t_abs_sec = value_sec
    
    def get_next_stimulus_meta_controller(self):
        if self.stimkey:
            klass, make_stimuli = self.stimdict[self.stimkey]
            stimuli = make_stimuli()
            return self.stimkey, klass, stimuli
        else:
            raise RuntimeError("No stimkey")

    def get_stimkey(self):
        return self.stimkey
        
    def set_next_stimkey(self,stimkey):
        self.stimkey = stimkey

    def get_cwd(self):
        return os.path.abspath(os.curdir)

    def save_image_sequence(self,fps=12.0,filename_base="im",filename_suffix=".tif",save_dir="."):
        try:
            self.presentation.export_movie_go(frames_per_sec=fps,
                                              filename_base=filename_base,
                                              filename_suffix=filename_suffix,
                                              path=save_dir
                                              )
        except Exception,x:
            # do this because Pyro doesn't (by default) print a traceback
            import traceback
            traceback.print_exc()
            raise

def start_server( server_modules, server_class=EPhysServer ):
    pyro_server = VisionEgg.PyroHelpers.PyroServer()

    # get Vision Egg stimulus ready to go
    screen = VisionEgg.Core.Screen.create_default()
    
    temp = ScreenPositionParameters()

    projection = VisionEgg.Core.PerspectiveProjection(temp.left,
                                                      temp.right,
                                                      temp.bottom,
                                                      temp.top,
                                                      temp.near,
                                                      temp.far)
    perspective_viewport = VisionEgg.Core.Viewport(screen=screen,
                                                      projection=projection)
    overlay2D_viewport = VisionEgg.Core.Viewport(screen=screen)
    p = VisionEgg.FlowControl.Presentation(viewports=[perspective_viewport, overlay2D_viewport]) # 2D overlay on top

    wait_text = VisionEgg.Text.Text(
        text = "Starting up...",
        position = (screen.size[0]/2.0,5),
        anchor='bottom',
        color = (1.0,0.0,0.0,0.0))

    overlay2D_viewport.parameters.stimuli = [wait_text]
    p.between_presentations() # draw wait_text

    # now hand over control of projection to ScreenPositionMetaController
    projection_controller = ScreenPositionMetaController(p,projection)
    pyro_server.connect(projection_controller,"projection_controller")

    ephys_server = server_class(p, server_modules)
    pyro_server.connect(ephys_server,"ephys_server")
    hostname,port = pyro_server.get_hostname_and_port()
    
    wait_text.parameters.text = "Waiting for connection at %s port %d"%(hostname,port)
    
    # get listener controller and register it
    p.add_controller(None,None, pyro_server.create_listener_controller())

    p.run_forever() # run until we get first connnection, which breaks out immmediately

    wait_text.parameters.text = "Loading new experiment, please wait."
    
    while not ephys_server.get_quit_status():

        perspective_viewport.parameters.stimuli = []
        overlay2D_viewport.parameters.stimuli = [wait_text]
        p.between_presentations() # draw wait_text
        
        pyro_name, meta_controller_class, stimulus_list = ephys_server.get_next_stimulus_meta_controller()
        stimulus_meta_controller = meta_controller_class(screen, p, stimulus_list) # instantiate meta_controller
        pyro_server.connect(stimulus_meta_controller, pyro_name)
            
        overlay2D_viewport.parameters.stimuli = [] # clear wait_text
            
        for stim in stimulus_list:
            if stim[0] == '3d_perspective':
                perspective_viewport.parameters.stimuli.append(stim[1])
            elif stim[0] == '3d_perspective_with_set_viewport_callback':
                key, stimulus, callback_function = stim
                callback_function(perspective_viewport)
                perspective_viewport.parameters.stimuli.append(stimulus)
            elif stim[0] == '2d_overlay':
                overlay2D_viewport.parameters.stimuli.append(stim[1])
            else:
                raise RuntimeError("Unknown viewport id %s"%stim[0])
        
        # enter loop
        p.parameters.enter_go_loop = 0
        p.parameters.quit = 0
        p.run_forever()

        pyro_server.disconnect(stimulus_meta_controller)
        del stimulus_meta_controller # we have to do this explicitly because Pyro keeps a copy of the reference

if __name__ == '__main__':
    start_server( server_modules )
