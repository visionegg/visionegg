"""Implements data acquisition over TCP.

This module controls data acquisition hardware running on a (probably)
different computer. The data acquisition server must be implement the
behavior exhibited by the fake_daq_server.py script in the
demo/daq/tcp directory.  fake_daq_server.py emulates the mac OS
program MacDaq, available as a separate project from the Vision Egg
download site.  MacDaq uses MacAdios hardware to acquire data under
control of a network (TCP) connection.

Realtime acquisition and display of the sampled signal is not the goal
of this module. That is the task of the computer actually performing
the data acquisition (i.e. the MacDaq system). This module gets the
data after the acquisition has occurred."""

# Copyright (c) 2001-2002 Andrew Straw.  Distributed under the terms of the
# GNU Lesser General Public License (LGPL)

####################################################################
#
#        Import all the necessary packages
#
####################################################################

import VisionEgg
import VisionEgg.Daq
import socket, re, types
import Numeric

import string

__version__ = VisionEgg.release_name
__cvs__ = string.split('$Revision$')[1]
__date__ = string.join(string.split('$Date$')[1:3], ' ')
__author__ = 'Andrew Straw <astraw@users.sourceforge.net>'

##################################################################
# DaqOverTCP - A subclass of Daq designed to connect to a server #
# with data acquisition capabilities running a simple protocol.  #
##################################################################

class DaqServerTrigger(VisionEgg.Daq.Trigger):
    valid_modes = ['immediate','rising_edge','falling_edge']
    parameters_and_defaults = {'mode':('immediate',types.StringType)}

class DaqServerInputChannel(VisionEgg.Daq.Input):
    def get_data(self):
        return self.channel.device.get_data_for_channel(self.channel.constant_parameters.channel_number)

class DaqServerChannel(VisionEgg.Daq.Channel):
    constant_parameters_and_defaults = {'channel_number':(0,types.IntType)}
    
    def __init__(self,**kw):
        apply(VisionEgg.Daq.Channel.__init__,(self,),kw)
        # Should let daq server raise this error if it can't set gain
        analog = self.constant_parameters.signal_type
        if not isinstance(analog,VisionEgg.Daq.Analog):
            raise NotImplementedError("Only analog channels implemented.")
        if analog.constant_parameters.gain not in [0.2048,2.048,20.48]:
            raise ValueError("Gain not right!")
        #self.constant_parameters.functionality.set_my_channel(self)

    def arm_trigger(self):
        # For MacAdios/DaqServ, only one trigger for everything
        if not hasattr(self,'device'):
            raise RuntimeError("Must add this channel to device using device.add_channel")
        self.device.arm()

class TCPDaqDevice(VisionEgg.Daq.Device):
    """Data acquisition over TCP.

    Interface to a remote data acquisition TCP server that implements
    a simple data acquisition protocol."""
    def __init__(self,hostname='localhost',port=50003,**kw):
        apply(VisionEgg.Daq.Device.__init__,(self,),kw)
        self.connection = DaqConnection(hostname=hostname,port=port)

    def add_channel(self,channel):
        if not isinstance(channel,DaqServerChannel):
            raise ValueError("Can only use DaqServerChannel types!")
        if isinstance(channel.constant_parameters.signal_type,VisionEgg.Daq.Analog):
            buffered = channel.constant_parameters.daq_mode
            if not isinstance(buffered,VisionEgg.Daq.Buffered):
                raise ValueError("channel must have buffered daq_mode.")
            input = channel.constant_parameters.functionality
            if not isinstance(input,VisionEgg.Daq.Input):
                raise NotImplementedError("Only input channels currently implemented.")
            if not isinstance(channel.constant_parameters.daq_mode.parameters.trigger,DaqServerTrigger):
                raise ValueError("channel trigger must be instance of DaqServerTrigger")
            # It's analog, buffered, input
            num = channel.constant_parameters.channel_number
            if num < 0 or num > 7:
                raise ValueError("Channel number %d not in range [0-7]."%num)
            if len(self.channels) > 0:
                for existing_channel in self.channels:
                    if existing_channel.constant_parameters.channel_number == num:
                        raise ValueError("Can only have channels with unique numbers.")
                analog = channel.constant_parameters.signal_type
                if analog.constant_parameters.gain != self.channels[0].constant_parameters.signal_type.constant_parameters.gain:
                    raise ValueError("gain for each channel must be equal.")
                if analog.constant_parameters.offset != 0.0:
                    raise ValueError("offset must be 0.0.")
                must_be_same = ['sample_rate_hz','duration_sec','trigger']
                for p_name in must_be_same:
                    orig_value = getattr(self.channels[0].constant_parameters.daq_mode.parameters,p_name)
                    if getattr(buffered.parameters,p_name) != orig_value:
                        raise ValueError("%s for each channel must be equal."%p_name)
            self.channels.append(channel)
            channel.device = self
        else:
            raise NotImplementedError("Only analog channels currently supported.")

    def remove_channel(self,channel):
        i = self.channels.index(channel)
        del self.channels[i]

    def get_data_for_channel(self, channel_number):
        return self.connection.current_data_array[channel_number,:]

###### The following methods are specific to tcp daq device ########

    def quit_server(self):
        self.connection.quit_server()

    def arm(self):
        # Must be device-wide because MacAdios triggers all channels together
        if len(self.channels) > 0:
            channel_numbers = []
            for existing_channel in self.channels:
                channel_numbers.append(existing_channel.constant_parameters.channel_number)
            channel_numbers.sort()
            sampled_channels = range(channel_numbers[-1]+1)
            num_channels = len(sampled_channels)
            # all the durations and sample frequencies and trigger modes are the same
            buffered = self.channels[0].constant_parameters.daq_mode
            trigger_num = None
            if buffered.parameters.trigger.parameters.mode == 'immediate':
                trigger_num = 0
            elif buffered.parameters.trigger.parameters.mode == 'rising_edge':
                trigger_num = 1
            elif buffered.parameters.trigger.parameters.mode == 'falling_edge':
                trigger_num = 2
            else:
                raise NotImplementedError("")
            self.connection.arm(num_channels,
                                buffered.parameters.sample_rate_hz,
                                buffered.parameters.duration_sec,
                                trigger_num)
        else:
            raise RuntimeError("Must have at least 1 channel")

##class DebugSocket(socket.socket):
##    def send(self,string):
##        #print "SEND",string
##        apply(socket.socket.send,(self,string))

##    def recv(self,bufsize):
##        results = apply(socket.socket.recv,(self,bufsize))
##        #print "RECV",results
##        return results

DebugSocket = socket.socket

class DaqConnection:
    # values for self.remote_state
    NOT_CONNECTED = 1
    COMMAND_PROMPT = 2
    READY = 3
    ARMED = 4

    # some constants
    CRLF = '\r\n'
    BUFSIZE = 4096

    # some more constants
    command_prompt = re.compile('^daqserv> ')
    ready_prompt = re.compile('^ready> ')
    re_crlf = re.compile(CRLF)
    begin_data_prompt = re.compile('^'+re.escape(
        'BEGIN ASCII DATA (32 bit big-endian signed int)'
        )+'$')
    end_data_prompt = re.compile('^'+re.escape(
        'END ASCII DATA'
        )+'$')
    
    def __init__(self,hostname='localhost',port=50003):
        self.remote_state = DaqConnection.NOT_CONNECTED

        # Connect to the server 
        self.socket = DebugSocket(socket.AF_INET, socket.SOCK_STREAM)
        #self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        self.socket.connect((hostname,port))
        self.buffer = ''
        self.gain = None # unknown

        # Wait until we get a command prompt
        while not DaqConnection.command_prompt.search(self.buffer):
            self.buffer = self.buffer + self.socket.recv(DaqConnection.BUFSIZE)
            # Prune all but the last line from the buffer
            self.buffer = string.split(self.buffer,"%s%s"%(chr(0x0D),chr(0x0A)))[-1]
        # XXX to-do: prune everything up to the end of command_prompt from self.buffer
        
        self.remote_state = DaqConnection.COMMAND_PROMPT

    def set_gain(self,gain):
        if self.remote_state != DaqConnection.COMMAND_PROMPT:
            raise RuntimeError("Must be in command prompt state!")
        
        # Set the gain
        self.socket.send('gain(%f)'%gain + DaqConnection.CRLF)
        self.gain = gain

        # Get a command prompt
        data = self.socket.recv(DaqConnection.BUFSIZE)
        if not self.command_prompt.search(data):
            raise RuntimeError("Got unexpected reply in DaqConnection: %s"%data)

        # Wait until we get a command prompt
        while not self.command_prompt.search(data):
            data = self.socket.recv(DaqConnection.BUFSIZE)

        self.remote_state = DaqConnection.COMMAND_PROMPT

    def arm(self,
            num_channels,
            sample_rate_hz,
            duration_sec,
            trigger_num):
        if self.remote_state != DaqConnection.COMMAND_PROMPT:
            raise RuntimeError('DaqConnection.arm() called when remote server not in command prompt state.')
        digitize_string = "digitize(%d,%f,%f,%d)"%(num_channels,
                                                   sample_rate_hz,
                                                   duration_sec,
                                                   trigger_num)
        self.current_data_array = Numeric.zeros((0,num_channels),'int')
        self.socket.send(digitize_string + DaqConnection.CRLF)

        # I should go into non-blocking mode and wait
        # a timeout period before giving up and
        # returning an error
        data = self.socket.recv(DaqConnection.BUFSIZE)
        if not DaqConnection.ready_prompt.search(data):
            raise RuntimeError("Got unexpected reply when preparing to digitize in DaqConnection: %s"%data)
        
        self.remote_state = DaqConnection.READY

        ######### Return here #######


        ##################################################
        
        if self.remote_state != DaqConnection.READY:
            raise RuntimeError('DaqOverTCP.go() called when remote server not in ready state.')
        self.socket.send('go' + DaqConnection.CRLF)
        self.remote_state = DaqConnection.ARMED

        ##################################################

        self.parse_data()

    def parse_data(self):
        if self.remote_state != DaqConnection.ARMED:
            raise RuntimeError('DaqConnection.parse_data() called when remote server not in aquiring state.')

        # Parse data
        done = 0
        getting_waves = 0
        leftover_data = ""
        while not done:
            data = self.socket.recv(DaqConnection.BUFSIZE)
            lines = string.split(data,DaqConnection.CRLF)

            # due to buffering not being lined up with lines:
            lines[0] = leftover_data + lines[0] # use last incomplete line
            leftover_data = lines.pop() # incomplete last line

            # because the command prompt doesn't end with CRLF, check for it:
            if self.command_prompt.search(leftover_data):
                done = 1

            for line in lines:
                if line == "": # Nothing in this line, do the next
                    continue 
                if not getting_waves:
                    if DaqConnection.begin_data_prompt.search(line):
                        #print "START!"
                        getting_waves = 1
                        waves = []
                    else:
                        raise ValueError("Unexpected string from daq server when parsing output: '%s'"%line)
                else: # getting_waves 
                    if DaqConnection.end_data_prompt.search(line):
                        self.current_data_array = Numeric.array(waves)
                        waves = []
                        getting_waves = 0
                    else: # The data!
                        this_row = map(int,string.split(line))
                        if len(this_row) > 0:
                            waves.append(this_row)
        self.current_data_array = Numeric.transpose(self.current_data_array)
        self.remote_state = DaqConnection.COMMAND_PROMPT

    def close_socket(self,command='exit'):
        if self.remote_state != DaqConnection.COMMAND_PROMPT:
            self.socket.send(command + DaqConnection.CRLF)
        del self
##            self.socket.setblocking( 0 ) # stop blocking - clear the receive buffer
##            try:
##                data = self.socket.recv(BUFSIZE) # clear the input buffer
##                #while len(data) > 0:
##                #    data = self.socket.recv(BUFSIZE) # clear the input buffer
##            except socket.error, x:
##                pass
        
    def quit_server(self):
        self.close_socket(command='server quit')
##        self.socket.send('server quit' +  CRLF)
##        data = self.socket.recv(BUFSIZE) # clear the input buffer

##    def __del__(self):
##        self.close_socket(command='exit')
##        # close socket connection nicely if possible
##        if self.remote_state != "not connected":
##            self.socket.send('exit' +  CRLF)
##            data = self.socket.recv(BUFSIZE) # clear the input buffer
##            while len(data) > 0:
##                data = self.socket.recv(BUFSIZE) # clear the input buffer


