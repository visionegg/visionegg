#!/usr/bin/env python

from VisionEgg.Core import *
from VisionEgg.AppHelper import *
from VisionEgg.Text import *

# Define a couple "controller" functions
def lowerleft_as_function_of_time(t):
    return (0.4,0.4*sin(0.1*2.0*math.pi*t)+0.5)

def on_during_experiment(t):
    if t < 0.0:
        return 0 # off between stimuli
    else:
        return 1 # on during stimulus presentation
    
screen = get_default_screen()
screen.parameters.bgcolor = (1.0,1.0,1.0,1.0) # background white (RGBA)
projection = OrthographicProjection(right=1.0,top=1.0) # normalized coordinates
viewport = Viewport(screen,
                    size=screen.size,
                    projection=projection)
text = BitmapText(text="Hello world!")
text.parameters.color = (0.0,0.0,0.0,1.0) # black text (RGBA)
viewport.add_stimulus(text)
p = Presentation(duration=(10.0,'seconds'),viewports=[viewport])
p.add_realtime_time_controller(text,'lowerleft', lowerleft_as_function_of_time)
p.add_transitional_controller(text,'on', on_during_experiment)
p.go()


