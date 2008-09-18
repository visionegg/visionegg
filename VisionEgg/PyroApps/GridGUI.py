#!/usr/bin/env python
#
# The Vision Egg: GridGUI
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

import sys, os
import Tkinter
import VisionEgg.PyroApps.EPhysGUIUtils as client_utils

def get_control_list():
    return [("grid_server",GridControlFrame,GridControlFrame.title)]

class GridMetaParameters:
    def __init__(self):
        pass

class GridControlFrame(client_utils.StimulusControlFrame):
    title = "Grid for 3D calibration"
    def __init__(self, master=None, suppress_go_buttons=0,**kw):
        client_utils.StimulusControlFrame.__init__(self,
                                                   master,
                                                   suppress_go_buttons,
                                                   GridControlFrame.title,
                                                   GridMetaParameters,
                                                   **kw)
        Tkinter.Label( self.param_frame,
                       text="No variables to control" ).grid()

    def get_shortname(self):
        """Used as basename for saving parameter files"""
        return "grid"

    def update_tk_vars(self):
        pass

    def send_values(self,dummy_arg=None):
        pass
        if self.connected:
            self.meta_controller.set_parameters( self.meta_params )

    def get_duration_sec(self):
        return 0.0

if __name__=='__main__':
    frame = GridControlFrame()
    frame.pack(expand=1,fill=Tkinter.BOTH)
    frame.winfo_toplevel().title("%s"%(os.path.basename(os.path.splitext(sys.argv[0])[0]),))
    frame.mainloop()
