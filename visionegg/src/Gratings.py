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

import VisionEgg
import VisionEgg.Core
import VisionEgg.Textures
import VisionEgg.ParameterTypes as ve_types
import Numeric
import math, types, string
import OpenGL.GL as gl

try:
    import OpenGL.GL.ARB.multitexture # Not necessary for most Vision Egg functions
except ImportError:
    pass
else:
    for attr in dir(OpenGL.GL.ARB.multitexture):
        # put attributes from multitexture module in "gl" module dictionary
        # (Namespace overlap as you'd get OpenGL apps written in C)
        if attr[0:2] != "__":
            setattr(gl,attr,getattr(OpenGL.GL.ARB.multitexture,attr))
        
__version__ = VisionEgg.release_name
__cvs__ = string.split('$Revision$')[1]
__date__ = string.join(string.split('$Date$')[1:3], ' ')
__author__ = 'Andrew Straw <astraw@users.sourceforge.net>'

# Use Python's bool constants if available, make aliases if not
try:
    True
except NameError:
    True = 1==1
    False = 1==0

class LuminanceGratingCommon(VisionEgg.Core.Stimulus):
    """Base class with common code to all ways of drawing luminance gratings."""

    parameters_and_defaults = {
        'bit_depth':(8,
                     ve_types.UnsignedInteger),
        }
    
    def calculate_bit_depth_dependencies(self):
        """Calculate a number of parameters dependent on bit depth."""
        bit_depth_warning = 0
        current_bit_depth = None # unknown
        if gl.glGetIntegerv( gl.GL_RED_BITS ) < self.parameters.bit_depth:
            bit_depth_warning = 1
            current_bit_depth = gl.glGetIntegerv( gl.GL_RED_BITS )
        elif gl.glGetIntegerv( gl.GL_GREEN_BITS ) < self.parameters.bit_depth:
            bit_depth_warning = 1
            current_bit_depth = gl.glGetIntegerv( gl.GL_GREEN_BITS )
        elif gl.glGetIntegerv( gl.GL_BLUE_BITS ) < self.parameters.bit_depth:
            bit_depth_warning = 1
            current_bit_depth = gl.glGetIntegerv( gl.GL_BLUE_BITS )
        if bit_depth_warning:
            VisionEgg.Core.message.add(
                """Requested bit depth of %d, which is greater than
                your current OpenGL context supports (%d)."""%
                (self.parameters.bit_depth,current_bit_depth),
                level=VisionEgg.Core.Message.WARNING)
        if self.parameters.bit_depth == 8:
            self.gl_internal_format = gl.GL_LUMINANCE
            self.format = gl.GL_LUMINANCE
            self.gl_type = gl.GL_UNSIGNED_BYTE
            self.numeric_type = Numeric.UnsignedInt8
            self.max_int_val = float((2**8)-1)
        elif self.parameters.bit_depth == 12:
            self.gl_internal_format = gl.GL_LUMINANCE
            self.format = gl.GL_LUMINANCE
            self.gl_type = gl.GL_SHORT
            self.numeric_type = Numeric.Int16
            self.max_int_val = float((2**15)-1)
        elif self.parameters.bit_depth == 16:
            self.gl_internal_format = gl.GL_LUMINANCE
            self.format = gl.GL_LUMINANCE
            self.gl_type = gl.GL_INT
            self.numeric_type = Numeric.Int32
            try:
                self.max_int_val = float((2**31)-1)
            except OverflowError:
                self.max_int_val = float((2.**31.)-1)
        else:
            raise ValueError("supported bitdepths are 8, 12, and 16.")
        self.cached_bit_depth = self.parameters.bit_depth
        
class AlphaGratingCommon(VisionEgg.Core.Stimulus):
    """Base class with common code to all ways of drawing gratings in alpha.

    This class is currently not used by any other classes."""

    parameters_and_defaults = {
        'bit_depth':(8,
                     ve_types.UnsignedInteger),
        }
    
    def calculate_bit_depth_dependencies(self):
        """Calculate a number of parameters dependent on bit depth."""
        alpha_bit_depth = gl.glGetIntegerv( gl.GL_ALPHA_BITS )
        if alpha_bit_depth < self.parameters.bit_depth:
            VisionEgg.Core.message.add(
                """Requested bit depth of %d, which is greater than
                your current OpenGL context supports (%d)."""%
                (self.parameters.bit_depth,alpha_bit_depth),
                level=VisionEgg.Core.Message.WARNING)
        if self.parameters.bit_depth == 8:
            self.gl_internal_format = gl.GL_ALPHA
            self.format = gl.GL_ALPHA
            self.gl_type = gl.GL_UNSIGNED_BYTE
            self.numeric_type = Numeric.UnsignedInt8
            self.max_int_val = float((2**8)-1)
        elif self.parameters.bit_depth == 12:
            self.gl_internal_format = gl.GL_ALPHA
            self.format = gl.GL_ALPHA
            self.gl_type = gl.GL_SHORT
            self.numeric_type = Numeric.Int16
            self.max_int_val = float((2**15)-1)
        elif self.parameters.bit_depth == 16:
            self.gl_internal_format = gl.GL_ALPHA
            self.format = gl.GL_ALPHA
            self.gl_type = gl.GL_INT
            self.numeric_type = Numeric.Int32
            try:
                self.max_int_val = float((2**31)-1)
            except OverflowError:
                self.max_int_val = float((2.**31.)-1)
        else:
            raise ValueError("supported bitdepths are 8, 12, and 16.")
        self.cached_bit_depth = self.parameters.bit_depth
       
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
        'center':((320.0,240.0), # in eye coordinates
                  ve_types.Sequence2(ve_types.Real)),
        'depth':(None, # if not None, turns on depth testing and allows for occlusion
                 ve_types.Real),
        'size':((640.0,480.0), # in eye coordinates
                ve_types.Sequence2(ve_types.Real)),
        'spatial_freq':(1.0/128.0, # cycles/eye coord units
                        ve_types.Real), 
        'temporal_freq_hz':(5.0, # hz
                            ve_types.Real),
        't0_time_sec_absolute':(None,
                                ve_types.Real),
        'phase_at_t0':(0.0, # degrees [0.0-360.0]
                       ve_types.Real),
        'orientation':(0.0, # 0=right, 90=up
                       ve_types.Real),
        'num_samples':(512, # number of spatial samples, should be a power of 2
                       ve_types.Integer),
        'max_alpha':(1.0, # controls "opacity": 1.0 = completely opaque, 0.0 = completely transparent
                     ve_types.Real), 
        'color1':((1.0, 1.0, 1.0), # alpha is ignored (if given) -- use max_alpha parameter
                  ve_types.AnyOf(ve_types.Sequence3(ve_types.Real),
                                 ve_types.Sequence4(ve_types.Real))),
        'color2':(None, # alpha is ignored (if given) -- use max_alpha parameter
                  ve_types.AnyOf(ve_types.Sequence3(ve_types.Real),
                                 ve_types.Sequence4(ve_types.Real))),
        }
    
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

        if p.t0_time_sec_absolute is None:
            p.t0_time_sec_absolute = VisionEgg.time_func()

        self.calculate_bit_depth_dependencies()
        
        w = p.size[0]
        inc = w/float(p.num_samples)
        phase = (VisionEgg.time_func() - p.t0_time_sec_absolute)*p.temporal_freq_hz*-360.0 + p.phase_at_t0
        floating_point_sin = Numeric.sin(2.0*math.pi*p.spatial_freq*Numeric.arange(0.0,w,inc,'d')+(phase/180.0*math.pi))*0.5*p.contrast+p.pedestal
        floating_point_sin = Numeric.clip(floating_point_sin,0.0,1.0) # allow square wave generation if contrast > 1
        texel_data = (floating_point_sin*self.max_int_val).astype(self.numeric_type).tostring()

        # Because the MAX_TEXTURE_SIZE method is insensitive to the current
        # state of the video system, another check must be done using
        # "proxy textures".
        gl.glTexImage1D(gl.GL_PROXY_TEXTURE_1D,            # target
                        0,                                 # level
                        self.gl_internal_format,           # video RAM internal format: RGB
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
                        self.gl_internal_format,           # video RAM internal format: RGB
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

    def __del__(self):
        gl.glDeleteTextures( [self._texture_object_id] )

    def draw(self):
        p = self.parameters # shorthand
        if p.on:
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
            gl.glTranslate(p.center[0],
                           p.center[1],
                           0.0)
            gl.glRotate(p.orientation,0.0,0.0,1.0)

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
            else:
                gl.glTexEnvi(gl.GL_TEXTURE_ENV, gl.GL_TEXTURE_ENV_MODE, gl.GL_MODULATE)
            
            w = p.size[0]
            inc = w/float(p.num_samples)
            phase = (VisionEgg.time_func() - p.t0_time_sec_absolute)*p.temporal_freq_hz*-360.0 + p.phase_at_t0
            floating_point_sin = Numeric.sin(2.0*math.pi*p.spatial_freq*Numeric.arange(0.0,w,inc,'d')+(phase/180.0*math.pi))*0.5*p.contrast+p.pedestal
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

            gl.glColor(p.color1[0],p.color1[1],p.color1[2],p.max_alpha)
            
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

class NumSamplesTooLargeError( VisionEgg.Core.EggError ):
    """Overrides VisionEgg.Core.EggError"""
    pass
