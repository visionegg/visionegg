"""Vision Egg GL module -- lump all OpenGL names in one namespace"""

from OpenGL.GL import * # get everything from OpenGL.GL

try:
    GL_UNSIGNED_INT_8_8_8_8_REV
except NameError:
    GL_UNSIGNED_INT_8_8_8_8_REV = 0x8367 # XXX why doesn't PyOpenGL define this?!

