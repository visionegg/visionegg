"""Texture (images mapped onto polygons) stimuli."""

# Copyright (c) 2001-2003 Andrew Straw.  Distributed under the terms of the
# GNU Lesser General Public License (LGPL).

####################################################################
#
#        Import all the necessary packages
#
####################################################################

import VisionEgg
import VisionEgg.Core
import Image, ImageDraw                         # Python Imaging Library packages
import math, types, os
import OpenGL.GL as gl
import Numeric

# These modules are part of PIL and get loaded as needed by Image.
# They are listed here so that Gordon McMillan's Installer properly
# locates them.  You will not hurt anything other than your ability to
# make executables using Intaller if you remove these lines.
import _imaging
import ImageFile, ImageFileIO, BmpImagePlugin, JpegImagePlugin, PngImagePlugin

import string
__version__ = VisionEgg.release_name
__cvs__ = string.split('$Revision$')[1]
__date__ = string.join(string.split('$Date$')[1:3], ' ')
__author__ = 'Andrew Straw <astraw@users.sourceforge.net>'

def __no_clamp_to_edge_callback():
    # Error callback automatically called if OpenGL version < 1.2
    
    # This function is called if the OpenGL version is < 1.2, in which
    # case GL_CLAMP_TO_EDGE is not defined by default.
    
    try:
        1/0 # raise exception -- ignore the code below for now
        import OpenGL.GL.SGIS.texture_edge_clamp
        if OpenGL.GL.SGIS.texture_edge_clamp.glInitTextureEdgeClampSGIS():
            gl.GL_CLAMP_TO_EDGE = OpenGL.GL.SGIS.texture_edge_clamp.GL_CLAMP_TO_EDGE_SGIS
        else:
            del gl.GL_CLAMP_TO_EDGE
            raise RuntimeError("No GL_CLAMP_TO_EDGE")
    except:
        
        VisionEgg.Core.message.add(
            
            """Your version of OpenGL is less than 1.2, and you do not
            have the GL_SGIS_texture_edge_clamp OpenGL extension.
            therefore, you do not have GL_CLAMP_TO_EDGE available.  It
            may be impossible to get exact 1:1 reproduction of your
            textures.  Using GL_CLAMP instead of GL_CLAMP_TO_EDGE.""",

            level=VisionEgg.Core.Message.WARNING)
        gl.GL_CLAMP_TO_EDGE = gl.GL_CLAMP

if "GL_CLAMP_TO_EDGE" not in dir(gl):
    # Hack because this isn't defined in my PyOpenGL modules:
    VisionEgg.Core.add_gl_assumption("GL_VERSION",1.2,__no_clamp_to_edge_callback)
    gl.GL_CLAMP_TO_EDGE = 0x812F # This value is in Mesa gl.h and nVidia gl.h, so hopefully it's OK for others

####################################################################
#
#        Textures
#
####################################################################

class Texture:
    """A 2 dimensional texture.

    The pixel data can come from an image file, an image file stream,
    an instance of Image from the Python Imaging Library, a Numeric
    Python array, or None.

    If the data is a Numeric python array, floating point numbers are
    assumed to be in the range 0.0 to 1.0, and integers are assumed to
    be in the range 0 to 255.
    
    The 2D texture data is not sent to OpenGL (video texture memory)
    until the load() method is called.  The unload() method may be
    used to remove the data from OpenGL.

    A reference to the original image data is maintained."""
    
    def __init__(self,pixels=None):

        if pixels is None: # draw default white "X" on blue background
            self.size = (256,256) # default size
            pixels = Image.new("RGB",self.size,(0,0,255))
            draw = ImageDraw.Draw(pixels)
            draw.line((0,0) + self.size, fill=(255,255,255))
            draw.line((0,self.size[1]) + (self.size[0],0), fill=(255,255,255))

        if type(pixels) == types.FileType:
            pixels = Image.open(pixels) # Attempt to open as an image file
        elif type(pixels) == types.StringType:
            # is this string a filename or raw image data?
            if os.path.isfile(pixels):
                # cache filename and file stream for later use (if possible)
                self._filename = pixels
                self._file_stream = open(pixels,"rb")
            pixels = Image.open(pixels) # Attempt to open as an image stream
            
        if isinstance(pixels, Image.Image): # PIL Image
            self.size = pixels.size
        elif type(pixels) == Numeric.ArrayType: # Numeric Python array
            if len(pixels.shape) == 3:
                if pixels.shape[2] not in [3,4]:
                    raise ValueError("Only 2D luminance, 3D RGB, and 3D RGBA arrays allowed")
            elif len(pixels.shape) != 2:
                raise ValueError("Only 2D luminance, 3D RGB, and 3D RGBA arrays allowed")
            self.size = ( pixels.shape[1], pixels.shape[0] )
        else:
            raise TypeError("pixel data could not be recognized. (Use a PIL Image or a Numeric array.)")

        self.pixels = pixels
        self.texture_object = None

    def make_half_size(self):
        if self.texture_object is not None:
            raise RuntimeError("make_half_size() only available BEFORE texture loaded to OpenGL.")
        
        if isinstance(self.pixels,Image.Image):
            w = self.size[0]/2
            h = self.size[1]/2
            small_pixels = self.pixels.resize((w,h),Image.BICUBIC)
            self.pixels = small_pixels
            self.size = (w,h)
        else:
            raise RuntimeError("Texture too large, but auto-rescaling of Numeric arrays not supported.")

    def unload(self):
        """Unload texture data from video texture memory.

        This only removes data from the video texture memory if there
        are no other references to the TextureObject instance.  To
        ensure this, all references to the texture_object argument
        passed to the load() method should be deleted."""
        
        self.texture_object = None

    def get_pixels_as_image(self):
        """Return pixel data as PIL image"""
        if type(self.pixels) == Numeric.ArrayType:
            if len(self.pixels.shape) == 2:
                a = self.pixels
                if a.typecode() == Numeric.UnsignedInt8:
                    mode = "L"
                elif a.typecode() == Numeric.Float32:
                    mode = "F"
                else:
                    raise ValueError("unsupported image mode")
                return Image.fromstring(mode, (a.shape[1], a.shape[0]), a.tostring())
            else:
                raise NotImplementedError("Currently only luminance data can be converted to images")
        elif isinstance(pixels, Image.Image):
            return self.pixels
        else:
            raise NotImplementedError("Don't know how to convert pixel data to PIL image")

    def load(self, texture_object, build_mipmaps = 1, rescale_original_to_fill_texture_object = 0):
        """Load texture data to video texture memory.

        This will cause the texture data to become resident in OpenGL
        video texture memory, enabling fast drawing.

        The texture_object argument is used to specify an instance of
        the TextureObject class, which is a wrapper for the OpenGL
        texture object holding the resident texture.

        To remove a texture from OpenGL's resident textures: 1) make
        sure no references are maintained to the instance of
        TextureObject passed as the texture_object argument and 2)
        call the unload() method"""

        assert( isinstance( texture_object, TextureObject ))
        assert( texture_object.dimensions == 2 )

        def next_power_of_2(f):
            return math.pow(2.0,math.ceil(math.log(f)/math.log(2.0)))

        width, height = self.size

        width_pow2  = int(next_power_of_2(width))
        height_pow2  = int(next_power_of_2(height))

        if rescale_original_to_fill_texture_object:
            if type(self.pixels) == Numeric.ArrayType:
                raise NotImplementedError("Automatic rescaling of Numeric arrays not implemented.")

        # fractional coverage
        self.buf_lf = 0.0
        self.buf_rf = float(width)/width_pow2
        self.buf_bf = 0.0
        self.buf_tf = float(height)/height_pow2

        # absolute (texel units) coverage
        self._buf_l = 0
        self._buf_r = width
        self._buf_b = 0
        self._buf_t = height

        if width != width_pow2 or height != height_pow2:
            if type(self.pixels) == Numeric.ArrayType:
                if len(self.pixels.shape) == 2:
                    buffer = Numeric.zeros( (height_pow2,width_pow2), self.pixels.typecode() )
                    buffer[0:height,0:width] = self.pixels
                elif len(self.pixels.shape) == 3:
                    buffer = Numeric.zeros( (height_pow2,width_pow2,self.pixels.shape[2]), self.pixels.typecode() )
                    buffer[0:height,0:width,:] = self.pixels
                else:
                    raise RuntimeError("Unexpected shape for self.pixels")
            else:
                if rescale_original_to_fill_texture_object:
                    buffer = self.pixels.resize((width_pow2,height_pow2),Image.BICUBIC)
                    
                    self._buf_l = 0
                    self._buf_r = width_pow2
                    self._buf_t = 0
                    self._buf_b = height_pow2
                    
                    self.buf_lf = 0.0
                    self.buf_rf = 1.0
                    self.buf_bf = 0.0
                    self.buf_tf = 1.0
                else:
                    buffer = Image.new(self.pixels.mode,(width_pow2, height_pow2))
                    buffer.paste( self.pixels, (0,height_pow2-height,width,height_pow2))
        else:
            buffer = self.pixels

        # Put data in texture object
        texture_object.put_new_image( buffer, mipmap_level=0 )
        if build_mipmaps:
            # Mipmap generation could be done in the TextureObject
            # class by GLU, but here we have more control
            if type(self.pixels) == Numeric.ArrayType:
                raise NotImplementedError("Building of mipmaps not implemented for Numeric arrays.")
            this_width, this_height = self.size
            biggest_dim = max(this_width,this_height)
            mipmap_level = 1
            while biggest_dim > 1:
                this_width = this_width/2.0
                this_height = this_height/2.0
                
                width_pix = int(math.ceil(this_width))
                height_pix = int(math.ceil(this_height))
                shrunk = self.pixels.resize((width_pix,height_pix),Image.BICUBIC)
                
                width_pow2  = int(next_power_of_2(width_pix))
                height_pow2  = int(next_power_of_2(height_pix))
                
                im = Image.new(shrunk.mode,(width_pow2,height_pow2))
                im.paste(shrunk,(0,height_pow2-height_pix,width_pix,height_pow2))
                
                texture_object.put_new_image( im, mipmap_level=mipmap_level )
                
                mipmap_level += 1
                biggest_dim = max(this_width,this_height)
                
        # Keep reference to texture_object
        self.texture_object = texture_object

    def get_texture_object(self):
        return self.texture_object

class TextureFromFile( Texture ):
    def __init__(self, filename ):
        VisionEgg.Core.message.add("class TextureFromFile outdated, use class Texture instead.",
                                   VisionEgg.Core.Message.DEPRECATION)
        Texture.__init__(self, filename)

class TextureObject:
    """Texture data in OpenGL. Potentially resident in video texture memory.

    This class encapsulates the state variables in OpenGL texture objects.  Do not
    change attribute values directly.  Use the methods provided instead."""

    _cube_map_side_names = ['positive_x', 'negative_x',
                            'positive_y', 'negative_y',
                            'positive_z', 'negative_z']
    
    def __init__(self,dimensions=2):
        if dimensions not in [1,2,3,'cube']:
            raise ValueError("TextureObject dimensions must be 1,2,3, or 'cube'")
        # default OpenGL values for these values
        self.min_filter = gl.GL_NEAREST_MIPMAP_LINEAR
        self.mag_filter = gl.GL_LINEAR
        self.wrap_mode_s = gl.GL_REPEAT
        if dimensions != 1:
            self.wrap_mode_t = gl.GL_REPEAT
        if dimensions == 3:
            self.wrap_mode_r = gl.GL_REPEAT
        self.border_color = (0, 0, 0, 0)

        # assign Vision Egg variables (not local copies of OpenGL information)
        if dimensions != 'cube':
            self.mipmap_arrays = {}
        else:
            self.cube_mipmap_arrays = {}
            for side in TextureObject._cube_map_side_names:
                self.cube_mipmap_arrays[side] = {}

        if dimensions == 1:
            self.target = gl.GL_TEXTURE_1D
        elif dimensions == 2:
            self.target = gl.GL_TEXTURE_2D
        elif dimensions == 3:
            self.target = gl.GL_TEXTURE_3D
        elif dimensions == 'cube':
            self.target = gl.GL_TEXTURE_CUBE

        self.dimensions = dimensions
        self.gl_id = gl.glGenTextures(1)

    def __del__(self):
        gl.glDeleteTextures(self.gl_id)

    def set_min_filter(self, filter):
        gl.glBindTexture(self.target, self.gl_id)
        gl.glTexParameteri( self.target, gl.GL_TEXTURE_MIN_FILTER,filter)
        self.min_filter = filter

    def set_mag_filter(self, filter):
        gl.glBindTexture( self.target, self.gl_id)
        gl.glTexParameteri( self.target, gl.GL_TEXTURE_MAG_FILTER, filter)
        self.mag_filter = filter

    def set_wrap_mode_s(self, wrap_mode):
        """Set to GL_CLAMP, GL_CLAMP_TO_EDGE, GL_REPEAT, or GL_CLAMP_TO_BORDER"""
        gl.glBindTexture( self.target, self.gl_id)
        gl.glTexParameteri( self.target, gl.GL_TEXTURE_WRAP_S, wrap_mode)
        self.wrap_mode_s = wrap_mode

    def set_wrap_mode_t(self, wrap_mode):
        """Set to GL_CLAMP, GL_CLAMP_TO_EDGE, GL_REPEAT, or GL_CLAMP_TO_BORDER"""
        gl.glBindTexture( self.target, self.gl_id)
        gl.glTexParameteri( self.target, gl.GL_TEXTURE_WRAP_T, wrap_mode)
        self.wrap_mode_t = wrap_mode

    def set_wrap_mode_r(self, wrap_mode):
        """Set to GL_CLAMP, GL_CLAMP_TO_EDGE, GL_REPEAT, or GL_CLAMP_TO_BORDER"""
        gl.glBindTexture( self.target, self.gl_id)
        gl.glTexParameteri( self.target, gl.GL_TEXTURE_WRAP_R, wrap_mode)
        self.wrap_mode_r = wrap_mode

    def set_border_color(self, border_color):
        """Set to a sequence of 4 floats in the range 0.0 to 1.0"""
        gl.glBindTexture( self.target, self.gl_id)
        gl.glTexParameteriv( self.target, gl.GL_TEXTURE_BORDER_COLOR, border_color)
        self.border_color = border_color

    def put_new_image(self,
                      image_data,
                      mipmap_level = 0,
                      border = 0,
                      check_opengl_errors = 1,
                      internal_format = gl.GL_RGB,
                      data_format = None,
                      data_type = None,
                      cube_side = None,
                      ):
        
        """Put Numeric array or PIL Image into OpenGL as texture data.

        The image_data parameter contains the texture data.  If it is
        a Numeric array, it must be 1D, 2D, or 3D data in grayscale or
        color (RGB or RGBA).  Remember that OpenGL begins its textures
        from the lower left corner, so image_data[0,:] = 1.0 would set
        the bottom line of the texture to white, while image_data[:,0]
        = 1.0 would set the left line of the texture to white.

        The mipmap_level parameter specifies which of the texture
        object's mipmap arrays you are filling.

        The border parameter specifies the width of the border.

        The check_opengl_errors parameter turns on (more
        comprehensible) error messages when something goes wrong.  It
        also slows down performance a little bit.

        The internal_format parameter specifies the format in which
        the image data is stored on the video card.  See the OpenGL
        specification for all possible values.
        
        If the data_format parameter is None (the default), an attempt
        is made to guess data_format according to the following
        description. For Numeric arrays: If image_data.shape is equal
        to the dimensions of the texture object, image_data is assumed
        to contain luminance (grayscale) information and data_format
        is set to GL_LUMINANCE.  If image_data.shape is equal to one
        plus the dimensions of the texture object, image_data is
        assumed to contain color information.  If image_data.shape[-1]
        is 3, this is assumed to be RGB data and data_format is set to
        GL_RGB.  If, image_data.shape[-1] is 4, this is assumed to be
        RGBA data and data_format is set to GL_RGBA. For PIL images:
        the "mode" attribute is queried.

        If the data_type parameter is None (the default), it is set to
        GL_UNSIGNED_BYTE. For Numeric arrays: image_data is (re)cast
        as UnsignedInt8 and, if it is a floating point type, values
        are assumed to be in the range 0.0-1.0 and are scaled to the
        range 0-255.  If the data_type parameter is not None, the
        image_data is not rescaled or recast.  Currently only
        GL_UNSIGNED_BYTE is supported. For PIL images: image_data is
        used as unsigned bytes.  This is the usual format for common
        computer graphics files."""

        if type(image_data) == Numeric.ArrayType:
            if self.dimensions != 'cube':
                assert(cube_side == None)
                data_dimensions = len(image_data.shape)
                assert((data_dimensions == self.dimensions) or (data_dimensions == self.dimensions+1))
            else:
                assert(cube_side in TextureObject._cube_map_side_names)
        elif isinstance(image_data,Image.Image):
            assert( self.dimensions == 2 )
        else:
            raise TypeError("Expecting Numeric array or PIL image")

        # make myself the active texture
        gl.glBindTexture(self.target, self.gl_id)

        # create local mipmap_array data
        new_mipmap_array = {}

        if self.dimensions != 'cube':
            self.mipmap_arrays[mipmap_level] = new_mipmap_array
        else:
            self.cube_mipmap_arrays[cube_side][mipmap_level] = new_mipmap_array

        # add data to mipmap array
        new_mipmap_array['border'] = border
        new_mipmap_array['internal_format'] = internal_format

        # Determine the data_format, data_type and rescale the data if needed
        data = image_data
        
        if data_format is None: # guess the format of the data
            if type(data) == Numeric.ArrayType:
                if len(data.shape) == self.dimensions:
                    data_format = gl.GL_LUMINANCE
                elif len(data.shape) == (self.dimensions+1):
                    if data.shape[-1] == 3:
                        data_format = gl.GL_RGB
                    elif data.shape[-1] == 4:
                        data_format = gl.GL_RGBA
                    else:
                        raise RuntimeError("Couldn't determine a format for your image_data.")
                else:
                    raise RuntimeError("Couldn't determine a format for your image_data.")
            else: # instance of Image.Image
                if data.mode == 'L':
                    data_format = gl.GL_LUMINANCE
                elif data.mode == 'RGB':
                    data_format = gl.GL_RGB
                elif data.mode in ['RGBA','RGBX']:
                    data_format = gl.GL_RGBA
                elif data.mode == 'P':
                    raise NotImplementedError("Paletted images are not supported.")
                else:
                    raise RuntimeError("Couldn't determine format for your image_data. (PIL mode = '%s')"%data.mode)

        if data_type is None: # guess the data type
            data_type = gl.GL_UNSIGNED_BYTE
            if type(data) == Numeric.ArrayType:
                if data.typecode() == Numeric.Float:
                    data = data*255.0

        if data_type == gl.GL_UNSIGNED_BYTE:
            if type(data) == Numeric.ArrayType:
                data = data.astype(Numeric.UnsignedInt8) # (re)cast if necessary
        else:
            raise NotImplementedError("Only data_type GL_UNSIGNED_BYTE currently supported")

        # determine size and make sure its power of 2
        def check_power_of_2(f):
            def next_power_of_2(f):
                return math.pow(2.0,math.ceil(math.log(f)/math.log(2.0)))
            if f != next_power_of_2(f):
                raise ValueError("image_data does not have all dimensions == n^2")
        if self.dimensions == 1:
            # must be Numeric array
            width = data.shape[0]
            check_power_of_2(width)
            new_mipmap_array['width'] = width
        else:
            if type(data) == Numeric.ArrayType:
                width = data.shape[1]
                height = data.shape[0]
            else:
                width, height = data.size
            check_power_of_2(width)
            check_power_of_2(height)
            new_mipmap_array['width'] = width
            new_mipmap_array['height'] = height
            if self.dimensions == 3:
                # must be Numeric array
                depth = data.shape[2]
                check_power_of_2(depth)
                new_mipmap_array['depth'] = height

        # check for OpenGL errors
        if check_opengl_errors:
            max_dim = gl.glGetIntegerv( gl.GL_MAX_TEXTURE_SIZE )
            if width > max_dim:
                raise TextureTooLargeError("image_data is too wide for your video system.")
            if self.dimensions == 1:
                gl.glTexImage1Dub(gl.GL_PROXY_TEXTURE_1D,
                                mipmap_level,
                                internal_format,
                                border,
                                data_format,
                                data)
                if gl.glGetTexLevelParameteriv(gl.GL_PROXY_TEXTURE_1D,mipmap_level,gl.GL_TEXTURE_WIDTH) == 0:
                    raise TextureTooLargeError("image_data is too wide for your video system.")
            elif self.dimensions in [2,'cube']:
                if height > max_dim:
                    raise TextureTooLargeError("image_data is too tall for your video system.")
                if self.dimensions == 2:
                    target = gl.GL_PROXY_TEXTURE_2D
                else:
                    target = gl.GL_PROXY_CUBE_MAP
                if type(data) == Numeric.ArrayType:
                    gl.glTexImage2Dub(target,
                                      mipmap_level,
                                      internal_format,
                                      border,
                                      data_format,
                                      data)
                else:
                    raw_data = data.tostring('raw',data.mode,0,-1)
                    gl.glTexImage2D(target,
                                    mipmap_level,
                                    internal_format,
                                    width,
                                    height,
                                    border,
                                    data_format,
                                    data_type,
                                    raw_data)
                if gl.glGetTexLevelParameteriv(target,mipmap_level,gl.GL_TEXTURE_WIDTH) == 0:
                    raise TextureTooLargeError("image_data is too wide for your video system.")
                if gl.glGetTexLevelParameteriv(target,mipmap_level,gl.GL_TEXTURE_HEIGHT) == 0:
                    raise TextureTooLargeError("image_data is too tall for your video system.")
            elif self.dimensions == 3:
                if max(height,depth) > max_dim:
                    raise TextureTooLargeError("image_data is too large for your video system.")
                gl.glTexImage3Dub(gl.GL_PROXY_TEXTURE_3D,
                                  mipmap_level,
                                  internal_format,
                                  border,
                                  data_format,
                                  data)
                if gl.glGetTexLevelParameteriv(gl.GL_PROXY_TEXTURE_3D,mipmap_level,gl.GL_TEXTURE_WIDTH) == 0:
                    raise TextureTooLargeError("image_data is too wide for your video system.")
                if gl.glGetTexLevelParameteriv(gl.GL_PROXY_TEXTURE_3D,mipmap_level,gl.GL_TEXTURE_HEIGHT) == 0:
                    raise TextureTooLargeError("image_data is too tall for your video system.")
                if gl.glGetTexLevelParameteriv(gl.GL_PROXY_TEXTURE_3D,mipmap_level,gl.GL_TEXTURE_DEPTH) == 0:
                    raise TextureTooLargeError("image_data is too deep for your video system.")
            else:
                raise RuntimeError("Unknown number of dimensions.")
                
        # No OpenGL error, put the texture in!
        if self.dimensions == 1:
            gl.glTexImage1Dub(gl.GL_TEXTURE_1D,
                              mipmap_level,
                              internal_format,
                              border,
                              data_format,
                              data)
        elif self.dimensions in [2,'cube']:
            if self.dimensions == 2:
                target = gl.GL_TEXTURE_2D
            else:
                target_name = 'GL_CUBE_MAP_'+string.upper(cube_side) # e.g. 'positive_x'
                target = getattr(gl,target_name)
            if type(data) == Numeric.ArrayType:
                gl.glTexImage2Dub(target,
                                  mipmap_level,
                                  internal_format,
                                  border,
                                  data_format,
                                  data)
            else:
                raw_data = data.tostring('raw',data.mode,0,-1)
                gl.glTexImage2D(target,
                                mipmap_level,
                                internal_format,
                                width,
                                height,
                                border,
                                data_format,
                                data_type,
                                raw_data)
        elif self.dimensions == 3:
            gl.glTexImage3Dub(gl.GL_TEXTURE_3D,
                              mipmap_level,
                              internal_format,
                              border,
                              data_format,
                              data)
        else:
            raise RuntimeError("Unknown number of dimensions.")

    def put_sub_image(self,
                      image_data,
                      mipmap_level = 0,
                      offset_tuple = None,
                      data_format = None,
                      data_type = None,
                      cube_side = None,
                      ):

        """Replace all or part of a texture object.

        This is faster that put_new_image(), and can be used to
        rapidly update textures.

        The offset_tuple parameter determines the lower left corner
        (for 2D textures) of your data in pixel units.  For example,
        (0,0) would be no offset and thus the new data would be placed
        in the lower left of the texture.

        For an explanation of most parameters, see the
        put_new_image() method."""

        if type(image_data) == Numeric.ArrayType:
            if self.dimensions != 'cube':
                assert(cube_side == None)
                data_dimensions = len(image_data.shape)
                assert((data_dimensions == self.dimensions) or (data_dimensions == self.dimensions+1))
            else:
                assert(cube_side in TextureObject._cube_map_side_names)
        elif isinstance(image_data,Image.Image):
            assert( self.dimensions == 2 )
        else:
            raise TypeError("Expecting Numeric array or PIL image")

        # make myself the active texture
        gl.glBindTexture(self.target, self.gl_id)

        if self.dimensions != 'cube':
            previous_mipmap_array = self.mipmap_arrays[mipmap_level]
        else:
            previous_mipmap_array = self.cube_mipmap_arrays[cube_side][mipmap_level]

        # Determine the data_format, data_type and rescale the data if needed
        data = image_data
        
        if data_format is None: # guess the format of the data
            if type(data) == Numeric.ArrayType:
                if len(data.shape) == self.dimensions:
                    data_format = gl.GL_LUMINANCE
                elif len(data.shape) == (self.dimensions+1):
                    if data.shape[-1] == 3:
                        data_format = gl.GL_RGB
                    elif data.shape[-1] == 4:
                        data_format = gl.GL_RGBA
                    else:
                        raise RuntimeError("Couldn't determine a format for your image_data.")
                else:
                    raise RuntimeError("Couldn't determine a format for your image_data.")
            else: # instance of Image.Image
                if data.mode == 'L':
                    data_format = gl.GL_LUMINANCE
                elif data.mode == 'RGB':
                    data_format = gl.GL_RGB
                elif data.mode in ['RGBA','RGBX']:
                    data_format = gl.GL_RGBA
                elif data.mode == 'P':
                    raise NotImplementedError("Paletted images are not supported.")
                else:
                    raise RuntimeError("Couldn't determine format for your image_data. (PIL mode = '%s')"%data.mode)

        if data_type is None: # guess the data type
            data_type = gl.GL_UNSIGNED_BYTE
            if type(data) == Numeric.ArrayType:
                if data.typecode() == Numeric.Float:
                    data = data*255.0

        if data_type == gl.GL_UNSIGNED_BYTE:
            if type(data) == Numeric.ArrayType:
                data = data.astype(Numeric.UnsignedInt8) # (re)cast if necessary
        else:
            raise NotImplementedError("Only data_type GL_UNSIGNED_BYTE currently supported")

        if self.dimensions == 1:
            if not offset_tuple:
                offset_tuple = (0,)
            if (offset_tuple[0] + data.shape[0]) > previous_mipmap_array['width']:
                raise TextureTooLargeError("put_sub_image trying to exceed previous width.")
            raw_data = data.astype(Numeric.UnsignedInt8).tostring()
            gl.glTexSubImage1D(gl.GL_TEXTURE_1D,
                               mipmap_level,
                               offset_tuple[0],
                               data.shape[0],
                               data_format,
                               data_type,
                               raw_data)
        elif self.dimensions in [2,'cube']:
            if self.dimensions == 2:
                target = gl.GL_TEXTURE_2D
            else:
                target_name = 'GL_CUBE_MAP_'+string.upper(cube_side) # e.g. 'positive_x'
                target = getattr(gl,target_name)
            if not offset_tuple:
                offset_tuple = (0,0)
            if type(data) == Numeric.ArrayType:
                width = data.shape[1]
                height = data.shape[0]
                raw_data = data.astype(Numeric.UnsignedInt8).tostring()
            else:
                width = data.size[0]
                height = data.size[1]
                raw_data = data.tostring('raw',data.mode,0,-1)
            gl.glTexSubImage2D(target,
                               mipmap_level,
                               offset_tuple[0],
                               offset_tuple[1],
                               width,
                               height,
                               data_format,
                               data_type,
                               raw_data)
        elif self.dimensions == 3:
            raise RuntimeError("Cannot put_sub_image on 3D texture_object.")
        else:
            raise RuntimeError("Unknown number of dimensions.")        

####################################################################
#
#        Stimulus - TextureStimulus
#
####################################################################

class TextureStimulusBaseClass(VisionEgg.Core.Stimulus):
    """Parameters common to all stimuli that use textures.

    Don't instantiate this class directly."""
    parameters_and_defaults = {'texture':(None,Texture), # instance of Texture class
                               'texture_mag_filter':(gl.GL_LINEAR,types.IntType),
                               'texture_min_filter':(gl.GL_LINEAR_MIPMAP_LINEAR,types.IntType),
                               'texture_wrap_s':(None,types.IntType), # set to gl.GL_CLAMP_TO_EDGE below
                               'texture_wrap_t':(None,types.IntType), # set to gl.GL_CLAMP_TO_EDGE below
                               }
                               
    constant_parameters_and_defaults = {'mipmaps_enabled':(1,types.IntType), # boolean
                                        'shrink_texture_ok':(0,types.IntType), # boolean
                                        }
                                        
    _mipmap_modes = [gl.GL_LINEAR_MIPMAP_LINEAR,gl.GL_LINEAR_MIPMAP_NEAREST,
                     gl.GL_NEAREST_MIPMAP_LINEAR,gl.GL_NEAREST_MIPMAP_NEAREST]
                     
    def __init__(self,**kw):
        apply(VisionEgg.Core.Stimulus.__init__,(self,),kw)

        if not self.constant_parameters.mipmaps_enabled:
            if self.parameters.texture_min_filter in TextureStimulusBaseClass._mipmap_modes:
                raise ValueError("texture_min_filter cannot be a mipmap type if mipmaps not enabled.")
        # We have to set these parameters here because we may hav
        # re-assigned gl.GL_CLAMP_TO_EDGE.  This allows us to use
        # symbol gl.GL_CLAMP_TO_EDGE even if our version of OpenG
        # doesn't support it.
        if self.parameters.texture_wrap_s is None:
            self.parameters.texture_wrap_s = gl.GL_CLAMP_TO_EDGE
        if self.parameters.texture_wrap_t is None:
            self.parameters.texture_wrap_t = gl.GL_CLAMP_TO_EDGE

        # Create an OpenGL texture object this instance "owns"
        self.texture_object = TextureObject(dimensions=2)

        self._reload_texture()

    def _reload_texture(self):
        """(Re)load texture to OpenGL"""
        p = self.parameters
        self._using_texture = p.texture

        if not self.constant_parameters.shrink_texture_ok:
            # send texture to OpenGL
            p.texture.load( self.texture_object,
                            build_mipmaps = self.constant_parameters.mipmaps_enabled )
        else:
            max_dim = gl.glGetIntegerv( gl.GL_MAX_TEXTURE_SIZE )
            resized = 0
            while max(p.texture.size) > max_dim:
                p.texture.make_half_size()
                resized = 1
            loaded_ok = 0
            while not loaded_ok:
                try:
                    # send texture to OpenGL
                    p.texture.load( self.texture_object,
                                       build_mipmaps = self.constant_parameters.mipmaps_enabled )
                except TextureTooLargeError:
                    p.texture.make_half_size()
                    resized = 1
                else:
                    loaded_ok = 1
            if resized:
                VisionEgg.Core.message.add(
                    "Resized texture in %s to %d x %d"%(
                    str(self),p.texture.size[0],p.texture.size[1]),VisionEgg.Core.Message.WARNING)

class TextureStimulus(TextureStimulusBaseClass):
    """A textured rectangle for 2D use (z coordinate fixed to 0.0)."""
    parameters_and_defaults = {'on':(1,types.IntType),
                               'lowerleft':((0.0,0.0),types.TupleType), # in eye coordinates
                               'size':((640.0,480.0),types.TupleType)} # in eye coordinates
    def draw(self):
        p = self.parameters
        if p.texture != self._using_texture: # self._using_texture is from TextureStimulusBaseClass
            self._reload_texture()
        if p.on:
            # Clear the modeview matrix
            gl.glMatrixMode(gl.GL_MODELVIEW)
            gl.glLoadIdentity()
            
            gl.glDisable(gl.GL_DEPTH_TEST)
            gl.glDisable(gl.GL_BLEND)
            gl.glEnable(gl.GL_TEXTURE_2D)

            if not self.constant_parameters.mipmaps_enabled:
                if p.texture_min_filter in TextureStimulusBaseClass._mipmap_modes:
                    raise RuntimeError("Specified a mipmap mode in texture_min_filter, but mipmaps not enabled.")
            self.texture_object.set_min_filter( p.texture_min_filter )
            self.texture_object.set_mag_filter( p.texture_mag_filter )
            self.texture_object.set_wrap_mode_s( p.texture_wrap_s )
            self.texture_object.set_wrap_mode_t( p.texture_wrap_t )
            
            gl.glTexEnvi(gl.GL_TEXTURE_ENV, gl.GL_TEXTURE_ENV_MODE, gl.GL_REPLACE)

            l = p.lowerleft[0]
            r = l + p.size[0]
            b = p.lowerleft[1]
            t = b + p.size[1]

            tex = p.texture
            
            gl.glBegin(gl.GL_QUADS)
            gl.glTexCoord2f(tex.buf_lf,tex.buf_bf)
            gl.glVertex2f(l,b)

            gl.glTexCoord2f(tex.buf_rf,tex.buf_bf)
            gl.glVertex2f(r,b)

            gl.glTexCoord2f(tex.buf_rf,tex.buf_tf)
            gl.glVertex2f(r,t)

            gl.glTexCoord2f(tex.buf_lf,tex.buf_tf)
            gl.glVertex2f(l,t)
            gl.glEnd() # GL_QUADS

class TextureStimulus3D(TextureStimulusBaseClass):
    """A textured rectangle placed arbitrarily in 3 space."""
    parameters_and_defaults = {'on':(1,types.IntType),
                               'lowerleft':(Numeric.array((0.0,0.0,-1.0)),
                                            Numeric.ArrayType), # in eye coordinates
                               'lowerright':(Numeric.array((1.0,0.0,-1.0)),
                                             Numeric.ArrayType), # in eye coordinates
                               'upperleft':(Numeric.array((0.0,1.0,-1.0)),
                                            Numeric.ArrayType), # in eye coordinates
                               'upperright':(Numeric.array((1.0,1.0,-1.0)),
                                             Numeric.ArrayType), # in eye coordinates
                               'depth_test':(1,types.IntType),
                               }
                                                                                
    def draw(self):
        p = self.parameters
        if p.texture != self._using_texture: # self._using_texture is from TextureStimulusBaseClass
            self._reload_texture()
        if p.on:
            # Clear the modeview matrix
            gl.glMatrixMode(gl.GL_MODELVIEW)
            gl.glLoadIdentity()

            if p.depth_test:
                gl.glEnable(gl.GL_DEPTH_TEST)
            else:
                gl.glDisable(gl.GL_DEPTH_TEST)

            gl.glDisable(gl.GL_BLEND)
            gl.glEnable(gl.GL_TEXTURE_2D)
            gl.glBindTexture(gl.GL_TEXTURE_2D,self.texture_object)

            if not self.constant_parameters.mipmaps_enabled:
                if p.texture_min_filter in TextureStimulusBaseClass._mipmap_modes:
                    raise RuntimeError("Specified a mipmap mode in texture_min_filter, but mipmaps not enabled.")
            self.texture_object.set_min_filter( p.texture_min_filter )
            self.texture_object.set_mag_filter( p.texture_mag_filter )
            self.texture_object.set_wrap_mode_s( p.texture_wrap_s )
            self.texture_object.set_wrap_mode_t( p.texture_wrap_t )
                                                                                                    
            gl.glTexEnvi(gl.GL_TEXTURE_ENV, gl.GL_TEXTURE_ENV_MODE, gl.GL_REPLACE)

            tex = self.parameters.texture
            
            gl.glBegin(gl.GL_QUADS)
            gl.glTexCoord2f(tex.buf_lf,tex.buf_bf)
            gl.glVertex3fv(p.lowerleft)

            gl.glTexCoord2f(tex.buf_rf,tex.buf_bf)
            gl.glVertex3fv(p.lowerright)

            gl.glTexCoord2f(tex.buf_rf,tex.buf_tf)
            gl.glVertex3fv(p.upperright)

            gl.glTexCoord2f(tex.buf_lf,tex.buf_tf)
            gl.glVertex3fv(p.upperleft)
            gl.glEnd() # GL_QUADS
                
####################################################################
#
#        Stimulus - Spinning Drum
#
####################################################################

class SpinningDrum(TextureStimulusBaseClass):
    parameters_and_defaults = {'num_sides':(50,types.IntType),
                               'angular_position':(0.0,types.FloatType),
                               'contrast':(1.0,types.FloatType),
                               'on':(1,types.IntType),
                               'flat':(0,types.IntType), # toggles flat vs. cylinder
                               'flip_image':(0,types.IntType), # toggles normal vs. horizonally flipped image
                               'radius':(1.0,types.FloatType), # radius if cylinder, z distance if flat
                               'position':( (0.0,0.0,0.0), types.TupleType), # 3D position of drum center
                               'drum_center_azimuth':(0.0,types.FloatType), # changes orientation of drum in space
                               'drum_center_elevation':(0.0,types.FloatType), # changes orientation of drum in space
                               'orientation':(0.0,types.FloatType) # 0=right, 90=down
                               }
    
    def __init__(self,**kw):
        apply(TextureStimulusBaseClass.__init__,(self,),kw)
        self.cached_display_list_normal = gl.glGenLists(1) # Allocate a new display list
        self.cached_display_list_mirror = gl.glGenLists(1) # Allocate a new display list
        self.rebuild_display_list()

    def draw(self):
    	"""Redraw the scene on every frame.
        """
        p = self.parameters
        if p.texture != self._using_texture: # self._using_texture is from TextureStimulusBaseClass
            self._reload_texture()
            self.rebuild_display_list()
        if p.on:
            # Set OpenGL state variables
            gl.glEnable( gl.GL_DEPTH_TEST )
            gl.glEnable( gl.GL_TEXTURE_2D )  # Make sure textures are drawn
            gl.glEnable( gl.GL_BLEND ) # Contrast control implemented through blending

            # All of the contrast control stuff is somewhat arcane and
            # not very clear from reading the code, so here is how it
            # works in English. (Not that it makes it any more clear!)
            #
            # In the final "textured fragment" (before being blended
            # to the framebuffer), the color values are equal to those
            # of the texture (with the exception of pixels around the
            # edges which have their amplitudes reduced due to
            # anti-aliasing and are intermediate between the color of
            # the texture and mid-gray), and the alpha value is set to
            # the contrast.  Blending occurs, and by choosing the
            # appropriate values for glBlendFunc, adds the product of
            # fragment alpha (contrast) and fragment color to the
            # product of one minus fragment alpha (contrast) and what
            # was already in the framebuffer. 

            gl.glBlendFunc( gl.GL_SRC_ALPHA, gl.GL_ONE_MINUS_SRC_ALPHA )
            
            gl.glTexEnvi(gl.GL_TEXTURE_ENV, gl.GL_TEXTURE_ENV_MODE, gl.GL_DECAL)
            
            # clear modelview matrix
            gl.glMatrixMode(gl.GL_MODELVIEW)
            gl.glLoadIdentity()

            gl.glColor(0.5,0.5,0.5,p.contrast) # Set the polygons' fragment color (implements contrast)

            if not self.constant_parameters.mipmaps_enabled:
                if p.texture_min_filter in TextureStimulusBaseClass._mipmap_modes:
                    raise RuntimeError("Specified a mipmap mode in texture_min_filter, but mipmaps not enabled.")
            self.texture_object.set_min_filter( p.texture_min_filter )
            self.texture_object.set_mag_filter( p.texture_mag_filter )
            self.texture_object.set_wrap_mode_s( p.texture_wrap_s )
            self.texture_object.set_wrap_mode_t( p.texture_wrap_t )

            if p.flat: # draw as flat texture on a rectange
                # do the orientation
                gl.glRotatef(p.orientation,0.0,0.0,-1.0)
                gl.glTranslate(p.position[0],p.position[1],p.position[2])
                
                if p.flip_image:
                    raise NotImplementedError("flip_image not yet supported for flat spinning drums.")
                w,h = p.texture.size

                # calculate texture coordinates based on current angle
                tex_phase = p.angular_position/-360.0 + 0.5 # offset to match non-flat
                tex_phase = tex_phase % 1.0 # make 0 <= tex_phase < 1.0
                
                TINY = 1.0e-10
                tex = p.texture
                if tex_phase < TINY: # it's effectively zero

                    gl.glBegin(gl.GL_QUADS)
                    gl.glTexCoord2f(tex.buf_lf,tex.buf_bf)
                    gl.glVertex2f(0.0,0.0)

                    gl.glTexCoord2f(tex.buf_rf,tex.buf_bf)
                    gl.glVertex2f(w,0.0)

                    gl.glTexCoord2f(tex.buf_rf,tex.buf_tf)
                    gl.glVertex2f(w,h)

                    gl.glTexCoord2f(tex.buf_lf,tex.buf_tf)
                    gl.glVertex2f(0.0,h)
                    gl.glEnd() # GL_QUADS

                else:
                    # Convert tex_phase into texture buffer fraction
                    buf_break_f = ( (tex.buf_rf - tex.buf_lf) * (1.0-tex_phase) ) + tex.buf_lf

                    # Convert tex_phase into object coords value
                    quad_x_break = w * tex_phase

                    gl.glBegin(gl.GL_QUADS)

                    # First quad

                    gl.glTexCoord2f(buf_break_f,tex.buf_bf)
                    gl.glVertex2f(0.0,0.0)

                    gl.glTexCoord2f(tex.buf_rf,tex.buf_bf)
                    gl.glVertex2f(quad_x_break,0.0)

                    gl.glTexCoord2f(tex.buf_rf,tex.buf_tf)
                    gl.glVertex2f(quad_x_break,h)

                    gl.glTexCoord2f(buf_break_f,tex.buf_tf)
                    gl.glVertex2f(0.0,h)

                    # Second quad

                    gl.glTexCoord2f(tex.buf_lf,tex.buf_bf)
                    gl.glVertex2f(quad_x_break,0.0)

                    gl.glTexCoord2f(buf_break_f,tex.buf_bf)
                    gl.glVertex2f(w,0.0)

                    gl.glTexCoord2f(buf_break_f,tex.buf_tf)
                    gl.glVertex2f(w,h)

                    gl.glTexCoord2f(tex.buf_lf,tex.buf_tf)
                    gl.glVertex2f(quad_x_break,h)
                    gl.glEnd() # GL_QUADS

            else: # draw as cylinder
                gl.glTranslatef(p.position[0],p.position[1],p.position[2])

                # center the drum on new coordinates
                gl.glRotatef(p.drum_center_azimuth,0.0,-1.0,0.0)
                gl.glRotatef(p.drum_center_elevation,1.0,0.0,0.0)

                # do the orientation
                gl.glRotatef(p.orientation,0.0,0.0,-1.0)
                
                # turn the coordinate system so we don't have to deal with
                # figuring out where to draw the texture relative to drum
                gl.glRotatef(p.angular_position,0.0,1.0,0.0)

                if p.num_sides != self.cached_display_list_num_sides:
                    self.rebuild_display_list()
                if not p.flip_image:
                    gl.glCallList(self.cached_display_list_normal)
                else:
                    gl.glCallList(self.cached_display_list_mirror)

    def rebuild_display_list(self):
        # (Re)build the display list
        #
        # A "display list" is a series of OpenGL commands that is
        # cached in a list for rapid re-drawing of the same object.
        #
        # This draws a display list for an approximation of a cylinder.
        # The cylinder has "num_sides" sides. The following code
        # generates a list of vertices and the texture coordinates
        # to be used by those vertices.
        r = self.parameters.radius # in OpenGL (arbitrary) units
        circum = 2.0*math.pi*r
        tex = self.parameters.texture
        h = circum/float(tex.size[0])*float(tex.size[1])/2.0

        num_sides = self.parameters.num_sides
        self.cached_display_list_num_sides = num_sides
        
        deltaTheta = 2.0*math.pi / num_sides
        for direction in ['normal','mirror']:
            if direction == 'normal':
                gl.glNewList(self.cached_display_list_normal,gl.GL_COMPILE)
            else:
                gl.glNewList(self.cached_display_list_mirror,gl.GL_COMPILE)
            gl.glBegin(gl.GL_QUADS)
            for i in range(num_sides):
                # angle of sides
                theta1 = i*deltaTheta
                theta2 = (i+1)*deltaTheta
                # fraction of texture
                if direction == 'normal':
                    frac1 = (tex.buf_lf + (float(i)/num_sides*tex.size[0]))/float(tex.size[0])
                    frac2 = (tex.buf_lf + (float(i+1)/num_sides*tex.size[0]))/float(tex.size[0])
                else:
                    j = num_sides-i-1
                    frac1 = (tex.buf_lf + (float(j+1)/num_sides*tex.size[0]))/float(tex.size[0])
                    frac2 = (tex.buf_lf + (float(j)/num_sides*tex.size[0]))/float(tex.size[0])
                # location of sides
                x1 = r*math.cos(theta1)
                z1 = r*math.sin(theta1)
                x2 = r*math.cos(theta2)
                z2 = r*math.sin(theta2)
    
                #Bottom left of quad
                gl.glTexCoord2f(frac1, tex.buf_bf)
                gl.glVertex4f( x1, -h, z1, 1.0 )
                
                #Bottom right of quad
                gl.glTexCoord2f(frac2, tex.buf_bf)
                gl.glVertex4f( x2, -h, z2, 1.0 )
                #Top right of quad
                gl.glTexCoord2f(frac2, tex.buf_tf); 
                gl.glVertex4f( x2,  h, z2, 1.0 )
                #Top left of quad
                gl.glTexCoord2f(frac1, tex.buf_tf)
                gl.glVertex4f( x1,  h, z1, 1.0 )
            gl.glEnd()
            gl.glEndList()

class TextureTooLargeError(VisionEgg.Core.EggError):
    pass
