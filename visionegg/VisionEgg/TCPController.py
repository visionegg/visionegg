# The Vision Egg: TCPController
#
# Copyright (C) 2001-2003 Andrew Straw.
# Author: Andrew Straw <astraw@users.sourceforge.net>
# URL: <http://www.visionegg.org/>
#
# Distributed under the terms of the GNU Lesser General Public License
# (LGPL). See LICENSE.TXT that came with this file.
#
# $Id$

"""
Allows control of parameter values over the network.

Don't use for realtime control unless you think your network is that
fast and reliable. Also, this code has not been optimized for speed,
and I think it is unwise to attempt to change the value of controllers
in realtime.  In other words, do not design an experiment where, on a
remote computer, you have determined that a certain amount of time has
passed, and you require a certain new controller value NOW.  In this
case, it would be better to use parameter=eval_str() with an if
statement involving time.

To control parameters over a network, start a server with an instance
of TCPServer.  The server spawns an instance of SocketListenController
for each connected socket.  (Most commonly you will only want
connection over a single socket.)  The instance of
SocketListenController handles all communication for that connection
and serves as a container and (meta) controller for instances of
TCPController.

This module contains ABSOLUTELY NO SECURITY FEATURES, and could easily
allow arbitrary execution of code on your computer. For this reason,
if you use this module, I recommend operating behind a firewall. This
could be an inexpensive "routing switch" used for cable modems, which
would provide the added benefit that your local network would be
isolated.  This would elimate all traffic not to or from computers on
the switch and therefore reduce/eliminate packet collisions, decrease
latency, and providing a network performance and reliability. To
address security concerns, you could also write code that implements
IP address checking or other security features.

"""

import VisionEgg
import VisionEgg.Core
import VisionEgg.FlowControl
import VisionEgg.ParameterTypes as ve_types
import socket, select, re, string, types
import numpy.oldnumeric as Numeric, math # for eval

try:
    import Tkinter
except:
    pass

import logging

__version__ = VisionEgg.release_name
__cvs__ = '$Revision$'.split()[1]
__date__ = ' '.join('$Date$'.split()[1:3])
__author__ = 'Andrew Straw <astraw@users.sourceforge.net>'

class TCPServer:
    """TCP server creates SocketListenController upon connection.

    This class is analagous to VisionEgg.PyroHelpers.PyroServer.

    """
    def __init__(self,
                 hostname="",
                 port=7834,
                 single_socket_but_reconnect_ok=0,
                 dialog_ok=1,
                 confirm_address_with_gui=1):
        """Bind to hostname and port, but don't listen yet.

        """
        server_address = (socket.getfqdn(hostname),port)
        self.dialog_ok = dialog_ok
        self.single_socket_but_reconnect_ok = single_socket_but_reconnect_ok
        self.buffer = ""
        self.server_socket=None
        if not globals().has_key("Tkinter") or (VisionEgg.config.VISIONEGG_TKINTER_OK==0):
            self.dialog_ok = 0

        class GetServerAddressWindow(Tkinter.Frame):
            def __init__(self,server_address,**kw):
                try:
                    Tkinter.Frame.__init__(self,**kw)
                except AttributeError,x:
                    tk=Tkinter.Tk() # restart Tk and see if that helps
                    Tkinter.Frame.__init__(self,tk,**kw)
                self.winfo_toplevel().title("Vision Egg: TCP Server get address")
                self.server_address = server_address
                hostname,port = self.server_address
                self.clicked_ok = 0
                self.hostname = Tkinter.StringVar()
                self.hostname.set(hostname)
                self.port = Tkinter.StringVar()
                self.port.set(port)
                row = 0
                Tkinter.Label(self,
                              text="Please enter the hostname and port you would like to listen for connections on.",
                              ).grid(row=row,columnspan=2)
                row += 1
                Tkinter.Label(self,
                              text="Hostname (blank means localhost):",
                              ).grid(row=row,column=0,sticky=Tkinter.E)
                Tkinter.Entry(self,textvariable=self.hostname).grid(row=row,column=1,sticky=Tkinter.W+Tkinter.E,padx=10)
                row += 1
                Tkinter.Label(self,
                              text="Port:",
                              ).grid(row=row,column=0,sticky=Tkinter.E)
                Tkinter.Entry(self,textvariable=self.port).grid(row=row,column=1,sticky=Tkinter.W+Tkinter.E,padx=10)
                row += 1
                b = Tkinter.Button(self,
                                   text="Bind port and listen for connections",
                                   command=self.click_ok)
                b.grid(row=row,columnspan=2)
                b.focus_force()
                b.bind('<Return>',self.click_ok)
            def click_ok(self,dummy_arg=None):
                hostname = self.hostname.get()
                try:
                    port = int(self.port.get())
                except:
                    port = self.port.get()
                self.server_address = (hostname,port)
                self.clicked_ok = 1
                self.winfo_toplevel().destroy()

        bound = 0
        if not bound:
#        while not bound: # don't loop until the code is cleaner
            if confirm_address_with_gui and self.dialog_ok:
                window = GetServerAddressWindow(server_address)
                window.pack()
                window.mainloop()
                if not window.clicked_ok:
                    return # User wants to quit
                server_address = window.server_address
            self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.server_socket.bind(server_address)
            bound = 1

    def create_listener_once_connected(self,eval_frequency=None):
        """Wait for connection and spawn instance of SocketListenController."""
        if eval_frequency is None:
            # Don't listen to socket during go loop -- especially don't want to skip frames then
            eval_frequency = VisionEgg.FlowControl.Controller.EVERY_FRAME | VisionEgg.FlowControl.Controller.NOT_DURING_GO
        host,port = self.server_socket.getsockname()
        fqdn = socket.getfqdn(host)
        logger = logging.getLogger('VisionEgg.TCPController')
        logger.info("Awaiting connection to TCP Server at '%s', port %d"%(fqdn,port))
        self.server_socket.listen(1)
        if self.dialog_ok:
            # Make a Tkinter dialog box
            class WaitingDialog(Tkinter.Frame):
                def __init__(self,server_socket=None,**kw):
                    Tkinter.Frame.__init__(self,**kw)
                    self.winfo_toplevel().title('Vision Egg TCP Server')
                    self.server_socket = server_socket
                    host,port = self.server_socket.getsockname()
                    fqdn = socket.getfqdn(host)
                    spacer = Tkinter.Frame(self,borderwidth=30)
                    spacer.pack()
                    Tkinter.Label(spacer,text=
                                  """Awaiting connection to TCP Server at "%s", port %d"""%(fqdn,port)
                                  ).pack()
                    b = Tkinter.Button(self,text="Cancel",command=self.stop_listening)
                    b.pack(side=Tkinter.BOTTOM)
                    b.focus_force()
                    b.bind('<Return>',self.stop_listening)
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

class SocketListenController(VisionEgg.FlowControl.Controller):
    r"""Handle connection from remote machine, control TCPControllers.

    This meta controller handles a TCP socket to control zero to many
    instances of TCPController.  As a subclass of Controller, it gets
    called at specified moments in time via the Presentation
    class. When called in this way, it checks for any strings from the
    TCP socket.  It parses this information into a command or fails
    and sends an error.

    This class is analagous to VisionEgg.PyroHelpers.PyroListenController.

    TCP commands (sent over network socket)
    =======================================

    close -- close the connection
    exit -- close the connection
    quit -- quit the server program
    help -- print help message
    <name> -- show the value of the controller of <name>
    <name>=const(<args>) -- assign a new ConstantController to <name>
    <name>=eval_str(<args>) -- assign a new EvalStringController to <name>
    <name>=exec_str(<args>) -- assign a new ExecStringController to <name>
    <name>=exec_str(*<args>) -- assign a new unrestricted namespace ExecStringController to <name>

    TCP commands are always on a single line.  (Newlines in string
    literals can be specified by using "\n" without the quotes.)

    The assignment commands share common behavior:

    <name> -- value passed as argument "tcp_name" to method create_tcp_controller
    <args> -- during_go [, between_go [, eval_frequency [, temporal_variables [, return_type ]]]]

    The <args> string is parsed by the Python's eval() function.  If
    you don't want to explicitly set an argument early in the argument
    list, but you need to set one late in the list, use "None".  If
    not set, the optional arguments default to:

    eval_frequency = EVERY_FRAME
    temporal_variables = TIME_SEC_SINCE_GO
    return_type = (evaluates during_go function to find)
    between_go = (see below, depends on assignment type)

    The only difference between the assignment commands are in the
    first two arguments.  For "const(...)", the first two arguments
    are constant values, for "eval_str(...)" they are strings that
    evaluate to a single variable, and for "exec_str(...)", they are
    strings that set the variable "x" in their local namespace, which
    is then returned.  (An unrestricted namespace is available with
    "exec_str(*...)".)  If the argument between_go is set to None or
    is not defined, the behavior depends on the assignment command.
    If this is a <name>=const(...) assignment, between_go_value is set
    to during_go_value.  If this is a <name>=eval_str(...) or
    <name>=exec_str(...) assignment, the correct value cannot be
    guessed, and therefore the between_go_eval function will never be
    called (the eval_frequency flag NOT_BETWEEN_GO is set).

    Because the default value for temporal_variables is
    TIME_SEC_SINCE_GO, the variable "t" may be safely used in the
    during_go string for the eval_str or exec_str assignment commands.
    See the documentation for VisionEgg.FlowControl.EvalStringController for
    more information.

    Example commands from TCP port (try with telnet):

    <name>=const(1.0)
    <name>=eval_str("t*360.0")
    <name>=exec_str("x=t*360.0")

    <name>=const(0.,1.,EVERY_FRAME)
    <name>=const(1,None,ONCE)

    <name>=const(1.0,0.0,EVERY_FRAME,TIME_INDEPENDENT,types.FloatType)
    <name>=eval_str("t*360.0","t_abs*360.0",None,TIME_SEC_ABSOLUTE|TIME_SEC_SINCE_GO)
    <name>=eval_str("t_abs*360.0","t_abs*360.0",EVERY_FRAME,TIME_SEC_ABSOLUTE,types.FloatType)
    <name>=exec_str("x=t*360.0","x=0.0",EVERY_FRAME,TIME_SEC_SINCE_GO)
    <name>=exec_str("print 'Time since go=%f'%(t,)\nx=t*360.0","x=0.0",EVERY_FRAME,TIME_SEC_SINCE_GO)

    """

    help_string = r"""    TCP commands (sent over network socket):

    close -- close the connection
    exit -- close the connection
    quit -- quit the server program
    help -- print this message
    <name> -- show the value of the controller of <name>
    <name>=const(<args>) -- assign a new ConstantController to <name>
    <name>=eval_str(<args>) -- assign a new EvalStringController to <name>
    <name>=exec_str(<args>) -- assign a new ExecStringController to <name>
    <name>=exec_str(*<args>) -- assign a new unrestricted namespace ExecStringController to <name>

    TCP commands are always on a single line.  (Newlines in string
    literals can be specified by using "\n" without the quotes.)

    The assignment commands share common behavior:

    <name> -- value passed as argument "tcp_name" to method create_tcp_controller
    <args> -- during_go [, between_go [, eval_frequency [, temporal_variables [, return_type ]]]]
    """

    _re_line = re.compile(r"^(.*)\n",re.MULTILINE)
    _re_x_finder = re.compile(r'\A|\Wx\s?=[^=]')
    # The real newlines have already been parsed by the time the buffer gets to these statements:
    _re_const = re.compile(r'^const\(\s?(.*)\s?\)$',re.DOTALL)
    _re_eval_str = re.compile(r'^eval_str\(\s?(.*)\s?\)$',re.DOTALL)
    _re_exec_str = re.compile(r'^exec_str\(\s?(\*)?\s?(.*)\s?\)$',re.DOTALL)
    _parse_args_globals = {'types':types}
    _parse_args_locals = VisionEgg.FlowControl.Controller.flag_dictionary
    def __init__(self,
                 socket,
                 disconnect_ok = 0,
                 server_socket = None, # Only needed if reconnecting ok
                 temporal_variables = VisionEgg.FlowControl.Controller.TIME_INDEPENDENT,
                 eval_frequency = VisionEgg.FlowControl.Controller.EVERY_FRAME):
        """Instantiated by TCPServer."""
        VisionEgg.FlowControl.Controller.__init__(self,
                                           return_type = types.NoneType,
                                           temporal_variables = temporal_variables,
                                           eval_frequency = eval_frequency)
        self.socket = socket
        self.disconnect_ok = disconnect_ok
        if self.disconnect_ok and server_socket is None:
            # Warning -- no ability to accept further incoming sockets...
            pass
        self.server_socket = server_socket

        logger = logging.getLogger('VisionEgg.TCPController')
        logger.info("Handling connection from %s"%(self.socket.getsockname(),))
        self.socket.setblocking(0) # don't block on this socket

        self.socket.send("Hello. This is %s version %s.\n"%(self.__class__,__version__))
        self.socket.send(SocketListenController.help_string+"\n")
        self.socket.send("Begin sending commands now.\n")

        self.buffer = ""

        self.last_command = {}

        self.names = {} # ( controller, name_re, parser, require_type )

    def send_raw_text(self,text):
        """Send text over the TCP socket."""
        self.socket.send(text)

    def __check_socket(self):
        if self.socket is not None: # Normal, connected behavior
            # First, update the buffer
            ready_to_read, temp, temp2 = select.select([self.socket],[],[],0)
            new_info = 0
            while len(ready_to_read):
                try:
                    new = self.socket.recv(1024) # When disconnected, this fails on Win32
                except socket.error, x:
                    if not self.disconnect_ok:
                        raise
                    else:
                        self.socket.close()
                        self.socket = None
                        if self.server_socket is not None:
                            self.server_socket.setblocking(0)
                        return
                if len(new) == 0: # When disconnected, this happens on unix
                    # Disconnected
                    self.socket.close() # close socket
                    self.socket = None
                    if not self.disconnect_ok:
                        raise RuntimeError("Socket disconnected!")
                    else:
                        if self.server_socket is not None:
                            self.server_socket.setblocking(0)
                    return # don't do any more
                #assert(ready_to_read[0] == self.socket)
                self.buffer += new
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
                    # sticks the result in self.last_command[tcp_name] by calling the parser function.
                    self.buffer = name_re_str.sub(parser,self.buffer)
                    # Now act based on the command parsed
                    command = self.last_command[tcp_name]
                    if command is not None:
                        self.__do_assignment_command(tcp_name,command,require_type)
                        self.last_command[tcp_name] = None
                # Clear any complete lines for which we don't have a tcp_name
                self.buffer = SocketListenController._re_line.sub(self.__unprocessed_line,self.buffer)
        elif self.server_socket is not None:
            # Not connected on self.socket, check self.server_socket for new connection
            try:
                # This line raises an exception unless there's an incoming connection (if server is not blocking, which it shouldn't be)
                (client, client_address) = self.server_socket.accept()
                self.socket = client
                self.socket.send("Hello. This is %s version %s.\n"%(self.__class__,__version__))
                self.socket.send(SocketListenController.help_string+"\n")
                self.socket.send("Begin sending commands now.\n")
                for tcp_name in self.names.keys():
                    (controller, name_re_str, parser, require_type) = self.names[tcp_name]
                    self.socket.send('"%s" controllable with this connection.\n'%tcp_name)
            except socket.error, x:
                pass

    def __unprocessed_line(self,match):
        text = match.group(1)
        text = string.strip(text).lower()
        if text=="quit": # this a hack, really (should be a controller in charge of Presentation.parameters.quit)
            raise SystemExit
        elif text=="close" or text=="exit":
            self.socket = None # close socket
            if not self.disconnect_ok:
                raise RuntimeError("Socket disconnected!")
            else:
                if self.server_socket is not None:
                    self.server_socket.setblocking(0)
            return ""
        elif text=="help":
            self.socket.send(SocketListenController.help_string+"\n")
            return ""
        elif text in self.names.keys():
            (controller, name_re_str, parser, require_type) = self.names[text]
            self.socket.send(text+"="+str(controller)+"\n")
            return ""
        self.socket.send("Error: Invalid command line \""+text+"\"\n")
        logger = logging.getLogger('VisionEgg.TCPController')
        logger.warning('Invalid command line: "%s"'%(text,))
        return ''

    def create_tcp_controller(self,
                              tcp_name=None,
                              initial_controller=None,
                              require_type=None):
        """Create new instance of TCPController.

        Arguments:

        tcp_name -- String to reference new TCPController over TCP

        Optional arguments:

        initial_controller -- Initial value of TCPController instance
        require_type -- force this as TCPController instance's return_type
        """
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
            initial_controller = VisionEgg.FlowControl.ConstantController(
                during_go_value=1.0,
                between_go_value=0.0)
        else:
            if not isinstance(initial_controller,VisionEgg.FlowControl.Controller):
                print initial_controller
                raise ValueError('initial_controller not an instance of VisionEgg.FlowControl.Controller')
        if require_type is None:
            require_type = initial_controller.returns_type()
        # Create initial None value for self.last_command dict
        self.last_command[tcp_name] = None
        # Create values for self.names dict tuple ( controller, name_re, most_recent_command, parser )
        controller = TCPController(
            tcp_name=tcp_name,
            initial_controller=initial_controller
            )
        name_re_str = re.compile("^"+tcp_name+r"\s*=\s*(.*)\s*\n$",re.MULTILINE)
        parser = Parser(tcp_name,self.last_command).parse_func
        self.names[tcp_name] = (controller, name_re_str, parser, require_type)
        self.socket.send('"%s" controllable with this connection.\n'%tcp_name)
        return controller

    def __get_five_args(self,arg_string):
        args = eval("("+arg_string+",)",SocketListenController._parse_args_globals,SocketListenController._parse_args_locals)
        num_args = len(args)
        if num_args == 0:
            args = (None,None,None,None,None)
        elif num_args == 1:
            args = (args[0],None,None,None,None)
        elif num_args == 2:
            args = (args[0],args[1],None,None,None)
        elif num_args == 3:
            args = (args[0],args[1],args[2],None,None)
        elif num_args == 4:
            args = (args[0],args[1],args[2],args[3],None)
        elif num_args > 5:
            raise ValueError("Too many arguments!")
        if args[0] is None:
            raise ValueError("First argument must be set.")
        return args

    def __process_common_args(self,kw_args,match_groups):
        if match_groups[2] is not None:
            kw_args['eval_frequency'] = match_groups[2]
        if match_groups[3] is not None:
            kw_args['temporal_variables'] = match_groups[3]
        if match_groups[4] is not None:
            kw_args['return_type'] = match_groups[4]

    def __do_assignment_command(self,tcp_name,command,require_type):
        new_contained_controller = None
        match = SocketListenController._re_const.match(command)
        if match is not None:
            try:
                match_groups = self.__get_five_args(match.group(1))
                kw_args = {}
                kw_args['during_go_value'] = match_groups[0]
                if match_groups[1] is not None:
                    kw_args['between_go_value'] = match_groups[1]
                self.__process_common_args(kw_args,match_groups)
                kw_args.setdefault('return_type',require_type)
                new_contained_controller = VisionEgg.FlowControl.ConstantController(**kw_args)
                new_type = new_contained_controller.returns_type()
                ve_types.assert_type( new_type, require_type)
            except Exception, x:
                import traceback
                traceback.print_exc()
                self.socket.send("Error %s parsing const for %s: %s\n"%(x.__class__,tcp_name,x))
                logger = logging.getLogger('VisionEgg.TCPController')
                logger.info("%s parsing const for %s: %s"%(x.__class__,tcp_name,x))
        else:
            match = SocketListenController._re_eval_str.match(command)
            if match is not None:
                try:
                    match_groups = self.__get_five_args(match.group(1))
                    kw_args = {}
                    kw_args['during_go_eval_string'] = string.replace(match_groups[0],r"\n","\n")
                    if match_groups[1] is not None:
                        kw_args['between_go_eval_string'] = string.replace(match_groups[1],r"\n","\n")
                    self.__process_common_args(kw_args,match_groups)
                    kw_args.setdefault('return_type',require_type)
                    new_contained_controller = VisionEgg.FlowControl.EvalStringController(**kw_args)
                    if not (new_contained_controller.eval_frequency & VisionEgg.FlowControl.Controller.NOT_DURING_GO):
                        logger = logging.getLogger('VisionEgg.TCPController')
                        logger.debug('Executing "%s" as safety check.'%(kw_args['during_go_eval_string'],))
                        new_contained_controller._test_self(1)
                    if not (new_contained_controller.eval_frequency & VisionEgg.FlowControl.Controller.NOT_BETWEEN_GO):
                        logger = logging.getLogger('VisionEgg.TCPController')
                        logger.debug('Executing "%s" as safety check.'%(kw_args['between_go_eval_string'],))
                        new_contained_controller._test_self(0)
                    new_type = new_contained_controller.returns_type()
                    ve_types.assert_type( new_type, require_type)
                except Exception, x:
                    new_contained_controller = None
                    self.socket.send("Error %s parsing eval_str for %s: %s\n"%(x.__class__,tcp_name,x))
                    logger = logging.getLogger('VisionEgg.TCPController')
                    logger.info("%s parsing eval_str for %s: %s"%(x.__class__,tcp_name,x))
            else:
                match = SocketListenController._re_exec_str.match(command)
                if match is not None:
                    try:
                        kw_args = {}
                        match_groups = match.groups()
                        if match_groups[0] == '*':
                            kw_args['restricted_namespace'] = 0
                        else:
                            kw_args['restricted_namespace'] = 1
                        match_groups = self.__get_five_args(match_groups[1])
                        tmp = string.replace(match_groups[0],r"\n","\n")
                        if not SocketListenController._re_x_finder.match(tmp):
                            raise ValueError("x is not defined for during_go_exec_string")
                        kw_args['during_go_exec_string'] = tmp
                        if match_groups[1] is not None:
                            tmp = string.replace(match_groups[1],r"\n","\n")
                            if not SocketListenController._re_x_finder.match(tmp):
                                raise ValueError("x is not defined for between_go_exec_string")
                            kw_args['between_go_exec_string'] = tmp
                        self.__process_common_args(kw_args,match_groups)
                        kw_args.setdefault('return_type',require_type)
                        new_contained_controller = VisionEgg.FlowControl.ExecStringController(**kw_args)
                        if not (new_contained_controller.eval_frequency & VisionEgg.FlowControl.Controller.NOT_DURING_GO):
                            logger = logging.getLogger('VisionEgg.TCPController')
                            logger.debug('Executing "%s" as safety check.'%(kw_args['during_go_exec_string'],))
                            new_contained_controller._test_self(1)
                        if not (new_contained_controller.eval_frequency & VisionEgg.FlowControl.Controller.NOT_BETWEEN_GO):
                            logger = logging.getLogger('VisionEgg.TCPController')
                            logger.debug('Executing "%s" as safety check.'%(kw_args['between_go_exec_string'],))
                            new_contained_controller._test_self(0)
                        new_type = new_contained_controller.returns_type()
                        ve_types.assert_type( new_type, require_type)
                    except Exception, x:
                        new_contained_controller = None
                        self.socket.send("Error %s parsing exec_str for %s: %s\n"%(x.__class__,tcp_name,x))
                        logger = logging.getLogger('VisionEgg.TCPController')
                        logger.debug("%s parsing exec_str for %s: %s"%(x.__class__,tcp_name,x))
                else:
                    self.socket.send("Error: Invalid assignment command for %s: %s\n"%(tcp_name,command))
                    logger = logging.getLogger('VisionEgg.TCPController')
                    logger.info("Invalid assignment command for %s: %s"%(tcp_name,command))
        # create controller based on last command_queue
        if new_contained_controller is not None:
            (controller, name_re_str, parser, require_type) = self.names[tcp_name]
            controller.set_new_controller(new_contained_controller)

    def during_go_eval(self):
        """Check socket and act accordingly. Called by instance of Presentation.

        Overrides base class Controller method."""
        self.__check_socket()
        return None

    def between_go_eval(self):
        """Check socket and act accordingly. Called by instance of Presentation.

        Overrides base class Controller method."""
        self.__check_socket()
        return None

class TCPController(VisionEgg.FlowControl.EncapsulatedController):
    """Control a parameter from a network (TCP) connection.

    Subclass of Controller to allow control of Parameters via the
    network.

    This class is analagous to VisionEgg.PyroHelpers.PyroEncapsulatedController.
    """
    # Contains another controller...
    def __init__(self, tcp_name, initial_controller):
        """Instantiated by SocketListenController.

        Users should create instance by using method
        create_tcp_controller of class SocketListenController."""
        VisionEgg.FlowControl.EncapsulatedController.__init__(self,initial_controller)
        self.tcp_name = tcp_name

    def __str__(self):
        value = ""
        my_class = self.contained_controller.__class__
        if my_class == VisionEgg.FlowControl.ConstantController:
            value += "const( "
            value += str(self.contained_controller.get_during_go_value()) + ", "
            value += str(self.contained_controller.get_between_go_value()) + ", "
        elif my_class == VisionEgg.FlowControl.EvalStringController:
            value += "eval_str( "
            str_val = self.contained_controller.get_during_go_eval_string()
            if str_val is None:
                value += "None, "
            else:
                value += '"' + string.replace(str_val,"\n",r"\n") + '", '
            str_val = self.contained_controller.get_between_go_eval_string()
            if str_val is None:
                value += "None, "
            else:
                value += '"' + string.replace(str_val,"\n",r"\n") + '", '
        elif my_class == VisionEgg.FlowControl.ExecStringController:
            value += "exec_str("
            if self.contained_controller.restricted_namespace:
                value += " "
            else: # unrestricted
                value += "* "
            str_val = self.contained_controller.get_during_go_exec_string()
            if str_val is None:
                value += "None, "
            else:
                value += '"' + string.replace(str_val,"\n",r"\n") + '", '
            str_val = self.contained_controller.get_between_go_exec_string()
            if str_val is None:
                value += "None, "
            else:
                value += '"' + string.replace(str_val,"\n",r"\n") + '", '
        never = 1
        ef = self.contained_controller.eval_frequency
        if ef & VisionEgg.FlowControl.Controller.EVERY_FRAME:
            value += "EVERY_FRAME | "
            never = 0
        if ef & VisionEgg.FlowControl.Controller.TRANSITIONS:
            value += "TRANSITIONS | "
            never = 0
        if ef & VisionEgg.FlowControl.Controller.ONCE:
            value += "ONCE | "
            never = 0
        if ef & VisionEgg.FlowControl.Controller.NOT_DURING_GO:
            value += "NOT_DURING_GO | "
            never = 0
        if ef & VisionEgg.FlowControl.Controller.NOT_BETWEEN_GO:
            value += "NOT_BETWEEN_GO | "
            never = 0
        if never:
            value += "NEVER"
        else:
            value = value[:-3] # get rid of trailing "| "
        value += ", "
        time_indep = 1
        tv = self.contained_controller.temporal_variables
        if tv & VisionEgg.FlowControl.Controller.TIME_SEC_ABSOLUTE:
            value += "TIME_SEC_ABSOLUTE | "
            time_indep = 0
        if tv & VisionEgg.FlowControl.Controller.TIME_SEC_SINCE_GO:
            value += "TIME_SEC_SINCE_GO | "
            time_indep = 0
        if tv & VisionEgg.FlowControl.Controller.FRAMES_ABSOLUTE:
            value += "FRAMES_ABSOLUTE | "
            time_indep = 0
        if tv & VisionEgg.FlowControl.Controller.FRAMES_SINCE_GO:
            value += "FRAMES_SINCE_GO | "
            time_indep = 0
        if time_indep:
            value += "TIME_INDEPENDENT"
        else:
            value = value[:-3] # get rid of trailing "| "
        value += ", "
        my_type = self.contained_controller.returns_type()
        if my_type == types.ClassType:
            value += str(my_type)
        else:
            for t in dir(types):
                if my_type == getattr(types,t):
                    value += "types."+t
                    break
        value += " )"
        return value
