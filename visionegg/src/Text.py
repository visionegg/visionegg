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

class TextStimulus(VisionEgg.Core.Stimulus):
    """Don't instantiate this class directly.

    It's a base class that defines the common interface between the
    other text stimuli."""
    parameters_and_defaults = {'on':1,
                               'color':(1.0,1.0,1.0,1.0),
                               'lowerleft':(320.0,240.),
                               'text':'the string to display'}
    def __init__(self,**kw):
        apply(VisionEgg.Core.Stimulus.__init__,(self,),kw)

class BitmapText(TextStimulus):
    parameters_and_defaults = {'font':GLUT_BITMAP_TIMES_ROMAN_24}
    def __init__(self,**kw):
        apply(TextStimulus.__init__,(self,),kw)

    def draw(self):
        if self.parameters.on:
            glDisable(GL_TEXTURE_2D)
            glDisable(GL_BLEND)
            glDisable(GL_DEPTH_TEST)

            glMatrixMode(GL_MODELVIEW)
            glLoadIdentity()
            glTranslate(self.parameters.lowerleft[0],self.parameters.lowerleft[1],0.0)

            c = self.parameters.color
            glColor(c[0],c[1],c[2],c[3])
            glDisable(GL_TEXTURE_2D)

            glRasterPos3f(0.0,0.0,0.0)
            for char in self.parameters.text:
                glutBitmapCharacter(self.parameters.font,ord(char))

class StrokeText(TextStimulus):
    parameters_and_defaults = {'font':GLUT_STROKE_ROMAN,
                               'orientation':0.0,
                               'linewidth':3.0, # in pixels
                               'anti_aliasing':1}
    def __init__(self,**kw):
        raise NotImplementedError("There's something broken with StrokeText, and I haven't figured it out yet!")
        apply(TextStimulus.__init__,(self,),kw)

    def draw(self):
        if self.parameters.on:
            glDisable(GL_TEXTURE_2D)
            glDisable(GL_DEPTH_TEST)

            glMatrixMode(GL_MODELVIEW)
            glLoadIdentity()
            glTranslate(self.parameters.lowerleft[0],self.parameters.lowerleft[1],0.0)
            glRotate(self.parameters.orientation,0.0,0.0,1.0)

            c = self.parameters.color
            glColor(c[0],c[1],c[2],c[3])

            glLineWidth(self.parameters.linewidth)

            if self.parameters.anti_aliasing:
                glEnable(GL_BLEND)
                glBlendFunc(GL_SRC_ALPHA,GL_ONE_MINUS_SRC_ALPHA)
                glEnable(GL_LINE_SMOOTH)
            else:
                glDisable(GL_BLEND)

##            # This code successfully draws a box...
##            glBegin(GL_QUADS)
##            glVertex2f(0.0,0.0)
##            glVertex2f(0.0,0.1)
##            glVertex2f(0.1,0.1)
##            glVertex2f(0.1,0.0)
##            glEnd()

            # But this code does not draw the string!?!
            for char in self.parameters.text:
                glutStrokeCharacter(self.parameters.font,ord(char))
