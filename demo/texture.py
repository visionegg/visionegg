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
                           size    = texture.size,
                           shrink_texture_ok=1)

viewport = Viewport(screen=screen,
                    stimuli=[stimulus])

p = Presentation(go_duration=(5.0,'seconds'),viewports=[viewport])
p.go()
