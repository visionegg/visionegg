#!/usr/bin/env python
"""Display a sequence of images using a pseudo-blit routine."""
from VisionEgg import *
from VisionEgg.Core import *
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
x = screen.size[0]/2.0 - image_size[0]/2.0
y = screen.size[1]/2.0 - image_size[1]/2.0
stimulus = TextureStimulus(mipmaps_enabled=0,
                           texture=TextureFromPILImage(image_list[0]),
                           size=image_size,
                           texture_min_filter=gl.GL_LINEAR,
                           lowerleft=(x,y))

viewport = Viewport(screen=screen,
                    stimuli=[stimulus])

p = Presentation(go_duration=(num_images*duration_per_image,'seconds'),viewports=[viewport])

# Use a controller to hook into go loop, but control texture buffer
# through direct manipulation.
texture_buffer = stimulus.texture.get_texture_buffer()
def put_image(t):
    i = int(t/duration_per_image) # choose image
    texture_buffer.put_sub_image_pil( image_list[i] ) # "blit" image
p.add_controller(None,None,FunctionController(during_go_func=put_image))

p.go()
