#!/usr/bin/env python
#
# The Vision Egg: TargetServer
#
# Copyright (C) 2001-2003 Andrew Straw.
# Author: Andrew Straw <astraw@users.sourceforge.net>
# URL: <http://www.visionegg.org/>
#
# Distributed under the terms of the GNU Lesser General Public License
# (LGPL). See LICENSE.TXT that came with this file.
#
# $Id$

"""Handle small targets gratings (server-side)"""

import VisionEgg
__version__ = VisionEgg.release_name
__cvs__ = '$Revision$'.split()[1]
__date__ = ' '.join('$Date$'.split()[1:3])
__author__ = 'Andrew Straw <astraw@users.sourceforge.net>'

import sys, os, math
import VisionEgg.Core
import VisionEgg.FlowControl
import VisionEgg.MoreStimuli
import VisionEgg.PyroHelpers
import Pyro.core

from VisionEgg.PyroApps.TargetGUI import TargetMetaParameters

class TargetExperimentMetaController( Pyro.core.ObjBase ):
    def __init__(self,screen,presentation,stimuli):
        Pyro.core.ObjBase.__init__(self)

        # get stimulus
        assert( stimuli[0][0] == '2d_overlay')
        target = stimuli[0][1]

        self.meta_params = TargetMetaParameters()
        if not isinstance(screen,VisionEgg.Core.Screen):
            raise ValueError("Expecting instance of VisionEgg.Core.Screen")
        if not isinstance(presentation,VisionEgg.FlowControl.Presentation):
            raise ValueError("Expecting instance of VisionEgg.FlowControl.Presentation")
        if not isinstance(target,VisionEgg.MoreStimuli.Target2D):
            raise ValueError("Expecting instance of VisionEgg.MoreStimuli.Target2D")

        self.screen = screen
        self.p = presentation
        self.stim = target

        self.p.add_controller(self.stim,'on',VisionEgg.FlowControl.FunctionController(
            during_go_func=self.on_function_during_go,
            between_go_func=self.on_function_between_go))

        self.p.add_controller(self.stim,'position',VisionEgg.FlowControl.FunctionController(
            during_go_func=self.center_during_go,
            between_go_func=self.center_between_go))

        self.update() # set stimulus parameters to initial defaults

    def __del__(self):
        self.p.remove_controller(self.stim,'on')
        self.p.remove_controller(self.stim,'position')
        Pyro.core.ObjBase.__del__(self) # call base class

    def on_function_during_go(self,t):
        if t <= self.meta_params.pre_stim_sec:
            return 0 # not on yet
        elif t <= (self.meta_params.pre_stim_sec + self.meta_params.stim_sec):
            return 1 # on
        else:
            return 0 # off again

    def on_function_between_go(self):
        return 0

    def center_during_go(self,t):
        t_adjusted = t - self.meta_params.pre_stim_sec
        distance = self.meta_params.velocity_pps * t_adjusted
        x_offset = math.cos(self.meta_params.direction_deg / 180.0 * math.pi)*distance
        y_offset = math.sin(self.meta_params.direction_deg / 180.0 * math.pi)*distance

        return (self.meta_params.start_x + x_offset,
                self.meta_params.start_y + y_offset)

    def center_between_go(self):
        return (0.0, 0.0) # doesn't matter -- it's off

    def get_parameters(self):
        return self.meta_params

    def set_parameters(self, new_parameters):
        if isinstance(new_parameters, TargetMetaParameters):
            self.meta_params = new_parameters
        else:
            raise ValueError("Argument to set_parameters must be instance of TargetMetaParameters")
        self.update()

    def update(self):
        stim_params = self.stim.parameters # shorthand
        meta_params = self.meta_params # shorthand

        # colors
        stim_params.color = meta_params.color
        self.screen.parameters.bgcolor = meta_params.bgcolor

        # size and orientation
        stim_params.size = (meta_params.width, meta_params.height)
        stim_params.orientation = meta_params.orientation_deg

        self.p.parameters.go_duration = ( meta_params.pre_stim_sec + meta_params.stim_sec + meta_params.post_stim_sec, 'seconds')

    def go(self):
        self.p.parameters.enter_go_loop = 1

    def quit_server(self):
        self.p.parameters.quit = 1

def get_meta_controller_class():
    return TargetExperimentMetaController

def make_stimuli():
    stimulus = VisionEgg.MoreStimuli.Target2D(anchor='center')
    return [('2d_overlay',stimulus)]

def get_meta_controller_stimkey():
    return "target_server"

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
    meta_controller = TargetExperimentMetaController(screen,p,stimuli)
    pyro_server.connect(meta_controller,get_meta_controller_stimkey())

    # get listener controller and register it
    p.add_controller(None,None, pyro_server.create_listener_controller())

    # enter endless loop
    p.run_forever()
