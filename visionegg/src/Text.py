"""Text display for the Vision Egg library.
"""

# Copyright (c) 2002 Andrew Straw.  Distributed under the terms
# of the GNU General Public License (GPL).

####################################################################
#
#        Import all the necessary packages
#
####################################################################

import string
__version__ = string.split('$Revision$')[1]
__date__ = string.join(string.split('$Date$')[1:3], ' ')
__author__ = 'Andrew Straw <astraw@users.sourceforge.net>'

import VisionEgg.Core
from OpenGL.GL import *
from OpenGL.GLUT import *

class BitmapText(VisionEgg.Core.Stimulus):
    def __init__(self,text="Text",font=GLUT_BITMAP_TIMES_ROMAN_24,projection=None):
        self.parameters = VisionEgg.Core.Parameters()
        self.parameters.on = 1
        if projection is None:
            self.parameters.projection = VisionEgg.Core.OrthographicProjection(right=1.0,top=1.0)
        else:
            self.parameters.projection = projection
        self.parameters.x = 0.0
        self.parameters.y = 0.0
        self.parameters.color = (1.0,1.0,1.0,1.0)
        self.parameters.text = text
        self.parameters.font = font

    def draw(self):
        if self.parameters.on:
            glDisable(GL_TEXTURE_2D)
            glDisable(GL_BLEND)
            glDisable(GL_DEPTH_TEST)

            glMatrixMode(GL_MODELVIEW)
            glLoadIdentity()
            glTranslate(self.parameters.x,self.parameters.y,0.0)

            # save and set the projection matrix
            self.parameters.projection.push_and_set_gl_projection()

            c = self.parameters.color
            glColor(c[0],c[1],c[2],c[3])
            glDisable(GL_TEXTURE_2D)

            glRasterPos3f(0.0,0.0,0.0)
            for char in self.parameters.text:
                glutBitmapCharacter(self.parameters.font,ord(char))

            # Now restore everything
            glPopMatrix() # restore projection matrix

class StrokeText(VisionEgg.Core.Stimulus):
    def __init__(self,text="Text",font=GLUT_STROKE_ROMAN,projection=None):
        raise NotImplementedError("There's something broken with StrokeText, and I haven't figured it out yet!")
        self.parameters = VisionEgg.Core.Parameters()
        self.parameters.on = 1
        if projection is None:
            self.parameters.projection = VisionEgg.Core.OrthographicProjection(right=1.0,top=1.0)
        else:
            self.parameters.projection = projection
        self.parameters.orientation = 0.0
        self.parameters.x = 0.0
        self.parameters.y = 0.0
        self.parameters.color = (1.0,1.0,1.0,1.0)
        self.parameters.text = text
        self.parameters.font = font
        self.parameters.linewidth = 3.0
        self.parameters.antialiasing = 0

    def draw(self):
        if self.parameters.on:
            glDisable(GL_TEXTURE_2D)
            glDisable(GL_BLEND)
            glDisable(GL_DEPTH_TEST)

            # save and set the projection matrix
            self.parameters.projection.push_and_set_gl_projection()

            glMatrixMode(GL_MODELVIEW)
            glLoadIdentity()
            glTranslate(self.parameters.x,self.parameters.y,0.0)
            glRotate(self.parameters.orientation,0.0,0.0,1.0)

            c = self.parameters.color
            glColor(c[0],c[1],c[2],c[3])

            glLineWidth(self.parameters.linewidth)

            if self.parameters.antialiasing:
                glEnable(GL_BLEND)
                glBlendFunc(GL_SRC_ALPHA,GL_ONE_MINUS_SRC_ALPHA)
                glEnable(GL_LINE_SMOOTH)

            # This code successfully draws a box...
##            glBegin(GL_QUADS)
##            glVertex2f(0.0,0.0)
##            glVertex2f(0.0,0.1)
##            glVertex2f(0.1,0.1)
##            glVertex2f(0.1,0.0)
##            glEnd()

            # But this code does not draw the string!?!
            for char in self.parameters.text:
                glutStrokeCharacter(self.parameters.font,ord(char))

            glMatrixMode(GL_PROJECTION)
            glPopMatrix() # restore projection matrix
