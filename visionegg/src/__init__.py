"""The Vision Egg package.

See the "Core" module for the fundamental Vision Egg classes.

The Vision Egg is a programming library (with demo applications) that
uses standard, inexpensive computer graphics cards to produce visual
stimuli for vision research experiments.

Today's consumer computer graphics cards, thanks to the demands of
computer gamers, are capable of drawing and updating computer graphics
suitable for producing research-quality visual stimuli. The Vision Egg
allows the vision scientist (or anyone else) to program these cards
using OpenGL, the standard in computer graphics
programming. Potentially difficult tasks, such as initializing
graphics, getting precise timing information, controlling stimulus
parameters in real-time, and synchronizing with data acquisition are
greatly eased by routines within the Vision Egg.

Modules:

Core -- Core Vision Egg functionality
Configuration -- Load config values
Daq -- Definition of data acquisition and triggering interfaces
DaqLPT -- Data acquisition and triggering over the parallel port
DaqOverTCP -- Implements data acquisition over TCP
GUI -- Graphical user interface classes and functions
Gratings -- Grating stimuli
Lib3DS -- Load .3DS files
MoreStimuli -- Assorted stimuli
PlatformDependent -- Set priority and other functions
PyroHelpers -- Python Remote Objects support
SphereMap -- Stimuli drawn as texture maps on inside of sphere
TCPController -- Allows control of parameter values over the network
Textures -- Texture (images mapped onto polygons) stimuli
Text -- Text stimuli
__init__ -- Loaded with "import VisionEgg" (This module)

Subpackages:

PyroApps -- Support for demo applications based on Pyro

Classes:

Parameters -- Parameter container
ClassWithParameters -- Base class for any class that uses parameters

Functions:

recursive_base_class_finder() -- A function to find all base classes
timing_func() -- Most accurate timing function available on a platform
get_type() -- Get the type or class of argument
assert_type() -- Verify the type of an instance

Public variables:

release_name -- Version information
config -- Instance of Config class from Configuration module

"""
# Copyright (c) 2001-2002 Andrew Straw.  Distributed under the terms of the
# GNU Lesser General Public License (LGPL).

release_name = '0.9.5a0'

import Configuration # a Vision Egg module
import string, os, sys, time, types # standard python modules
import Numeric
import warnings
import traceback
try:
    import cStringIO as StringIO
except:
    import StringIO

__version__ = release_name
__cvs__ = string.split('$Revision$')[1]
__date__ = string.join(string.split('$Date$')[1:3], ' ')
__author__ = 'Andrew Straw <astraw@users.sourceforge.net>'

# Make sure we don't have an old version of the VisionEgg installed.
# (There used to be a module named VisionEgg.VisionEgg.  If it still
# exists, it will randomly crash things.)
try:
    __import__('VisionEgg.VisionEgg')
except ImportError:
    pass # It's OK, the old version isn't there
else:
    # If we can import it, report error
    raise RuntimeError('Outdated "VisionEgg.py" and/or "VisionEgg.pyc" found.  Please delete from your VisionEgg package directory.')

############# Get config defaults #############
config = Configuration.Config()

############# Default exception handler #############

if not sys.argv[0]: # Interactive mode
    config.VISIONEGG_GUI_ON_ERROR = 0

class _ExceptionHookKeeper:
    def handle_exception(self, exc_type, exc_value, exc_traceback):

        # send exception to log file
        if hasattr(config,"_message"):
            traceback_stream = StringIO.StringIO()
            traceback.print_exception(exc_type,exc_value,exc_traceback,None,traceback_stream)
            traceback_stream.seek(0)

            config._message.add(traceback_stream.read(),
                                level=config._message.WARNING,
                                preserve_formatting=1,
                                no_sys_stderr=1) # prevent exception from going to console twice

        if config.VISIONEGG_GUI_ON_ERROR and config.VISIONEGG_TKINTER_OK:
            # Should really check if any GUI windows are open and only do this then

            # close any open screens
            if hasattr(config,'_open_screens'):
                for screen in config._open_screens:
                    screen.close()

            traceback_stream = StringIO.StringIO()
            traceback.print_tb(exc_traceback,None,traceback_stream)
            traceback_stream.seek(0)

            import GUI
            pygame_bug_workaround = 0 # do we need to workaround pygame bug?
            if hasattr(config,"_pygame_started"):
                if config._pygame_started:
                    pygame_bug_workaround = 1
            if sys.platform[:5] == "linux": # doesn't affect linux for some reason
                pygame_bug_workaround = 0
            if not pygame_bug_workaround:
                GUI.showexception(exc_type, exc_value, traceback_stream.getvalue())

        # continue on with normal exception processing:
        self.orig_hook(exc_type, exc_value, exc_traceback)

    def __init__(self):
        self._sys = sys # preserve ref to sys module
        self.orig_hook = self._sys.excepthook # keep copy
        sys.excepthook = self.handle_exception
    def __del__(self):
        self._sys.excepthook = self.orig_hook # restore original
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
    
############# Setup timing functions #############
if sys.platform == "win32":
    # on win32, time.clock() theoretically has better resolution than time.time()
    true_time_func = time.clock 
else:
    true_time_func = time.time

config._FRAMECOUNT_ABSOLUTE = 0 # initialize global variable
def time_func():
    """Return current time.

    This returns a floating point timestamp.  It uses the most
    accurate time available on a given platform (unless in "lock time
    to frames" mode.")."""
    if config.VISIONEGG_LOCK_TIME_TO_FRAMES:
        return config._FRAMECOUNT_ABSOLUTE * (1.0/ config.VISIONEGG_MONITOR_REFRESH_HZ)
    else:
        return true_time_func()

def timing_func():
    """DEPRECATED.  Use time_func instead"""
    if globals().has_key('_gave_timing_func_warning'):
        global _gave_timing_func_warning
        _gave_timing_func_warning = 1
        warnings.warn("timing_func() has been changed to time_func(). "+\
                      "This warning will only be issued once, but each call to "+\
                      "timing_func() will be slower than if you called time_func() "+\
                      "directly",DeprecationWarning, stacklevel=2)
    return time_func()

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

class CallableType:
    """Fake class to represent the type of any callable object"""
    pass

class ClassWithParameters:
    """Base class for any class that uses parameters.

    Any class that uses parameters potentially modifiable in realtime
    should be a subclass of ClassWithParameters.  This class enforces
    a standard system of parameter specification with type checking
    and default value setting.  See classes Screen, Viewport, or any
    daughter class of Stimulus for examples.

    Any subclass of ClassWithParameters can define two class (not
    instance) attributes, "parameters_and_defaults" and
    "constant_parameters_and_defaults". These are dictionaries where
    the key is a string containing the name of the parameter and the
    the value is a tuple of length 2 containing the default value and
    the type.  For example, an acceptable dictionary would be
    {"parameter1" : (1.0, types.FloatType)}
    
    The name "constant_parameters_and_defaults" is slightly
    misleading. Although the distinction is fine, a more precise name
    would be "immutable" rather than "constant".  The Vision Egg does
    no checking to see if applications follow these rules, but to
    violate them risks undefined behavior.  Here's a quote from the
    Python Reference Manual that describes immutable containers, such
    as a tuple:

        The value of an immutable container object that contains a
        reference to a mutable object can change when the latter's
        value is changed; however the container is still considered
        immutable, because the collection of objects it contains
        cannot be changed. So, immutability is not strictly the same
        as having an unchangeable value, it is more subtle.

    """
    parameters_and_defaults = {} # empty for base class
    constant_parameters_and_defaults = {} # empty for base class

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
                    if kw.has_key(parameter_name): 
                        value = kw[parameter_name]
                        done_kw.append(parameter_name)
                    # Allow None to pass as acceptable value -- lets __init__ set own default
                    if type(value) != types.NoneType:
                        # Check anything other than None
                        if not tipe == CallableType:
                            if not isinstance(value,tipe):
                                if type(value) != Numeric.ArrayType:
                                    value_str = str(value)
                                else:
                                    if Numeric.multiply.reduce(value.shape) < 10:
                                        value_str = str(value) # print array if it's smallish
                                    else:
                                        value_str = "(array data)" # don't pring if it's big
                                raise TypeError("Parameter '%s' value %s is type %s (not type %s)"%(parameter_name,value_str,type(value),tipe))
                        else: # make sure it's a callable type
                            if not type(value) == types.FunctionType:
                                if not type(value) == types.MethodType:
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
                    if kw.has_key(parameter_name): 
                        value = kw[parameter_name]
                        done_kw.append(parameter_name)
                    # Allow None to pass as acceptable value -- lets __init__ set own default
                    if type(value) != types.NoneType:
                        # Check anything other than None
                        if not isinstance(value,tipe):
                            if not (type(value) == types.IntType and tipe == types.FloatType): # allow ints to pass as floats
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
            if klass.constant_parameters_and_defaults.has_key(parameter_name):
                return 1
        # The for loop only completes if parameter_name is not in any subclass
        return 0

    def get_specified_type(self,parameter_name):
        # Get a list of all classes this instance is derived from
        classes = recursive_base_class_finder(self.__class__)
        for klass in classes:
            if klass.parameters_and_defaults.has_key(parameter_name):
                return klass.parameters_and_defaults[parameter_name][1]
        # The for loop only completes if parameter_name is not in any subclass
        raise AttributeError("%s has no parameter named '%s'"%(self.__class__,parameter_name))

class StaticClassMethod:
    """Used within the Vision Egg to create static class methods.

    This comes from Alex Martelli's recipe at
    http://aspn.activestate.com/ASPN/Cookbook/Python/Recipe/52304
    Static class methods are methods which do not require the class to
    be instantiated.  In fact, they are often used as constructors."""
    def __init__(self,method):
        self.__call__ = method

def get_type(value):
    """Get the type of a value.

    This implements a Vision Egg specific version of "type" used for
    type checking by the VisionEgg.Core.Controller class. Return the
    type if it the value is not an instance of a class, return the
    class if it is."""
    
    my_type = type(value)
    if my_type == types.InstanceType:
        my_type = value.__class__
    return my_type

def assert_type(check_type,require_type):
    """Perform type check for the Vision Egg.

    All type checking done to verify that a parameter is set to the
    type defined in its class's "parameters_and_defaults" attribute
    should call use method."""
    
    if check_type != require_type:
        type_error = 0
        if type(require_type) == types.ClassType:
            if not issubclass( check_type, require_type ):
                type_error = 1
        else:
            type_error = 1
        if type_error:
            raise TypeError("%s is not of type %s"%(check_type,require_type))

def _get_lowerleft(position,anchor,size):
    """Private helper function"""
    if anchor == 'lowerleft':
        lowerleft = position
    elif anchor == 'center':
        lowerleft = (position[0] - size[0]/2.0, position[1] - size[1]/2.0)
    elif anchor == 'lowerright':
        lowerleft = (position[0] - size[0],position[1])
    elif anchor == 'upperright':
        lowerleft = (position[0] - size[0],position[1] - size[1])
    elif anchor == 'upperleft':
        lowerleft = (position[0],position[1] - size[1])
    elif anchor == 'left':
        lowerleft = (position[0],position[1] - size[1]/2.0)
    elif anchor == 'right':
        lowerleft = (position[0] - size[0],position[1] - size[1]/2.0)
    elif anchor == 'bottom':
        lowerleft = (position[0] - size[0]/2.0,position[1])
    elif anchor == 'top':
        lowerleft = (position[0] - size[0]/2.0,position[1] - size[1])
    else:
        raise ValueError("No anchor position %s"%anchor)
    return lowerleft
