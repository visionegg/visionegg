"""Data acquisition module for the Vision Egg library.
"""

# Copyright (c) 2001-2002 Andrew Straw.  Distributed under the terms of the
# GNU Lesser General Public License (LGPL).

import VisionEgg
import string

__version__ = VisionEgg.release_name
__cvs__ = string.split('$Revision$')[1]
__date__ = string.join(string.split('$Date$')[1:3], ' ')
__author__ = 'Andrew Straw <astraw@users.sourceforge.net>'

####################################################################
#
#        Data acquisition classes
#
####################################################################

class Trigger(VisionEgg.ClassWithParameters):
    """(Abstract) Defines trigger behavior."""
    parameters_and_defaults = { 'use_trigger' : 0 }
    def arm(self):
        """(Abstract) Start data acquisition when trigger received, or go immediately if use_trigger = 0."""
        pass

class DaqSetup(VisionEgg.ClassWithParameters):
    """(Abstract) Data acquisition hardware interface."""
    parameters_and_defaults = { 'num_channels_used' : 1,
                                'num_channels_max' : 1,
                                'duration_sec': 0.01,
                                'trigger' : None,
                                }
    def add_daq_channel(self,daq_channel):
        """(Abstract) Add a new data acquisition channel"""
        pass

class DaqChannel(VisionEgg.ClassWithParameters):
    parameters_and_defaults = { 'signal_name' : 'Default signal',
                                'channel_num' : 0,
                                'gain' : 0.2048,
                                'offset' : 0.0,
                                'sample_freq_hz' : 1000.0,
                                'units' : 'mV',
                                }

######### old crap below this line #################################
class ChannelParams:
    def __init__(self,channel_number,sample_freq_hz,duration_sec,gain):
        self.channel_number = channel_number
        self.sample_freq_hz = sample_freq_hz
        self.duration_sec = duration_sec
        self.gain = gain

class TriggerMethod:
    pass

class NoTrigger(TriggerMethod):
    pass

class TriggerLowToHigh(TriggerMethod):
    pass

class TriggerHighToLow(TriggerMethod):
    pass
    
class Daq:
    """Abstract base class that defines interface for any data acquisition implementation
    """
    def __init__(self,channel_params_list,trigger_method):
        if not isinstance(trigger_method,TriggerMethod):
            raise RuntimeError("trigger_method must be a subclass of TriggerMethod")
        for channel_params in channel_params_list:
            if not isinstance(channel_params, ChannelParams):
                raise RuntimeError("each element of channel_params_list must be a subclass of ChannelParams")
        self.channel_params_list = channel_params_list
        self.trigger_method = trigger_method
    
