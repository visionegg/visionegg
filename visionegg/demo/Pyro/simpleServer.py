#!/usr/bin/env python
"""Script to run a VisionEgg Pyro server.

You will need to have a Pyro Name Server running on your network for
this to work.  It comes with the Pyro distribution as a script in the
bin directory called ns.  Run it, run this script, and then run
simpleClient.py from any computer on your network!"""

from VisionEgg.Core import *
from VisionEgg.MoreStimuli import *
from VisionEgg.AppHelper import *
from VisionEgg.PyroHelpers import *

pyro_server = PyroServer()

# get visionegg stimulus ready to go
screen = get_default_screen()
projection = SimplePerspectiveProjection(fov_x=45.0)
viewport = Viewport(screen,(0,0),screen.size,projection)
stimulus = Teapot()
stimulus.init_gl()
viewport.add_stimulus(stimulus)
p = Presentation(duration_sec=5.0,viewports=[viewport])

# make a controller, serve it via pyro, and glue it to the Presentation
angle_controller = EvalStringPyroController('90.0*t')
pyro_server.connect(angle_controller,'angle_controller')
p.add_realtime_controller(stimulus.parameters,'yrot', angle_controller.eval)

on_controller = BiStatePyroController(1,0) # on during stimulus, off otherwise
pyro_server.connect(on_controller,'on_controller')
p.add_transitional_controller(stimulus.parameters,'on', on_controller.eval)

# initialize graphics to between presentations state
p.between_presentations() 

# register the go function and serve it with pyro
go_object = PyroGoClass(p.go)
pyro_server.connect(go_object,'go_object')

pyro_server.mainloop()
