#!/usr/bin/env python
"""Use frame information to display stimuli."""

import VisionEgg
VisionEgg.start_default_logging(); VisionEgg.watch_exceptions()

from VisionEgg.Core import get_default_screen, Viewport
from VisionEgg.FlowControl import Presentation, FunctionController, FRAMES_ABSOLUTE
from VisionEgg.Text import Text

screen = get_default_screen()
screen.parameters.bgcolor = (0.0,0.0,1.0) # background blue (RGB)

textvar = Text(color=(1.0,1.0,1.0), # alpha is ignored (set with max_alpha_param)
               position=(screen.size[0]/4,screen.size[1]/2),
               font_size=50,
               anchor='left')

def text_func(f_abs):
    return "framecount: % 4d"%f_abs

t_controller = FunctionController(during_go_func=text_func,
                                  temporal_variables = FRAMES_ABSOLUTE)

viewport = Viewport(screen=screen,
                    size=screen.size,
                    stimuli=[textvar])

p = Presentation(go_duration=(5.0,'seconds'),viewports=[viewport])
p.add_controller(textvar,'text',t_controller)
p.go()
