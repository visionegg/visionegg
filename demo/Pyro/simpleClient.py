#!/usr/bin/env python

from VisionEgg.PyroHelpers import *
from VisionEgg.Core import *
import time

# Get the controllers

client = PyroClient()

tf_controller = client.get('tf_controller')
quit_controller = client.get('quit_controller')

# Set a temporal frequency

# Note that we never enter the 'go' loop in this demo, so we are only
# concerned with setting the between_go_value

tf_controller.set_between_go_value(1.0)
tf_controller.evaluate_now()

time.sleep(5.0) # show for 5 seconds

quit_controller.set_between_go_value(1)
quit_controller.evaluate_now()
