#!/usr/bin/env python
#
# The Vision Egg: SpinningDrumServer
#
# Copyright (C) 2001-2003 Andrew Straw.
# Author: Andrew Straw <astraw@users.sourceforge.net>
# URL: <http://www.visionegg.org/>
#
# Distributed under the terms of the GNU Lesser General Public License
# (LGPL). See LICENSE.TXT that came with this file.
#
# $Id$

import VisionEgg, string
__version__ = VisionEgg.release_name
__cvs__ = string.split('$Revision$')[1]
__date__ = string.join(string.split('$Date$')[1:3], ' ')
__author__ = 'Andrew Straw <astraw@users.sourceforge.net>'

import sys, os, math
import VisionEgg.Core
import VisionEgg.FlowControl
import VisionEgg.Textures
import VisionEgg.PyroHelpers
import Pyro.core

from VisionEgg.PyroApps.ScreenPositionServer import ScreenPositionMetaController
from VisionEgg.PyroApps.ScreenPositionGUI import ScreenPositionParameters
from VisionEgg.PyroApps.SpinningDrumGUI import SpinningDrumMetaParameters

class SpinningDrumExperimentMetaController( Pyro.core.ObjBase ):
    def __init__(self,screen,presentation,stimuli):

        # get the instance of Stimulus that was created
        assert( stimuli[0][0] == '3d_perspective' )
        spinning_drum = stimuli[0][1]

        Pyro.core.ObjBase.__init__(self)
        self.meta_params = SpinningDrumMetaParameters()
        if not isinstance(screen,VisionEgg.Core.Screen):
            raise ValueError("Expecting instance of VisionEgg.Core.Screen")
        if not isinstance(presentation,VisionEgg.FlowControl.Presentation):
            raise ValueError("Expecting instance of VisionEgg.FlowControl.Presentation")
        if not isinstance(spinning_drum,VisionEgg.Textures.SpinningDrum):
            raise ValueError("Expecting instance of VisionEgg.Textures.SpinningDrum")
        self.p = presentation
        self.stim = spinning_drum

        screen.parameters.bgcolor = (0.5, 0.5, 0.5, 0.0)

        self.p.add_controller(self.stim,'on',VisionEgg.FlowControl.FunctionController(
            during_go_func=self.on_function_during_go,
            between_go_func=self.on_function_between_go))

        self.p.add_controller(self.stim,'angular_position',VisionEgg.FlowControl.FunctionController(
            during_go_func=self.angular_position_during_go,
            between_go_func=self.angular_position_between_go))

    def __del__(self):
        self.p.remove_controller(self.stim,'on')
        self.p.remove_controller(self.stim,'angular_position')
        Pyro.core.ObjBase.__del__(self) # call base class

    def on_function_during_go(self,t):
        if t <= self.meta_params.pre_stim_sec:
            return 0 # not on yet
        elif t <= (self.meta_params.pre_stim_sec + self.meta_params.stim_sec):
            return 1 # on
        else:
            return 0 # off again

    def on_function_between_go(self):
        return 0 # off

    def angular_position_during_go(self,t):
        adjusted_t = t - self.meta_params.pre_stim_sec
        return (adjusted_t * self.meta_params.velocity_dps) + self.meta_params.startpos_deg

    def angular_position_between_go(self):
        return 0.0 # doesn't matter -- stimulus off

    def get_parameters(self):
        return self.meta_params

    def set_parameters(self, new_parameters):
        if isinstance(new_parameters, SpinningDrumMetaParameters):
            self.meta_params = new_parameters
        else:
            raise ValueError("Argument to set_parameters must be instance of SpinningDrumMetaParameters")
        self.update()

    def update(self):
        stim_params = self.stim.parameters # shorthand
        meta_params = self.meta_params # shorthand
        stim_params.contrast = meta_params.contrast
        self.p.parameters.go_duration = ( meta_params.pre_stim_sec + meta_params.stim_sec + meta_params.post_stim_sec, 'seconds')

    def go(self):
        self.p.parameters.enter_go_loop = 1

    def quit_server(self):
        self.p.parameters.quit = 1

def get_meta_controller_class():
    return SpinningDrumExperimentMetaController

def make_stimuli():
    filename = os.path.join(VisionEgg.config.VISIONEGG_SYSTEM_DIR,"data/panorama.jpg")
    texture = VisionEgg.Textures.Texture(filename)
    stimulus = VisionEgg.Textures.SpinningDrum(texture=texture) # could add shrink_texture_ok=1
    return [('3d_perspective',stimulus)] # return ordered list of tuples

def get_meta_controller_stimkey():
    return "spinning_drum_server"

# Don't do anything unless this script is being run
if __name__ == '__main__':

    pyro_server = VisionEgg.PyroHelpers.PyroServer()

    screen = VisionEgg.Core.Screen.create_default()

    # get Vision Egg stimulus ready to go
    stimuli = make_stimuli()
    stimulus = stimuli[0][1]
    temp = ScreenPositionParameters()

    projection = VisionEgg.Core.PerspectiveProjection(temp.left,
                                                      temp.right,
                                                      temp.bottom,
                                                      temp.top,
                                                      temp.near,
                                                      temp.far)
    viewport = VisionEgg.Core.Viewport(screen=screen,stimuli=[stimulus],projection=projection)
    p = VisionEgg.FlowControl.Presentation(viewports=[viewport])

    # now hand over control of projection to ScreenPositionMetaController
    projection_controller = ScreenPositionMetaController(p,projection)
    pyro_server.connect(projection_controller,"projection_controller")

    # now hand over control of drum to SpinningDrumExperimentMetaController
    meta_controller = SpinningDrumExperimentMetaController(screen,p,stimuli)
    pyro_server.connect(meta_controller,get_meta_controller_stimkey())

    # get listener controller and register it
    p.add_controller(None,None, pyro_server.create_listener_controller())

    # enter endless loop
    p.run_forever()
