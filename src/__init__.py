"""VisionEgg - The Vision Egg package.
"""
# Copyright (c) 2001 Andrew Straw.  Distributed under the terms of the
# GNU General Public License (GPL).

import string
__version__ = string.split('$Revision$')[1]
__date__ = string.join(string.split('$Date$')[1:3], ' ')
__author__ = 'Andrew Straw <astraw@users.sourceforge.net>'


# Let "import VisionEgg" do what would otherwise be "import VisionEgg.VisionEgg"
from VisionEgg import * 

