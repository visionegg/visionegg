"""VisionEgg Pyro (Python Remote Objects) module
"""

# Copyright (c) 2002 Andrew Straw.  Distributed under the terms of the
# GNU General Public License (GPL).

import string
__version__ = string.split('$Revision$')[1]
__date__ = string.join(string.split('$Date$')[1:3], ' ')
__author__ = 'Andrew Straw <astraw@users.sourceforge.net>'

import os
import VisionEgg

# Work around Pyro configuration glitch in Mac OS X
if 'PYRO_STORAGE' not in os.environ.keys():
    os.environ['PYRO_STORAGE'] = VisionEgg.config.VISIONEGG_STORAGE

try:
    import Pyro.core
    import Pyro.naming
    from Pyro.errors import PyroError,NamingError
except ImportError,x:
    print "ERROR: Could not import Pyro. Download from http://pyro.sourceforge.net/"
    import sys
    sys.exit(1)

import sys
from math import *

Pyro.config.PYRO_MULTITHREADED = 0 # Turn off multithreading -- kills OpenGL

class PyroGoClass(Pyro.core.ObjBase):
    """Allows any function to be called remotely.

    Used to allow a remote computer to tell a stimulus presentation to
    go.
    """
    def __init__(self, go_func, quit_func=lambda:None):
        """Create and instance with appropriate go function."""
        self.go_func = go_func
        self.quit_func = quit_func
        Pyro.core.ObjBase.__init__(self)
    def go(self):
        """Call the go function."""
        self.go_func()
    def quit(self):
        """Quit the server."""
        self.quit_func()

class PyroController(Pyro.core.ObjBase):
    """Abstract base class for remote controllers"""
    def __init__(self,*args):
        if len(args) > 0:
            apply(self.set_value,args)
        Pyro.core.ObjBase.__init__(self)

class ConstantPyroController(PyroController):
    """A remote controller with a constant value"""
    def set_value(self,value):
        self.value = value
    def eval(self,t):
        return self.value

class BiStatePyroController(PyroController):
    """A remote controller with a stimus state and a between stimuli state."""
    def set_value(self,during_stimulus,between_stimuli):
        self.during_stimulus = during_stimulus
        self.between_stimuli = between_stimuli        
    def eval(self,t):
        if t < 0.0:
            return self.between_stimuli
        else:
            return self.during_stimulus

class EvalStringPyroController(PyroController):
    """A remote controller that allows a string to be evaluated."""
    def set_value(self,eval_string):
        # Make sure eval_string can be evaluated
        try:
            t = 1.0
            test = eval(eval_string)
        except Exception,x:
            raise ValueError('"%s" raised exception when evaluated: %s'%(eval_string,str(x)))
        self.eval_string = eval_string
    def eval(self,t):
        return eval(self.eval_string)
    
class LocalDictPyroController(PyroController):
    """A remote controller set by key.

    LocalDictPyroController(dict) where dict is a dictionary.  This
    allows local objects to be set from a remote location.  For example:
    LocalDictPyroController({'a':a,'b':b}) would allow a remote Pyro client
    to set a controller to value a without having to touch object a, only
    using a name for it, such as the string 'a'."""
    def __init__(self,dict):
        PyroController.__init__(self)
        self.dict = dict
        self.set_value(self.dict.keys()[0]) # use first key as default
    def set_value(self,key):
        self.value = self.dict[key]
    def eval(self,t):
        return self.value

class PyroServer:
    """Set up a Pyro server for your PyroControllers and PyroGoClass"""
    def __init__(self):
        # Start Pyro
        Pyro.core.initServer()
        self.daemon = Pyro.core.Daemon()
        # locate the Pyro name server
        locator = Pyro.naming.NameServerLocator()
        print 'searching for Pyro Name Server...'
        self.ns = locator.getNS(Pyro.config.PYRO_NS_HOSTNAME)
        print 'Pyro Name Server found at',self.ns.URI.address,'('+(Pyro.protocol.getHostname(self.ns.URI.address) or '??')+') port',self.ns.URI.port
        self.daemon.useNameServer(self.ns)
        self.ok_to_run = 1
        
    def connect(self,object,name):
        """Serve an object under a name"""
        try:
            self.ns.unregister(name)
        except NamingError:
            pass
        self.daemon.connect(object,name)
        
    def mainloop(self, idle_func=lambda: None, time_out=3.0):
        """Handle requests for objects."""
        print "VisionEgg.PyroHelpers.PyroServer handling requests..."
        while self.ok_to_run:
            self.daemon.handleRequests(time_out)
            idle_func()

    def quit_mainloop(self):
        self.ok_to_run = 0

class PyroClient:
    """A client for calling a Pyro server."""
    def __init__(self):
        """Initialize client and find Pyro Name Server."""
        Pyro.core.initClient()
        # locate the NS
        locator = Pyro.naming.NameServerLocator()
        print 'Searching Name Server...',
        self.ns = locator.getNS(Pyro.config.PYRO_NS_HOSTNAME)
        print 'Name Server found at',self.ns.URI.address,'('+(Pyro.protocol.getHostname(self.ns.URI.address) or '??')+') port',self.ns.URI.port

    def get(self,name):
        """Return a remote Pyro object being served by a Pyro server."""
        try:
            URI=self.ns.resolve(name)
            print '%s URI: %s'%(name,URI)
        except Pyro.core.PyroError,x:
            print 'Couldn\'t bind object, nameserver says:',x
            raise SystemExit
        return Pyro.core.getProxyForURI(URI)
