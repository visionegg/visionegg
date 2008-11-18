#!/usr/bin/env python
"""Get texture as numpy array and manipulate it."""

import VisionEgg
VisionEgg.start_default_logging(); VisionEgg.watch_exceptions()

from VisionEgg.Core import get_default_screen, Viewport, gl
from VisionEgg.FlowControl import Presentation
from VisionEgg.Text import Text
from VisionEgg.Textures import Texture, TextureStimulus

screen = get_default_screen()
screen.parameters.bgcolor = (0.0,0.0,1.0) # background blue (RGB)

orig_text = Text(text="Hello world!",
                 color=(1.0,1.0,1.0),
                 font_size=50,
                 )

arr=orig_text.parameters.texture.get_texels_as_array() # get numpy array
arr = arr[::-1] # flip upside down
flipped_text = TextureStimulus(texture=Texture(arr),
                               position=(screen.size[0]/2,screen.size[1]/2),
                               anchor='center',
                               internal_format = gl.GL_RGBA,
                               mipmaps_enabled = False,
                               )

viewport = Viewport(screen=screen,
                    size=screen.size,
                    stimuli=[flipped_text])
p = Presentation(go_duration=(5.0,'seconds'),viewports=[viewport])
p.go()
