#!/usr/bin/env python

import sys
import tkMessageBox
import Pyro

from VisionEgg.PyroApps.UberServer import server_modules, start_server

# You can add your own server modules to the server_modules list

start_server( server_modules )
