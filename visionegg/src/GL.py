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

try:
    GL_UNSIGNED_INT_8_8_8_8_REV
except NameError:
    GL_UNSIGNED_INT_8_8_8_8_REV = 0x8367 # XXX why doesn't PyOpenGL define this?!

