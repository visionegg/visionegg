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
    parameters_and_defaults = {'angular_position':0.0,
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
            glRotatef(self.parameters.angular_position,0.0,1.0,0.0)
            glutSolidTeapot(0.5)
        
class Target2D(VisionEgg.Core.Stimulus):
    parameters_and_defaults = {'on':1,
                               'color':(1.0,1.0,1.0,1.0),
                               'anti_aliasing':1,
                               'orientation':135.0,
                               'center':(320.0,240.0),
                               'size':(64.0,16.0)}
                        
    def __init__(self,projection=None,**kw):
        apply(VisionEgg.Core.Stimulus.__init__,(self,),kw)

    def draw(self):
        if self.parameters.on:
            glMatrixMode(GL_MODELVIEW)
            glLoadIdentity()
            glTranslate(self.parameters.center[0],self.parameters.center[1],0.0)
            glRotate(self.parameters.orientation,0.0,0.0,1.0)

            c = self.parameters.color
            glColor(c[0],c[1],c[2],c[3])
            glDisable(GL_TEXTURE_2D)
            glDisable(GL_BLEND)

            w = self.parameters.size[0]/2.0
            h = self.parameters.size[1]/2.0
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
