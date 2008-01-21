# The Vision Egg: GL
#
# Copyright (C) 2001-2003 Andrew Straw.
# Author: Andrew Straw <astraw@users.sourceforge.net>
# URL: <http://www.visionegg.org/>
#
# Distributed under the terms of the GNU Lesser General Public License
# (LGPL). See LICENSE.TXT that came with this file.
#
# $Id$

"""
Vision Egg GL module -- lump all OpenGL names in one namespace.

"""

from pyglet.gl import * # get everything from pyglet.gl
from pyglet.gl import gl_info
import pyglet.gl
import ctypes
import numpy

__version__ = pyglet.gl.__version__

## # why doesn't PyOpenGL define this?!
## try:
##     GL_UNSIGNED_INT_8_8_8_8_REV
## except NameError:
##     GL_UNSIGNED_INT_8_8_8_8_REV = 0x8367

float_ptr = ctypes.POINTER(ctypes.c_float)

# maintain compatibility with PyOpenGL #############################
def glLoadMatrixf( arr ):
    arr = numpy.asarray( arr )
    pyglet.gl.glLoadMatrixf( arr.ctypes.data_as( float_ptr ))

def glGenTextures( num ):
    if num != 1:
        raise NotImplementedError('')
    gl_id = ctypes.c_uint(0)
    pyglet.gl.glGenTextures(num,ctypes.byref(gl_id))
    return gl_id.value

def glDeleteTextures( id ):
    gl_id = ctypes.c_uint(id)
    pyglet.gl.glDeleteTextures( ctypes.byref(gl_id) )

def glGetIntegerv( attr ):
    val = gl.GLint()
    pyglet.gl.glGetIntegerv(attr,ctypes.byref(val))
    return val.value

def glGetString( attr ):
    return cast( pyglet.gl.glGetString(attr), c_char_p).value
