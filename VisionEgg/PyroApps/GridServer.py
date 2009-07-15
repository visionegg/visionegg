#!/usr/bin/env python
#
# The Vision Egg: GridServer
#
# Copyright (C) 2001-2003 Andrew Straw.
# Author: Andrew Straw <astraw@users.sourceforge.net>
# URL: <http://www.visionegg.org/>
#
# Distributed under the terms of the GNU Lesser General Public License
# (LGPL). See LICENSE.TXT that came with this file.

import VisionEgg, string

import sys, os, math
import VisionEgg.Core
import VisionEgg.FlowControl
import VisionEgg.Textures
import VisionEgg.SphereMap
import VisionEgg.PyroHelpers
import Pyro.core

from VisionEgg.PyroApps.ScreenPositionServer import ScreenPositionMetaController
from VisionEgg.PyroApps.ScreenPositionGUI import ScreenPositionParameters
from VisionEgg.PyroApps.GridGUI import GridMetaParameters

class GridMetaController( Pyro.core.ObjBase ):
    def __init__(self,screen,presentation,stimuli):

        # get the instance of Stimulus that was created
        assert( stimuli[0][0] == '3d_perspective_with_set_viewport_callback' )
        grid = stimuli[0][1]

        Pyro.core.ObjBase.__init__(self)
        self.meta_params = GridMetaParameters()
        if not isinstance(screen,VisionEgg.Core.Screen):
            raise ValueError("Expecting instance of VisionEgg.Core.Screen")
        if not isinstance(presentation,VisionEgg.FlowControl.Presentation):
            raise ValueError("Expecting instance of VisionEgg.FlowControl.Presentation")
        if not isinstance(grid,VisionEgg.SphereMap.AzElGrid):
            raise ValueError("Expecting instance of VisionEgg.SphereMap.SphereMap")
        self.p = presentation
        self.stim = grid

        screen.parameters.bgcolor = (1.0, 1.0, 1.0, 0.0)

    def get_parameters(self):
        return self.meta_params

    def set_parameters(self, new_parameters):
        if isinstance(new_parameters, GridMetaParameters):
            self.meta_params = new_parameters
        else:
            raise ValueError("Argument to set_parameters must be instance of GridMetaParameters")
        self.update()

    def update(self):
        self.p.parameters.go_duration = ( 0.0, 'seconds')

    def go(self):
        self.p.parameters.enter_go_loop = 1

    def quit_server(self):
        self.p.parameters.quit = 1

def get_meta_controller_class():
    return GridMetaController

def make_stimuli():
    stimulus = VisionEgg.SphereMap.AzElGrid()
    def set_az_el_grid_viewport(viewport):
        stimulus.parameters.my_viewport = viewport
    return [('3d_perspective_with_set_viewport_callback',stimulus,set_az_el_grid_viewport)] # return ordered list of tuples

def get_meta_controller_stimkey():
    return "grid_server"

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

    # now hand over control of drum to GridMetaController
    meta_controller = GridMetaController(screen,p,stimuli)
    pyro_server.connect(meta_controller,get_meta_controller_stimkey())

    # get listener controller and register it
    p.add_controller(None,None, pyro_server.create_listener_controller())

    # enter endless loop
    p.run_forever()
