#!/usr/bin/env python
"""Display text strings."""

from VisionEgg.Core import *
from VisionEgg.Text import *
import math

# Define a couple "controller" functions
def lowerleft_as_function_of_time(t):
    return (0.4,0.4*math.sin(0.1*2.0*math.pi*t)+0.5)

screen = get_default_screen()
screen.parameters.bgcolor = (1.0,1.0,1.0,1.0) # background white (RGBA)
projection = OrthographicProjection(right=1.0,top=1.0) # normalized coordinates

text = BitmapText(text="Hello world!")
text.parameters.color = (0.0,0.0,0.0,1.0) # black text (RGBA)

viewport = Viewport(screen=screen,
                    size=screen.size,
                    projection=projection,
                    stimuli=[text])
p = Presentation(go_duration=(10.0,'seconds'),viewports=[viewport])
p.add_controller(text,'lowerleft', FunctionController(during_go_func=lowerleft_as_function_of_time))
p.go()


