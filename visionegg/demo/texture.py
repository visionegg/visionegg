#!/usr/bin/env python

from VisionEgg.Core import *
from VisionEgg.Textures import *

import sys

filename = "orig.bmp"
if len(sys.argv) > 1:
    filename = sys.argv[1]
    
try:
    texture = TextureFromFile(filename)
except:
    print "Could not open image file '%s', generating texture."%filename
    texture = Texture(size=(256,256))

screen = get_default_screen()

# Create the instance of TextureStimulus
# Set the stimulus to have 1:1 scaling (requires projection as set above)
# This may result in clipping if texture is bigger than screen
stimulus = TextureStimulus(texture = texture,
                           size    = texture.orig.size)

lower_y = screen.size[1]/2 - texture.orig.size[1]/2
viewport = Viewport(screen=screen,
                    lowerleft=(0,lower_y),
                    size=screen.size,
                    stimuli=[stimulus])

p = Presentation(duration=(5.0,'seconds'),viewports=[viewport])
p.go()
