"""Text stimuli"""

# Copyright (c) 2002 Andrew Straw.  Distributed under the terms
# of the GNU Lesser General Public License (LGPL).

####################################################################
#
#        Import all the necessary packages
#
####################################################################

import string, types
import VisionEgg.Core

import OpenGL.GL
gl = OpenGL.GL

import OpenGL.GLUT
glut = OpenGL.GLUT

__version__ = VisionEgg.release_name
__cvs__ = string.split('$Revision$')[1]
__date__ = string.join(string.split('$Date$')[1:3], ' ')
__author__ = 'Andrew Straw <astraw@users.sourceforge.net>'

class TextStimulus(VisionEgg.Core.Stimulus):
    """Don't instantiate this class directly.

    It's a base class that defines the common interface between the
    other text stimuli."""
    parameters_and_defaults = {'on':(1,types.IntType),
                               'color':((1.0,1.0,1.0,1.0),types.TupleType),
                               'lowerleft':((320.0,240.),types.TupleType),
                               'text':('the string to display',types.StringType)}
    def __init__(self,**kw):
        apply(VisionEgg.Core.Stimulus.__init__,(self,),kw)

class BitmapText(TextStimulus):
    parameters_and_defaults = {'font':(glut.GLUT_BITMAP_TIMES_ROMAN_24,types.IntType)}
    def __init__(self,**kw):
        apply(TextStimulus.__init__,(self,),kw)

    def draw(self):
        if self.parameters.on:
            gl.glDisable(gl.GL_TEXTURE_2D)
            gl.glDisable(gl.GL_BLEND)
            gl.glDisable(gl.GL_DEPTH_TEST)

            gl.glMatrixMode(gl.GL_MODELVIEW)
            gl.glLoadIdentity()
            gl.glTranslate(self.parameters.lowerleft[0],self.parameters.lowerleft[1],0.0)

            c = self.parameters.color
            gl.glColor(c[0],c[1],c[2],c[3])
            gl.glDisable(gl.GL_TEXTURE_2D)

            gl.glRasterPos3f(0.0,0.0,0.0)
            for char in self.parameters.text:
                glut.glutBitmapCharacter(self.parameters.font,ord(char))

class StrokeText(TextStimulus):
    parameters_and_defaults = {'font':(glut.GLUT_STROKE_ROMAN,types.IntType),
                               'orientation':(0.0,types.FloatType),
                               'linewidth':(3.0,types.FloatType), # in pixels
                               'anti_aliasing':(1,types.IntType)}
    def __init__(self,**kw):
        raise NotImplementedError("There's something broken with StrokeText, and I haven't figured it out yet!")
        apply(TextStimulus.__init__,(self,),kw)

    def draw(self):
        if self.parameters.on:
            gl.glDisable(gl.GL_TEXTURE_2D)
            gl.glDisable(gl.GL_DEPTH_TEST)

            gl.glMatrixMode(gl.GL_MODELVIEW)
            gl.glLoadIdentity()
            gl.glTranslate(self.parameters.lowerleft[0],self.parameters.lowerleft[1],0.0)
            gl.glRotate(self.parameters.orientation,0.0,0.0,1.0)

            c = self.parameters.color
            gl.glColor(c[0],c[1],c[2],c[3])

            gl.glLineWidth(self.parameters.linewidth)

            if self.parameters.anti_aliasing:
                gl.glEnable(gl.GL_BLEND)
                gl.glBlendFunc(gl.GL_SRC_ALPHA,gl.GL_ONE_MINUS_SRC_ALPHA)
                gl.glEnable(gl.GL_LINE_SMOOTH)
            else:
                gl.glDisable(gl.GL_BLEND)

##            # This code successfully draws a box...
##            gl.glBegin(gl.GL_QUADS)
##            gl.glVertex2f(0.0,0.0)
##            gl.glVertex2f(0.0,0.1)
##            gl.glVertex2f(0.1,0.1)
##            gl.glVertex2f(0.1,0.0)
##            gl.glEnd()

            # But this code does not draw the string!?!
            for char in self.parameters.text:
                glut.glutStrokeCharacter(self.parameters.font,ord(char))
