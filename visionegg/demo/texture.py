#!/usr/bin/env python

from VisionEgg.Core import *
from VisionEgg.Textures import *
from VisionEgg.AppHelper import *

filename = "orig.bmp"
if len(sys.argv) > 1:
    filename = sys.argv[1]
    
try:
    texture = TextureFromFile(filename)
except:
    print "Could not open image file '%s', generating texture."%filename
    texture = Texture(size=(256,256))

screen = get_default_screen()

# Set the projection so that eye coordinates are window coordinates
projection = OrthographicProjection(right=screen.size[0],top=screen.size[1])

# Create the instance of TextureStimulus
stimulus = TextureStimulus(texture=texture,projection=projection)

# Set the stimulus to have 1:1 scaling (requires projection as set above)
# This may result in clipping if texture is bigger than screen
stimulus.parameters.upper_right = ( texture.orig.size[0], texture.orig.size[1] )
stimulus.init_gl()

# Because the stimulus has a projection, we don't care what default is that the viewport uses.
lower_y = screen.size[1]/2 - texture.orig.size[1]/2
viewport = Viewport(screen,(0,lower_y),screen.size)

viewport.add_stimulus(stimulus)
p = Presentation(duration=(5.0,'seconds'),viewports=[viewport])
p.go()
