"""Allows control of parameter values over the network.

This code has not been optimized for speed, and I think it is unwise
to attempt to change the value of controllers in realtime.  In other
words, do not design an experiment where, on a remote computer, you
have determined that a certain amount of time has passed, and you
require a certain new controller value NOW.  In this case, it would be
better to use parameter=eval_str() with an if statement involving time.

The following are examples of how to change the controller for "name".

name=const(1.0,0.0,Types.Floattype,Time_sec_absolute,Every_frame)
name=eval_str("t*360.0","0.0",types.FloatType,TIME_SEC_ABSOLUTE,EVERY_FRAME)
"""

# Copyright (c) 2002 Andrew Straw.  Distributed under the terms
# of the GNU Lesser General Public License (LGPL).

import VisionEgg
import VisionEgg.Core
import socket, select, re, string, types
import Numeric, math # for eval

try:
    import Tkinter
except:
    pass

__version__ = VisionEgg.release_name
__cvs__ = string.split('$Revision$')[1]
__date__ = string.join(string.split('$Date$')[1:3], ' ')
__author__ = 'Andrew Straw <astraw@users.sourceforge.net>'

class TCPServer:
    def __init__(self,
                 hostname="localhost",
                 port=7834,
                 single_socket_but_reconnect_ok=0,
                 dialog_ok=1):
        server_address = (hostname,port)
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.bind(server_address)
        self.single_socket_but_reconnect_ok = single_socket_but_reconnect_ok
        self.dialog_ok = dialog_ok
        if not hasattr(globals(),"Tkinter"):
            self.dialog_ok = 0
        
    def create_listener_once_connected(self):
        VisionEgg.Core.message.add(
            """Awaiting connection to TCP Server at %s"""%(self.server_socket.getsockname(),),
            level=VisionEgg.Core.Message.INFO)
        self.server_socket.listen(1)
        if self.dialog_ok:
            # Make a Tkinter dialog box
            class WaitingDialog(Tkinter.Frame):
                def __init__(self,server_socket=None,**kw):
                    if 'borderwidth' not in kw.keys():
                        kw['borderwidth'] = 20
                    apply(Tkinter.Frame.__init__,(self,),kw)
                    self.winfo_toplevel().title('Vision Egg TCP Server')
                    self.server_socket = server_socket
                    Tkinter.Label(self,text=
                                  """Awaiting connection to TCP Server at %s"""%(self.server_socket.getsockname(),),).pack()
                    self.winfo_toplevel().protocol("WM_DELETE_WINDOW", self.stop_listening)
                    self.server_socket.setblocking(0)
                    self.after(1,self.idle_func)
                def stop_listening(self,dummy=None):
                    raise SystemExit
                def idle_func(self):
                    try:
                        # This line raises an exception unless there's an incoming connection
                        self.accepted = self.server_socket.accept()
                        self.quit()
                    except socket.error, x:
                        self.after(1,self.idle_func)
            dialog = WaitingDialog(server_socket = self.server_socket)
            dialog.pack()
            dialog.mainloop()
            client, client_address = dialog.accepted
            dialog.winfo_toplevel().destroy()
        else:
            client, client_address = self.server_socket.accept()
        if self.single_socket_but_reconnect_ok:
            return SocketListenController(client,
                                          disconnect_ok = 1,
                                          server_socket = self.server_socket)
        else:
            return SocketListenController(client)

class SocketListenController(VisionEgg.Core.Controller):
    re_line = re.compile(r"(?:^(.*)\n)+",re.MULTILINE)
    re_const = re.compile(r'const\(\s?(.*)\s?(?:,\s?(.*)\s?(?:,\s?(.*)\s?(?:\,\s?(.*)\s?(?:,\s?(.*)\s?)?)?)?)?\)',re.MULTILINE)
    re_eval_str = re.compile(r'eval_str\(\s?"(.*)"\s?(?:,\s?"(.*)"\s?(?:,\s?(.*)\s?(?:\,\s?(.*)\s?(?:,\s?(.*)\s?)?)?)?)?\)',re.MULTILINE)
    def __init__(self,
                 socket,
                 disconnect_ok = 0,
                 server_socket = None, # Only needed if reconnecting ok
                 temporal_variable_type = VisionEgg.Core.Controller.TIME_SEC_ABSOLUTE,
                 eval_frequency = VisionEgg.Core.Controller.EVERY_FRAME):
        VisionEgg.Core.Controller.__init__(self,
                                           return_type = types.NoneType,
                                           temporal_variable_type = temporal_variable_type,
                                           eval_frequency = eval_frequency)
        self.socket = socket
        self.disconnect_ok = disconnect_ok
        if self.disconnect_ok and server_socket is None:
            # Warning -- no ability to accept further incoming sockets...
            pass
        self.server_socket = server_socket
        
        VisionEgg.Core.message.add(
            "Handling connection from %s"%(self.socket.getsockname(),),
            level=VisionEgg.Core.Message.INFO)
        
        self.socket.setblocking(0) # don't block on this socket
        
        self.socket.send("Hello. This is %s version %s.\n"%(self.__class__,__version__))
        self.socket.send("Begin sending commands now.\n")

        self.buffer = ""

        self.last_command = {}

        self.names = {} # ( controller, name_re, parser, require_type )

    def send_raw_text(self,text):
        self.socket.send(text)

    def __check_socket(self):
        if self.socket is not None: # Normal, connected behavior
            # First, update the buffer
            ready_to_read, temp, temp2 = select.select([self.socket],[],[],0)
            new_info = 0
            while len(ready_to_read):
                new = self.socket.recv(1024)
                if len(new) == 0:
                    # Disconnected
                    self.socket = None # close socket
                    if not self.disconnect_ok:
                        raise RuntimeError("Socket disconnected!")
                    else:
                        if self.server_socket is not None:
                            self.server_socket.setblocking(0)
                    return # don't do any more
                #assert(ready_to_read[0] == self.socket)
                self.buffer = self.buffer + new
                new_info = 1
                ready_to_read, temp, temp2 = select.select([self.socket],[],[],0)

            # Second, convert the buffer to command_queue entries
            if new_info:
                # Handle variations on newlines:
                self.buffer = string.replace(self.buffer,chr(0x0D),"") # no CR
                self.buffer = string.replace(self.buffer,chr(0x0A),"\n") # LF = newline
                # Handle each line for which we have a tcp_name
                for tcp_name in self.names.keys():
                    (controller, name_re_str, parser, require_type) = self.names[tcp_name]
                    # If the following line makes a match, it
                    # sticks the result in self.last_command[tcp_name].
                    self.buffer = name_re_str.sub(parser,self.buffer)
                    # Now act based on the command parsed
                    command = self.last_command[tcp_name]
                    if command is not None:
                        self.__do_command(tcp_name,command,require_type)
                        self.last_command[tcp_name] = None
                # Clear any complete lines for which we don't have a tcp_name
                self.buffer = SocketListenController.re_line.sub(self.__unknown_line,self.buffer)
        elif self.server_socket is not None:
            # Not connected on self.socket, check self.server_socket for new connection
            try:
                # This line raises an exception unless there's an incoming connection (if server is not blocking, which it shouldn't be)
                (client, client_address) = self.server_socket.accept()
                self.socket = client
                self.socket.send("Hello. This is %s version %s.\n"%(self.__class__,__version__))
                self.socket.send("Begin sending commands now.\n")
                for tcp_name in self.names.keys():
                    (controller, name_re_str, parser, require_type) = self.names[tcp_name]
                    self.socket.send('"%s" controllable with this connection.\n'%tcp_name)
            except socket.error, x:
                pass
                        
    def __unknown_line(self,match):
        for str in match.groups():
            if str=="quit":
                raise SystemExit
            elif str=="close" or str=="exit":
                self.socket = None # close socket
                if not self.disconnect_ok:
                    raise RuntimeError("Socket disconnected!")
                else:
                    if self.server_socket is not None:
                        self.server_socket.setblocking(0)
                return ""
            self.socket.send("Error with line: "+str+"\n")
            VisionEgg.Core.message.add("Error with line: "+str+"\n",
                                       level=VisionEgg.Core.Message.INFO)
        return ""

    def create_tcp_controller(self,
                              tcp_name=None,
                              initial_controller=None,
                              require_type=None):
        class Parser:
            def __init__(self,tcp_name,most_recent_command):
                self.tcp_name = tcp_name
                self.most_recent_command = most_recent_command

            def parse_func(self,match):
                # Could make this into a lambda function
                self.most_recent_command[self.tcp_name] = match.groups()[-1]
                return ""
        if tcp_name is None:
            raise ValueError("Must specify tcp_name")
        if tcp_name in self.names.keys():
            raise ValueError('tcp_name "%s" already in use.'%tcp_name)
        if string.count(tcp_name,' '):
            raise ValueError('tcp_name "%s" cannot have spaces.'%tcp_name)
        if tcp_name == "quit":
            raise ValueError('tcp_name "%s" conflicts with reserved word.'%tcp_name)
        if initial_controller is None:
            # create default controller
            initial_controller = VisionEgg.Core.ConstantController(
                during_go_value=1.0,
                between_go_value=0.0)
        else:
            if not isinstance(initial_controller,VisionEgg.Core.Controller):
                raise ValueError('initial_controller not an instance of VisionEgg.Core.Controller')
        if require_type is None:
            require_type = initial_controller.returns_type()
        # Create initial None value for self.last_command dict
        self.last_command[tcp_name] = None
        # Create values for self.names dict tuple ( controller, name_re, most_recent_command, parser )
        controller = TCPController(
            tcp_name=tcp_name,
            contained_controller=initial_controller
            )
        name_re_str = re.compile(r"^"+tcp_name+r"\s*=\s*(.*)\s*$",re.MULTILINE)
        parser = Parser(tcp_name,self.last_command).parse_func
        self.names[tcp_name] = (controller, name_re_str, parser, require_type)
        self.socket.send('"%s" controllable with this connection.\n'%tcp_name)
        return controller
    
    def __do_command(self,tcp_name,command,require_type):
        new_contained_controller = None
        match = SocketListenController.re_const.match(command)
        if match is not None:
            try:
                match_groups = match.groups()
                kw_args = {}
                kw_args['during_go_value'] = eval(match_groups[0])
                if match_groups[1] is not None:
                    kw_args['during_go_value'] = eval(match_groups[1])
                if match_groups[2] is not None:
                    kw_args['return_type'] = eval(match_groups[2])
                if match_groups[3] is not None:
                    kw_args['temporal_variable_type'] = eval("VisionEgg.Core.Controller.%s"%match_groups[3])
                if match_groups[4] is not None:
                    kw_args['eval_frequency'] = eval("VisionEgg.Core.Controller.%s"%match_groups[4])
                new_contained_controller = apply(VisionEgg.Core.ConstantController,[],kw_args)
                new_type = new_contained_controller.returns_type()
                if new_type != require_type:
                    if not issubclass( new_type, require_type):
                        new_contained_controller = None
                        raise TypeError("New controller returned type %s, but should return type %s"%(new_type,require_type))
            except Exception, x:
                self.socket.send("Error parsing const for %s: %s\n"%(tcp_name,x))
                VisionEgg.Core.message.add("Error parsing const for %s: %s\n"%(tcp_name,x),
                                           level=VisionEgg.Core.Message.INFO)
        else:
            match = SocketListenController.re_eval_str.match(command)
            if match is not None:
                try:
                    match_groups = match.groups()
                    kw_args = {}
                    kw_args['during_go_eval_string'] = match_groups[0]
                    if match_groups[1] is not None:
                        kw_args['between_go_eval_string'] = match_groups[1]
                    if match_groups[2] is not None:
                        kw_args['return_type'] = eval(match_groups[2])
                    if match_groups[3] is not None:
                        kw_args['temporal_variable_type'] = eval("VisionEgg.Core.Controller.%s"%match_groups[3])
                    if match_groups[4] is not None:
                        kw_args['eval_frequency'] = eval("VisionEgg.Core.Controller.%s"%match_groups[4])
                    new_contained_controller = apply(VisionEgg.Core.EvalStringController,[],kw_args)
                    new_type = new_contained_controller.returns_type()
                    if new_type != require_type:
                        if not issubclass( new_type, require_type):
                            new_contained_controller = None
                            raise TypeError("New controller returned type %s, but should return type %s"%(new_type,require_type))
                except Exception, x:
                    self.socket.send("Error parsing eval_str for %s: %s\n"%(tcp_name,x))
                    VisionEgg.Core.message.add("Error parsing eval_str for %s: %s\n"%(tcp_name,x),
                                               level=VisionEgg.Core.Message.INFO)
            else:
                self.socket.send("Error parsing command for %s: %s\n"%(tcp_name,command))
                VisionEgg.Core.message.add("Error parsing command for %s: %s\n"%(tcp_name,command),
                                           level=VisionEgg.Core.Message.INFO)
        # create controller based on last command_queue
        if new_contained_controller is not None:
            (controller, name_re_str, parser, require_type) = self.names[tcp_name]
            controller.set_value(new_contained_controller)

    def during_go_eval(self):
        self.__check_socket()
        return None

    def between_go_eval(self):
        self.__check_socket()
        return None   

class TCPController(VisionEgg.Core.Controller):
    """Control a parameter from a network (TCP) connection.

    SocketListenController"""
    # Contains another controller...
    def __init__(self, tcp_name, contained_controller):
        self.tcp_name = tcp_name
        self.contained_controller = contained_controller
        self.__sync_mimic()

    def set_value(self,new_contained_controller):
        self.contained_controller = new_contained_controller
        self.__sync_mimic()

    def __sync_mimic(self):
        self.return_type = self.contained_controller.return_type
        self.temporal_variable = self.contained_controller.temporal_variable
        self.temporal_variable_type = self.contained_controller.temporal_variable_type
        self.eval_frequency = self.contained_controller.eval_frequency
        
    def during_go_eval(self):
        self.contained_controller.temporal_variable = self.temporal_variable
        return self.contained_controller.during_go_eval()

    def between_go_eval(self):
        self.contained_controller.temporal_variable = self.temporal_variable
        return self.contained_controller.between_go_eval()
