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

import VisionEgg.Core
from OpenGL.GL import *

# for Teapot
from OpenGL.GLUT import *

class Teapot(VisionEgg.Core.Stimulus):
    """A very simple stimulus because GLUT can draw a teapot"""
    parameters_and_defaults = {'yrot':0.0,
                               'on':1}

    def __init__(self,**kw):
        apply(VisionEgg.Core.Stimulus.__init__,(self,),kw)
        
    def draw(self):
        if self.parameters.on:
            glDisable(GL_TEXTURE_2D)
            glDisable(GL_BLEND)
            glDisable(GL_DEPTH_TEST)
            # clear modelview matrix
            glMatrixMode(GL_MODELVIEW)
            glLoadIdentity() 
            glTranslatef(0.0, 0.0, -6.0)
            glRotatef(self.parameters.yrot,0.0,1.0,0.0)
            glutSolidTeapot(0.5)
        
class Target2D(VisionEgg.Core.Stimulus):
    parameters_and_defaults = {'projection':None, # set in __init__
                               'on':1,
                               'color':(1.0,1.0,1.0,1.0),
                               'anti_aliasing':1,
                               'orientation':135.0,
                               'width':0.1,
                               'height':0.025,
                               'x':0.5,
                               'y':0.5}
                        
    def __init__(self,projection=None,**kw):
        apply(VisionEgg.Core.Stimulus.__init__,(self,),kw)
        # Make sure the projection is set
        if projection is not None:
            # Use the user-supplied projection
            self.parameters.projection = projection
        else:
            # No user-supplied projection, use the default. (Which is probably None.)
            if self.parameters.projection is None:
                # Since the default projection is None, set it to something useful.
                # Assume spot is in center of viewport.
                self.parameters.projection = VisionEgg.Core.OrthographicProjection(right=1.0,top=1.0)

    def draw(self):
        if self.parameters.on:
            glMatrixMode(GL_MODELVIEW)
            glLoadIdentity()
            glTranslate(self.parameters.x,self.parameters.y,0.0)
            glRotate(self.parameters.orientation,0.0,0.0,1.0)

            # before we clear the projection matrix, save its state
            self.parameters.projection.push_and_set_gl_projection()

            c = self.parameters.color
            glColor(c[0],c[1],c[2],c[3])
            glDisable(GL_TEXTURE_2D)
            glDisable(GL_BLEND)

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
                # We've already drawn a filled polygon (aliased),
                # now redraw the outline of the polygon (with anti-aliasing)

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

            glPopMatrix() # restore projection matrix
