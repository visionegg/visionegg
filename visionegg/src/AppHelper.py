"""Application Helper functions for the Vision Egg library
"""

# Copyright (c) 2002 Andrew Straw.  Distributed under the terms of the
# GNU Lesser General Public License (LGPL).

import string
import VisionEgg
import VisionEgg.Core
import VisionEgg.GUI

__version__ = VisionEgg.release_name
__cvs__ = string.split('$Revision$')[1]
__date__ = string.join(string.split('$Date$')[1:3], ' ')
__author__ = 'Andrew Straw <astraw@users.sourceforge.net>'

def get_default_screen():
    """Return an instance of screen opened with to default values.

    Uses VisionEgg.config.VISIONEGG_DEFAULT_INIT to determine how the
    default screen parameters should are determined.  If this value is
    'config', the values from VisionEgg.config are used.  If this
    value is 'GUI', a GUI panel is opened and allows manual settings
    of the screen parameters.  """

    if VisionEgg.config.VISIONEGG_DEFAULT_INIT == 'config':
        return VisionEgg.Core.Screen(size=(VisionEgg.config.VISIONEGG_SCREEN_W,
                                           VisionEgg.config.VISIONEGG_SCREEN_H),
                                     fullscreen=VisionEgg.config.VISIONEGG_FULLSCREEN,
                                     preferred_bpp=VisionEgg.config.VISIONEGG_PREFERRED_BPP,
                                     bgcolor=VisionEgg.config.VISIONEGG_SCREEN_BGCOLOR)
    elif VisionEgg.config.VISIONEGG_DEFAULT_INIT == 'GUI':
        return VisionEgg.GUI.get_screen_via_GUI()
    else:
        raise ValueError("VISIONEGG_DEFAULT_INIT must be 'config' or 'GUI'.  (Was given '%s')."%VisionEgg.config.VISIONEGG_DEFAULT_INIT)
