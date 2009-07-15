#!/usr/bin/env python
#
# The Vision Egg: ColorCalServer
#
# Copyright (C) 2001-2003 Andrew Straw.
# Author: Andrew Straw <astraw@users.sourceforge.net>
# URL: <http://www.visionegg.org/>
#
# Distributed under the terms of the GNU Lesser General Public License
# (LGPL). See LICENSE.TXT that came with this file.
#
# $Id$

"""Handle luminance and color calibration stimulus (server-side)"""

import VisionEgg, string

import sys, os, math
import VisionEgg.Core
import VisionEgg.FlowControl
import VisionEgg.PyroHelpers
import Pyro.core
import pygame, pygame.locals

from VisionEgg.PyroApps.ColorCalGUI import ColorCalMetaParameters

class ColorCalMetaController( Pyro.core.ObjBase ):
    def __init__(self,screen,presentation,stimuli):
        Pyro.core.ObjBase.__init__(self)
        self.meta_params = ColorCalMetaParameters()
        if not isinstance(screen,VisionEgg.Core.Screen):
            raise ValueError("Expecting instance of VisionEgg.Core.Screen")
        if not isinstance(presentation,VisionEgg.FlowControl.Presentation):
            raise ValueError("Expecting instance of VisionEgg.FlowControl.Presentation")

        self.screen = screen
        self.p = presentation

        self.update() # set stimulus parameters to initial defaults

    def get_parameters(self):
        return self.meta_params

    def set_parameters(self, new_parameters):
        if isinstance(new_parameters, ColorCalMetaParameters):
            self.meta_params = new_parameters
        else:
            raise ValueError("Argument to set_parameters must be instance of ColorCalMetaParameters")
        self.update()

    def update(self):
        self.screen.parameters.bgcolor = self.meta_params.color

    def go(self):
        pass

    def quit_server(self):
        self.p.parameters.quit = 1

def get_meta_controller_class():
    return ColorCalMetaController

def make_stimuli():
    return []

def get_meta_controller_stimkey():
    return "color_cal_server"

# Don't do anything unless this script is being run
if __name__ == '__main__':

    pyro_server = VisionEgg.PyroHelpers.PyroServer()

    screen = VisionEgg.Core.Screen.create_default()

    # get Vision Egg stimulus ready to go
    p = VisionEgg.FlowControl.Presentation()

    stimuli = make_stimuli()

    # now hand over control of grating and mask to FlatGratingExperimentMetaController
    meta_controller = ColorCalMetaController(screen,p,stimuli)
    pyro_server.connect(meta_controller,get_meta_controller_stimkey())

    # get listener controller and register it
    p.add_controller(None,None, pyro_server.create_listener_controller())

    # enter endless loop
    p.run_forever()
