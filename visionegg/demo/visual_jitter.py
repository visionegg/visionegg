#!/usr/bin/env python

# Visual jitter demonstration for the Vision Egg.

# Copyright (C) 2002 Andrew Straw. This software may be
# (re)distributed under the terms of the LGPL (Lesser GNU Public
# License).

# Inspired by

# Murakami, I. & Cavanagh, P. (2001). Visual jitter: evidence for
# visual-motion-based compensation of retinal slip due to small eye
# movements. Vision Research, 41, 173-186.

# Murakami, I. & Cavanagh, P. (1998). A jitter after-effect reveals
# motion-based stabilization of vision. Nature, 395, 798-801.

from VisionEgg import *
from VisionEgg.Core import *
from VisionEgg.Textures import *

import Image, ImageDraw # Python Imaging Library (PIL)

import OpenGL.GL as gl # PyOpenGL

import RandomArray # Numeric

dynamic_time = 10.0 # seconds
static_time = 10.0 # seconds

scale = 6 # magification of checkerboard
dynamic_checkerboard_size = (32,32)
static_checkerboard_size = (50,50)

screen = get_default_screen()

# allocate temporary texture in grayscale mode for dynamic texture
temp_grayscale_image = Image.new("L",dynamic_checkerboard_size,0)
temp_texture = Texture(temp_grayscale_image)
    
# create TextureStimulus for dynamic stimulus
scaled_dynamic_size = (scale*dynamic_checkerboard_size[0],scale*dynamic_checkerboard_size[1])

# find lowerleft to center stimulus
x = round(screen.size[0]/2.0 - scaled_dynamic_size[0]/2.0)
y = round(screen.size[1]/2.0 - scaled_dynamic_size[1]/2.0)
dynamic_checkerboard = TextureStimulus(texture=temp_texture,
                                       lowerleft=(x,y),
                                       mipmaps_enabled=0,
                                       size=scaled_dynamic_size,
                                       texture_min_filter=gl.GL_NEAREST,
                                       texture_mag_filter=gl.GL_NEAREST,
                                       )

# allocate static texture
static_data = RandomArray.randint(0,2,static_checkerboard_size)*255
static_texture = Texture(static_data)
    
# create TextureStimulus for static stimulus
scaled_static_size = (scale*static_checkerboard_size[0],scale*static_checkerboard_size[1])
# find lowerleft to center stimulus
x = round(screen.size[0]/2.0 - scaled_static_size[0]/2.0)
y = round(screen.size[1]/2.0 - scaled_static_size[1]/2.0)
static_checkerboard = TextureStimulus(texture=static_texture,
                                      lowerleft=(x,y),
                                      mipmaps_enabled=0,
                                      size=scaled_static_size,
                                      texture_min_filter=gl.GL_NEAREST,
                                      texture_mag_filter=gl.GL_NEAREST,
                                      )

fixation_spot = FixationSpot(center=(screen.size[0]/2,screen.size[1]/2),
                             color=(255,0,0,0),
                             size=(4,4))

viewport = Viewport(screen=screen,
                    stimuli=[static_checkerboard,
                             dynamic_checkerboard,
                             fixation_spot])

p = Presentation(go_duration=(dynamic_time+static_time,'seconds'),
                 viewports=[viewport])

# Use a controller to hook into go loop, but control texture buffer
# through direct manipulation.
dynamic_texture_object = dynamic_checkerboard.texture.get_texture_object()
def control_dynamic(t):
    if t <= dynamic_time:
        random_data = RandomArray.randint(0,2,dynamic_checkerboard_size)*255
        dynamic_texture_object.put_sub_image( random_data )
p.add_controller(None,None,FunctionController(during_go_func=control_dynamic))

p.go()
