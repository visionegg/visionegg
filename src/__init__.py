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

############ A base class finder utility function ###########

def recursive_base_class_finder(klass):
    """A function to find all base classes."""
    result = [klass]
    for base_class in klass.__bases__:
        for base_base_class in recursive_base_class_finder(base_class):
            result.append(base_base_class)
    # Make only a single copy of each class found
    result2 = []
    for r in result:
        if r not in result2:
            result2.append(r)
    return result2
    
############# What is the best timing function? #############
if sys.platform == 'win32':
    timing_func = time.clock
else:
    timing_func = time.time    
