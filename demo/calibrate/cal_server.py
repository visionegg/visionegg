#!/usr/bin/env python

from VisionEgg import *
from VisionEgg.Core import *
from VisionEgg.MoreStimuli import *
from VisionEgg.Gratings import *
from VisionEgg.PyroHelpers import *
from VisionEgg.DaqLPT import *
try:
    from VisionEgg.Text import *
    # In case GLUT isn't working
    text_ok = 1
except:
    text_ok = 0
    pass
import sys

# Connet to Pyro Name Server
pyro_server = PyroServer()

# Setup normal stuff

screen = get_default_screen()

bg = SinGrating2D(center           = ( screen.size[0]/2.0, screen.size[1]/2.0 ),
                  size             = screen.size,
                  spatial_freq     = 10.0 / screen.size[0], # units of cycles/pixel
                  temporal_freq_hz = 0.1)

cal_spot = Target2D(size  = ( screen.size[0]/3.0, screen.size[1]/3.0 ),
                    center           = ( screen.size[0]/2.0, screen.size[1]/2.0 )
                    )

if text_ok:
    go_symbol = BitmapText(text='In "go" loop',
                           lowerleft=(10.0,10.0),
                           color=(0.0,1.0,0.5,0.0))

    no_go_symbol = BitmapText(text='Between "go" loops',
                              lowerleft=(10.0,10.0),
                              color=(0.8,0.0,0.5,0.0))
else:
    go_symbol = Target2D(center=(10.0,10.0),
                         size=(10.0,10.0),
                         color=(0.0,1.0,0.5,0.0))
    
    no_go_symbol = Target2D(center=(10.0,10.0),
                            size=(10.0,10.0),
                            color=(0.8,0.0,0.5,0.0))
    
viewport = Viewport(screen=screen, stimuli=[bg,cal_spot,go_symbol,no_go_symbol])

p = Presentation(go_duration=(0.5,'seconds'),viewports=[viewport],check_events=1)

# Show when in go loop vs. not

p.add_controller(go_symbol,'on',ConstantController(1,0,eval_frequency=Controller.TRANSITIONS))
p.add_controller(no_go_symbol,'on',ConstantController(0,1,eval_frequency=Controller.TRANSITIONS))

# The main controller for the task

color_controller = PyroExecStringController(during_go_exec_string="x=(1.0,1.0,1.0,0.0)",
                                            between_go_exec_string="x=(0.5,0.5,0.5,0.0)")
pyro_server.connect(color_controller,'color_controller')
p.add_controller(cal_spot,'color', color_controller)

# Other controllers

go_controller = PyroConstantController(during_go_value=0,between_go_value=0)
pyro_server.connect(go_controller,'go_controller')
p.add_controller(p,'enter_go_loop', go_controller)

duration_controller = PyroConstantController(during_go_value=(5.0,'seconds'))
pyro_server.connect(duration_controller,'duration_controller')
p.add_controller(p,'go_duration', duration_controller)

quit_controller = PyroConstantController(during_go_value=0)
pyro_server.connect(quit_controller,'quit_controller')
p.add_controller(p,'quit', quit_controller)

# Make sure pyro server gets a chance to listen
p.add_controller(None,None, pyro_server.create_listener_controller())

# Use it if you've got it
if sys.platform in ['win32','linux']:
    p.add_controller(None,None,LPTTriggerOutController())

# Go!
p.run_forever()
