"""Python Remote Objects support

Use this class if you don't want to deal with TCP directly and Python
is the program on both ends of the network.

The module provides some Vision Egg specific code for Pyro.  Pyro
allows you to call python objects on remote machines just like they
are on the local machine.  This makes the task of writing a two
computer Vision Egg application quite easy, because one can mostly
ignore the network-based intermediate stage.

PyroControllers are run on the computer performing the presentation.
The PyroServer class also runs on this computer, and allows these
controllers to be changed from a computer running PyroClient. To
listen to the network PyroListenerController must be instantiated by
the PyroServer -- this checks for any requests coming over the
network, but only at times specified because it is a subclass of
VisionEgg.Core.Controller.

Just like TCPControllers, don't use this class for realtime control
unless you think your network is that fast and reliable.  It's great
for setting up parameters in advance and sending a trigger pulse,
though!"""

# Copyright (c) 2002-2003 Andrew Straw.  Distributed under the terms
# of the GNU Lesser General Public License (LGPL).

import string
import VisionEgg
import VisionEgg.Core

__version__ = VisionEgg.release_name
__cvs__ = string.split('$Revision$')[1]
__date__ = string.join(string.split('$Date$')[1:3], ' ')
__author__ = 'Andrew Straw <astraw@users.sourceforge.net>'

import Pyro.core
import Pyro.errors

Pyro.config.PYRO_MULTITHREADED = 0 # No multithreading!

class PyroServer:
    """Set up a Pyro server for your PyroControllers and PyroGoClass.

    This class is analagous to VisionEgg.TCPController.TCPServer.

    """
    def __init__(self):
        # Start Pyro
        Pyro.core.initServer()
        self.daemon = Pyro.core.Daemon()
        self.ok_to_run = 1

    def get_hostname_and_port(self):
        return self.daemon.hostname, self.daemon.port
        
    def connect(self,object,name):
        """Serve an object under a name"""
        URI=self.daemon.connect(object,name)
        return URI

    def disconnect(self,object):
        # Should do this:
        # self.daemon.disconnect(object)
        # But there's a bug in Pyro 3.0 and 3.1 (at least)
        #
        # Anyhow, here's what daemon.disconnect should do:
        del self.daemon.implementations[object.GUID()]
        object.setDaemon(None)
        
    def create_listener_controller(self):
        if hasattr(self,'listen_controller'):
            raise RuntimeError("Only one pyro listen controller allowed per server!")
        self.listen_controller = PyroListenController(self)
        return self.listen_controller

class PyroConstantController(VisionEgg.Core.ConstantController,Pyro.core.ObjBase):
    def __init__(self, **kw):
        VisionEgg.Core.ConstantController.__init__(self,**kw)
        Pyro.core.ObjBase.__init__(self)

class PyroEvalStringController(VisionEgg.Core.EvalStringController,Pyro.core.ObjBase):
    def __init__(self, **kw):
        VisionEgg.Core.EvalStringController.__init__(self,**kw)
        Pyro.core.ObjBase.__init__(self)

class PyroExecStringController(VisionEgg.Core.ExecStringController,Pyro.core.ObjBase):
    def __init__(self, **kw):
        VisionEgg.Core.ExecStringController.__init__(self,**kw)
        Pyro.core.ObjBase.__init__(self)

class PyroEncapsulatedController(VisionEgg.Core.EncapsulatedController,Pyro.core.ObjBase):
    """Create the instance of Controller on client, and send it to server.

    This class is analagous to VisionEgg.TCPController.TCPController.
    """
    def __init__(self,initial_controller=None,**kw):
        VisionEgg.Core.EncapsulatedController.__init__(self,initial_controller)
        Pyro.core.ObjBase.__init__(self)

class PyroLocalDictController(VisionEgg.Core.EncapsulatedController,Pyro.core.ObjBase):
    """Contain several dictionary entries, set controller accordingly.
    """
    def __init__(self, dict=None, key=None, **kw):
        if dict is None:
            self.dict = {}
            initial_controller = VisionEgg.Core.ConstantController(during_go_value=0,
                                                                   between_go_value=0,
                                                                   eval_frequency=VisionEgg.Core.Controller.NEVER)
        else:
            self.dict = dict
        if key is None:
            if len(self.dict.keys()):
                key = self.dict.keys()[0]
                initial_controller = self.dict[key]
            else:
                initial_controller = VisionEgg.Core.ConstantController(during_go_value=0,
                                                                       between_go_value=0,
                                                                       eval_frequency=VisionEgg.Core.Controller.NEVER)
        else:
            initial_controller = dict[key]
        VisionEgg.Core.EncapsulatedController.__init__(self,initial_controller)
        Pyro.core.ObjBase.__init__(self)
    def use_controller(self,key):
        self.set_new_controller(self.dict[key])
    def add_controller(self,key,new_controller):
        self.dict[key] = new_controller

class PyroListenController(VisionEgg.Core.Controller):
    """Handle connection from remote machine, control PyroControllers.

    This meta controller handles a Pyro daemon, which checks the TCP
    socket for new input and acts accordingly.

    This class is analagous to VisionEgg.TCPController.SocketListenController.

    """

    def __init__(self,server=None,**kw):
        """Called by PyroServer. Creates a PyroListenerController instance."""
        if not isinstance(server,PyroServer):
            raise ValueError("Must specify a Pyro Server.") 
        if 'eval_frequency' not in kw.keys():
            kw['eval_frequency'] = VisionEgg.Core.Controller.EVERY_FRAME
        if 'return_type' not in kw.keys():
            kw['return_type'] = type(None)
        VisionEgg.Core.Controller.__init__(self,**kw)
        self.server=server

    def during_go_eval(self):
        # setting timeout = 0 means return ASAP
        self.server.daemon.handleRequests(timeout=0)

    def between_go_eval(self):
        # setting timeout = 0 means return ASAP
        self.server.daemon.handleRequests(timeout=0)
