#!/usr/bin/env python
from VisionEgg.PyroHelpers import *

client = PyroClient()

go_object = client.get('go_object')
angle_controller = client.get('angle_controller')
on_controller = client.get('on_controller')

go_object.go()
