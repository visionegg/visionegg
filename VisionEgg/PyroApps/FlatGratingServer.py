#!/usr/bin/env python
#
# The Vision Egg: FlatGratingServer
#
# Copyright (C) 2001-2003 Andrew Straw.
# Author: Andrew Straw <astraw@users.sourceforge.net>
# URL: <http://www.visionegg.org/>
#
# Distributed under the terms of the GNU Lesser General Public License
# (LGPL). See LICENSE.TXT that came with this file.
#
# $Id$

"""Handle sinusoidal gratings (server-side)"""

import VisionEgg, string
__version__ = VisionEgg.release_name
__cvs__ = string.split('$Revision$')[1]
__date__ = string.join(string.split('$Date$')[1:3], ' ')
__author__ = 'Andrew Straw <astraw@users.sourceforge.net>'

import sys, os, math
import VisionEgg.Core
import VisionEgg.FlowControl
import VisionEgg.Gratings
import VisionEgg.PyroHelpers
import Pyro.core

from VisionEgg.PyroApps.FlatGratingGUI import FlatGratingMetaParameters

class FlatGratingExperimentMetaController( Pyro.core.ObjBase ):
    def __init__(self,screen,presentation,stimuli):

        # get stimulus
        assert( stimuli[0][0] == '2d_overlay')
        grating = stimuli[0][1]

        Pyro.core.ObjBase.__init__(self)
        self.meta_params = FlatGratingMetaParameters()
        if not isinstance(screen,VisionEgg.Core.Screen):
            raise ValueError("Expecting instance of VisionEgg.Core.Screen")
        if not isinstance(presentation,VisionEgg.FlowControl.Presentation):
            raise ValueError("Expecting instance of VisionEgg.FlowControl.Presentation")
        if not isinstance(grating,VisionEgg.Gratings.SinGrating2D):
            raise ValueError("Expecting instance of VisionEgg.Gratings.SinGrating2D")
        self.p = presentation
        self.stim = grating

        screen.parameters.bgcolor = (0.5, 0.5, 0.5, 0.0)

        self.p.add_controller(self.stim,'on',VisionEgg.FlowControl.FunctionController(
            during_go_func=self.on_function_during_go,
            between_go_func=self.on_function_between_go))

    def __del__(self):
        self.p.remove_controller(self.stim,'on')
        Pyro.core.ObjBase.__del__(self) # call base class

    def on_function_during_go(self,t):
        """Compute when the grating is on"""
        if t <= self.meta_params.pre_stim_sec:
            return 0 # not on yet
        elif t <= (self.meta_params.pre_stim_sec + self.meta_params.stim_sec):
            return 1 # on
        else:
            return 0 # off again

    def on_function_between_go(self):
        """Compute when the grating is off"""
        return 0 # off again

    def get_parameters(self):
        return self.meta_params

    def set_parameters(self, new_parameters):
        if isinstance(new_parameters, FlatGratingMetaParameters):
            self.meta_params = new_parameters
        else:
            raise ValueError("Argument to set_parameters must be instance of FlatGratingMetaParameters")
        self.update()

    def update(self):
        stim_params = self.stim.parameters # shorthand
        meta_params = self.meta_params # shorthand
        stim_params.contrast = meta_params.contrast
        stim_params.orientation = meta_params.orient
        stim_params.spatial_freq = meta_params.sf
        stim_params.temporal_freq_hz = meta_params.tf
        stim_params.size = (meta_params.size_x, meta_params.size_y)
        stim_params.position = (meta_params.center_x, meta_params.center_y)
        self.p.parameters.go_duration = ( meta_params.pre_stim_sec + meta_params.stim_sec + meta_params.post_stim_sec, 'seconds')

    def go(self):
        self.p.parameters.enter_go_loop = 1

    def quit_server(self):
        self.p.parameters.quit = 1

def get_meta_controller_class():
    return FlatGratingExperimentMetaController

def make_stimuli():
    stimulus = VisionEgg.Gratings.SinGrating2D( spatial_freq=1.0/100.0, # wavelength = 100 pixels
                                                temporal_freq_hz = 1.0,
                                                anchor='center',
                                                )
    return [('2d_overlay',stimulus)]

def get_meta_controller_stimkey():
    return "flat_grating_server"

# Don't do anything unless this script is being run
if __name__ == '__main__':

    pyro_server = VisionEgg.PyroHelpers.PyroServer()

    screen = VisionEgg.Core.Screen.create_default()

    # get Vision Egg stimulus ready to go
    stimuli = make_stimuli()
    stimulus = stimuli[0][1]
    viewport = VisionEgg.Core.Viewport(screen=screen,stimuli=[stimulus])
    p = VisionEgg.FlowControl.Presentation(viewports=[viewport])

    # now hand over control of grating and mask to FlatGratingExperimentMetaController
    meta_controller = FlatGratingExperimentMetaController(screen,p,stimuli)
    pyro_server.connect(meta_controller,get_meta_controller_stimkey())

    # get listener controller and register it
    p.add_controller(None,None, pyro_server.create_listener_controller())

    # enter endless loop
    p.run_forever()
