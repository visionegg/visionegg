"""Data acquisition over the parallel port for the Vision Egg.

Only x86 computers seem to have parallel ports.  This module was
programmed using information from "Interfacing the Standard Parallel
Port" by Craig Peacock, http://www.senet.com.au/~cpeacock.

This module only uses the Standard Parallel Port (SPP) protocol, not
ECP or EPP."""

# Copyright (c) 2001-2002 Andrew Straw.  Distributed under the terms of the
# GNU Lesser General Public License (LGPL)

####################################################################
#
#        Import all the necessary packages
#
####################################################################

import VisionEgg
import VisionEgg.Core
import VisionEgg.Daq
import sys, types, string
if sys.platform == 'win32':
    import winioport
    raw_lpt_module = winioport
elif sys.platform == 'linux2':
    import VisionEgg._raw_lpt_linux
    raw_lpt_module = VisionEgg._raw_lpt_linux
    
__version__ = VisionEgg.release_name
__cvs__ = string.split('$Revision$')[1]
__date__ = string.join(string.split('$Date$')[1:3], ' ')
__author__ = 'Andrew Straw <astraw@users.sourceforge.net>'

class LPTInput(VisionEgg.Daq.Input):
    def get_data(self):
        """Get status bits 0-7 of the LPT port.

        The status bits were not really meant for data input
        Nevertheless, for sampling one or two digital inputs, they
        work fine.

        Bits 4 and 5 (pins 13 and 12, respectively) should be first
        choice to sample a digital voltage.  The other bits have some
        oddities. Bits 0 and 1 are designated reserved. Others are
        "active low"; they show a logic 0 when +5v is applied.

        bit4 = value & 0x10
        bit5 = value & 0x20
        """
        return raw_lpt_module.inp(self.channel.device.base_address+1)

class LPTOutput(VisionEgg.Daq.Output):
    def put_data(self,data):
        """Set output bits 0-7 (pins 2-9) on the LPT port."""
        raw_lpt_module.out(self.channel.device.base_address,data)
    def __del__(self):
        """Set output bits low when closing."""
        raw_lpt_module.out(self.channel.device.base_address,0)

class LPTChannel(VisionEgg.Daq.Channel):
    """A data acquisition channel using the parallel port."""
    def __init__(self,**kw):
        if not 'raw_lpt_module' in dir():
            raise RuntimeError("LPT output not supported on this platform.")
        apply(VisionEgg.Daq.Channel.__init__,(self,),kw)
        signal_type = self.constant_parameters.signal_type
        if not isinstance(signal_type,VisionEgg.Daq.Digital):
            raise ValueError("Channel must be digital.")
        daq_mode = self.constant_parameters.daq_mode
        if not isinstance(daq_mode,VisionEgg.Daq.Immediate):
            raise ValueError("Channel must be immediate mode.")
        functionality = self.constant_parameters.functionality
        if not isinstance(functionality,LPTInput):
            if not isinstance(functionality,LPTOutput):
                raise ValueError("Channel functionality must be instance of LPTInput or LPTOutput.")

class LPTDevice(VisionEgg.Daq.Device):
    """A single parallel port. (Line PrinTer port.)
    
    Typically, LPT1 has a base address of 0x0378, and LPT2 has a base
    address of 0x0278."""
    
    def __init__(self,base_address=0x378,**kw):
        if not 'raw_lpt_module' in dir():
            raise RuntimeError("LPT output not supported on this platform.")
        apply(VisionEgg.Daq.Device.__init__,(self,),kw)
        for channel in self.channels:
            if not isinstance(channel,LPTChannel):
                raise ValueError("LPTDevice only has LPTChannels.")
        self.base_address = base_address

    def add_channel(self,channel):
        if not isinstance(channel,LPTChannel):
            raise ValueError("LPTDevice only has LPTChannels.")
        VisionEgg.Daq.Device.add_channel(self,channel)
        
class LPTTriggerOutController(VisionEgg.Core.Controller):
    """Use 8 bits of digital output for triggering and frame timing verification.

    Bit 0 (pin 2) goes high when the go loop begins and low when the
    loop ends.  Bits 1-7 (pins 3-9) count the frame_number (modulo
    2^7) in binary.  Looking at any one of these pins therefore
    provides verification that your stimulus is not skipping
    frames."""
    
    def __init__(self,lpt_device=None):
        if not 'raw_lpt_module' in dir():
            raise RuntimeError("LPT output not supported on this platform.")
        VisionEgg.Core.Controller.__init__(self,
                                           return_type=types.NoneType,
                                           eval_frequency=VisionEgg.Core.Controller.EVERY_FRAME)
        # Initialize DAQ stuff:
        self.trigger_out_channel = LPTChannel(signal_type = VisionEgg.Daq.Digital(),
                                              daq_mode = VisionEgg.Daq.Immediate(),
                                              functionality = LPTOutput())
        if lpt_device is None:
            self.device = LPTDevice()
        else:
            if not isinstance(lpt_device,LPTDevice):
                raise ValueError("lpt_device must be instance of LPTDevice.")
            self.device = lpt_device
        self.device.add_channel(self.trigger_out_channel)
                                           
        self.total_frames = 0
    def during_go_eval(self):
        self.total_frames = (self.total_frames + 1) % (2**7)
        value = self.total_frames*2 + 1
        self.trigger_out_channel.constant_parameters.functionality.put_data(value)
    def between_go_eval(self):
        self.total_frames = (self.total_frames + 1) % (2**7)
        value = self.total_frames*2 + 0
        self.trigger_out_channel.constant_parameters.functionality.put_data(value)

class LPTTriggerInController(VisionEgg.Core.Controller):
    def __init__(self,lpt_device=None,pin=13):
        if not 'raw_lpt_module' in dir():
            raise RuntimeError("LPT input not supported on this platform.")
        VisionEgg.Core.Controller.__init__(self,
                                           return_type=types.IntType,
                                           eval_frequency=VisionEgg.Core.Controller.EVERY_FRAME)
        # Initialize DAQ stuff:
        self.trigger_in_channel = LPTChannel(signal_type = VisionEgg.Daq.Digital(),
                                             daq_mode = VisionEgg.Daq.Immediate(),
                                             functionality = LPTInput())
        if lpt_device is None:
            self.device = LPTDevice()
        else:
            if not isinstance(lpt_device,LPTDevice):
                raise ValueError("lpt_device must be instance of LPTDevice.")
            self.device = lpt_device
        self.device.add_channel(self.trigger_in_channel)
        if pin==13:
            bit = 4
        elif pin==12:
            bit = 5
        else:
            raise ValueError("Only pins 12 and 13 supported at this time.")
        self.mask = 2**bit
    def during_go_eval(self):
        return 1
    def between_go_eval(self):
        value = self.trigger_in_channel.constant_parameters.functionality.get_data()
        return (value & self.mask)
