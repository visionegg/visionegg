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
import pygame, pygame.display

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

############# What function do we use to swap the buffers? #########
swap_buffers = pygame.display.flip

####################################################################
#
#        Parameters
#
####################################################################

class Parameters:
    """Hold stimulus parameters.

    This abstraction of parameters is useful so that parameters can be
    controlled via any number of means: evaluating a python function,
    acquiring some data with a digital or analog input, etc.

    All parameters (such as contrast, position, etc.) which should be
    modifiable in runtime should be attributes of an instance of this
    class, which serves as a nameholder for just this purpose.

    Any class which has parameters should be subclass of ParameterUser.

    See the Presentation class for more information about parameters
    and controllers.
    """
    pass

class ClassWithParameters:
    """Base class for any Vision Egg class that uses parameters.

    Any class that uses parameters potentially modifiable in realtime
    should be a subclass of ClassWithParameters.  This class enforces
    a standard system of parameter specification and default value
    setting.  See classes Screen, Viewport, or any daughter class of
    Stimulus for examples."""
    
    parameters_and_defaults = {} # empty for base class

    def __init__(self,**kw):
        """Create self.parameters and set values."""
        
        self.parameters = Parameters() # create self.parameters
        
        # Get a list of all classes this instance is derived from
        classes = recursive_base_class_finder(self.__class__)

        done_parameters_and_defaults = []

        # Fill self.parameters with parameter names and set to default values
        for klass in classes:
            # If a class didn't override base class's parameters_and_defaults dictionary, don't deal with it twice
            if klass.parameters_and_defaults not in done_parameters_and_defaults:
                done_parameters_and_defaults.append(klass.parameters_and_defaults)
                for parameter_name in klass.parameters_and_defaults.keys():
                    # Make sure this parameter key/value pair doesn't exist already
                    if hasattr(self.parameters,parameter_name):
                        raise ValueError("More than one definition of parameter '%s'"%parameter_name)
                    setattr(self.parameters,parameter_name,klass.parameters_and_defaults[parameter_name])

        # Set self.parameters to the value in "kw"
        for kw_parameter_name in kw.keys():
            # Make sure this parameter exists already
            if not hasattr(self.parameters,kw_parameter_name):
                raise ValueError("parameter '%s' passed as keyword argument, but not specified by %s (or subclasses) as potential parameter"%(kw_parameter_name,self.__class__))
            else:
                setattr(self.parameters,kw_parameter_name,kw[kw_parameter_name])
