#!/usr/bin/env python
"""Display a sequence of images.

The displayed image is changes by changing the TextureStimulus's
Texture parameter, which will delete the old OpenGL texture object and
create a new one.

This method to switch images is slower than that demonstrated in the
image_sequence_fast.py demo.

The images need not all be the same size.
"""

from VisionEgg import *
start_default_logging(); watch_exceptions()

from VisionEgg.Core import *
from VisionEgg.FlowControl import Presentation, FunctionController
from VisionEgg.Textures import *

import Image, ImageDraw

import OpenGL.GL as gl

num_images = 20
duration_per_image = 0.1 # seconds

image_size = (256,256)

# Generate some images
image_list = []
for i in range(num_images):
    image = Image.new("RGB",image_size,(0,0,255)) # Blue background
    draw = ImageDraw.Draw(image)
    line_x = image_size[0]/float(num_images) * i
    draw.line((line_x, 0, line_x, image_size[1]), fill=(255,255,255))
    image_list.append(image)

texture_list = map(Texture,image_list) # create instances of Texture from images

screen = get_default_screen()

stimulus = TextureStimulus(texture=texture_list[0],
                           position = (screen.size[0]/2.0,screen.size[1]/2.0),
                           anchor='center',
                           size=image_size)

viewport = Viewport(screen=screen,
                    stimuli=[stimulus])

p = Presentation(go_duration=(num_images*duration_per_image,'seconds'),viewports=[viewport])

def put_image(t):
    i = int(t/duration_per_image) # choose image
    stimulus.parameters.texture = texture_list[i]
p.add_controller(None,None,FunctionController(during_go_func=put_image))

p.go()
