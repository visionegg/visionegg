"""Python Remote Objects support - Client side"""

# Copyright (c) 2002 Andrew Straw.  Distributed under the terms of the
# GNU Lesser General Public License (LGPL).

import string, socket
import VisionEgg

__version__ = VisionEgg.release_name
__cvs__ = string.split('$Revision$')[1]
__date__ = string.join(string.split('$Date$')[1:3], ' ')
__author__ = 'Andrew Straw <astraw@users.sourceforge.net>'

import Pyro.core

# Use Python's bool constants if available, make aliases if not
try:
    True
except NameError:
    True = 1==1
    False = 1==0

class PyroClient:
    """Simplifies getting PyroControllers from a remote computer."""
    def __init__(self,server_hostname='',server_port=7766,lookup_fqdn=False):
        """Initialize Pyro client."""
        Pyro.core.initClient()
        if lookup_fqdn:
            self.server_hostname = socket.getfqdn(server_hostname)
        else:
            self.server_hostname = server_hostname
        self.server_port = server_port

    def get(self,name):
        """Return a remote Pyro object being served by Pyro server."""
        URI = "PYROLOC://%s:%d/%s" % (self.server_hostname, self.server_port, name)
        return Pyro.core.getProxyForURI(URI)
