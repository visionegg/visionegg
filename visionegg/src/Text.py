"""Text stimuli"""

# Copyright (c) 2002-2003 Andrew Straw.  Distributed under the terms
# of the GNU Lesser General Public License (LGPL).

####################################################################
#
#        Import all the necessary packages
#
####################################################################

try:
    import logging
    import logging.handlers
except ImportError:
    import VisionEgg.py_logging as logging

import VisionEgg.Core
import VisionEgg.Textures
import VisionEgg.ParameterTypes as ve_types

import VisionEgg.GL as gl # get all OpenGL stuff in one namespace

import OpenGL.GLUT
glut = OpenGL.GLUT

import pygame

__version__ = VisionEgg.release_name
__cvs__ = '$Revision$'.split()[1]
__date__ = ' '.join('$Date$'.split()[1:3])
__author__ = 'Andrew Straw <astraw@users.sourceforge.net>'

# Use Python's bool constants if available, make aliases if not
try:
    True
except NameError:
    True = 1==1
    False = 1==0

class Text(VisionEgg.Textures.TextureStimulus):

    parameters_and_defaults = {
        'text': ( 'the string to display', #changing this redraws texture, may cause slowdown
                  ve_types.String),
        'ignore_size_parameter':(True, # when true, draws text at 100% size
                                 ve_types.Boolean),
        }
    
    constant_parameters_and_defaults = {
        'font_size':(30,
                     ve_types.UnsignedInteger),
        'font_name':(None, # None = use default font
                     ve_types.String),
        }
    
    __slots__ = VisionEgg.Textures.TextureStimulus.__slots__ + (
        'font',
        '_text',
        )
    
    def __init__(self,**kw):
        if not pygame.font:
            raise RuntimeError("no pygame font module")
        if not pygame.font.get_init():
            pygame.font.init()
            if not pygame.font.get_init():
                raise RuntimeError("pygame doesn't init")
        # override some defaults
        if 'internal_format' not in kw.keys():
            kw['internal_format'] = gl.GL_RGBA        
        if 'mipmaps_enabled' not in kw.keys():
            kw['mipmaps_enabled'] = 0
        if 'texture_min_filter' not in kw.keys():
            kw['texture_min_filter'] = gl.GL_LINEAR        
        VisionEgg.Textures.TextureStimulus.__init__(self,**kw)
        cp = self.constant_parameters
        self.font = pygame.font.Font(cp.font_name,cp.font_size)
        self._render_text()
        
    def _render_text(self):
        p = self.parameters
        rendered_surf = self.font.render(p.text, 1, (255,255,255)) # pygame.Surface object
        
        # we could use put_new_image for speed (or put_sub_image for more)
        p.texture = VisionEgg.Textures.Texture(rendered_surf)
        self._reload_texture()
        self._text = p.text # cache string so we know when to re-render
        if p.ignore_size_parameter:
            p.size = p.texture.size
        
    def draw(self):
        p = self.parameters
        if p.texture != self._using_texture: # self._using_texture is from TextureStimulusBaseClass
            raise RuntimeError("my texture has been modified, but it shouldn't be")
        if p.text != self._text: # new text
            self._render_text()
        if p.ignore_size_parameter:
            p.size = p.texture.size
        VisionEgg.Textures.TextureStimulus.draw(self) # call base class

class GlutTextBase(VisionEgg.Core.Stimulus):
    """Deprecated base class. Don't instantiate this class directly.

    Base class that defines the common interface between the
    other glut-based text stimuli."""

    parameters_and_defaults = {
        'on':(True,
              ve_types.Boolean),
        'color':((1.0,1.0,1.0),
                 ve_types.AnyOf(ve_types.Sequence3(ve_types.Real),
                                ve_types.Sequence4(ve_types.Real))),
        'lowerleft':((320,240),
                     ve_types.Sequence2(ve_types.Real)),
        'text':('the string to display',
                ve_types.String)}
    
    __slots__ = VisionEgg.Core.Stimulus.__slots__
    
    def __init__(self,**kw):
        if not hasattr(VisionEgg.config,"_GAVE_GLUT_TEXT_DEPRECATION"):
            logger = logging.getLogger('VisionEgg.Text')
            logger.warning("Using GlutTextBase class.  This will be "
                           "removed in a future release. Use "
                           "VisionEgg.Text.Text instead.")
            VisionEgg.config._GAVE_GLUT_TEXT_DEPRECATION = 1
            VisionEgg.Core.Stimulus.__init__(self,**kw)

class BitmapText(GlutTextBase):
    """This class is deprecated.  Don't use it anymore."""

    parameters_and_defaults = {
        'font':(glut.GLUT_BITMAP_TIMES_ROMAN_24,
                ve_types.Integer),
        }
    
    __slots__ = GlutTextBase.__slots__
    
    def __init__(self,**kw):
        GlutTextBase.__init__(self,**kw)

    def draw(self):
        if self.parameters.on:
            gl.glDisable(gl.GL_TEXTURE_2D)
            gl.glDisable(gl.GL_BLEND)
            gl.glDisable(gl.GL_DEPTH_TEST)

            gl.glMatrixMode(gl.GL_MODELVIEW)
            gl.glLoadIdentity()
            gl.glTranslate(self.parameters.lowerleft[0],self.parameters.lowerleft[1],0.0)

            c = self.parameters.color
            gl.glColorf(*c)
            gl.glDisable(gl.GL_TEXTURE_2D)

            gl.glRasterPos3f(0.0,0.0,0.0)
            for char in self.parameters.text:
                glut.glutBitmapCharacter(self.parameters.font,ord(char))

class StrokeText(GlutTextBase):

    parameters_and_defaults = {
        'font':(glut.GLUT_STROKE_ROMAN,
                ve_types.Integer),
        'orientation':(0.0,
                       ve_types.Real),
        'linewidth':(3.0, # pixels
                     ve_types.Real),
        'anti_aliasing':(True,
                         ve_types.Boolean),
        }
    
    __slots__ = GlutTextBase.__slots__
    
    def __init__(self,**kw):
        raise NotImplementedError("There's something broken with StrokeText, and I haven't figured it out yet!")
        GlutTextBase.__init__(self,**kw)

    def draw(self):
        if self.parameters.on:
            gl.glDisable(gl.GL_TEXTURE_2D)
            gl.glDisable(gl.GL_DEPTH_TEST)

            gl.glMatrixMode(gl.GL_MODELVIEW)
            gl.glLoadIdentity()
            gl.glTranslate(self.parameters.lowerleft[0],self.parameters.lowerleft[1],0.0)
            gl.glRotate(self.parameters.orientation,0.0,0.0,1.0)

            c = self.parameters.color
            gl.glColorf(*c)

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
