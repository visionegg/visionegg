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

from OpenGL.GL import * # get everything from OpenGL.GL
import OpenGL
import numpy
__version__ = OpenGL.__version__

# tell py2exe we want these modules
try:
    import OpenGL.GL.GL__init___
except:
    pass
try:
    import OpenGL.GL.ARB.multitexture
except:
    pass
try:
    import OpenGL.GL.EXT.bgra
except:
    pass
try:
    import SGIS.texture_edge_clamp
except:
    pass

# why doesn't PyOpenGL define this?!
try:
    GL_UNSIGNED_INT_8_8_8_8_REV
except NameError:
    GL_UNSIGNED_INT_8_8_8_8_REV = 0x8367

if OpenGL.__version__[0] == '3':
    if (OpenGL.__version__.startswith('3.0.0a')) or (OpenGL.__version__ == '3.0.0b1'):

        # A bug in early PyOpenGL 3.x had problems with some arrays
        _orig_glLoadMatrixf = glLoadMatrixf
        def glLoadMatrixf(M):
            M = numpy.array([ Mi for Mi in M ])
            return _orig_glLoadMatrixf(M)
