"""Grating stimuli"""

# Copyright (c) 2002-2003 Andrew Straw.  Distributed under the terms
# of the GNU Lesser General Public License (LGPL).

all = ['AlphaGratingCommon', 'LuminanceGratingCommon',
       'NumSamplesTooLargeError', 'SinGrating2D', ]

####################################################################
#
#        Import all the necessary packages
#
####################################################################

try:
    import logging                              # available in Python 2.3
except ImportError:
    import VisionEgg.py_logging as logging      # use local copy otherwise

import VisionEgg
import VisionEgg.Core
import VisionEgg.Textures
import VisionEgg.ParameterTypes as ve_types
import Numeric
import math, types, string
import VisionEgg.GL as gl # get all OpenGL stuff in one namespace

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

def _get_type_info( bitdepth ):
    """Private helper function to calculate type info based on bit depth"""
    if bitdepth == 8:
        gl_type = gl.GL_UNSIGNED_BYTE
        numeric_type = Numeric.UnsignedInt8
        max_int_val = float((2**8)-1)
    elif bitdepth == 12:
        gl_type = gl.GL_SHORT
        numeric_type = Numeric.Int16
        max_int_val = float((2**15)-1)
    elif bitdepth == 16:
        gl_type = gl.GL_INT
        numeric_type = Numeric.Int32
        max_int_val = float((2.**31.)-1) # do as float to avoid overflow
    else:
        raise ValueError("supported bitdepths are 8, 12, and 16.")
    return gl_type, numeric_type, max_int_val

class LuminanceGratingCommon(VisionEgg.Core.Stimulus):
    """Base class with common code to all ways of drawing luminance gratings."""

    parameters_and_defaults = {
        'bit_depth':(8,
                     ve_types.UnsignedInteger),
        }
    
    __slots__ = VisionEgg.Core.Stimulus.__slots__ + (
        'gl_internal_format',
        'format',
        'gl_type',
        'numeric_type',
        'max_int_val',
        'cached_bit_depth',
        )

    def calculate_bit_depth_dependencies(self):
        """Calculate a number of parameters dependent on bit depth."""
        bit_depth_warning = False
        p = self.parameters # shorthand
        
        red_bits = gl.glGetIntegerv( gl.GL_RED_BITS )
        green_bits = gl.glGetIntegerv( gl.GL_GREEN_BITS )
        blue_bits = gl.glGetIntegerv( gl.GL_BLUE_BITS )
        min_bits = min( (red_bits,green_bits,blue_bits) )
        if min_bits < p.bit_depth:
            logger = logging.getLogger('VisionEgg.Gratings')
            logger.warning("Requested bit depth of %d, which is "
                           "greater than your current OpenGL context "
                           "supports (%d)."% (p.bit_depth,min_bits))
        self.gl_internal_format = gl.GL_LUMINANCE
        self.format = gl.GL_LUMINANCE
        self.gl_type, self.numeric_type, self.max_int_val = _get_type_info( p.bit_depth )
        self.cached_bit_depth = p.bit_depth
        
class AlphaGratingCommon(VisionEgg.Core.Stimulus):
    """Base class with common code to all ways of drawing gratings in alpha.

    This class is currently not used by any other classes."""

    parameters_and_defaults = {
        'bit_depth':(8,
                     ve_types.UnsignedInteger),
        }
    
    __slots__ = VisionEgg.Core.Stimulus.__slots__ + (
        'gl_internal_format',
        'format',
        'gl_type',
        'numeric_type',
        'max_int_val',
        'cached_bit_depth',
        )

    def calculate_bit_depth_dependencies(self):
        """Calculate a number of parameters dependent on bit depth."""
        p = self.parameters # shorthand
        alpha_bit_depth = gl.glGetIntegerv( gl.GL_ALPHA_BITS )
        if alpha_bit_depth < p.bit_depth:
            logger = logging.getLogger('VisionEgg.Gratings')
            logger.warning("Requested bit depth of %d, which is "
                           "greater than your current OpenGL context "
                           "supports (%d)."% (p.bit_depth,min_bits))
        self.gl_internal_format = gl.GL_ALPHA
        self.format = gl.GL_ALPHA
        self.gl_type, self.numeric_type, self.max_int_val = _get_type_info( p.bit_depth )
        self.cached_bit_depth = p.bit_depth
       
class SinGrating2D(LuminanceGratingCommon):
    """Sine wave grating stimulus

    This is a general-purpose, realtime sine-wave luminace grating
    generator. To acheive an arbitrary orientation, this class rotates
    a textured quad.  To draw a grating with sides that always remain
    horizontal and vertical, draw a large grating in a small viewport.
    (The viewport will clip anything beyond its edges.)"""

    parameters_and_defaults = {
        'on':(True,
              ve_types.Boolean),
        'mask':(None, # allows window onto otherwise (tilted) rectangular grating
                ve_types.Instance(VisionEgg.Textures.Mask2D)),
        'contrast':(1.0,
                    ve_types.Real),
        'pedestal':(0.5,
                    ve_types.Real),
        'position':((320.0,240.0), # in eye coordinates
                    ve_types.Sequence2(ve_types.Real)),
        'anchor':('center',
                  ve_types.String),
        'depth':(None, # if not None, turns on depth testing and allows for occlusion
                 ve_types.Real),
        'size':((640.0,480.0), # in eye coordinates
                ve_types.Sequence2(ve_types.Real)),
        'spatial_freq':(1.0/128.0, # cycles/eye coord units
                        ve_types.Real), 
        'temporal_freq_hz':(5.0, # hz
                            ve_types.Real),
        't0_time_sec_absolute':(None, # Will be assigned during first call to draw()
                                ve_types.Real),
        'ignore_time':(False, # ignore temporal frequency variable - allow control purely with phase_at_t0
                       ve_types.Boolean),
        'phase_at_t0':(0.0, # degrees [0.0-360.0]
                       ve_types.Real),
        'orientation':(0.0, # 0=right, 90=up
                       ve_types.Real),
        'num_samples':(512, # number of spatial samples, should be a power of 2
                       ve_types.UnsignedInteger),
        'max_alpha':(1.0, # controls "opacity": 1.0 = completely opaque, 0.0 = completely transparent
                     ve_types.Real), 
        'color1':((1.0, 1.0, 1.0), # alpha is ignored (if given) -- use max_alpha parameter
                  ve_types.AnyOf(ve_types.Sequence3(ve_types.Real),
                                 ve_types.Sequence4(ve_types.Real))),
        'color2':(None, # perform interpolation with color1 in RGB space.
                  ve_types.AnyOf(ve_types.Sequence3(ve_types.Real),
                                 ve_types.Sequence4(ve_types.Real))),
        'recalculate_phase_tolerance':(None, # only recalculate texture when phase is changed by more than this amount, None for always recalculate. (Saves time.)
                                       ve_types.Real), 
        'center':(None,  # DEPRECATED -- don't use
                  ve_types.Sequence2(ve_types.Real)),
        }
    
    __slots__ = LuminanceGratingCommon.__slots__ + (
        '_texture_object_id',
        '_last_phase',
        )

    def __init__(self,**kw):
        LuminanceGratingCommon.__init__(self,**kw)

        p = self.parameters # shorthand
        
        self._texture_object_id = gl.glGenTextures(1)
        if p.mask:
            gl.glActiveTextureARB(gl.GL_TEXTURE0_ARB)
        gl.glBindTexture(gl.GL_TEXTURE_1D,self._texture_object_id)
        
        # Do error-checking on texture to make sure it will load
        max_dim = gl.glGetIntegerv(gl.GL_MAX_TEXTURE_SIZE)
        if p.num_samples > max_dim:
            raise NumSamplesTooLargeError("Grating num_samples too large for video system.\nOpenGL reports maximum size of %d"%(max_dim,))

        self.calculate_bit_depth_dependencies()
        
        w = p.size[0]
        inc = w/float(p.num_samples)
        phase = 0.0 # this data won't get used - don't care about phase
        self._last_phase = phase
        floating_point_sin = Numeric.sin(2.0*math.pi*p.spatial_freq*Numeric.arange(0.0,w,inc,typecode=Numeric.Float)+(phase/180.0*math.pi))*0.5*p.contrast+p.pedestal
        floating_point_sin = Numeric.clip(floating_point_sin,0.0,1.0) # allow square wave generation if contrast > 1
        texel_data = (floating_point_sin*self.max_int_val).astype(self.numeric_type).tostring()

        # Because the MAX_TEXTURE_SIZE method is insensitive to the current
        # state of the video system, another check must be done using
        # "proxy textures".
        gl.glTexImage1D(gl.GL_PROXY_TEXTURE_1D,            # target
                        0,                                 # level
                        self.gl_internal_format,           # video RAM internal format
                        p.num_samples,                     # width
                        0,                                 # border
                        self.format,                       # format of texel data
                        self.gl_type,                      # type of texel data
                        texel_data)                        # texel data (irrelevant for proxy)
        if gl.glGetTexLevelParameteriv(gl.GL_PROXY_TEXTURE_1D,0,gl.GL_TEXTURE_WIDTH) == 0:
            raise NumSamplesTooLargeError("Grating num_samples is too wide for your video system!")
        
        # If we got here, it worked and we can load the texture for real.
        gl.glTexImage1D(gl.GL_TEXTURE_1D,                  # target
                        0,                                 # level
                        self.gl_internal_format,           # video RAM internal format
                        p.num_samples,                     # width
                        0,                                 # border
                        self.format,                       # format of texel data
                        self.gl_type,                      # type of texel data
                        texel_data)                        # texel data
        
        # Set texture object defaults
        gl.glTexParameteri(gl.GL_TEXTURE_1D,gl.GL_TEXTURE_WRAP_S,gl.GL_CLAMP_TO_EDGE)
        gl.glTexParameteri(gl.GL_TEXTURE_1D,gl.GL_TEXTURE_WRAP_T,gl.GL_CLAMP_TO_EDGE)
        gl.glTexParameteri(gl.GL_TEXTURE_1D,gl.GL_TEXTURE_MAG_FILTER,gl.GL_LINEAR)
        gl.glTexParameteri(gl.GL_TEXTURE_1D,gl.GL_TEXTURE_MIN_FILTER,gl.GL_LINEAR)

        if p.color2 is not None:
            if VisionEgg.Core.gl_renderer == 'ATi Rage 128 Pro OpenGL Engine' and VisionEgg.Core.gl_version == '1.1 ATI-1.2.22':
                logger = logging.getLogger('VisionEgg.Gratings')
                logger.warning("Your video card and driver have known "
                               "bugs which prevent them from rendering "
                               "color gratings properly.")

    def __del__(self):
        gl.glDeleteTextures( [self._texture_object_id] )

    def draw(self):
        p = self.parameters # shorthand
        if p.center is not None:
            if not hasattr(SinGrating2D,"_gave_center_warning"):
                logger = logging.getLogger('VisionEgg.Gratings')
                logger.warning("center parameter of SinGrating2D class "
                               "is deprecated and will stop being "
                               "supported. Use 'position' instead "
                               "with anchor set to 'center'.")
                SinGrating2D._gave_center_warning = True
            p.anchor = 'center'
            p.position = p.center[0], p.center[1] # copy values (don't copy ref to tuple)
        if p.on:
            # calculate center
            center = VisionEgg._get_center(p.position,p.anchor,p.size)
            if p.mask:
                gl.glActiveTextureARB(gl.GL_TEXTURE0_ARB)
            gl.glBindTexture(gl.GL_TEXTURE_1D,self._texture_object_id)
            
            gl.glEnable(gl.GL_TEXTURE_1D)
            gl.glDisable(gl.GL_TEXTURE_2D)
            if p.bit_depth != self.cached_bit_depth:
                self.calculate_bit_depth_dependencies()
                    
            # Clear the modeview matrix
            gl.glMatrixMode(gl.GL_MODELVIEW)
            gl.glLoadIdentity()
            # Rotate about the center of the texture
            gl.glTranslate(center[0],
                           center[1],
                           0)
            gl.glRotate(p.orientation,0,0,1)

            if p.depth is None:
                gl.glDisable(gl.GL_DEPTH_TEST)
                depth = 0.0
            else:
                gl.glEnable(gl.GL_DEPTH_TEST)
                depth = p.depth

            # allow max_alpha value to control blending
            gl.glEnable( gl.GL_BLEND )
            gl.glBlendFunc( gl.GL_SRC_ALPHA, gl.GL_ONE_MINUS_SRC_ALPHA )

            if p.color2:
                gl.glTexEnvi(gl.GL_TEXTURE_ENV, gl.GL_TEXTURE_ENV_MODE, gl.GL_BLEND)
                gl.glTexEnvfv(gl.GL_TEXTURE_ENV, gl.GL_TEXTURE_ENV_COLOR, p.color2)
                ## alpha is ignored because the texture base internal format is luminance
            else:
                gl.glTexEnvi(gl.GL_TEXTURE_ENV, gl.GL_TEXTURE_ENV_MODE, gl.GL_MODULATE)
            
            if p.t0_time_sec_absolute is None and not p.ignore_time:
                p.t0_time_sec_absolute = VisionEgg.time_func()

            w = p.size[0]
            inc = w/float(p.num_samples)
            if p.ignore_time:
                phase = p.phase_at_t0
            else:
                t_var = VisionEgg.time_func() - p.t0_time_sec_absolute
                phase = t_var*p.temporal_freq_hz*-360.0 + p.phase_at_t0
            if p.recalculate_phase_tolerance is None or abs(self._last_phase - phase) > p.recalculate_phase_tolerance:
                self._last_phase = phase # we're re-drawing the phase at this angle
                floating_point_sin = Numeric.sin(2.0*math.pi*p.spatial_freq*Numeric.arange(0.0,w,inc,typecode=Numeric.Float)+(phase/180.0*math.pi))*0.5*p.contrast+p.pedestal
                floating_point_sin = Numeric.clip(floating_point_sin,0.0,1.0) # allow square wave generation if contrast > 1
                texel_data = (floating_point_sin*self.max_int_val).astype(self.numeric_type).tostring()

                gl.glTexSubImage1D(gl.GL_TEXTURE_1D, # target
                                   0,                # level
                                   0,                # x offset
                                   p.num_samples,    # width
                                   self.format,      # format of new texel data
                                   self.gl_type,     # type of new texel data
                                   texel_data)       # new texel data
            
            h_w = p.size[0]/2.0
            h_h = p.size[1]/2.0

            l = -h_w
            r = h_w
            b = -h_h
            t = h_h

            # in the case of only color1,
            # the texel data multiplies color1 to produce a color

            # with color2,
            # the texel data linearly interpolates between color1 and color2
            
            gl.glColorf(p.color1[0],p.color1[1],p.color1[2],p.max_alpha)
            
            if p.mask:
                p.mask.draw_masked_quad(0.0,1.0,0.0,1.0, # l,r,b,t for texture coordinates
                                        l,r,b,t, # l,r,b,t in eye coordinates
                                        depth ) # also in eye coordinates
            else:
                # draw unmasked quad
                gl.glBegin(gl.GL_QUADS)
                
                gl.glTexCoord2f(0.0,0.0)
                gl.glVertex3f(l,b,depth)

                gl.glTexCoord2f(1.0,0.0)
                gl.glVertex3f(r,b,depth)

                gl.glTexCoord2f(1.0,1.0)
                gl.glVertex3f(r,t,depth)

                gl.glTexCoord2f(0.0,1.0)
                gl.glVertex3f(l,t,depth)
                gl.glEnd() # GL_QUADS
            
            gl.glDisable(gl.GL_TEXTURE_1D)

class NumSamplesTooLargeError( RuntimeError ):
    pass
