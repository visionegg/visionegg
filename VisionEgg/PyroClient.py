# The Vision Egg: PyroClient
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
Python Remote Objects support - Client side.

"""

import socket
import VisionEgg

try:
    import logging                              # available in Python 2.3
except ImportError:
    import VisionEgg.py_logging as logging      # use local copy otherwise

__version__ = VisionEgg.release_name
__cvs__ = '$Revision$'.split()[1]
__date__ = ' '.join('$Date$'.split()[1:3])
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
    def __init__(self,server_hostname='',server_port=7766):
        """Initialize Pyro client."""
        Pyro.core.initClient()
        try:
            self.server_hostname = socket.getfqdn(server_hostname)
        except Exception, x:
            logger = logging.getLogger('VisionEgg.PyroClient')
            logger.warning("while getting fully qualified domain name: %s: %s"%
                           (str(x.__class__),str(x)))
            self.server_hostname = server_hostname
        self.server_port = server_port

    def get(self,name):
        """Return a remote Pyro object being served by Pyro server."""
        URI = "PYROLOC://%s:%d/%s" % (self.server_hostname, self.server_port, name)
        return Pyro.core.getProxyForURI(URI)
