#!/usr/bin/env python
#
# This test can be run before building any files.
# It checks the existance of PyOpenGL and various
# modules from that package.  The Vision Egg
# may be able to run without all of the modules,
# but some functionality will be lost.
#
# Copyright (c) 2001 Andrew Straw.  Distributed under the terms of the
# GNU General Public License (GPL).

import string
__version__ = string.split('$Revision$')[1]
__date__ = string.join(string.split('$Date$')[1:3], ' ')
__author__ = 'Andrew Straw <astraw@users.sourceforge.net>'

from OpenGL.GL import * # PyOpenGL packages
from OpenGL.GL.ARB.texture_env_combine import * # this is needed to do contrast
from OpenGL.GL.ARB.texture_compression import *
from OpenGL.GLU import *
from OpenGL.GLUT import *

p = 1
print "glGetTexParameteriv(GL_TEXTURE_WIDTH) =", glGetTexParameteriv(GL_TEXTURE_WIDTH,p)
print p
print "glGetTexParameteriv(GL_TEXTURE_HEIGHT) =", glGetTexParameteriv(GL_TEXTURE_HEIGHT,p)
print p
