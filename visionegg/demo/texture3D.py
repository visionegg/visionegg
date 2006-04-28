#!/usr/bin/env python
"""Display a texture in 3D coordinates."""

import os
import VisionEgg
VisionEgg.start_default_logging(); VisionEgg.watch_exceptions()

from VisionEgg.Core import *
from VisionEgg.FlowControl import Presentation, FunctionController
from VisionEgg.Textures import *

filename = os.path.join(VisionEgg.config.VISIONEGG_SYSTEM_DIR,"data","panorama.jpg")
texture = Texture(filename)

screen = get_default_screen()

# Create the instance of TextureStimulus3D
duration = 5.0
speed = 1.0
z = duration*speed
stimulus = TextureStimulus3D(texture = texture,
                             shrink_texture_ok=True,
                             )

def every_frame_func(t=None):
    z=t*speed-duration
    stimulus.parameters.upperleft=(-5,1,z)
    stimulus.parameters.lowerleft=(-5,-1,z)
    stimulus.parameters.lowerright=(5,-1,z)
    stimulus.parameters.upperright=(5,1,z)

every_frame_func(0.0) # set initial stimulus postion

projection = SimplePerspectiveProjection(fov_x=135.0)

viewport = Viewport(screen=screen,
                    projection=projection,
                    stimuli=[stimulus])

p = Presentation(go_duration=(duration,'seconds'),viewports=[viewport])
p.add_controller(None, None, FunctionController(during_go_func=every_frame_func) )
p.go()
