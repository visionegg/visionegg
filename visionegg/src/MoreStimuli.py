"""More Stimuli for the Vision Egg library.
"""

# Copyright (c) 2001, 2002 Andrew Straw.  Distributed under the terms
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

# for Teapot
from OpenGL.GLUT import *

class Teapot(Stimulus):
    """A very simple stimulus because GLUT can draw a teapot"""
    def __init__(self):
        Stimulus.__init__(self)
        self.parameters.yrot = 0.0
        self.parameters.on = 1
        
    def draw(self):
        if self.parameters.on:
            glBlendFunc(GL_ONE,GL_ZERO) # If blending enabled, draw over everything            
            glLoadIdentity() # clear (hopefully the) modelview matrix
            glTranslatef(0.0, 0.0, -6.0)
            glRotatef(self.parameters.yrot,0.0,1.0,0.0)
            glutSolidTeapot(0.5)
        
class Target2D(Stimulus):
    def __init__(self):
        self.parameters = Parameters()
        self.parameters.on = 1
        self.parameters.projection_matrix = eye(4)
        self.parameters.orientation = 0.0
        self.parameters.width = 5.0
        self.parameters.height = 2.0
        self.parameters.x = 0.0
        self.parameters.y = 0.0
        self.parameters.color = (1.0,1.0,1.0,1.0)
        self.parameters.anti_aliasing = 1

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
            glBegin(GL_QUADS)
            glVertex3f(-w,-h, 0.0);
            glVertex3f( w,-h, 0.0);
            glVertex3f( w, h, 0.0);
            glVertex3f(-w, h, 0.0);
            glEnd() # GL_QUADS

            if self.parameters.anti_aliasing:
                # GL_POLYGON_SMOOTH doesn't seem to work
                # so we'll first draw a filled polygon (aliased)
                # then draw the outline of the polygon (with anti-aliasing)

                # Calculate coverage value for each pixel of outline
                # and store as alpha
                glEnable(GL_LINE_SMOOTH)
                # Now specify how to use the alpha value
                glBlendFunc(GL_SRC_ALPHA,GL_ONE_MINUS_SRC_ALPHA)
                glEnable(GL_BLEND)

                # Draw a second polygon in line mode, so the edges are anti-aliased
                glPolygonMode(GL_FRONT_AND_BACK,GL_LINE)
                glBegin(GL_QUADS)
                glVertex3f(-w,-h, 0.0);
                glVertex3f( w,-h, 0.0);
                glVertex3f( w, h, 0.0);
                glVertex3f(-w, h, 0.0);
                glEnd() # GL_QUADS

                # Set the polygon mode back to fill mode
                glPolygonMode(GL_FRONT_AND_BACK,GL_FILL)

            # Now restore everything
            glEnable(GL_TEXTURE_2D)
            glPopMatrix() # restore projection matrix
            glMatrixMode(GL_MODELVIEW)
            glPopMatrix() # restore modelview matrix
            glMatrixMode(matrix_mode)   # restore matrix state
