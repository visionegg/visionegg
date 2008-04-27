#!/usr/bin/env python
"""Display text strings."""

import VisionEgg
VisionEgg.start_default_logging(); VisionEgg.watch_exceptions()

from VisionEgg.Core import get_default_screen, Viewport
from VisionEgg.FlowControl import Presentation
from VisionEgg.Text import Text

screen = get_default_screen()
screen.parameters.bgcolor = (0.0,0.0,1.0) # background blue (RGB)

text = Text(text="Hello world!",
            color=(1.0,1.0,1.0), # alpha is ignored (set with max_alpha_param)
            position=(screen.size[0]/2,screen.size[1]/2),
            font_size=50,
            anchor='center')

viewport = Viewport(screen=screen,
                    size=screen.size,
                    stimuli=[text])
p = Presentation(go_duration=(5.0,'seconds'),viewports=[viewport])
p.go()
