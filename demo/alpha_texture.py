#!/usr/bin/env python
"""
Textures with alpha (transparency).

"""

from VisionEgg import *
start_default_logging(); watch_exceptions()

from VisionEgg.Core import *
from VisionEgg.FlowControl import Presentation
from VisionEgg.Textures import *

import Image, ImageDraw # Python Imaging Library (PIL)

import OpenGL.GL as gl # PyOpenGL

import RandomArray # Numeric

screen = get_default_screen()
texel_scale = 5

# create background texture from image file
bg_filename = os.path.join(VisionEgg.config.VISIONEGG_SYSTEM_DIR,"data","panorama.jpg")
bg_texture = Texture(bg_filename)
bg = TextureStimulus(texture = bg_texture,
                     size    = bg_texture.size,
                     shrink_texture_ok=1)


# create alpha texture from Numeric python ("numpy")
numpy_size = (50,50,4)
numpy_data = Numeric.ones(numpy_size,Numeric.Float)*1.0 # white
numpy_data[:,:,3] = RandomArray.uniform(0.0,1.0,numpy_size[:2]) # random alpha
numpy_texture = Texture(numpy_data)
    
numpy_stim = TextureStimulus(texture=numpy_texture,
                             internal_format = gl.GL_RGBA,
                             position = (10,10),
                             mipmaps_enabled=0,
                             size=(numpy_size[0]*texel_scale,numpy_size[1]*texel_scale),
                             texture_min_filter=gl.GL_NEAREST,
                             texture_mag_filter=gl.GL_NEAREST,
                             )

# create alpha texture from Image
im_size = (50*texel_scale,50*texel_scale)
im_texels = Image.new("RGBA",im_size,(0,0,0,0)) # transparent
im_draw = ImageDraw.Draw(im_texels)
im_draw.ellipse((0,0) + im_size, fill=(255,255,255,255)) # opaque circle
r,g,b,a = im_texels.split() # get individual bands (we only use alpha below)
im_draw.rectangle((0,0) + (im_size[0]/2,im_size[1]), fill=(255,255,255,255)) # white
im_draw.rectangle((im_size[0]/2,0) + (im_size[0],im_size[1]), fill=(0,0,0,255)) # white
im_texels.putalpha(a)
im_texture = Texture(im_texels)
im_stim = TextureStimulus(texture=im_texture,
                          internal_format = gl.GL_RGBA,
                          position = (20+numpy_size[0]*texel_scale,10),
                          mipmaps_enabled=0,
                          size=(im_size[0],im_size[1]),
                          texture_min_filter=gl.GL_NEAREST,
                          texture_mag_filter=gl.GL_NEAREST,
                          )

viewport = Viewport(screen=screen,
                    stimuli=[bg,numpy_stim,im_stim])

p = Presentation(go_duration=(5.0,'seconds'),
                 viewports=[viewport])

p.go()
