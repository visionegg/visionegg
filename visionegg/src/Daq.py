"""Data acquisition module for the Vision Egg library.
"""

# Copyright (c) 2001-2002 Andrew Straw.  Distributed under the terms of the
# GNU Lesser General Public License (LGPL).

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
    
