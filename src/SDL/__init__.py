"""VisionEgg.SDL - A python binding of SDL for use by the Vision Egg package.

VisionEgg.SDL is a python binding of SDL for use by the Vision Egg package.  It only implements a small fraction of the SDL library, primarily the graphics initialization routines.
"""
import string
__version__ = string.split('$Revision$')[1]
__date__ = string.join(string.split('$Date$')[1:3], ' ')
__author__ = 'Andrew Straw <astraw@users.sourceforge.net>'

from sdlconst import *
from _sdl import *
