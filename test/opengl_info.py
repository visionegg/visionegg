#!/usr/bin/env python
#
# This is the python source code for a utility which checks
# lots of things about the current OpenGL system.
#
# It is part of the Vision Egg package, but does not require
# the Vision Egg to be installed.
#
# Copyright (c) 2001, 2002 Andrew Straw.  Distributed under the terms of the
# GNU General Public License (GPL).

import string
__version__ = string.split('$Revision$')[1]
__date__ = string.join(string.split('$Date$')[1:3], ' ')
__author__ = 'Andrew Straw <astraw@users.sourceforge.net>'

import time, sys
import pygame
from pygame.locals import *
from OpenGL.GL import * # PyOpenGL packages
from Numeric import *

def capitalize_word(word):
    result = word
    if word[0] in string.lowercase:
        result = string.upper(word[0]) + word[1:]
    return result

ARB_exts = ['matrix_palette','multisample','multitexture','point_parameters',
        'texture_border_clamp','texture_compression','texture_cube_map',
        'texture_env_add','texture_env_combine','texture_env_crossbar',
        'texture_env_dot3','transpose_matrix','vertex_blend']

EXT_exts = ['abgr','bgra','blend_color','blend_minmax','blend_subtract',
            'clip_volume_hint','compiled_vertex_array','draw_range_elements',
            'fog_coord','multi_draw_arrays','packed_pixels',
            'paletted_texture','point_parameters','rescale_normal',
            'secondary_color','separate_specular_color','shared_texture_palette',
            'stencil_wrap','texture_compression_s3tc','texture3D','texture_cube_map',
            'texture_edge_clamp','texture_env_add','texture_env_combine',
            'texture_env_dot3','texture_filter_anisotropic','texture_lod_bias',
            'texture_object','vertex_array','vertex_weighting']

if sys.platform == 'win32':
    time_func = time.clock
else:
    time_func = time.time

### Setup graphics

width = 640
height = 480

size = (width,height)

pygame.display.init()
pygame.display.set_caption("OpenGL Test")

try_bpps = [0,32,24] # bits per pixel (32 = 8 bits red, 8 green, 8 blue, 8 alpha)
flags = OPENGL | DOUBLEBUF
found_mode = 0
for bpp in try_bpps:
    modeList = pygame.display.list_modes( bpp, flags )
    if modeList == -1: # equal to -1 if any resolution will work
        found_mode = 1
    else:
        if len(modeList) == 0: # any resolution is OK
            found_mode = 1
        else:
            if size in modeList:
                found_mode = 1
            else:
                size = modeList[0]
                print "WARNING: Using %dx%d video mode instead of requested size."%(size[0],size[1])
    if found_mode:
        break
if found_mode == 0:
    print "WARNING: Could not find acceptable video mode! Trying anyway..."

print "Initializing graphics at %d x %d ( %d bpp )."%(size[0],size[1],bpp)
pygame.display.set_mode((width,height), flags, bpp )

print

### Get OpenGL info

print "GL_VENDOR =",glGetString(GL_VENDOR)
print "GL_RENDERER =",glGetString(GL_RENDERER)
print "GL_VERSION = ",glGetString(GL_VERSION)
print "GL_EXTENSIONS = ",glGetString(GL_EXTENSIONS)

print

### Buffer information

print "Buffer information"
#print "glGetIntegerv( GL_DRAW_BUFFER ) =",glGetIntegerv( GL_DRAW_BUFFER )
print "glGetIntegerv( GL_AUX_BUFFERS ) =",glGetIntegerv( GL_AUX_BUFFERS )
print "glGetBooleanv( GL_RGBA_MODE ) =",glGetBooleanv( GL_RGBA_MODE )
print "glGetBooleanv( GL_DOUBLEBUFFER ) = ",glGetBooleanv( GL_DOUBLEBUFFER )
print "glGetBooleanv( GL_STEREO ) = ",glGetBooleanv( GL_STEREO )

print "glGetIntegerv( GL_RED_BITS ) =",glGetIntegerv( GL_RED_BITS )
print "glGetIntegerv( GL_GREEN_BITS ) =",glGetIntegerv( GL_GREEN_BITS )
print "glGetIntegerv( GL_BLUE_BITS ) =",glGetIntegerv( GL_BLUE_BITS )
print "glGetIntegerv( GL_ALPHA_BITS ) =",glGetIntegerv( GL_ALPHA_BITS )

print "glGetIntegerv( GL_ACCUM_RED_BITS ) =",glGetIntegerv( GL_ACCUM_RED_BITS )
print "glGetIntegerv( GL_ACCUM_GREEN_BITS ) =",glGetIntegerv( GL_ACCUM_GREEN_BITS )
print "glGetIntegerv( GL_ACCUM_BLUE_BITS ) =",glGetIntegerv( GL_ACCUM_BLUE_BITS )
print "glGetIntegerv( GL_ACCUM_ALPHA_BITS ) =",glGetIntegerv( GL_ACCUM_ALPHA_BITS )

print

### Test OpenGL extensions

print "Testing OpenGL extensions"

for ext in ARB_exts:
    print " GL_ARB_%s:"%ext,
    module_name = "OpenGL.GL.ARB.%s"%ext
    try:
        mod = __import__(module_name,globals(),locals(),[])
        components = string.split(module_name, '.') # make mod refer to deepest module
        for comp in components[1:]:
            mod = getattr(mod, comp)
        init_name = "glInit%sARB"%string.join(map(capitalize_word,string.split(ext,'_')),'')
        init_func = getattr(mod,init_name)
        if init_func():
            print "OK"
        else:
            print "Failed"
    except Exception, x:
        print "Failed (exception raised):",x
        
for ext in EXT_exts:
    print " GL_EXT_%s:"%ext,
    module_name = "OpenGL.GL.EXT.%s"%ext
    try:
        mod = __import__(module_name,globals(),locals(),[])
        components = string.split(module_name, '.') # make mod refer to deepest module
        for comp in components[1:]:
            mod = getattr(mod, comp)
        init_name = "glInit%sEXT"%string.join(map(capitalize_word,string.split(ext,'_')),'')
        init_func = getattr(mod,init_name)
        if init_func():
            print "OK"
        else:
            print "Failed"
    except Exception, x:
        print "Failed (exception raised):",x
        
print

print "Texture information"
max_dim = glGetIntegerv(GL_MAX_TEXTURE_SIZE)
print " GL_MAX_TEXTURE_SIZE is", max_dim

def list_smaller_pow2s(pow2_list):
    """Recursive function for generating all powers of 2 less than a number.

    >>>list_smaller_pow2s([1024])
    [1024, 512, 256, 128, 64, 32, 16, 8, 4, 2, 1]
    """
    smallest = 128
    next = pow2_list[-1]/2
    pow2_list.append(next)
    if next <= smallest:
        return pow2_list
    else:
        return list_smaller_pow2s(pow2_list)

try_dims = list_smaller_pow2s([max_dim])
try_dims.reverse()

for w in try_dims:
    for h in try_dims:
        print " GL_PROXY_TEXTURE_2D trying (%d x %d):"%(w,h),
        data = resize(3.0*arange(w)*2.0*math.pi/w,(w,h)).astype('b')
        
        tic = time_func()
        glTexImage2D(GL_PROXY_TEXTURE_2D,0,GL_RGB,w,h,0,GL_RGB,GL_UNSIGNED_BYTE,data)
        toc = time_func()
        if glGetTexLevelParameteriv(GL_PROXY_TEXTURE_2D,0,GL_TEXTURE_WIDTH) != 0:
            if glGetTexLevelParameteriv(GL_PROXY_TEXTURE_2D,0,GL_TEXTURE_HEIGHT) != 0:
                print "OK (%.1f msec)"%((toc-tic)*1000.0,)
            else:
                print "Failed"
        else:
            print "Failed"
            
