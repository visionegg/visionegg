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

# Copyright (c) 2002 Andrew Straw.  Distributed under the terms of the
# GNU Lesser General Public License (LGPL).

import os, string, math
import Numeric
import VisionEgg

try:
    import VisionEgg.Core # not required
except:
    if "Core" in dir(VisionEgg):
        del VisionEgg.Core

__version__ = VisionEgg.release_name
__cvs__ = string.split('$Revision$')[1]
__date__ = string.join(string.split('$Date$')[1:3], ' ')
__author__ = 'Andrew Straw <astraw@users.sourceforge.net>'

import Pyro.core
import Pyro.naming
import Pyro.errors

##try:
##    import Pyro.core
##    import Pyro.naming
##    import Pyro.errors
##except ImportError,x:
##    print "ERROR: Could not import Pyro. Download from http://pyro.sourceforge.net/"
##    import sys
##    sys.exit(1)

Pyro.config.PYRO_MULTITHREADED = 0 # No multithreading!

class PyroServer:
    """Set up a Pyro server for your PyroControllers and PyroGoClass.

    This class is analagous to VisionEgg.TCPController.TCPServer.

    """
    def __init__(self):
        # Start Pyro
        Pyro.core.initServer()
        self.daemon = Pyro.core.Daemon()
        # locate the Pyro name server
        locator = Pyro.naming.NameServerLocator()
        self.ns = locator.getNS(Pyro.config.PYRO_NS_HOSTNAME)
        self.daemon.useNameServer(self.ns)
        self.ok_to_run = 1
        
    def connect(self,object,name):
        """Serve an object under a name"""
        try:
            self.ns.unregister(name)
        except Pyro.errors.NamingError:
            pass
        self.daemon.connect(object,name)
        
    def create_listener_controller(self):
        if hasattr(self,'listen_controller'):
            raise RuntimeError("Only one pyro listen controller allowed per server!")
        self.listen_controller = PyroListenController(self)
        return self.listen_controller

class PyroClient:
    """Simplifies getting PyroControllers from a remote computer."""
    def __init__(self):
        """Initialize client and find Pyro Name Server."""
        Pyro.core.initClient()
        # locate the NS
        locator = Pyro.naming.NameServerLocator()
        #print 'Searching Name Server...',
        self.ns = locator.getNS(Pyro.config.PYRO_NS_HOSTNAME)
        #print 'Name Server found at',self.ns.URI.address,'('+(Pyro.protocol.getHostname(self.ns.URI.address) or '??')+') port',self.ns.URI.port

    def get(self,name):
        """Return a remote Pyro object being served by a Pyro server."""
        URI=self.ns.resolve(name)
        return Pyro.core.getProxyForURI(URI)

if "Core" in dir(VisionEgg): # we have VisionEgg.Core and therefore can make Controllers

    class PyroConstantController(VisionEgg.Core.ConstantController,Pyro.core.ObjBase):
        def __init__(self, **kw):
            apply(VisionEgg.Core.ConstantController.__init__,(self,),kw)
            apply(Pyro.core.ObjBase.__init__,(self,))

    class PyroEvalStringController(VisionEgg.Core.EvalStringController,Pyro.core.ObjBase):
        def __init__(self, **kw):
            apply(VisionEgg.Core.EvalStringController.__init__,(self,),kw)
            apply(Pyro.core.ObjBase.__init__,(self,))

    class PyroExecStringController(VisionEgg.Core.ExecStringController,Pyro.core.ObjBase):
        def __init__(self, **kw):
            apply(VisionEgg.Core.ExecStringController.__init__,(self,),kw)
            apply(Pyro.core.ObjBase.__init__,(self,))

    class PyroEncapsulatedController(VisionEgg.Core.EncapsulatedController,Pyro.core.ObjBase):
        """Create the instance of Controller on client, and send it to server.

        This class is analagous to VisionEgg.TCPController.TCPController.
        """
        def __init__(self,initial_controller=None,**kw):
            apply(VisionEgg.Core.EncapsulatedController.__init__,(self,initial_controller))
            apply(Pyro.core.ObjBase.__init__,(self,))

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
            apply(VisionEgg.Core.EncapsulatedController.__init__,(self,initial_controller))
            apply(Pyro.core.ObjBase.__init__,(self,))
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
            apply(VisionEgg.Core.Controller.__init__,(self,),kw)
            self.server=server

        def during_go_eval(self):
            # setting timeout = 0 means return ASAP
            self.server.daemon.handleRequests(timeout=0)

        def between_go_eval(self):
            # setting timeout = 0 means return ASAP
            self.server.daemon.handleRequests(timeout=0)
