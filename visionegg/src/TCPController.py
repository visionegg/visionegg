"""VisionEgg TCPController module
"""

# Copyright (c) 2001-2002 Andrew Straw.  Distributed under the terms
# of the GNU Lesser General Public License (LGPL).

import VisionEgg
import VisionEgg.Core
import socket, select, re, string

__version__ = VisionEgg.release_name
__cvs__ = string.split('$Revision$')[1]
__date__ = string.join(string.split('$Date$')[1:3], ' ')
__author__ = 'Andrew Straw <astraw@users.sourceforge.net>'

names = {}

class Handler:
    # TODO: fix code to not need re_eol (module re already does good multiline stuff)
    re_eol = re.compile(r"(.*)[\n]+(.*)")
    re_eval = re.compile(r'eval_str\(\s?"(.*)"\s?,\s?"(.*)"\s?,\s?(.*)\s?\)')
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

    def prepare_for(self,tcp_name):
        self.match_names[tcp_name] = re.compile("%s\((.*)\)"%tcp_name)
        self.most_recent_command[tcp_name] = None
        
    def check_input(self):
        # First, update the buffer
        ready_to_read, temp, temp2 = select.select([self.request],[],[],0)
        new_info = 0
        if len(ready_to_read):
            #assert(ready_to_read[0] == self.request)
            self.buffer = self.buffer + self.request.recv(1024)
            new_info = 1
            
        # Second, convert the buffer to command_queue entries
        if new_info:
            match = Handler.re_eol.match(self.buffer)

            if match is not None:
                self.buffer = match.group(2)
                this_command = match.group(1)

                #print "this_command",this_command
                for name in self.match_names.keys():
                    match = self.match_names[name].match(this_command)
                    if match is not None:
                        self.most_recent_command[name] = match.group(1)
                        #print "self.most_recent_command[name]",self.most_recent_command[name]
                        break # No need to keep going through list

    def create_new_controller_if_needed_for(self,tcp_name):
        return_value = None
        if tcp_name not in self.match_names.keys():
            self.prepare_for(tcp_name)
        self.check_input()
        params = self.most_recent_command[tcp_name]
        if params is not None:
            match = Handler.re_eval.match(params)
            if match is not None:
                go_str = match.group(1)
                #print "go_str",go_str
                not_go_str = match.group(2)
                return_type = match.group(3)
                return_type = eval("type(%s)"%match.group(3))
                #eval_frequency = match.group(4)
                eval_frequency = VisionEgg.Core.Controller.EVERY_FRAME
                temporal_variable_type = VisionEgg.Core.Controller.TIME_SEC_ABSOLUTE
                return_value = VisionEgg.Core.EvalStringController(
                    during_go_eval_string = go_str,
                    between_go_eval_string = not_go_str,
                    return_type = return_type,
                    temporal_variable_type = temporal_variable_type,
                    eval_frequency = eval_frequency)
            else:
                print " unknown command"
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
