# The Vision Egg: DropinServer
#
# Copyright (C) 2004 Imran S. Ali, Lachlan Dowd, Andrew Straw
# Copyright (C) 2004 California Institute of Technology
#
# Authors: Imran S. Ali, Lachlan Dowd, Andrew Straw
# URL: <http://www.visionegg.org/>
#
# Distributed under the terms of the GNU Lesser General Public License
# (LGPL). See LICENSE.TXT that came with this file.
#
# $Id$

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
from VisionEgg.PyroApps.DropinGUI import DropinMetaParameters

class DropinMetaController( Pyro.core.ObjBase ):
    def __init__(self,screen,presentation,stimuli):
        Pyro.core.ObjBase.__init__(self)
        self.meta_params = DropinMetaParameters()
        self.p = presentation
        print 'DropinMetaController presentation',self.p

    def get_parameters(self):
        return self.meta_params

    def set_parameters(self, new_parameters):
        self.meta_params = new_parameters
        self.update()

    def update(self):
        pass

    def go(self):
        self.p.parameters.enter_go_loop = 1

    def quit_server(self):
        self.p.parameters.quit = 1

def get_meta_controller_class():
    return DropinMetaController

def make_stimuli():
    pass

def get_meta_controller_stimkey():
    return "dropin_server"
