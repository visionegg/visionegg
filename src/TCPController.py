"""VisionEgg TCPController module

The following are examples of how to change the controller for "name".

name=const(1.0,0.0,Types.Floattype,Time_sec_absolute,Every_frame)
name=eval_str("t*5.0*360.0","0.0",types.FloatType,TIME_SEC_ABSOLUTE,EVERY_FRAME)
"""

# Copyright (c) 2002 Andrew Straw.  Distributed under the terms
# of the GNU Lesser General Public License (LGPL).

import VisionEgg
import VisionEgg.Core
import socket, select, re, string
import types

__version__ = VisionEgg.release_name
__cvs__ = string.split('$Revision$')[1]
__date__ = string.join(string.split('$Date$')[1:3], ' ')
__author__ = 'Andrew Straw <astraw@users.sourceforge.net>'

names = {}

class Parser:
    def __init__(self,tcp_name,most_recent_command):
        self.tcp_name = tcp_name
        self.most_recent_command = most_recent_command

    def parse_func(self,match):
        self.most_recent_command[self.tcp_name] = match.groups()[-1]
        return ""

class Handler:
    re_line = re.compile(r"(?:^(.*)\n)+",re.MULTILINE)
    re_const = re.compile(r'const\(\s?(.*)\s?,\s?(.*)\s?,\s?(.*)\s?\,\s?(.*)\s?,\s?(.*)\s?\)',re.MULTILINE)
    re_eval_str = re.compile(r'eval_str\(\s?"(.*)"\s?,\s?"(.*)"\s?,\s?(.*)\s?\,\s?(.*)\s?,\s?(.*)\s?\)',re.MULTILINE)
    def __init__(self,request,client_address):
        self.request = request
        self.client_address = client_address
        
        VisionEgg.Core.message.add(
            "Handling connection from %s"%(self.client_address,),
            level=VisionEgg.Core.Message.INFO)
        
        self.request.setblocking(0) # don't block on this socket
        
        self.request.send("Hello. This is the Vision Egg TCPServer version '%s'.\n"%__version__)
        self.request.send("The following names may be controlled:\n")
        self.request.send("--------------------------------------\n")
        for tcp_name in names.keys():
            self.request.send(tcp_name+"\n")
            names[tcp_name].register_handler(self)
        self.request.send("--------------------------------------\n")
        self.request.send("Begin sending commands now.\n")

        self.most_recent_command = {}
        self.buffer = ""

        self.match_names = {}
        self.parse_for = {}

    def prepare_for(self,tcp_name):
        self.match_names[tcp_name] = re.compile(r"^"+tcp_name+r"\s*=\s*(.*)\s*$",re.MULTILINE)
        self.most_recent_command[tcp_name] = None
        self.parse_for[tcp_name] = Parser(tcp_name,self.most_recent_command).parse_func
        
    def check_input(self):
        # First, update the buffer
        ready_to_read, temp, temp2 = select.select([self.request],[],[],0)
        new_info = 0
        while len(ready_to_read):
            #assert(ready_to_read[0] == self.request)
            self.buffer = self.buffer + self.request.recv(1024)
            new_info = 1
            ready_to_read, temp, temp2 = select.select([self.request],[],[],0)
            
        # Second, convert the buffer to command_queue entries
        if new_info:
            # Handle variations on newlines:
            self.buffer = string.replace(self.buffer,chr(0x0D),"") # no CR
            self.buffer = string.replace(self.buffer,chr(0x0A),"\n") # LF = newline
            # Handle each line for which we have a tcp_name
            for tcp_name in self.match_names.keys():
                # If the following line makes a match, it
                # sticks the result in self.most_recent_command[tcp_name].
                self.buffer = self.match_names[tcp_name].sub(self.parse_for[tcp_name],self.buffer)
            # Clear any complete lines for which we don't have a tcp_name
            self.buffer = Handler.re_line.sub(self.unknown_line,self.buffer)
            
    def unknown_line(self,match):
        for str in match.groups():
            self.request.send("Error with line: "+str+"\n")
        return ""

    def create_new_controller_if_needed_for(self,tcp_name):
        return_value = None
        if tcp_name not in self.match_names.keys():
            self.prepare_for(tcp_name)
        self.check_input()
        params = self.most_recent_command[tcp_name]
        if params is not None:
            match = Handler.re_const.match(params)
            if match is not None:
                try:
                    go_val = eval(match.group(1))
                    #print "go_str",go_str
                    not_go_val = eval(match.group(2))
                    namespace = {'types':types}
                    return_type = eval(match.group(3),namespace)
                    temporal_variable_type = eval("VisionEgg.Core.Controller.%s"%match.group(4))
                    eval_frequency = eval("VisionEgg.Core.Controller.%s"%match.group(5))
                    #eval_frequency = VisionEgg.Core.Controller.EVERY_FRAME
                    #temporal_variable_type = VisionEgg.Core.Controller.TIME_SEC_ABSOLUTE
                    return_value = VisionEgg.Core.ConstantController(
                        during_go_value = go_val,
                        between_go_value = not_go_val,
                        return_type = return_type,
                        temporal_variable_type = temporal_variable_type,
                        eval_frequency = eval_frequency)
                except Exception, x:
                    self.request.send("Error parsing eval_str for %s: %s\n"%(tcp_name,x))
            else:
                match = Handler.re_eval_str.match(params)
                if match is not None:
                    try:
                        go_str = match.group(1)
                        #print "go_str",go_str
                        not_go_str = match.group(2)
                        namespace = {'types':types}
                        return_type = eval(match.group(3),namespace)
                        temporal_variable_type = eval("VisionEgg.Core.Controller.%s"%match.group(4))
                        eval_frequency = eval("VisionEgg.Core.Controller.%s"%match.group(5))
                        #eval_frequency = VisionEgg.Core.Controller.EVERY_FRAME
                        #temporal_variable_type = VisionEgg.Core.Controller.TIME_SEC_ABSOLUTE
                        return_value = VisionEgg.Core.EvalStringController(
                            during_go_eval_string = go_str,
                            between_go_eval_string = not_go_str,
                            return_type = return_type,
                            temporal_variable_type = temporal_variable_type,
                            eval_frequency = eval_frequency)
                    except Exception, x:
                        self.request.send("Error parsing eval_str for %s: %s\n"%(tcp_name,x))
                else:
                    self.request.send("Error parsing command for %s: %s\n"%(tcp_name,params))
            self.most_recent_command[tcp_name] = None
        # create controller based on last command_queue
        return return_value
        
class TCPServer:
    def __init__(self,
                 hostname="localhost",
                 port=7834):
        server_address = (hostname,port)
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.bind(server_address)

    def wait_for_one_connection(self):
        VisionEgg.Core.message.add(
            """Awaiting connection to TCPServer at %s"""%(self.socket.getsockname(),),
            level=VisionEgg.Core.Message.INFO)
        self.socket.listen(1)
        client, client_address = self.socket.accept()
        self.handler = Handler(client,client_address)

    def create_tcp_controller(self,
                              tcp_name=None,
                              initial_controller=None):
        if tcp_name is None:
            raise ValueError("Must specify tcp_name")
        if tcp_name in names.keys():
            raise ValueError('tcp_name "%s" already in use.'%tcp_name)
        if initial_controller is None:
            # create default controller
            initial_controller = VisionEgg.Core.ConstantController(
                during_go_value=1.0,
                between_go_value=0.0)
        else:
            if not isinstance(initial_controller,VisionEgg.Core.Controller):
                raise ValueError('initial_controller not an instance of VisionEgg.Core.Controller')
        names[tcp_name] = TCPController(
            tcp_name=tcp_name,
            contained_controller=initial_controller
            )
        return names[tcp_name]

class TCPController(VisionEgg.Core.Controller):
    # Contains another controller...
    def __init__(self, tcp_name, contained_controller):
        self.tcp_name = tcp_name
        self.contained_controller = contained_controller
        self.handler = None
        self.sync_mimic()

    def register_handler(self,handler):
        self.handler = handler

    def sync_mimic(self):
        self.return_type = self.contained_controller.return_type
        self.temporal_variable = self.contained_controller.temporal_variable
        self.temporal_variable_type = self.contained_controller.temporal_variable_type
        self.eval_frequency = self.contained_controller.eval_frequency
        
    def check_socket(self):
        if self.handler is not None:
            new_contained_controller = self.handler.create_new_controller_if_needed_for(self.tcp_name)
            if new_contained_controller is not None:
                self.contained_controller = new_contained_controller
                self.sync_mimic()

    def during_go_eval(self):
        self.check_socket()
        self.contained_controller.temporal_variable = self.temporal_variable
        # XXX HACK to fix:
        if self.contained_controller.temporal_variable is None:
            self.contained_controller.temporal_variable = 0.0
        return self.contained_controller.during_go_eval()

    def between_go_eval(self):
        self.check_socket()
        self.contained_controller.temporal_variable = self.temporal_variable
        return self.contained_controller.between_go_eval()
