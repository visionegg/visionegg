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
# Copyright (c) 2001-2002 Andrew Straw.  Distributed under the terms of the
# GNU Lesser General Public License (LGPL).

release_name = '0.8.3a0'

import Configuration # a Vision Egg module
import string, os, sys, time, types # standard python modules

__version__ = release_name
__cvs__ = string.split('$Revision$')[1]
__date__ = string.join(string.split('$Date$')[1:3], ' ')
__author__ = 'Andrew Straw <astraw@users.sourceforge.net>'

# Make sure we don't have an old version of the VisionEgg installed.
# (There used to be a module named VisionEgg.VisionEgg.  If it still
# exists, it will randomly crash things.)
try:
    __import__('VisionEgg.VisionEgg') # If we can import it, report error
    raise RuntimeError('Outdated "VisionEgg.py" and/or "VisionEgg.pyc" found.  Please delete from your VisionEgg package directory.')
except ImportError:
    pass # It's OK, the old version isn't there

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
        done_kw = []
        
        # Fill self.parameters with parameter names and set to default values
        for klass in classes:
            # If a class didn't override base class's parameters_and_defaults dictionary, don't deal with it twice
            if klass.parameters_and_defaults not in done_parameters_and_defaults:
                for parameter_name in klass.parameters_and_defaults.keys():
                    # Make sure this parameter key/value pair doesn't exist already
                    if hasattr(self.parameters,parameter_name):
                        raise ValueError("More than one definition of parameter '%s'"%parameter_name)
                    # Get default value and the type
                    value,tipe = klass.parameters_and_defaults[parameter_name]
                    # Was a non-default value passed for this parameter?
                    if parameter_name in kw.keys(): 
                        value = kw[parameter_name]
                        done_kw.append(parameter_name)
                    # Allow None to pass as acceptable value -- lets __init__ set own default
                    if type(value) != types.NoneType:
                        # Check anything other than None
                        if not isinstance(value,tipe):
                            raise TypeError("Parameter %s value %s is not of type %s"%(parameter_name,value,tipe))
                    setattr(self.parameters,parameter_name,value)
                done_parameters_and_defaults.append(klass.parameters_and_defaults)

        # Set self.parameters to the value in "kw"
        for kw_parameter_name in kw.keys():
            if kw_parameter_name not in done_kw:
                raise ValueError("parameter '%s' passed as keyword argument, but not specified by %s (or subclasses) as potential parameter"%(kw_parameter_name,self.__class__))

    def get_specified_type(self,parameter_name):
        # Get a list of all classes this instance is derived from
        classes = recursive_base_class_finder(self.__class__)
        for klass in classes:
            if parameter_name in klass.parameters_and_defaults.keys():
                return klass.parameters_and_defaults[parameter_name][1]
        # The for loop only completes if parameter_name is not in any subclass
        raise AttributeError("%s has no parameter named '%s'"%(self.__class__,parameter_name))

