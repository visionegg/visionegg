#!/usr/bin/env python
"""Load a texture from a file."""

import os
from VisionEgg import *
from VisionEgg.Core import *
from VisionEgg.Textures import *

filename = os.path.join(config.VISIONEGG_SYSTEM_DIR,"data/panorama.jpg")
texture = TextureFromFile(filename)

screen = get_default_screen()

# Create the instance of TextureStimulus
stimulus = TextureStimulus(texture = texture,
                           size    = texture.orig.size,
                           shrink_texture_ok=1)

left_x = max(screen.size[0]/2 - texture.orig.size[0]/2,0)
lower_y = max(screen.size[1]/2 - texture.orig.size[1]/2,0)
viewport = Viewport(screen=screen,
                    lowerleft=(left_x,lower_y),
                    size=screen.size,
                    stimuli=[stimulus])

p = Presentation(duration=(5.0,'seconds'),viewports=[viewport])
p.go()
