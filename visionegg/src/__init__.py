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

Modules:

Core -- Core Vision Egg functionality
TCPController -- Allows control of parameter values over the network
PlatformDependent -- Attempt to isolate platform dependencies in one place
Daq -- Definition of data acquisition and triggering interfaces
DaqLPT -- Data acquisition and triggering over the parallel port
DaqOverTCP -- Implements data acquisition over TCP
Configuration -- Load config values from environment, config file, or defaults
Gratings -- Grating stimuli
Textures -- Texture (images mapped onto polygons) stimuli
Text -- Text stimuli
MoreStimuli -- Assorted stimuli
GUI -- Graphical user interface classes and functions
PyroHelpers -- Python Remote Objects support

Classes:

Parameters -- Parameter container
ClassWithParameters -- Base class for any class that uses parameters

Functions:

recursive_base_class_finder -- A function to find all base classes
timing_func -- Most accurate timing function available on a platform
get_type -- Get the type or class of argument
assert_type -- Assert that argument 1 is of the type argument 2

Public variables:

release_name -- Version information
config -- Instance of Config class from Configuration module

"""
# Copyright (c) 2001-2002 Andrew Straw.  Distributed under the terms of the
# GNU Lesser General Public License (LGPL).

release_name = '0.9.0'

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

############# Default exception handler #############

# Mac OS X weirdness test:
if sys.platform == 'darwin' and not os.path.isabs(sys.argv[0]):
    # When run directly from commandline, no GUIs!
    config.VISIONEGG_TKINTER_OK = 0

if config.VISIONEGG_GUI_ON_ERROR and config.VISIONEGG_TKINTER_OK:
    import traceback, StringIO
    import GUI
    def _vision_egg_exception_hook(exc_type, exc_value, exc_traceback):
        traceback_stream = StringIO.StringIO()
        traceback.print_tb(exc_traceback,None,traceback_stream)
        GUI.showexception(exc_type, exc_value, traceback_stream.getvalue())
        traceback.print_exception(exc_type,exc_value,exc_traceback)
    class _ExceptionHookKeeper:
        def __init__(self):
            self.orig_hook = sys.excepthook
            sys.excepthook = _vision_egg_exception_hook
        def __del__(self):
            sys.excepthook = self.orig_hook
    _exception_hook_keeper = _ExceptionHookKeeper()

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
    """Parameter container.

    This parameter container is useful so that parameters can be
    controlled via any number of means: evaluating a python function,
    acquiring some data with a digital or analog input, etc.

    Any class which has parameters should be subclass of
    ClassWithParameters, which will create an instance of this
    (Parameters) class automatically based on the default parameters
    and arguments.

    All parameters (such as contrast, position, etc.) which should be
    modifiable in runtime should be attributes of an instance of this
    class, which serves as a nameholder for just this purpose."""
    pass

class ClassWithParameters:
    """Base class for any class that uses parameters.

    Any class that uses parameters potentially modifiable in realtime
    should be a subclass of ClassWithParameters.  This class enforces
    a standard system of parameter specification with type checking
    and default value setting.  See classes Screen, Viewport, or any
    daughter class of Stimulus for examples."""
    
    constant_parameters_and_defaults = {} # empty for base class
    parameters_and_defaults = {} # empty for base class

    def __init__(self,**kw):
        """Create self.parameters and set values."""
        
        self.constant_parameters = Parameters() # create self.constant_parameters
        self.parameters = Parameters() # create self.parameters
        
        # Get a list of all classes this instance is derived from
        classes = recursive_base_class_finder(self.__class__)

        done_constant_parameters_and_defaults = []
        done_parameters_and_defaults = []
        done_kw = []
        
        # Fill self.parameters with parameter names and set to default values
        for klass in classes:
            # Create self.parameters and set values to keyword argument if found,
            # otherwise to default value.
            #
            # If a class didn't override base class's parameters_and_defaults dictionary, don't deal with it twice
            if klass.parameters_and_defaults not in done_parameters_and_defaults:
                for parameter_name in klass.parameters_and_defaults.keys():
                    # Make sure this parameter key/value pair doesn't exist already
                    if hasattr(self.parameters,parameter_name):
                        raise ValueError("More than one definition of parameter '%s'"%parameter_name)
                    # Get default value and the type
                    if type(klass.parameters_and_defaults[parameter_name]) != types.TupleType:
                        raise ValueError("Definition of parameter '%s' in class %s must be a 2 tuple specifying value and type."%(parameter_name,klass))
                    if len(klass.parameters_and_defaults[parameter_name]) != 2:
                        raise ValueError("Definition of parameter '%s' in class %s must be a 2 tuple specifying value and type."%(parameter_name,klass))
                    value,tipe = klass.parameters_and_defaults[parameter_name]
                    if type(tipe) not in [types.TypeType,types.ClassType]:
                        raise ValueError("In definition of parameter '%s', %s is not a valid type declaration."%(parameter_name,tipe))
                    # Was a non-default value passed for this parameter?
                    if parameter_name in kw.keys(): 
                        value = kw[parameter_name]
                        done_kw.append(parameter_name)
                    # Allow None to pass as acceptable value -- lets __init__ set own default
                    if type(value) != types.NoneType:
                        # Check anything other than None
                        if not isinstance(value,tipe):
                            raise TypeError("Parameter '%s' value %s is type %s (not type %s)"%(parameter_name,value,type(value),tipe))
                    setattr(self.parameters,parameter_name,value)
                done_parameters_and_defaults.append(klass.parameters_and_defaults)
            # Create self.constant_parameters and set values to keyword argument if found,
            # otherwise to default value.
            #
            # If a class didn't override base class's parameters_and_defaults dictionary, don't deal with it twice
            if klass.constant_parameters_and_defaults not in done_constant_parameters_and_defaults:
                for parameter_name in klass.constant_parameters_and_defaults.keys():
                    # Make sure this parameter key/value pair doesn't exist already
                    if hasattr(self.parameters,parameter_name):
                        raise ValueError("Definition of '%s' as variable parameter and constant parameter."%parameter_name)
                    if hasattr(self.constant_parameters,parameter_name):
                        raise ValueError("More than one definition of constant parameter '%s'"%parameter_name)
                    # Get default value and the type
                    if type(klass.constant_parameters_and_defaults[parameter_name]) != types.TupleType:
                        raise ValueError("Definition of constant parameter '%s' in class %s must be a 2 tuple specifying value and type."%(parameter_name,klass))
                    if len(klass.constant_parameters_and_defaults[parameter_name]) != 2:
                        raise ValueError("Definition of constant parameter '%s' in class %s must be a 2 tuple specifying value and type."%(parameter_name,klass))
                    value,tipe = klass.constant_parameters_and_defaults[parameter_name]
                    if type(tipe) not in [types.TypeType,types.ClassType]:
                        raise ValueError("In definition of constant parameter '%s', %s is not a valid type declaration."%(parameter_name,tipe))
                    # Was a non-default value passed for this parameter?
                    if parameter_name in kw.keys(): 
                        value = kw[parameter_name]
                        done_kw.append(parameter_name)
                    # Allow None to pass as acceptable value -- lets __init__ set own default
                    if type(value) != types.NoneType:
                        # Check anything other than None
                        if not isinstance(value,tipe):
                            raise TypeError("Constant parameter '%s' value %s is not of type %s"%(parameter_name,value,tipe))
                    setattr(self.constant_parameters,parameter_name,value)
                done_constant_parameters_and_defaults.append(klass.constant_parameters_and_defaults)

        # Set self.parameters to the value in "kw"
        for kw_parameter_name in kw.keys():
            if kw_parameter_name not in done_kw:
                raise ValueError("parameter '%s' passed as keyword argument, but not specified by %s (or subclasses) as potential parameter"%(kw_parameter_name,self.__class__))

    def is_constant_parameter(self,parameter_name):
        # Get a list of all classes this instance is derived from
        classes = recursive_base_class_finder(self.__class__)
        for klass in classes:
            if parameter_name in klass.constant_parameters_and_defaults.keys():
                return 1
        # The for loop only completes if parameter_name is not in any subclass
        return 0

    def get_specified_type(self,parameter_name):
        # Get a list of all classes this instance is derived from
        classes = recursive_base_class_finder(self.__class__)
        for klass in classes:
            if parameter_name in klass.parameters_and_defaults.keys():
                return klass.parameters_and_defaults[parameter_name][1]
        # The for loop only completes if parameter_name is not in any subclass
        raise AttributeError("%s has no parameter named '%s'"%(self.__class__,parameter_name))

def get_type(value):
    """Return the type if it's not an instance, return the class if it is."""
    my_type = type(value)
    if my_type == types.InstanceType:
        my_type = value.__class__
    return my_type

def assert_type(check_type,require_type):
    """Perform type check for the Vision Egg."""
    if check_type != require_type:
        type_error = 0
        if type(require_type) == types.ClassType:
            if not issubclass( check_type, require_type ):
                type_error = 1
        else:
            type_error = 1
        if type_error:
            raise TypeError("%s is not of type %s"%(check_type,require_type))
