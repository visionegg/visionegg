"""Implements data acquisition over TCP.

This module controls data acquisition hardware running on a (probably)
different computer. The data acquisition server must be implement the
behavior exhibited by fake_daq_server.

Realtime acquisition and display of the sampled signal is not the
priority of this module. That is the task of the computer actually
performing the data acquisition. This module merely gets the data
after the acquisition has occurred."""

# Copyright (c) 2001-2002 Andrew Straw.  Distributed under the terms of the
# GNU Lesser General Public License (LGPL)

####################################################################
#
#        Import all the necessary packages
#
####################################################################

import VisionEgg
import VisionEgg.Daq
import VisionEgg.Message
import socket, re
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

class DaqOverTCP(VisionEgg.Daq.DaqSetup):
    """Data acquisition over TCP.

    Interface to a remote data acquisition TCP server that implements
    a simple data acquisition protocol."""
    parameters_and_defaults = { 'daq_server_hostname' : 'localhost',
                                'daq_server_port' : 50003,
                                }
    def __init__(self,**cnf):
        apply(VisionEgg.Daq.DaqSetup.__init__,(self,),cnf)
        self.connection = DaqServerConnection(hostname=self.parameters.daq_server_hostname,
                                              port=self.parameters.daq_server_port,
                                              
                                              )

class DaqConnection(VisionEgg.ClassWithParameters):
    parameters_and_defaults = { 'hostname' : 'localhost',
                                'port' : 50003,
                                }

    # values for self.remote_state
    NOT_CONNECTED = 1
    COMMAND_PROMPT = 2

    # some constants
    CRLF = '\r\n'
    BUFSIZE = 4096

    # some more constants
    command_prompt = re.compile('^daqserv> ')
    ready_prompt = re.compile('^ready> ')
    begin_data_prompt = re.compile('^'+re.escape(
        'BEGIN HEX DATA (32 bit "short" big-endian signed int)'
        )+'$')
    end_data_prompt = re.compile('^'+re.escape(
        'END HEX DATA'
        )+'$')
    
    def __init__(self,**cnf):
        apply(VisionEgg.ClassWithParameters.__init__,(self,),cnf)
        
        self.remote_state = DaqConnection.NOT_CONNECTED

        # Connect to the server 
        self.socket = debug_socket(socket.AF_INET, socket.SOCK_STREAM)
        #self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        self.socket.connect((self.parameters.hostname,
                             self.parameters.port))
        self.buffer = ''
        
        # Wait until we get a command prompt
        while not DaqConnection.command_prompt.search(self.buffer):
            self.buffer = self.buffer + self.socket.recv(DaqConnection.BUFSIZE)
        # XXX prune everything up to the end of command_prompt from self.buffer
        
        self.remote_state = DaqConnection.COMMAND_PROMPT

        self.parameters.trigger.register_daq_setup(self)

    def sync(self):
        if self.remote_state != 'command prompt':
            raise RuntimeError("Must be in command prompt state!")
        
        # Set the gain
        self.socket.send('gain(%f)'%self.daq_params.parameters.gain + CRLF)

        # Get a command prompt
        data = self.socket.recv(BUFSIZE)
        if not self.command_prompt.search(data):
            raise RuntimeError("Got unexpected reply in DaqConnection: %s"%data)

        # Wait until we get a command prompt
        while not self.command_prompt.search(data):
            data = self.socket.recv(BUFSIZE)

        self.remote_state = 'command prompt'

    def go(self):
        if self.remote_state != 'command prompt':
            raise RuntimeError('DaqConnection.go() called when remote server not in command prompt state.')
        digitize_string = "digitize(%d,%f,%f,%d)"%(self.daq_params.parameters.num_channels,
                                                   self.daq_params.parameters.sample_freq_hz,
                                                   self.daq_params.parameters.duration_sec,
                                                   self.daq_params.parameters.trigger_mode)
        self.socket.send(digitize_string + CRLF)

        # I should go into non-blocking mode and wait
        # a timeout period before giving up and
        # returning an error
        data = self.socket.recv(BUFSIZE)
        if not self.ready_to_go_prompt.search(data):
            raise RuntimeError("Got unexpected reply when preparing to digitize in DaqConnection: %s"%data)
        
        self.remote_state = 'ready' # waiting for "go"

        ##################################################
        
        if self.remote_state != 'ready':
            raise RuntimeError('DaqOverTCP.go() called when remote server not in ready state.')
        self.socket.send('go' + CRLF)
        self.remote_state = 'acquiring'

        ##################################################

        print "parsing..."
        self.parse_data()

    def parse_data(self):
        if self.remote_state != 'acquiring':
            raise RuntimeError('DaqConnection.parse_data() called when remote server not in aquiring state.')

        # Parse data
        done = 0
        getting_waves = 0
        waves = []
        leftover_data = ""
        print "a"
        while not done:
            print "b"
            data = self.socket.recv(BUFSIZE)
            print "c"
            lines = string.split(data,CRLF)

            print "lines",lines

            # due to buffering not being lined up with lines:
            lines[0] = leftover_data + lines[0] # use last incomplete line
            leftover_data = lines.pop() # incomplete last line

            print "leftover_data",leftover_data

            # because the command prompt doesn't end with CRLF, check for it:
            if self.command_prompt.search(leftover_data):
                done = 1

            for line in lines:
                print line
                if line == "": # Nothing in this line, do the next
                    continue 
                if not getting_waves:
                    if self.begin_data.search(line):
                        print "START!"
                        getting_waves = 1
                    else:
                        raise ValueError("Unexpected string from daq server when parsing output: '%s'"%line)
                else: # getting_waves 
                    if self.end_data.search(line):
                        print "DONE!"
                        self.current_data_array = Numeric.array(waves)
                        waves = []
                        getting_waves = 0
                    else: # The data!
                        this_row = map(lambda hex: int(hex,16),string.split(line))
##                        samples = string.split(line)
##                        for sample in samples:
##                            this_row.append(int(sample))
                        print this_row
                        if len(this_row) > 0:
                            this_row = Numeric.array(this_row)
                            waves.append(this_row)
                            ## Could speed next line up with concatenate?
                            # (Also would have to save waves...)
                            self.current_data_array = Numeric.array(waves)
        print self.current_data_array
        self.remote_state = 'command prompt'

    def close_socket(self,command='exit'):
        if self.remote_state != "not connected":
            self.socket.send(command + CRLF)
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

###################### OLD CRAP ######################################33
    
    def __init__(self,host,port,channel_params_list,trigger_method):
        # Make sure all my arguments are acceptable
        self.sample_freq_hz = channel_params_list[0].sample_freq_hz
        self.duration_sec = channel_params_list[0].duration_sec
        self.gain = channel_params_list[0].gain
        channel_numbers = []
        for channel_params in channel_params_list:
            channel_numbers.append(channel_params.channel_number)
            if channel_params.sample_freq_hz != self.sample_freq_hz or channel_params.duration_sec != self.duration_sec or channel_params.gain != self.gain:
                raise EggError("Each channel passed to DaqOverTCP must have the same parameters.")
        channel_numbers.sort()
        for i in range(len(channel_numbers)):
            if i != channel_numbers[i]:
                raise EggError("DaqOverTCP only records from contiguous channels starting with 0.")
        self.num_channels = len(channel_numbers)
        Daq.__init__(self,channel_params_list,trigger_method)

        # TCP server prompts
        self.command_prompt = re.compile('^daqserv> ')
        self.ready_to_go_prompt = re.compile('^ready> ')
        self.begin_data = re.compile('^BEGIN TEXT WAVES$')
        self.end_data = re.compile('^END TEXT WAVES$')
        
        # Connect to the server 
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((host,port))
        data = self.socket.recv(BUFSIZE)

        # Wait until we get a command prompt
        while not self.command_prompt.search(data):
            data = self.socket.recv(BUFSIZE)

        # Set the gain
        self.socket.send('gain(%f)'%self.gain + CRLF)

        # Get a command prompt
        data = self.socket.recv(BUFSIZE)
        if not self.command_prompt.search(data):
            raise EggError("Got unexpected reply trying to set gain in DaqOverTCP: %s"%data)

        self.remote_state = 'command prompt'

    def __del__(self):
        # close socket connection nicely if possible
        try:
            self.socket.send('exit' +  CRLF)
            data = self.socket.recv(BUFSIZE) # clear the input buffer
        except:
            pass
    
    def prepare_to_go(self):
        if hasattr(self,'current_data_array'):
            del self.current_data_array # it's no longer current!
        if self.remote_state != 'command prompt':
            raise EggError('DaqOverTCP.prepare_to_go() called when remote server not in command prompt state.')
        if isinstance(self.trigger_method,NoTrigger):
            trigger_mode = 0
        elif isinstance(self.trigger_method,TriggerLowToHigh):
            trigger_mode = 1
        elif isinstance(self.trigger_method,TriggerHighToLow):
            trigger_mode = 2
        digitize_string = "digitize(%d,%f,%f,%d)"%(self.num_channels,
                                                   self.sample_freq_hz,
                                                   self.duration_sec,
                                                   trigger_mode)
        self.socket.send(digitize_string + CRLF)

        # I should go into non-blocking mode and wait
        # a timeout period before giving up and
        # returning an error
        data = self.socket.recv(BUFSIZE)
        if not self.ready_to_go_prompt.search(data):
            lines = string.split(data,CRLF)
            for line in lines:
                print line
            raise EggError("Got unexpected reply when preparing to digitize in DaqOverTCP: %s"%data)
        self.remote_state = 'ready' # waiting for "go"

    def go(self):
        if self.remote_state != 'ready':
            raise EggError('DaqOverTCP.go() called when remote server not in ready state.')
        self.socket.send('go' + CRLF)
        self.remote_state = 'acquiring'

    def get_data(self,channel_params):
        # Check to see if we've already parsed this data
        if not hasattr(self,'current_data_array'):
            self.parse_data()
        if not isinstance(channel_params,ChannelParams):
            raise TypeError()
        return self.current_data_array[:,channel_params.channel_number]

    def parse_data(self):
        if self.remote_state != 'acquiring':
            raise EggError('DaqOverTCP.parse_data() called when remote server not in aquiring state.')

        # Parse data
        done = 0
        getting_waves = 0
        waves = []
        leftover_data = ""
        while not done:
            data = self.socket.recv(BUFSIZE)
            lines = string.split(data,CRLF)

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
                    if self.begin_data.search(line):
                        getting_waves = 1
                    elif self.command_prompt.search(line): # Never the case, because the command prompt doesn't end with CRLF
                        done = 1
                    else:
                        raise EggError("Unexpected string from daq server when parsing output: '%s'"%line)
                else: # getting_waves 
                    if self.end_data.search(line):
                        self.current_data_array = Numeric.array(waves)
                        waves = []
                        getting_waves = 0
                    else: # The data!
                        this_row = []
                        samples = string.split(line)
                        for sample in samples:
                            this_row.append(int(sample))
                        if len(this_row) > 0:
                            this_row = Numeric.array(this_row)
                            waves.append(this_row)
                            self.current_data_array = Numeric.array(waves)
                     
        self.remote_state = 'command prompt'
    
    
