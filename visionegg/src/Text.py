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

from VisionEgg import *
from VisionEgg.Core import *
from OpenGL.GLUT import *

class BitmapText(Stimulus):
    def __init__(self,text="Text",font=GLUT_BITMAP_TIMES_ROMAN_24):
        self.parameters = Parameters()
        self.parameters.on = 1
        self.parameters.projection_matrix = eye(4)
        self.parameters.x = 0.0
        self.parameters.y = 0.0
        self.parameters.color = (1.0,1.0,1.0,1.0)
        self.parameters.text = text
        self.parameters.font = font

        # Now set self.parameters.projection_matrix

        # impose our own measurement grid on the viewport
        viewport_aspect = 4.0/3.0 # guess for the default
        pseudo_width = 100.0
        pseudo_height = 100.0 / viewport_aspect
        (l,r,b,t) = (-0.5*pseudo_width,0.5*pseudo_width,-0.5*pseudo_height,0.5*pseudo_height)
        z_near = -1.0
        z_far = 1.0
        
        matrix_mode = glGetIntegerv(GL_MATRIX_MODE)

        glMatrixMode(GL_PROJECTION)
        glPushMatrix()
        glLoadIdentity()
        glOrtho(l,r,b,t,z_near,z_far)
        self.parameters.projection_matrix = glGetFloatv(GL_PROJECTION_MATRIX)
        glPopMatrix()

        glMatrixMode(matrix_mode)

    def draw(self):
        if self.parameters.on:
            # save current matrix mode
            matrix_mode = glGetIntegerv(GL_MATRIX_MODE)

            glMatrixMode(GL_MODELVIEW)
            glPushMatrix() # save the current modelview to the stack
            glLoadIdentity()
            glTranslate(self.parameters.x,self.parameters.y,0.0)

            # before we clear the projection matrix, save its state
            glMatrixMode(GL_PROJECTION) 
            glPushMatrix()
            glLoadMatrixf(self.parameters.projection_matrix) # set the projection matrix

            c = self.parameters.color
            glColor(c[0],c[1],c[2],c[3])
            glDisable(GL_TEXTURE_2D)

            glRasterPos3f(0.0,0.0,0.0)
            for char in self.parameters.text:
                glutBitmapCharacter(self.parameters.font,ord(char))

            # Now restore everything
            glEnable(GL_TEXTURE_2D)
            glPopMatrix() # restore projection matrix
            glMatrixMode(GL_MODELVIEW)
            glPopMatrix() # restore modelview matrix
            glMatrixMode(matrix_mode)   # restore matrix state

class StrokeText(Stimulus):
    """This is has some scaling issues."""
    def __init__(self,text="Text"):
        self.parameters = Parameters()
        self.parameters.on = 1
        self.parameters.projection_matrix = eye(4)
        self.parameters.orientation = 0.0
        self.parameters.width = 5.0
        self.parameters.height = 2.0
        self.parameters.x = 0.0
        self.parameters.y = 0.0
        self.parameters.color = (1.0,1.0,1.0,1.0)
        self.parameters.text = text
        self.parameters.font = GLUT_STROKE_ROMAN
        self.parameters.linewidth = 3.0
        self.parameters.antialiasing = 1

        # Now set self.parameters.projection_matrix

        # impose our own measurement grid on the viewport
        viewport_aspect = 4.0/3.0 # guess for the default
        pseudo_width = 100.0
        pseudo_height = 100.0 / viewport_aspect
        (l,r,b,t) = (-0.5*pseudo_width,0.5*pseudo_width,-0.5*pseudo_height,0.5*pseudo_height)
        z_near = -1.0
        z_far = 1.0
        
        matrix_mode = glGetIntegerv(GL_MATRIX_MODE)

        glMatrixMode(GL_PROJECTION)
        glPushMatrix()
        glLoadIdentity()
        glOrtho(l,r,b,t,z_near,z_far)
        self.parameters.projection_matrix = glGetFloatv(GL_PROJECTION_MATRIX)
        glPopMatrix()

        glMatrixMode(matrix_mode)

    def draw(self):
        if self.parameters.on:
            # save current matrix mode
            matrix_mode = glGetIntegerv(GL_MATRIX_MODE)

            glMatrixMode(GL_MODELVIEW)
            glPushMatrix() # save the current modelview to the stack
            glLoadIdentity()
            glTranslate(self.parameters.x,self.parameters.y,0.0)
            glRotate(self.parameters.orientation,0.0,0.0,1.0)

            # before we clear the projection matrix, save its state
            glMatrixMode(GL_PROJECTION) 
            glPushMatrix()
            glLoadMatrixf(self.parameters.projection_matrix) # set the projection matrix

            c = self.parameters.color
            glColor(c[0],c[1],c[2],c[3])
            glDisable(GL_TEXTURE_2D)

            w = self.parameters.width/2.0
            h = self.parameters.height/2.0

            glLineWidth(self.parameters.linewidth)

            if self.parameters.antialiasing:
                glBlendFunc(GL_SRC_ALPHA,GL_ONE_MINUS_SRC_ALPHA)
                glEnable(GL_BLEND)
                glEnable(GL_LINE_SMOOTH)

            # This sorta works, but size is huge
            glTranslatef(-w,-h,0.0)
            for char in self.parameters.text:
                glutStrokeCharacter(self.parameters.font,ord(char))

            # Now restore everything
            glEnable(GL_TEXTURE_2D)
            glPopMatrix() # restore projection matrix
            glMatrixMode(GL_MODELVIEW)
            glPopMatrix() # restore modelview matrix
            glMatrixMode(matrix_mode)   # restore matrix state
