# This is the python source code for the primary module of the Vision Egg package.
#
#
# Copyright (c) 2001 Andrew Straw.  Distributed under the terms of the
# GNU General Public License (GPL).

####################################################################
#
#        Import all the necessary packages
#
####################################################################

import string
__version__ = string.split('$Revision$')[1]
__date__ = string.join(string.split('$Date$')[1:3], ' ')
__author__ = 'Andrew Straw <astraw@users.sourceforge.net>'

from VisionEgg import *
from MotionBlur import *

class TargetOnBackground(BlurredDrum,MovingTarget):
    def __init__(self,**kwargs):
        apply(MovingTarget.__init__,(self,),kwargs)
        apply(BlurredDrum.__init__,(self,),kwargs)
                                  
    def init_GL(self):
        BlurredDrum.init_GL(self)
        MovingTarget.init_GL(self)

    def draw_GL_scene(self):
        # Must resort to a bit of trickery here because our class
        # is derived from two subclasses of Stimulus, and we don't
        # want to clear the viewport and swap the buffers twice on
        # each frame.
        if self.swap_buffers:
            self.swap_buffers = 0
            BlurredDrum.draw_GL_scene(self)
            self.swap_buffers = 1
        else:
            BlurredDrum.draw_GL_scene(self)
            
        if self.clear_viewport:
            self.clear_viewport = 0
            MovingTarget.draw_GL_scene(self)
            self.clear_viewport = 1
        else:
            MovingTarget.draw_GL_scene(self)
        
