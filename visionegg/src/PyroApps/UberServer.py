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
import VisionEgg.Core
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
server_modules = [ VisionEgg.PyroApps.TargetServer,
                   VisionEgg.PyroApps.MouseTargetServer,
                   VisionEgg.PyroApps.FlatGratingServer,
                   VisionEgg.PyroApps.SphereGratingServer,
                   VisionEgg.PyroApps.SpinningDrumServer,
                   VisionEgg.PyroApps.GridServer ]

# 3D screen positioning parameters
from VisionEgg.PyroApps.ScreenPositionServer import ScreenPositionMetaController
from VisionEgg.PyroApps.ScreenPositionGUI import ScreenPositionParameters

class UberServer(  Pyro.core.ObjBase ):
    def __init__(self, presentation, server_modules ):
        Pyro.core.ObjBase.__init__(self)
        self.stimdict = {}
        self.stimkey = server_modules[0].get_meta_controller_stimkey() # first stimulus will be this
        self.quit_status = 0
        self.presentation = presentation

        for server_module in server_modules:
            stimkey = server_module.get_meta_controller_stimkey()
            klass = server_module.get_meta_controller_class()
            make_stimuli = server_module.make_stimuli
            self.stimdict[stimkey] = (klass, make_stimuli)

    def __del__(self):
        Pyro.core.ObjBase.__del__(self)
            
    def get_quit_status(self):
        return self.quit_status
    
    def set_quit_status(self,quit_status):
        self.quit_status = quit_status
        self.presentation.parameters.quit = quit_status

    def first_connection(self):
        # break out of initial run_forever loop        
        self.presentation.parameters.quit = 1
    
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

def start_server( server_modules ):
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
    p = VisionEgg.Core.Presentation(viewports=[perspective_viewport, overlay2D_viewport]) # 2D overlay on top

    wait_text = VisionEgg.Text.BitmapText(
        text = "Waiting for connection",
        lowerleft = (5,10),
        color = (1.0,0.0,0.0,0.0))

    overlay2D_viewport.parameters.stimuli = [wait_text]
    p.between_presentations() # draw wait_text

    # now hand over control of projection to ScreenPositionMetaController
    projection_controller = ScreenPositionMetaController(p,projection)
    pyro_server.connect(projection_controller,"projection_controller")

    uber_server = UberServer(p, server_modules)
    pyro_server.connect(uber_server,"uber_server")
    hostname,port = pyro_server.get_hostname_and_port()
    
    wait_text.parameters.text = "Waiting for connection at %s port %d"%(hostname,port)
    
    # get listener controller and register it
    p.add_controller(None,None, pyro_server.create_listener_controller())

    p.run_forever() # run until we get first connnection, which breaks out immmediately

    wait_text.parameters.text = "Loading new experiment, please wait."
    
    while not uber_server.get_quit_status():

        perspective_viewport.parameters.stimuli = []
        overlay2D_viewport.parameters.stimuli = [wait_text]
        p.between_presentations() # draw wait_text
        
        pyro_name, meta_controller_class, stimulus_list = uber_server.get_next_stimulus_meta_controller()
        stimulus_meta_controller = meta_controller_class(screen, p, stimulus_list) # instantiate meta_controller
        pyro_server.connect(stimulus_meta_controller, pyro_name)
            
        overlay2D_viewport.parameters.stimuli = [] # clear wait_text
            
        for stim in stimulus_list:
            if stim[0] == '3d_perspective':
                perspective_viewport.parameters.stimuli.append(stim[1])
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
