#!/usr/bin/env python

import sys
import tkMessageBox
import Pyro

from VisionEgg.PyroApps.UberServer import server_modules, start_server

# You can add your own server modules to the server_modules list

try:
    start_server( server_modules )
except Pyro.errors.PyroError, x:
    if str(x) in ["Name Server not responding","connection failed"]:
        try:
            tkMessageBox.showerror("Can't find Pyro Name Server","Can't find Pyro Name Server on network.")
            sys.exit(1)
        except:
            raise # Can't find Pyro Name Server on network
    else:
            raise        
