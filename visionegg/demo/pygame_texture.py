#!/usr/bin/env python
"""Load a texture from a file using pygame"""

import os
import VisionEgg
VisionEgg.start_default_logging(); VisionEgg.watch_exceptions()

from VisionEgg.Core import *
from VisionEgg.FlowControl import Presentation
from VisionEgg.Textures import *
import pygame.image
import OpenGL.GL as gl

filename = os.path.join(VisionEgg.config.VISIONEGG_SYSTEM_DIR,"data","visionegg.bmp")
pygame_surface = pygame.image.load(filename)
texture = Texture(pygame_surface)

screen = get_default_screen()

# Create the instance of TextureStimulus
stimulus = TextureStimulus(texture = texture,
                           position = (screen.size[0]/2.0,screen.size[1]/2.0),
                           anchor = 'center',
                           size    = texture.size,
                           mipmaps_enabled = 0,
                           texture_min_filter=gl.GL_LINEAR,
                           shrink_texture_ok=1)

viewport = Viewport(screen=screen,
                    stimuli=[stimulus])

p = Presentation(go_duration=(5.0,'seconds'),viewports=[viewport])
p.go()
