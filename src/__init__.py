"""The Vision Egg package.

The Vision Egg is a programming library (with demo applications) that
uses standard, inexpensive computer graphics cards to produce visual
stimuli for vision research experiments.

Today's computer graphics cards, thanks to the demands of computer
gamers, are capable of drawing very complex scenes in a very short
amount of time. The Vision Egg allows the vision scientist (or anyone
else) to program these cards using OpenGL, the standard in computer
graphics programming. Potentially difficult tasks, such as initializing
graphics, getting precise timing information, controlling stimulus
parameters in real-time, and synchronizing with data acquisition are
greatly eased by routines within the Vision Egg.
"""
# Copyright (c) 2001, 2002 Andrew Straw.  Distributed under the terms of the
# GNU General Public License (GPL).

VISIONEGG_VERSION = '0.8.0'

import string
__version__ = string.split('$Revision$')[1]
__date__ = string.join(string.split('$Date$')[1:3], ' ')
__author__ = 'Andrew Straw <astraw@users.sourceforge.net>'

# Make sure we don't have an old version of the VisionEgg installed.
# (There used to be a module named VisionEgg.VisionEgg.  If it still
# exists, it'll crash stuff randomly)
try:
    __import__('VisionEgg.VisionEgg') # If we can import it, report error
    raise RuntimeError('Outdated "VisionEgg.py" and/or "VisionEgg.pyc" found.  Please delete from your VisionEgg package directory.')
except ImportError:
    pass # It's OK, the old version isn't there

import Configuration # a Vision Egg module
import os, sys, time # standard python modules

############# Get config defaults #############
config = Configuration.Config()
try:
    confFile = os.environ['VISIONEGG_CONFIG_FILE']
except KeyError:
    confFile = ''
if not confFile and os.path.isfile('VisionEgg.conf'):
    confFile='VisionEgg.conf'
config.setup(confFile)

############# Now set up a bunch of obscure stuff  #############

############# Import Vision Egg C routines, if they exist #############
try:
    from _maxpriority import *                  # gets set_realtime() function
except ImportError:
    def set_realtime():
        """Fake function definition.  Your system doesn't support the real function.
        """
        pass

try:
    from _dout import *
except ImportError:
    def toggle_dout():
        """Fake function definition.  Your system doesn't support the real function.
        """
        pass
    def set_dout(dummy_argument):
        """Fake function definition.  Your system doesn't support the real function.
        """
        pass
    
############# What is the best timing function? #############
if sys.platform == 'win32':
    timing_func = time.clock
else:
    timing_func = time.time    
