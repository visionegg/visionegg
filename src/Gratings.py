"""Grating stimuli"""

# Copyright (c) 2002 Andrew Straw.  Distributed under the terms of the
# GNU Lesser General Public License (LGPL).

####################################################################
#
#        Import all the necessary packages
#
####################################################################

import VisionEgg
import VisionEgg.Core
import VisionEgg.Textures # ensures gl.GL_CLAMP_TO_EDGE is set
import Numeric
import math, types, string
import OpenGL.GL
gl = OpenGL.GL

__version__ = VisionEgg.release_name
__cvs__ = string.split('$Revision$')[1]
__date__ = string.join(string.split('$Date$')[1:3], ' ')
__author__ = 'Andrew Straw <astraw@users.sourceforge.net>'

class LuminanceGratingCommon(VisionEgg.Core.Stimulus):
    """Base class with common code to all ways of drawing luminance gratings."""

    parameters_and_defaults = {'bit_depth':(8,types.IntType)}
    
    def __init__(self,**kw):
        apply(VisionEgg.Core.Stimulus.__init__,(self,),kw)
        self.red_bits = gl.glGetIntegerv( gl.GL_RED_BITS )
        
    def calculate_bit_depth_dependencies(self):
        """Calculate a number of parameters dependent on bit depth."""
        if self.red_bits < self.parameters.bit_depth:
            VisionEgg.Core.message.add(
                """Requesting a bit depth of %d, which is greater than
                your current OpenGL context supports (%d)."""%
                (self.parameters.bit_depth,self.red_bits),
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
        
class SinGrating2D(LuminanceGratingCommon):
    """Sine wave grating stimulus

    This is a general-purpose, realtime sine-wave luminace grating
    generator. To acheive an arbitrary orientation, this class rotates
    a textured quad.  To draw a grating with sides that always remain
    horizontal and vertical, draw a large grating in a small viewport.
    The viewport will clip anything beyond its edges. Alternatively,
    try one of the "SquareSides" gratings in this module."""

    parameters_and_defaults = {'on':(1,types.IntType),
                               'contrast':(1.0,types.FloatType),
                               'center':((320.0,240.0),types.TupleType),
                               'size':((640.0,480.0),types.TupleType), # in eye coordinates
                               'spatial_freq':(1.0/128.0,types.FloatType), # cycles/eye coord units
                               'temporal_freq_hz':(5.0,types.FloatType), # hz
                               't0_time_sec_absolute':(None,types.FloatType),
                               'phase_at_t0':(0.0,types.FloatType), # degrees [0.0-360.0]
                               'orientation':(0.0,types.FloatType), # 0=right, 90=down
                               'num_samples':(512, types.IntType) # number of spatial samples, should be a power of 2
                               }
    
    def __init__(self,projection = None,**kw):
        apply(LuminanceGratingCommon.__init__,(self,),kw)

        self.texture_object = gl.glGenTextures(1)
        gl.glBindTexture(gl.GL_TEXTURE_1D,self.texture_object)
        
        # Do error-checking on texture to make sure it will load
        max_dim = gl.glGetIntegerv(gl.GL_MAX_TEXTURE_SIZE)
        if self.parameters.num_samples > max_dim:
            raise NumSamplesTooLargeError("Grating num_samples too large for video system.\nOpenGL reports maximum size of %d"%(max_dim,))

        if self.parameters.t0_time_sec_absolute is None:
            self.parameters.t0_time_sec_absolute = VisionEgg.timing_func()

        self.calculate_bit_depth_dependencies()
        
        w = self.parameters.size[0]
        inc = w/float(self.parameters.num_samples)
        phase = (VisionEgg.timing_func() - self.parameters.t0_time_sec_absolute)*self.parameters.temporal_freq_hz*-360.0 + self.parameters.phase_at_t0
        floating_point_sin = Numeric.sin(2.0*math.pi*self.parameters.spatial_freq*Numeric.arange(0.0,w,inc,'d')+(phase/180.0*math.pi))*0.5*self.parameters.contrast+0.5
        floating_point_sin = Numeric.clip(floating_point_sin,0.0,1.0) # allow square wave generation if contrast > 1
        texel_data = (floating_point_sin*self.max_int_val).astype(self.numeric_type).tostring()

        # Because the MAX_TEXTURE_SIZE method is insensitive to the current
        # state of the video system, another check must be done using
        # "proxy textures".
        gl.glTexImage1D(gl.GL_PROXY_TEXTURE_1D,            # target
                     0,                              # level
                     self.gl_internal_format,                   # video RAM internal format: RGB
                     self.parameters.num_samples,    # width
                     0,                              # border
                     self.format,                   # format of image data
                     self.gl_type,               # type of image data
                     texel_data)                     # texel data
        if gl.glGetTexLevelParameteriv(gl.GL_PROXY_TEXTURE_1D,0,gl.GL_TEXTURE_WIDTH) == 0:
            raise NumSamplesTooLargeError("Grating num_samples is too wide for your video system!")
        
        # If we got here, it worked and we can load the texture for real.
        gl.glTexImage1D(gl.GL_TEXTURE_1D,            # target
                     0,                              # level
                     self.gl_internal_format,                   # video RAM internal format: RGB
                     self.parameters.num_samples,    # width
                     0,                              # border
                     self.format,                   # format of image data
                     self.gl_type,               # type of image data
                     texel_data)                     # texel data
        # Set some texture object defaults
        gl.glTexParameteri(gl.GL_TEXTURE_1D,gl.GL_TEXTURE_WRAP_S,gl.GL_CLAMP_TO_EDGE)
        gl.glTexParameteri(gl.GL_TEXTURE_1D,gl.GL_TEXTURE_WRAP_T,gl.GL_CLAMP_TO_EDGE)
        gl.glTexParameteri(gl.GL_TEXTURE_1D,gl.GL_TEXTURE_MAG_FILTER,gl.GL_LINEAR)
        gl.glTexParameteri(gl.GL_TEXTURE_1D,gl.GL_TEXTURE_MIN_FILTER,gl.GL_LINEAR)

    def get_texel_data(self):
        w = self.parameters.size[0]
        inc = w/float(self.parameters.num_samples)
        phase = (VisionEgg.timing_func() - self.parameters.t0_time_sec_absolute)*self.parameters.temporal_freq_hz*-360.0 + self.parameters.phase_at_t0
        floating_point_sin = Numeric.sin(2.0*math.pi*self.parameters.spatial_freq*Numeric.arange(0.0,w,inc,'d')+(phase/180.0*math.pi))*0.5*self.parameters.contrast+0.5
        floating_point_sin = Numeric.clip(floating_point_sin,0.0,1.0) # allow square wave generation if contrast > 1
        texel_data = (floating_point_sin*self.max_int_val).astype(self.numeric_type).tostring()
        return texel_data

    def convert_texel_data_to_array(self,texel_data):
        return Numeric.fromstring(texel_data,self.numeric_type)

    def get_raw_array(self):
        w = self.parameters.size[0]
        inc = w/float(self.parameters.num_samples)
        phase = (VisionEgg.timing_func() - self.parameters.t0_time_sec_absolute)*self.parameters.temporal_freq_hz*-360.0 + self.parameters.phase_at_t0
        floating_point_sin = Numeric.sin(2.0*math.pi*self.parameters.spatial_freq*Numeric.arange(0.0,w,inc,'d')+(phase/180.0*math.pi))*0.5*self.parameters.contrast+0.5
        floating_point_sin = Numeric.clip(floating_point_sin,0.0,1.0) # allow square wave generation if contrast > 1
        raw_array = (floating_point_sin*self.max_int_val).astype(self.numeric_type)
        return raw_array

    def draw(self):
        if self.parameters.on:
            if self.parameters.bit_depth != self.cached_bit_depth:
                self.calculate_bit_depth_dependencies()
                    
            # Clear the modeview matrix
            gl.glMatrixMode(gl.GL_MODELVIEW)
            gl.glLoadIdentity()
            gl.glTranslate(self.parameters.center[0],self.parameters.center[1],0.0) # Rotate about the center of the texture
            gl.glRotate(self.parameters.orientation,0.0,0.0,-1.0)
            gl.glTranslate(-self.parameters.center[0],-self.parameters.center[1],0.0) # Rotate about the center of the texture
            
            gl.glDisable(gl.GL_DEPTH_TEST)
            gl.glDisable(gl.GL_BLEND)
            gl.glDisable(gl.GL_TEXTURE_2D)
            gl.glEnable(gl.GL_TEXTURE_1D)
            gl.glBindTexture(gl.GL_TEXTURE_1D,self.texture_object)

            w = self.parameters.size[0]
            inc = w/float(self.parameters.num_samples)
            phase = (VisionEgg.timing_func() - self.parameters.t0_time_sec_absolute)*self.parameters.temporal_freq_hz*-360.0 + self.parameters.phase_at_t0
            floating_point_sin = Numeric.sin(2.0*math.pi*self.parameters.spatial_freq*Numeric.arange(0.0,w,inc,'d')+(phase/180.0*math.pi))*0.5*self.parameters.contrast+0.5
            floating_point_sin = Numeric.clip(floating_point_sin,0.0,1.0) # allow square wave generation if contrast > 1
            texel_data = (floating_point_sin*self.max_int_val).astype(self.numeric_type).tostring()
        
            gl.glTexSubImage1D(gl.GL_TEXTURE_1D, # target
                            0, # level
                            0, # x offset
                            self.parameters.num_samples, # width
                            self.format, # data format
                            self.gl_type, # data type
                            texel_data)
            
            gl.glTexEnvi(gl.GL_TEXTURE_ENV, gl.GL_TEXTURE_ENV_MODE, gl.GL_REPLACE)

            h_w = self.parameters.size[0]/2.0
            h_h = self.parameters.size[1]/2.0
            l = self.parameters.center[0]-h_w
            r = self.parameters.center[0]+h_w
            b = self.parameters.center[1]-h_h
            t = self.parameters.center[1]+h_h

            gl.glBegin(gl.GL_QUADS)
            gl.glTexCoord2f(0.0,0.0)
            gl.glVertex2f(l,b)

            gl.glTexCoord2f(1.0,0.0)
            gl.glVertex2f(r,b)

            gl.glTexCoord2f(1.0,1.0)
            gl.glVertex2f(r,t)

            gl.glTexCoord2f(0.0,1.0)
            gl.glVertex2f(l,t)
            gl.glEnd() # GL_QUADS
            
            gl.glDisable(gl.GL_TEXTURE_1D)

class SinGrating2DSquareSidesFast(LuminanceGratingCommon):
    """Fast sine wave grating stimulus with square sides.

    Assumes integer number of cycles for speed, which results in
    discontinuity in grating when non-integer number of cycles
    used."""
    
    parameters_and_defaults = {'on':(1,types.IntType),
                               'contrast':(1.0,types.FloatType),
                               'lowerleft':((0.0,0.0),types.TupleType),
                               'size':((640.0,640.0),types.TupleType),
                               'spatial_freq':(1.0/128.0,types.FloatType), # cycles/eye coord unit (default viewport projection = cycles/pixel)
                               'temporal_freq_hz':(5.0,types.FloatType), # hz
                               't0_time_sec_absolute':(None,types.FloatType),
                               'phase_at_t0':(0.0,types.FloatType), # degrees [0.0-360.0]
                               'orientation':(0.0,types.FloatType), # 0=right, 90=down
                               'num_samples':(512, types.IntType) # number of spatial samples, should be a power of 2
                               }
    
    def __init__(self,projection = None,**kw):
        apply(LuminanceGratingCommon.__init__,(self,),kw)

        self.texture_object = gl.glGenTextures(1)
        gl.glBindTexture(gl.GL_TEXTURE_1D,self.texture_object)
        
        # Do error-checking on texture to make sure it will load
        max_dim = gl.glGetIntegerv(gl.GL_MAX_TEXTURE_SIZE)
        if self.parameters.num_samples > max_dim:
            raise NumSamplesTooLargeError("Grating num_samples too large for video system.\nOpenGL reports maximum size of %d"%(max_dim,))

        if self.parameters.t0_time_sec_absolute is None:
            self.parameters.t0_time_sec_absolute = VisionEgg.timing_func()

        self.calculate_bit_depth_dependencies()
        
        w = self.parameters.size[0]
        inc = w/float(self.parameters.num_samples)
        phase = (VisionEgg.timing_func() - self.parameters.t0_time_sec_absolute)*self.parameters.temporal_freq_hz*-360.0 + self.parameters.phase_at_t0
        floating_point_sin = Numeric.sin(2.0*math.pi*self.parameters.spatial_freq*Numeric.arange(0.0,w,inc,'d')+(phase/180.0*math.pi))*0.5*self.parameters.contrast+0.5
        floating_point_sin = Numeric.clip(floating_point_sin,0.0,1.0) # allow square wave generation if contrast > 1
        texel_data = (floating_point_sin*self.max_int_val).astype(self.numeric_type).tostring()

        # Because the MAX_TEXTURE_SIZE method is insensitive to the current
        # state of the video system, another check must be done using
        # "proxy textures".
        gl.glTexImage1D(gl.GL_PROXY_TEXTURE_1D,            # target
                     0,                              # level
                     self.gl_internal_format,                   # video RAM internal format: RGB
                     self.parameters.num_samples,    # width
                     0,                              # border
                     self.format,                   # format of image data
                     self.gl_type,               # type of image data
                     texel_data)                     # texel data
        if gl.glGetTexLevelParameteriv(gl.GL_PROXY_TEXTURE_1D,0,gl.GL_TEXTURE_WIDTH) == 0:
            raise NumSamplesTooLargeError("Grating num_samples is too wide for your video system!")
        
        # If we got here, it worked and we can load the texture for real.
        gl.glTexImage1D(gl.GL_TEXTURE_1D,            # target
                     0,                              # level
                     self.gl_internal_format,                   # video RAM internal format: RGB
                     self.parameters.num_samples,    # width
                     0,                              # border
                     self.format,                   # format of image data
                     self.gl_type,               # type of image data
                     texel_data)                     # texel data
        # Set some texture object defaults
        gl.glTexParameteri(gl.GL_TEXTURE_1D,gl.GL_TEXTURE_WRAP_S,gl.GL_REPEAT)
        gl.glTexParameteri(gl.GL_TEXTURE_1D,gl.GL_TEXTURE_WRAP_T,gl.GL_REPEAT)
        gl.glTexParameteri(gl.GL_TEXTURE_1D,gl.GL_TEXTURE_MAG_FILTER,gl.GL_LINEAR)
        gl.glTexParameteri(gl.GL_TEXTURE_1D,gl.GL_TEXTURE_MIN_FILTER,gl.GL_LINEAR)

        if self.parameters.size[0] != self.parameters.size[1]:
            self.__give_size_warning()
        else:
            self.gave_size_warning = 0
            
    def __give_size_warning(self):
        VisionEgg.Core.message.add(
            """%s does not have equal width and height.  Gratings will
            have variable size based on orientation."""%(self,),
            level=VisionEgg.Core.Message.WARNING)
        self.gave_size_warning = 1

    def draw(self):
        if self.parameters.on:
            if self.parameters.size[0] != self.parameters.size[1]:
                if not self.gave_size_warning:
                    self.__give_size_warning()
            if self.parameters.bit_depth != self.cached_bit_depth:
                self.calculate_bit_depth_dependencies()
                    
            # Clear the modeview matrix
            gl.glMatrixMode(gl.GL_MODELVIEW)
            gl.glLoadIdentity()

            gl.glDisable(gl.GL_DEPTH_TEST)
            gl.glDisable(gl.GL_BLEND)
            gl.glDisable(gl.GL_TEXTURE_2D)
            gl.glEnable(gl.GL_TEXTURE_1D)
            gl.glBindTexture(gl.GL_TEXTURE_1D,self.texture_object)

            w = self.parameters.size[0]
            inc = w/float(self.parameters.num_samples)
            phase = (VisionEgg.timing_func() - self.parameters.t0_time_sec_absolute)*self.parameters.temporal_freq_hz*-360.0 + self.parameters.phase_at_t0
            floating_point_sin = Numeric.sin(2.0*math.pi*self.parameters.spatial_freq*Numeric.arange(0.0,w,inc,'d')+(phase/180.0*math.pi))*0.5*self.parameters.contrast+0.5
            floating_point_sin = Numeric.clip(floating_point_sin,0.0,1.0) # allow square wave generation if contrast > 1
            texel_data = (floating_point_sin*self.max_int_val).astype(self.numeric_type).tostring()
        
            gl.glTexSubImage1D(gl.GL_TEXTURE_1D, # target
                            0, # level
                            0, # x offset
                            self.parameters.num_samples, # width
                            self.format, # data format
                            self.gl_type, # data type
                            texel_data)
            
            gl.glTexEnvi(gl.GL_TEXTURE_ENV, gl.GL_TEXTURE_ENV_MODE, gl.GL_REPLACE)

            l = self.parameters.lowerleft[0]
            r = l + self.parameters.size[0]
            b = self.parameters.lowerleft[1]
            t = b + self.parameters.size[1]

            # Get a matrix used to rotate the texture coordinates
            gl.glMatrixMode(gl.GL_TEXTURE)
            gl.glPushMatrix()
            gl.glLoadIdentity()
            gl.glRotate(self.parameters.orientation,0.0,0.0,1.0)
            gl.glTranslate(-0.5,-0.5,0.0) # Rotate about the center of the texture
            
            gl.glBegin(gl.GL_QUADS)
            gl.glTexCoord2f(0.0,0.0)
            gl.glVertex2f(l,b)

            gl.glTexCoord2f(1.0,0.0)
            gl.glVertex2f(r,b)

            gl.glTexCoord2f(1.0,1.0)
            gl.glVertex2f(r,t)

            gl.glTexCoord2f(0.0,1.0)
            gl.glVertex2f(l,t)
            gl.glEnd() # GL_QUADS
            
            gl.glPopMatrix() # restore the texture matrix
            
            gl.glDisable(gl.GL_TEXTURE_1D)

class SinGrating2DSquareSidesSlow(LuminanceGratingCommon):
    """Sine wave grating stimulus with square sides.

    Very slow, but included as an example of calculating and drawing a
    2D matrix on every frame.  So slow that it drops framerates
    unacceptably on my computer."""
    
    parameters_and_defaults = {'on':(1,types.IntType),
                               'contrast':(1.0,types.FloatType),
                               'lowerleft':((0.0,0.0),types.TupleType),
                               'size':((640.0,640.0),types.TupleType),
                               'spatial_freq':(1.0/128.0,types.FloatType), # cycles/eye coord unit (default viewport projection = cycles/pixel)
                               'temporal_freq_hz':(5.0,types.FloatType), # hz
                               't0_time_sec_absolute':(None,types.FloatType),
                               'phase_at_t0':(0.0,types.FloatType), # degrees [0.0-360.0]
                               'orientation':(0.0,types.FloatType), # 0=right, 90=down
                               'num_samples':(512, types.IntType) # number of spatial samples, should be a power of 2
                               }
    
    def __init__(self,projection = None,**kw):
        apply(LuminanceGratingCommon.__init__,(self,),kw)

        self.texture_object = gl.glGenTextures(1)
        gl.glBindTexture(gl.GL_TEXTURE_2D,self.texture_object)
        
        # Do error-checking on texture to make sure it will load
        max_dim = gl.glGetIntegerv(gl.GL_MAX_TEXTURE_SIZE)
        if self.parameters.num_samples > max_dim:
            raise NumSamplesTooLargeError("Grating num_samples too large for video system.\nOpenGL reports maximum size of %d"%(max_dim,))

        if self.parameters.t0_time_sec_absolute is None:
            self.parameters.t0_time_sec_absolute = VisionEgg.timing_func()

        self.calculate_bit_depth_dependencies()
        
        self.__remake_phase_array()
        phase = (VisionEgg.timing_func() - self.parameters.t0_time_sec_absolute)*self.parameters.temporal_freq_hz*-360.0 + self.parameters.phase_at_t0
        floating_point_sin = Numeric.sin(2.0*math.pi*self.parameters.spatial_freq*self.base_phase_array+(phase/180.0*math.pi))*0.5*self.parameters.contrast+0.5
        floating_point_sin = Numeric.clip(floating_point_sin,0.0,1.0) # allow square wave generation if contrast > 1
        texel_data = (floating_point_sin*self.max_int_val).astype(self.numeric_type).tostring()

        # Because the MAX_TEXTURE_SIZE method is insensitive to the current
        # state of the video system, another check must be done using
        # "proxy textures".
        gl.glTexImage2D(gl.GL_PROXY_TEXTURE_2D,            # target
                     0,                              # level
                     self.gl_internal_format,                   # video RAM internal format: RGB
                     self.parameters.num_samples,    # width
                     self.parameters.num_samples,    # height
                     0,                              # border
                     self.format,                   # format of image data
                     self.gl_type,               # type of image data
                     texel_data)                     # texel data
        if gl.glGetTexLevelParameteriv(gl.GL_PROXY_TEXTURE_2D,0,gl.GL_TEXTURE_WIDTH) == 0:
            raise NumSamplesTooLargeError("Grating num_samples is too wide for your video system!")
        
        # If we got here, it worked and we can load the texture for real.
        gl.glTexImage2D(gl.GL_TEXTURE_2D,            # target
                     0,                              # level
                     self.gl_internal_format,                   # video RAM internal format: RGB
                     self.parameters.num_samples,    # width
                     self.parameters.num_samples,    # height
                     0,                              # border
                     self.format,                   # format of image data
                     self.gl_type,               # type of image data
                     texel_data)                     # texel data
        # Set some texture object defaults
        gl.glTexParameteri(gl.GL_TEXTURE_2D,gl.GL_TEXTURE_WRAP_S,gl.GL_CLAMP_TO_EDGE)
        gl.glTexParameteri(gl.GL_TEXTURE_2D,gl.GL_TEXTURE_WRAP_T,gl.GL_CLAMP_TO_EDGE)
        gl.glTexParameteri(gl.GL_TEXTURE_2D,gl.GL_TEXTURE_MAG_FILTER,gl.GL_LINEAR)
        gl.glTexParameteri(gl.GL_TEXTURE_2D,gl.GL_TEXTURE_MIN_FILTER,gl.GL_LINEAR)

        if self.parameters.size[0] != self.parameters.size[1]:
            self.__give_size_warning()
        else:
            self.gave_size_warning = 0

    def __remake_phase_array(self):
        ori = (-self.parameters.orientation)/180.0*math.pi
        n = self.parameters.num_samples
        xg = float(self.parameters.size[0])
        yg = float(self.parameters.size[1])
        self.base_phase_array = Numeric.fromfunction(lambda x,y: x*xg/float(n)*math.sin(ori)+y*yg/float(n)*math.cos(ori), (n,n))
        self.cached_orientation = self.parameters.orientation
        self.cached_size = self.parameters.size
        self.cached_num_samples = n
        
    def __give_size_warning(self):
        VisionEgg.Core.message.add(
            """%s does not have equal width and height.  Gratings will
            have variable size based on orientation."""%(self,),
            level=VisionEgg.Core.Message.WARNING)
        self.gave_size_warning = 1

    def draw(self):
        if self.parameters.on:
            if self.parameters.size[0] != self.parameters.size[1]:
                if not self.gave_size_warning:
                    self.__give_size_warning()
            if self.parameters.bit_depth != self.cached_bit_depth:
                self.calculate_bit_depth_dependencies()
                
            # Clear the modeview matrix
            gl.glMatrixMode(gl.GL_MODELVIEW)
            gl.glLoadIdentity()

            gl.glDisable(gl.GL_DEPTH_TEST)
            gl.glDisable(gl.GL_BLEND)
            gl.glEnable(gl.GL_TEXTURE_2D)
            gl.glBindTexture(gl.GL_TEXTURE_2D,self.texture_object)

            if self.parameters.orientation != self.cached_orientation or self.parameters.size != self.cached_size or self.parameters.num_samples != self.cached_num_samples:
                self.__remake_phase_array()
            phase = (VisionEgg.timing_func() - self.parameters.t0_time_sec_absolute)*self.parameters.temporal_freq_hz*-360.0 + self.parameters.phase_at_t0
            floating_point_sin = Numeric.sin(2.0*math.pi*self.parameters.spatial_freq*self.base_phase_array+(phase/180.0*math.pi))*0.5*self.parameters.contrast+0.5
            floating_point_sin = Numeric.clip(floating_point_sin,0.0,1.0) # allow square wave generation if contrast > 1
            texel_data = (floating_point_sin*self.max_int_val).astype(self.numeric_type).tostring()
        
            gl.glTexSubImage2D(gl.GL_TEXTURE_2D, # target
                            0, # level
                            0, # x offset
                            0, # y offset
                            self.parameters.num_samples, # width
                            self.parameters.num_samples, # height
                            self.format, # data format
                            self.gl_type, # data type
                            texel_data)
            
            gl.glTexEnvi(gl.GL_TEXTURE_ENV, gl.GL_TEXTURE_ENV_MODE, gl.GL_REPLACE)

            l = self.parameters.lowerleft[0]
            r = l + self.parameters.size[0]
            b = self.parameters.lowerleft[1]
            t = b + self.parameters.size[1]

            # Get a matrix used to rotate the texture coordinates
            gl.glBegin(gl.GL_QUADS)
            gl.glTexCoord2f(0.0,0.0)
            gl.glVertex2f(l,b)

            gl.glTexCoord2f(1.0,0.0)
            gl.glVertex2f(r,b)

            gl.glTexCoord2f(1.0,1.0)
            gl.glVertex2f(r,t)

            gl.glTexCoord2f(0.0,1.0)
            gl.glVertex2f(l,t)
            gl.glEnd() # GL_QUADS
            
            gl.glDisable(gl.GL_TEXTURE_2D)

class SinGrating3D(LuminanceGratingCommon):
    """Sine wave grating mapped on the inside of a cylinder."""
    parameters_and_defaults = {'on':(1,types.IntType),
                               'contrast':(1.0,types.FloatType),
                               'radius':(1.0,types.FloatType),
                               'height':(10000.0,types.FloatType),
                               'spatial_freq_cpd':(1.0/36.0,types.FloatType), # cycles/degree
                               'temporal_freq_hz':(5.0,types.FloatType), # hz
                               't0_time_sec_absolute':(None,types.FloatType),
                               'phase_at_t0':(0.0,types.FloatType), # degrees
                               'orientation':(0.0,types.FloatType), # 0=right, 90=down
                               'num_samples':(1024,types.IntType), # number of spatial samples, should be a power of 2
                               'num_sides':(50,types.IntType) # number of sides of cylinder
                               }
    def __init__(self,projection = None,**kw):
        apply(LuminanceGratingCommon.__init__,(self,),kw)

        self.texture_object = gl.glGenTextures(1)
        gl.glBindTexture(gl.GL_TEXTURE_1D,self.texture_object)
        
        # Do error-checking on texture to make sure it will load
        max_dim = gl.glGetIntegerv(gl.GL_MAX_TEXTURE_SIZE)
        if self.parameters.num_samples > max_dim:
            raise NumSamplesTooLargeError("Grating num_samples too large for video system.\nOpenGL reports maximum size of %d"%(max_dim,))

        self.calculate_bit_depth_dependencies()
        
        if self.parameters.t0_time_sec_absolute is None:
            self.parameters.t0_time_sec_absolute = VisionEgg.timing_func()
            
        l = 0.0
        r = 360.0
        inc = 360.0/float(self.parameters.num_samples)
        phase = (VisionEgg.timing_func() - self.parameters.t0_time_sec_absolute)*self.parameters.temporal_freq_hz*360.0 + self.parameters.phase_at_t0
        floating_point_sin = Numeric.sin(2.0*math.pi*self.parameters.spatial_freq_cpd*Numeric.arange(l,r,inc,'d')-(phase/180.0*math.pi))*0.5*self.parameters.contrast+0.5
        floating_point_sin = Numeric.clip(floating_point_sin,0.0,1.0) # allow square wave generation if contrast > 1
        texel_data = (floating_point_sin*self.max_int_val).astype(self.numeric_type).tostring()

        # Because the MAX_TEXTURE_SIZE method is insensitive to the current
        # state of the video system, another check must be done using
        # "proxy textures".
        gl.glTexImage1D(gl.GL_PROXY_TEXTURE_1D,            # target
                     0,                              # level
                     self.gl_internal_format,                   # video RAM internal format: RGB
                     self.parameters.num_samples,    # width
                     0,                              # border
                     self.format,                   # format of image data
                     self.gl_type,               # type of image data
                     texel_data)                     # texel data
        if gl.glGetTexLevelParameteriv(gl.GL_PROXY_TEXTURE_1D,0,gl.GL_TEXTURE_WIDTH) == 0:
            raise NumSamplesTooLargeError("Grating num_samples is too wide for your video system!")
        
        # If we got here, it worked and we can load the texture for real.
        gl.glTexImage1D(gl.GL_TEXTURE_1D,            # target
                     0,                              # level
                     self.gl_internal_format,                   # video RAM internal format: RGB
                     self.parameters.num_samples,    # width
                     0,                              # border
                     self.format,                   # format of image data
                     self.gl_type,               # type of image data
                     texel_data)                     # texel data
        # Set some texture object defaults
        gl.glTexParameteri(gl.GL_TEXTURE_1D,gl.GL_TEXTURE_WRAP_S,gl.GL_REPEAT)
        gl.glTexParameteri(gl.GL_TEXTURE_1D,gl.GL_TEXTURE_WRAP_T,gl.GL_REPEAT)
        gl.glTexParameteri(gl.GL_TEXTURE_1D,gl.GL_TEXTURE_MAG_FILTER,gl.GL_LINEAR)
        gl.glTexParameteri(gl.GL_TEXTURE_1D,gl.GL_TEXTURE_MIN_FILTER,gl.GL_LINEAR)    

        self.cached_display_list = gl.glGenLists(1) # Allocate a new display list
        self.__rebuild_display_list()

    def draw(self):
    	"""Redraw the scene on every frame.
        """
        if self.parameters.on:
            if self.parameters.bit_depth != self.cached_bit_depth:
                self.calculate_bit_depth_dependencies()
            # Set OpenGL state variables
            gl.glDisable( gl.GL_DEPTH_TEST )
            gl.glEnable( gl.GL_TEXTURE_1D )  # Make sure textures are drawn
            gl.glDisable( gl.GL_TEXTURE_2D )
            gl.glDisable( gl.GL_BLEND )

            gl.glBindTexture(gl.GL_TEXTURE_1D,self.texture_object)

            l = 0.0
            r = 360.0
            inc = 360.0/float(self.parameters.num_samples)
            phase = (VisionEgg.timing_func() - self.parameters.t0_time_sec_absolute)*self.parameters.temporal_freq_hz*360.0 + self.parameters.phase_at_t0
            floating_point_sin = Numeric.sin(2.0*math.pi*self.parameters.spatial_freq_cpd*Numeric.arange(l,r,inc,'d')-(phase/180.0*math.pi))*0.5*self.parameters.contrast+0.5
            floating_point_sin = Numeric.clip(floating_point_sin,0.0,1.0) # allow square wave generation if contrast > 1
            texel_data = (floating_point_sin*self.max_int_val).astype(self.numeric_type).tostring()
        
            gl.glTexSubImage1D(gl.GL_TEXTURE_1D, # target
                            0, # level
                            0, # x offset
                            self.parameters.num_samples, # width
                            self.format, # data format
                            self.gl_type, # data type
                            texel_data)
            
            gl.glTexEnvi(gl.GL_TEXTURE_ENV, gl.GL_TEXTURE_ENV_MODE, gl.GL_REPLACE)

            # clear modelview matrix
            gl.glMatrixMode(gl.GL_MODELVIEW)
            gl.glLoadIdentity()

            # do the orientation
            gl.glRotatef(self.parameters.orientation,0.0,0.0,1.0)

            if self.parameters.num_sides != self.cached_display_list_num_sides:
                self.__rebuild_display_list()
            gl.glCallList(self.cached_display_list)

            gl.glDisable( gl.GL_TEXTURE_1D )

    def __rebuild_display_list(self):
        # (Re)build the display list
        #
        # This draws a display list for an approximation of a cylinder.
        # The cylinder has "num_sides" sides. The following code
        # generates a list of vertices and the texture coordinates
        # to be used by those vertices.
        r = self.parameters.radius # in OpenGL (arbitrary) units
        circum = 2.0*math.pi*r
        h = self.parameters.height/2.0

        num_sides = self.parameters.num_sides
        self.cached_display_list_num_sides = num_sides
        
        deltaTheta = 2.0*math.pi / num_sides
        gl.glNewList(self.cached_display_list,gl.GL_COMPILE)
        gl.glBegin(gl.GL_QUADS)
        for i in range(num_sides):
            # angle of sides
            theta1 = i*deltaTheta
            theta2 = (i+1)*deltaTheta
            # fraction of texture
            frac1 = float(i)/num_sides
            frac2 = float(i+1)/num_sides
            # location of sides
            x1 = r*math.cos(theta1)
            z1 = r*math.sin(theta1)
            x2 = r*math.cos(theta2)
            z2 = r*math.sin(theta2)

            #Bottom left of quad
            gl.glTexCoord2f(frac1, 0.0)
            gl.glVertex4f( x1, -h, z1, 1.0 )
            
            #Bottom right of quad
            gl.glTexCoord2f(frac2, 0.0)
            gl.glVertex4f( x2, -h, z2, 1.0 )
            #Top right of quad
            gl.glTexCoord2f(frac2, 1.0); 
            gl.glVertex4f( x2,  h, z2, 1.0 )
            #Top left of quad
            gl.glTexCoord2f(frac1, 1.0)
            gl.glVertex4f( x1,  h, z1, 1.0 )
        gl.glEnd()
        gl.glEndList()

class NumSamplesTooLargeError( VisionEgg.Core.EggError ):
    """Overrides VisionEgg.Core.EggError"""
    pass
