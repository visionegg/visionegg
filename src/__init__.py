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
Dots -- Random dot stimuli
GLTrace -- Trace calls to OpenGL
GUI -- Graphical user interface classes and functions
Gratings -- Grating stimuli
Lib3DS -- Load .3DS files
MoreStimuli -- Assorted stimuli
ParameterTypes -- Type checking for the Vision Egg
PlatformDependent -- Set priority and other functions
PyroClient -- Python Remote Objects support - Client side
PyroHelpers -- Python Remote Objects support
SphereMap -- Stimuli drawn as texture maps on inside of sphere
TCPController -- Allows control of parameter values over the network
Text -- Text stimuli
Textures -- Texture (images mapped onto polygons) stimuli
__init__ -- Loaded with "import VisionEgg" (This module)
darwin_app_stuff -- (Platform dependent) wrappers for low-level C code
darwin_maxpriority -- (Platform dependent) wrappers for low-level C code
posix_maxpriority -- (Platform dependent) wrappers for low-level C code
win32_maxpriority -- (Platform dependent) wrappers for low-level C code

Subpackages:

PyroApps -- Support for demo applications based on Pyro

Classes:

Parameters -- Parameter container
ClassWithParameters -- Base class for any class that uses parameters

Functions:

recursive_base_class_finder() -- A function to find all base classes
time_func() -- Most accurate timing function available on a platform
get_type() -- Get the type or class of argument
assert_type() -- Verify the type of an instance

Public variables:

release_name -- Version information
config -- Instance of Config class from Configuration module

"""
# Copyright (c) 2001-2002 Andrew Straw.  Distributed under the terms of the
# GNU Lesser General Public License (LGPL).

release_name = '0.9.5a3'

import VisionEgg.Configuration
import VisionEgg.ParameterTypes as ve_types
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

# Use Python's bool constants if available, make aliases if not
try:
    True
except NameError:
    True = 1==1
    False = 1==0

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
config = VisionEgg.Configuration.Config()

############# Default exception handler #############

if not sys.argv[0]: # Interactive mode
    config.VISIONEGG_GUI_ON_ERROR = 0

class _ExceptionHookKeeper:
    def handle_exception(self, exc_type, exc_value, exc_traceback):
        global config # XXX hmm -- I don't know why this is necessary.  (Because we're in an exception?)
        # send exception to log file (if it's open yet)
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
        __keep_config__ = config # bizarre that the exception handler changes our values...
        self.orig_hook(exc_type, exc_value, exc_traceback)
        config = __keep_config__ # but we work around it!

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
                    # Check tipe is valid
                    if not ve_types.is_parameter_type_def(tipe):
                        raise ValueError("In definition of parameter '%s', %s is not a valid type declaration."%(parameter_name,tipe))
                    # Was a non-default value passed for this parameter?
                    if kw.has_key(parameter_name): 
                        value = kw[parameter_name]
                        done_kw.append(parameter_name)
                    # Allow None to pass as acceptable value -- lets __init__ set own defaults
                    if type(value) != type(None):
                        # Check anything other than None
                        if not tipe.verify(value):
                            if type(value) != Numeric.ArrayType:
                                value_str = str(value)
                            else:
                                if Numeric.multiply.reduce(value.shape) < 10:
                                    value_str = str(value) # print array if it's smallish
                                else:
                                    value_str = "(array data)" # don't pring if it's big
                            raise TypeError("Parameter '%s' value %s is type %s (not type %s) in %s"%(parameter_name,value_str,type(value),tipe,self))
                    setattr(self.parameters,parameter_name,value)
                done_parameters_and_defaults.append(klass.parameters_and_defaults)

            # Same thing as above for self.constant_parameters:
            #
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
                    
                    if not ve_types.is_parameter_type_def(tipe):
                        raise ValueError("In definition of constant parameter '%s', %s is not a valid type declaration."%(parameter_name,tipe))
                    # Was a non-default value passed for this parameter?
                    if kw.has_key(parameter_name): 
                        value = kw[parameter_name]
                        done_kw.append(parameter_name)
                    # Allow None to pass as acceptable value -- lets __init__ set own default
                    if type(value) != type(None):
                        # Check anything other than None
                        if not tipe.verify(value):
                            if type(value) != Numeric.ArrayType:
                                value_str = str(value)
                            else:
                                if Numeric.multiply.reduce(value.shape) < 10:
                                    value_str = str(value) # print array if it's smallish
                                else:
                                    value_str = "(array data)" # don't pring if it's big
                            raise TypeError("Constant parameter '%s' value %s is type %s (not type %s) in %s"%(parameter_name,value_str,type(value),tipe,self))
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
                return True
        # The for loop only completes if parameter_name is not in any subclass
        return False

    def get_specified_type(self,parameter_name):
        # Get a list of all classes this instance is derived from
        classes = recursive_base_class_finder(self.__class__)
        for klass in classes:
            if klass.parameters_and_defaults.has_key(parameter_name):
                return klass.parameters_and_defaults[parameter_name][1]
        # The for loop only completes if parameter_name is not in any subclass
        raise AttributeError("%s has no parameter named '%s'"%(self.__class__,parameter_name))

def get_type(value):
    warnings.warn("VisionEgg.get_type() has been moved to "+\
                  "VisionEgg.ParameterTypes.get_type()",
                  DeprecationWarning, stacklevel=2)
    return  ve_types.get_type(value)

def assert_type(*args):
    warnings.warn("VisionEgg.assert_type() has been moved to "+\
                  "VisionEgg.ParameterTypes.assert_type()",
                  DeprecationWarning, stacklevel=2)
    return ve_types.assert_type(*args)

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


