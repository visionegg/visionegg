"""Python Remote Objects support - Client side"""

# Copyright (c) 2002 Andrew Straw.  Distributed under the terms of the
# GNU Lesser General Public License (LGPL).

import string
import VisionEgg

__version__ = VisionEgg.release_name
__cvs__ = string.split('$Revision$')[1]
__date__ = string.join(string.split('$Date$')[1:3], ' ')
__author__ = 'Andrew Straw <astraw@users.sourceforge.net>'

import Pyro.core
import Pyro.naming

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
