# The Vision Egg: DaqLPT
#
# Copyright (C) 2001-2003 Andrew Straw.
# Copyright (C) 2005 Hubertus Becker
# Author: Andrew Straw <astraw@users.sourceforge.net>
# URL: <http://www.visionegg.org/>
#
# Distributed under the terms of the GNU Lesser General Public License
# (LGPL). See LICENSE.TXT that came with this file.

"""
Data acquisition and triggering over the parallel port.

This module was programmed using information from "Interfacing the
Standard Parallel Port" by Craig Peacock,
http://www.senet.com.au/~cpeacock.

You may also be interested in http://www.lvr.com/files/ibmlpt.txt.

This module only uses the Standard Parallel Port (SPP) protocol, not
ECP or EPP.  You may have to set your computer's BIOS accordingly.

You may need to be root or otherwise have permission to access the
parallel port.

Example usage:

>>> from VisionEgg.DaqLPT import raw_lpt_module
>>> address = 0x378
>>> out_value = 0
>>> raw_lpt_module.out( address, out_value )
>>> in_value = raw_lpt_module.inp( address+1 )

"""

####################################################################
#
#        Import all the necessary packages
#
####################################################################

import VisionEgg
import VisionEgg.Core
import VisionEgg.FlowControl
import VisionEgg.Daq
import VisionEgg.ParameterTypes as ve_types
import sys

# See the raw LPT module for your platform for direct LPT access
# without VisionEgg DAQ overhead.  In particular, the inp and out
# functions are useful.

if sys.platform == 'win32':
    try:
        # Dincer Aydin's module http://www.geocities.com/dinceraydin
        import winioport as raw_lpt_module
    except ImportError:
        # Andrew Straw's module http://www.its.caltech.edu/~astraw/coding.html
        import dlportio as raw_lpt_module
elif sys.platform.startswith('linux'):
    import VisionEgg._raw_lpt_linux as raw_lpt_module
elif sys.platform.startswith('irix'):
### IRIX implementation not done, but possible
    raise NotImplementedError("VisionEgg.DaqLPT not implemented on IRIX")
##    import VisionEgg._raw_plp_irix
##    raw_lpt_module = VisionEgg._raw_plp_irix
else:
    raise RuntimeError("VisionEgg.DaqLPT not supported on this platform")

__version__ = VisionEgg.release_name

class LPTInput(VisionEgg.Daq.Input):
    def get_data(self):
        """Get status bits 0-7 of the LPT port.

        The status bits were not meant for high speed digital input.
        Nevertheless, for sampling one or two digital inputs at slow
        rates, they work fine.

        Bits 4 and 5 (pins 13 and 12, respectively) should be first
        choice to sample a digital voltage.  The other bits have some
        oddities. Bits 0 and 1 are designated reserved. Others are
        "active low"; they show a logic 0 when +5v is applied.

        bit3 = value & 0x08
        bit4 = value & 0x10
        bit5 = value & 0x20
        bit6 = value & 0x40
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
        if not 'raw_lpt_module' in globals().keys():
            raise RuntimeError("LPT output not supported on this platform.")
        VisionEgg.Daq.Channel.__init__(self,**kw)
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
        if not 'raw_lpt_module' in globals().keys():
            raise RuntimeError("LPT output not supported on this platform.")
        VisionEgg.Daq.Device.__init__(self,**kw)
        for channel in self.channels:
            if not isinstance(channel,LPTChannel):
                raise ValueError("LPTDevice only has LPTChannels.")
        self.base_address = base_address

    def add_channel(self,channel):
        if not isinstance(channel,LPTChannel):
            raise ValueError("LPTDevice only has LPTChannels.")
        VisionEgg.Daq.Device.add_channel(self,channel)

class LPTTriggerOutController(VisionEgg.FlowControl.Controller):
    """Use 8 bits of digital output for triggering and frame timing verification.

    Bit 0 (pin 2) goes high when the go loop begins and low when the
    loop ends.  Bits 1-7 (pins 3-9) count the frame_number (modulo
    2^7) in binary.  Looking at any one of these pins therefore
    provides verification that your stimulus is not skipping
    frames."""

    def __init__(self,lpt_device=None):
        if not 'raw_lpt_module' in globals().keys():
            raise RuntimeError("LPT output not supported on this platform.")
        VisionEgg.FlowControl.Controller.__init__(self,
                                           return_type=ve_types.NoneType,
                                           eval_frequency=VisionEgg.FlowControl.Controller.EVERY_FRAME)
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

class LPTTriggerInController(VisionEgg.FlowControl.Controller):
    def __init__(self,lpt_device=None,pin=13):
        if not 'raw_lpt_module' in globals().keys():
            raise RuntimeError("LPT input not supported on this platform.")
        VisionEgg.FlowControl.Controller.__init__(self,
                                           return_type=ve_types.Integer,
                                           eval_frequency=VisionEgg.FlowControl.Controller.EVERY_FRAME)
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
        if pin==15:
            bit = 3
        elif pin==13:
            bit = 4
        elif pin==12:
            bit = 5
        elif pin==10:
            bit = 6
        elif pin==11:
            bit = 7
        else:
            raise ValueError("Only pins 10, 11, 12, 13 and 15 supported at this time.")
        self.mask = 2**bit
    def during_go_eval(self):
        return 1
    def between_go_eval(self):
        value = self.trigger_in_channel.constant_parameters.functionality.get_data()
        return (value & self.mask)
