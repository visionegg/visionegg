#!/usr/bin/env python
"""Display a sequence of images using a pseudo-blit routine.

This is a fast way to switch images because the OpenGL texture object
is already created and the image data is already in system RAM.
Switching the image merely consists of putting the new data into
OpenGL.

Currently, there is no support for ensuring image sizes remain
constant, so if you get strange behavior, please ensure that all your
images are the same size.
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

screen = get_default_screen()

# create a TextureStimulus to allocate memory in OpenGL
stimulus = TextureStimulus(mipmaps_enabled=0,
                           texture=Texture(image_list[0]),
                           size=image_size,
                           texture_min_filter=gl.GL_LINEAR,
                           position=(screen.size[0]/2.0,screen.size[1]/2.0),
                           anchor='center')

viewport = Viewport(screen=screen,
                    stimuli=[stimulus])

p = Presentation(go_duration=(num_images*duration_per_image,'seconds'),viewports=[viewport])

# Use a controller to hook into go loop, but control texture buffer
# through direct manipulation.
texture_object = stimulus.parameters.texture.get_texture_object()
def put_image(t):
    i = int(t/duration_per_image) # choose image
    texture_object.put_sub_image( image_list[i] )
p.add_controller(None,None,FunctionController(during_go_func=put_image))

p.go()
