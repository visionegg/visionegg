# The Vision Egg: Text
#
# Copyright (C) 2001-2003 Andrew Straw.
# Copyright (C) 2005,2008 California Institute of Technology
#
# URL: <http://www.visionegg.org/>
#
# Distributed under the terms of the GNU Lesser General Public License
# (LGPL). See LICENSE.TXT that came with this file.

"""
Text stimuli.

"""

####################################################################
#
#        Import all the necessary packages
#
####################################################################

import logging
import logging.handlers

import VisionEgg.Core
import VisionEgg.Textures
import VisionEgg.ParameterTypes as ve_types

import VisionEgg.GL as gl # get all OpenGL stuff in one namespace

import pygame

try:
    import OpenGL.GLUT as glut
    have_glut = True
except:
    have_glut = False

_font_objects = {} # global variable to cache pygame font objects

def delete_font_objects():
    for key in _font_objects.keys():
        del _font_objects[key]

VisionEgg.Core.pygame_keeper.register_func_to_call_on_quit(delete_font_objects)

class Text(VisionEgg.Textures.TextureStimulus):
    """Single line of text rendered using pygame/SDL true type fonts.

    Parameters
    ==========
    anchor                -- specifies how position parameter is interpreted (String)
                             Inherited from VisionEgg.Textures.TextureStimulus
                             Default: lowerleft
    angle                 -- units: degrees, 0=right, 90=up (Real)
                             Inherited from VisionEgg.Textures.TextureStimulus
                             Default: 0.0
    color                 -- texture environment color. alpha ignored (if given) for max_alpha parameter (AnyOf(Sequence3 of Real or Sequence4 of Real))
                             Inherited from VisionEgg.Textures.TextureStimulus
                             Default: (1.0, 1.0, 1.0)
    depth_test            -- perform depth test? (Boolean)
                             Inherited from VisionEgg.Textures.TextureStimulus
                             Default: False
    ignore_size_parameter -- (Boolean)
                             Default: True
    mask                  -- optional masking function (Instance of <class 'VisionEgg.Textures.Mask2D'>)
                             Inherited from VisionEgg.Textures.TextureStimulus
                             Default: (determined at runtime)
    max_alpha             -- controls opacity. 1.0=copletely opaque, 0.0=completely transparent (Real)
                             Inherited from VisionEgg.Textures.TextureStimulus
                             Default: 1.0
    on                    -- draw stimulus? (Boolean)
                             Inherited from VisionEgg.Textures.TextureStimulus
                             Default: True
    position              -- units: eye coordinates (AnyOf(Sequence2 of Real or Sequence3 of Real or Sequence4 of Real))
                             Inherited from VisionEgg.Textures.TextureStimulus
                             Default: (0.0, 0.0)
    size                  -- defaults to texture data size (units: eye coordinates) (Sequence2 of Real)
                             Inherited from VisionEgg.Textures.TextureStimulus
                             Default: (determined at runtime)
    text                  -- (AnyOf(String or Unicode))
                             Default: the string to display
    texture               -- source of texture data (Instance of <class 'VisionEgg.Textures.Texture'>)
                             Inherited from VisionEgg.Textures.TextureStimulusBaseClass
                             Default: (determined at runtime)
    texture_mag_filter    -- OpenGL filter enum (Integer)
                             Inherited from VisionEgg.Textures.TextureStimulusBaseClass
                             Default: GL_LINEAR (9729)
    texture_min_filter    -- OpenGL filter enum (Integer)
                             Inherited from VisionEgg.Textures.TextureStimulusBaseClass
                             Default: (GL enum determined at runtime)
    texture_wrap_s        -- OpenGL texture wrap enum (Integer)
                             Inherited from VisionEgg.Textures.TextureStimulusBaseClass
                             Default: (GL enum determined at runtime)
    texture_wrap_t        -- OpenGL texture wrap enum (Integer)
                             Inherited from VisionEgg.Textures.TextureStimulusBaseClass
                             Default: (GL enum determined at runtime)

    Constant Parameters
    ===================
    font_name         -- (AnyOf(String or Unicode))
                         Default: (determined at runtime)
    font_size         -- (UnsignedInteger)
                         Default: 30
    internal_format   -- format with which OpenGL uses texture data (OpenGL data type enum) (Integer)
                         Inherited from VisionEgg.Textures.TextureStimulus
                         Default: GL_RGB (6407)
    mipmaps_enabled   -- Are mipmaps enabled? (Boolean)
                         Inherited from VisionEgg.Textures.TextureStimulus
                         Default: True
    shrink_texture_ok -- Allow automatic shrinking of texture if too big? (Boolean)
                         Inherited from VisionEgg.Textures.TextureStimulus
                         Default: False
    """

    parameters_and_defaults = {
        'text': ( 'the string to display', #changing this redraws texture, may cause slowdown
                  ve_types.AnyOf(ve_types.String,ve_types.Unicode)),
        'ignore_size_parameter':(True, # when true, draws text at 100% size
                                 ve_types.Boolean),
        }

    constant_parameters_and_defaults = {
        'font_size':(30,
                     ve_types.UnsignedInteger),
        'font_name':(None, # None = use default font
                     ve_types.AnyOf(ve_types.String,ve_types.Unicode)),
        }

    __slots__ = (
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
        fontobject_args = (cp.font_name,cp.font_size)
        if fontobject_args not in _font_objects:
            # make global cache of font objects
            fontobject = pygame.font.Font(*fontobject_args)
            _font_objects[fontobject_args] = fontobject
        # get font object from global cache
        self.font = _font_objects[fontobject_args]
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

if have_glut:

    class GlutTextBase(VisionEgg.Core.Stimulus):
        """DEPRECATED. Base class: don't instantiate this class directly.

        Base class that defines the common interface between the
        other glut-based text stimuli.

        Parameters
        ==========
        color     -- (AnyOf(Sequence3 of Real or Sequence4 of Real))
                     Default: (1.0, 1.0, 1.0)
        lowerleft -- (Sequence2 of Real)
                     Default: (320, 240)
        on        -- (Boolean)
                     Default: True
        text      -- (String)
                     Default: the string to display
        """

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

        def __init__(self,**kw):
            if not hasattr(VisionEgg.config,"_GAVE_GLUT_TEXT_DEPRECATION"):
                logger = logging.getLogger('VisionEgg.Text')
                logger.warning("Using GlutTextBase class.  This will be "
                               "removed in a future release. Use "
                               "VisionEgg.Text.Text instead.")
                VisionEgg.config._GAVE_GLUT_TEXT_DEPRECATION = 1
                VisionEgg.Core.Stimulus.__init__(self,**kw)

    class BitmapText(GlutTextBase):
        """DEPRECATED. Bitmap fonts from GLUT.

        Parameters
        ==========
        color     -- (AnyOf(Sequence3 of Real or Sequence4 of Real))
                     Inherited from GlutTextBase
                     Default: (1.0, 1.0, 1.0)
        font      -- (Integer)
                     Default: 5
        lowerleft -- (Sequence2 of Real)
                     Inherited from GlutTextBase
                     Default: (320, 240)
        on        -- (Boolean)
                     Inherited from GlutTextBase
                     Default: True
        text      -- (String)
                     Inherited from GlutTextBase
                     Default: the string to display
        """

        parameters_and_defaults = {
            'font':(glut.GLUT_BITMAP_TIMES_ROMAN_24,
                    ve_types.Integer),
            }

        def __init__(self,**kw):
            GlutTextBase.__init__(self,**kw)

        def draw(self):
            if self.parameters.on:
                gl.glDisable(gl.GL_TEXTURE_2D)
                gl.glDisable(gl.GL_BLEND)
                gl.glDisable(gl.GL_DEPTH_TEST)

                gl.glMatrixMode(gl.GL_MODELVIEW)
                gl.glPushMatrix()
                gl.glTranslate(self.parameters.lowerleft[0],self.parameters.lowerleft[1],0.0)

                c = self.parameters.color

                if len(c)==3:
                    gl.glColor3f(*c)
                elif len(c)==4:
                    gl.glColor4f(*c)
                gl.glDisable(gl.GL_TEXTURE_2D)

                gl.glRasterPos3f(0.0,0.0,0.0)
                for char in self.parameters.text:
                    glut.glutBitmapCharacter(self.parameters.font,ord(char))
                gl.glPopMatrix()

    class StrokeText(GlutTextBase):
        """DEPRECATED. Text rendered by GLUT using stroke fonts.

        Parameters
        ==========
        anti_aliasing -- (Boolean)
                         Default: True
        color         -- (AnyOf(Sequence3 of Real or Sequence4 of Real))
                         Inherited from GlutTextBase
                         Default: (1.0, 1.0, 1.0)
        font          -- (Integer)
                         Default: 0
        linewidth     -- (Real)
                         Default: 3.0
        lowerleft     -- (Sequence2 of Real)
                         Inherited from GlutTextBase
                         Default: (320, 240)
        on            -- (Boolean)
                         Inherited from GlutTextBase
                         Default: True
        orientation   -- (Real)
                         Default: 0.0
        text          -- (String)
                         Inherited from GlutTextBase
                         Default: the string to display
        """

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

        def __init__(self,**kw):
            raise NotImplementedError("There's something broken with StrokeText, and I haven't figured it out yet!")
            GlutTextBase.__init__(self,**kw)

        def draw(self):
            if self.parameters.on:
                gl.glDisable(gl.GL_TEXTURE_2D)
                gl.glDisable(gl.GL_DEPTH_TEST)

                gl.glMatrixMode(gl.GL_MODELVIEW)
                gl.glPushMatrix()
                gl.glTranslate(self.parameters.lowerleft[0],self.parameters.lowerleft[1],0.0)
                gl.glRotate(self.parameters.orientation,0.0,0.0,1.0)

                c = self.parameters.color
                if len(c)==3:
                    gl.glColor3f(*c)
                elif len(c)==4:
                    gl.glColor4f(*c)

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
                gl.glPopMatrix()
