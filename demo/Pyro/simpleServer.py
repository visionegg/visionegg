#!/usr/bin/env python
"""Run a simple VisionEgg Pyro server.

You will need to have a Pyro Name Server running on your network for
this to work.  It comes with the Pyro distribution as a script in the
bin directory called ns.  Run it, run this script, and then run
simpleClient.py from any computer on your network!

"""

import VisionEgg
VisionEgg.start_default_logging(); VisionEgg.watch_exceptions()

from VisionEgg.Core import *
from VisionEgg.FlowControl import Presentation
from VisionEgg.Gratings import *
from VisionEgg.PyroHelpers import *

pyro_server = PyroServer()

# get visionegg stimulus ready to go
screen = get_default_screen()
stimulus = SinGrating2D(temporal_freq_hz=0.0)
viewport = Viewport(screen=screen,stimuli=[stimulus])
p = Presentation(go_duration=(5.0,'seconds'),viewports=[viewport])

# make a controller, serve it via pyro, and glue it to the Presentation
tf_controller = PyroConstantController(during_go_value=0.0)
pyro_server.connect(tf_controller,'tf_controller')
p.add_controller(stimulus,'temporal_freq_hz', tf_controller)

quit_controller = PyroConstantController(during_go_value=0)
pyro_server.connect(quit_controller,'quit_controller')
p.add_controller(p,'quit', quit_controller)

# get listener controller and register it
p.add_controller(None,None, pyro_server.create_listener_controller())

# initialize graphics to between presentations state
p.run_forever()
