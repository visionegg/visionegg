"""Attempt to isolate platform dependencies in one place

Functions:

set_realtime -- Raise the Vision Egg to maximum priority
linux_but_not_nvidia -- Warn that platform is linux, but drivers not nVidia
sync_swap_with_vbl_pre_gl_init -- Try to synchronize buffer swapping and vertical retrace before starting OpenGL
sync_swap_with_vbl_post_gl_init -- Try to synchronize buffer swapping and vertical retrace after starting OpenGL
"""

# Copyright (c) 2001-2002 Andrew Straw.  Distributed under the terms of the
# GNU Lesser General Public License (LGPL).

####################################################################
#
#        Import all the necessary packages
#
####################################################################

import sys,os,string
import VisionEgg.Core

__version__ = VisionEgg.release_name
__cvs__ = string.split('$Revision$')[1]
__date__ = string.join(string.split('$Date$')[1:3], ' ')
__author__ = 'Andrew Straw <astraw@users.sourceforge.net>'

############# Import Vision Egg C routines, if they exist #############
try:
    from _maxpriority import *                  # pickup set_realtime() function
except:
    def set_realtime():
        """Raise the Vision Egg to maximum priority. (NOT SUPPORTED)"""
        pass
            
def linux_but_not_nvidia():
    """Warn that platform is linux, but drivers not nVidia."""
    # If you've added support for other drivers to sync with VBL under
    # linux, please let me know how!
    VisionEgg.Core.message.add(
        """VISIONEGG WARNING: Could not sync buffer swapping to
        vertical blank pulse because you are running linux but not the
        nVidia drivers.  It is quite possible this can be enabled,
        it's just that I haven't had access to anything but nVidia
        cards under linux!""", level=VisionEgg.Core.Message.WARNING)
    
def sync_swap_with_vbl_pre_gl_init():
    """Try to synchronize buffer swapping and vertical retrace before starting OpenGL."""
    success = 0
    if sys.platform == "linux2":
        # Unfotunately, cannot check do glGetString(GL_VENDOR) to
        # check if drivers are nVidia because we have to do that requires
        # OpenGL context started, but this variable must be set
        # before OpenGL context started!
        
        # Assume drivers are nVidia
        VisionEgg.Core.add_gl_assumption("GL_VENDOR","nvidia",linux_but_not_nvidia)
        # Set nVidia linux environmental variable
        os.environ["__GL_SYNC_TO_VBLANK"] = "1"
        success = 1
        
    return success

def sync_swap_with_vbl_post_gl_init():
    """Try to synchronize buffer swapping and vertical retrace after starting OpenGL."""
    success = 0
    try:
        if sys.platform == "win32":
            import OpenGL.WGL.EXT.swap_control
            if OpenGL.WGL.EXT.swap_control.wglInitSwapControlARB(): # Returns 1 if it's working
                OpenGL.WGL.EXT.swap_control.wglSwapIntervalEXT(1) # Swap only at frame syncs
                if OpenGL.WGL.EXT.swap_control.wglGetSwapIntervalEXT() == 1:
                    success = 1
    except:
        pass
    
    return success
