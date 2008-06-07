# The Vision Egg: Textures
#
# Copyright (C) 2001-2004 Andrew Straw
# Copyright (C) 2004-2008 California Institute of Technology
#
# URL: <http://www.visionegg.org/>
#
# Distributed under the terms of the GNU Lesser General Public License
# (LGPL). See LICENSE.TXT that came with this file.

"""
Texture (images mapped onto polygons) stimuli.

"""

####################################################################
#
#        Import all the necessary packages
#
####################################################################

import logging                              # available in Python 2.3

import VisionEgg
import VisionEgg.Core
import VisionEgg.ParameterTypes as ve_types

import Image, ImageDraw                         # Python Imaging Library packages
import pygame.surface, pygame.image             # pygame
import math, types, os
import numpy
import numpy.oldnumeric as numpyNumeric, numpy.oldnumeric.mlab as MLab

import VisionEgg.GL as gl # get all OpenGL stuff in one namespace
import OpenGL.GLU as glu

# These modules are part of PIL and get loaded as needed by Image.
# They are listed here so that Gordon McMillan's Installer properly
# locates them.  You will not hurt anything other than your ability to
# make executables using Intaller if you remove these lines.
import _imaging
import ImageFile, ImageFileIO, BmpImagePlugin, JpegImagePlugin, PngImagePlugin

if Image.VERSION >= '1.1.3':
    shrink_filter = Image.ANTIALIAS # Added in PIL 1.1.3
else:
    shrink_filter = Image.BICUBIC # Fallback filtering

array_types = [numpy.ndarray]
# Allow use of numarray and original Numeric texels without requiring either
try:
    import numarray
    array_types.append( numarray.numarraycore.NumArray )
except ImportError:
    pass
try:
    import Numeric as orig_Numeric
    array_types.append( orig_Numeric.ArrayType )
except ImportError:
    pass

def convert_to_numpy_if_array(A):
    if type(A) in array_types:
        # with late release Numeric and numarray this is a view of the data
        return numpy.asarray(A)
    else:
        return A

####################################################################
#
# XXX ToDo:

# The main remaining feature to add to this module is automatic
# management of texture objects.  This would allow many small images
# (e.g. a bit of text) to live in one large texture object.  This
# would be much faster when many small textures are drawn in rapid
# succession. (Apparently this might not be such a big improvement on
# OS X. (See http://crystal.sourceforge.net/phpwiki/index.php?MacXGL)

# Here's a sample from Apple's TextureRange demo which is supposed
# to speed up texture transfers.
# glBindTextures( target, &texID);
# glPixelStorei(GL_UNPACK_CLIENT_STORAGE_APPLE, 1);
# glTexImage2D(target, 0, GL_RGBA, width, height, 0, GL_BGRA, GL_UNSIGNED_INT_8_8_8_8_REV,image_ptr);
# Update the texture with:
# glTexSubImage2D(target, 0, 0, 0, width, height, GL_BGRA, GL_UNSIGNED_INT_8_8_8_8_REV,image_ptr);

####################################################################

####################################################################
#
#        Textures
#
####################################################################

def next_power_of_2(f):
    return int(math.pow(2.0,math.ceil(math.log(f)/math.log(2.0))))

def is_power_of_2(f):
    return f == next_power_of_2(f)

class Texture(object):
    """A 2 dimensional texture.

    The pixel data can come from an image file, an image file stream,
    an instance of Image from the Python Imaging Library, a numpy
    array, or None.

    If the data is a numpy array, floating point numbers are assumed
    to be in the range 0.0 to 1.0, and integers are assumed to be in
    the range 0 to 255.  The first index is the row (y position), the
    second index is the column (x position), and if it's RGB or RGBA
    data, the third index specifies the color band.  Thus, if the
    texel data was 640 pixels wide by 480 pixels tall, the array would
    have shape (480,640) for luminance information, (480,640,3) for
    RGB information, and (480,640,4) for RGBA information.

    The 2D texture data is not sent to OpenGL (video texture memory)
    until the load() method is called.  The unload() method may be
    used to remove the data from OpenGL.

    A reference to the original image data is maintained."""

    __slots__ = ('texels',
                 'texture_object',
                 'size',
                 '_filename',
                 '_file_stream',
                 'buf_lf',
                 'buf_rf',
                 'buf_bf',
                 'buf_tf',
                 '_buf_l',
                 '_buf_r',
                 '_buf_b',
                 '_buf_t',
                 )

    def __init__(self,texels=None,size=None):
        """Creates instance of Texture object.

        texels -- Texture data. If not specified, a blank white
                  texture is created.
        size -- If a tuple, force size of texture data if possible,
                raising an exception if not. If None, has no effect.
        """

        if texels is None: # no texel data: make default
            if size is None:
                size = (256,256) # an arbitrary default size
            texels = Image.new("RGB",size,(255,255,255)) # white

        if type(texels) == types.FileType:
            texels = Image.open(texels) # Attempt to open as an image file
        elif type(texels) in (types.StringType,types.UnicodeType):
            # is this string a filename or raw image data?
            if os.path.isfile(texels):
                # cache filename and file stream for later use (if possible)
                self._filename = texels
                self._file_stream = open(texels,"rb")
            texels = Image.open(texels) # Attempt to open as an image stream

        texels = convert_to_numpy_if_array(texels)

        if isinstance(texels, Image.Image): # PIL Image
            if texels.mode == 'P': # convert from paletted
                texels = texels.convert('RGBX')
            self.size = texels.size
        elif isinstance(texels, pygame.surface.Surface): # pygame surface
            self.size = texels.get_size()
        elif isinstance(texels,numpy.ndarray): # numpy array
            if len(texels.shape) == 3:
                if texels.shape[2] not in [3,4]:
                    raise ValueError("Only luminance (rank 2), and RGB, RGBA (rank 3) arrays allowed")
            elif len(texels.shape) != 2:
                raise ValueError("Only luminance (rank 2), and RGB, RGBA (rank 3) arrays allowed")
            self.size = ( texels.shape[1], texels.shape[0] )
        else:
            raise TypeError("texel data could not be recognized. (Use a PIL Image, numpy array, or pygame surface.)")

        self.texels = texels
        self.texture_object = None

        if size is not None and size != self.size:
            raise ValueError("size was specified, but data could not be rescaled")

    def update(self):
        """Update texture data

        This method does nothing, but may be overriden in classes that
        need to update their texture data whenever drawn.

        It it called by the draw() method of any stimuli using
        textures when its texture object is active, so it can safely
        use put_sub_image() to manipulate its own texture data.
        """
        pass

    def make_half_size(self):
        if self.texture_object is not None:
            raise RuntimeError("make_half_size() only available BEFORE texture loaded to OpenGL.")

        if isinstance(self.texels,Image.Image):
            w = self.size[0]/2
            h = self.size[1]/2
            small_texels = self.texels.resize((w,h),shrink_filter)
            self.texels = small_texels
            self.size = (w,h)
        else:
            raise NotImplementedError("Texture too large, but rescaling only implemented for PIL images.")

    def unload(self):
        """Unload texture data from video texture memory.

        This only removes data from the video texture memory if there
        are no other references to the TextureObject instance.  To
        ensure this, all references to the texture_object argument
        passed to the load() method should be deleted."""

        self.texture_object = None

    def get_texels_as_image(self):
        """Return texel data as PIL image"""
        if isinstance(self.texels,numpy.ndarray):
            if len(self.texels.shape) == 2:
                a = self.texels
                if a.dtype == numpy.uint8:
                    mode = "L"
                elif a.dtype == numpy.float32:
                    mode = "F"
                else:
                    raise ValueError("unsupported image mode")
                return Image.fromstring(mode, (a.shape[1], a.shape[0]), a.tostring())
            else:
                raise NotImplementedError("Currently only luminance data can be converted to images")
        elif isinstance(self.texels, Image.Image):
            return self.texels
        else:
            raise NotImplementedError("Don't know how to convert texel data to PIL image")

    def get_pixels_as_image(self):
        logger = logging.getLogger('VisionEgg.Textures')
        logger.warning("Using deprecated method get_pixels_as_image(). "
                       "Use get_texels_as_image() instead.")
        return self.get_texels_as_image()

    def load(self,
             texture_object,
             build_mipmaps = True,
             rescale_original_to_fill_texture_object = False,
             internal_format=gl.GL_RGB):
        """Load texture data to video texture memory.

        This will cause the texture data to become resident in OpenGL
        video texture memory, enabling fast drawing.

        The texture_object argument is used to specify an instance of
        the TextureObject class, which is a wrapper for the OpenGL
        texture object holding the resident texture.

        To remove a texture from OpenGL's resident textures:       TextureObject passed as the texture_object argument and 2)
        call the unload() method"""

        assert( isinstance( texture_object, TextureObject ))
        assert( texture_object.dimensions == 2 )

        width, height = self.size

        width_pow2  = next_power_of_2(width)
        height_pow2  = next_power_of_2(height)

        if rescale_original_to_fill_texture_object:
            if not isinstance(self.texels,Image.Image):
                raise NotImplementedError("Automatic rescaling not implemented for this texel data type.")

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
            if isinstance(self.texels,numpy.ndarray):
                if len(self.texels.shape) == 2:
                    buffer = numpy.zeros( (height_pow2,width_pow2), dtype=self.texels.dtype )
                    buffer[0:height,0:width] = self.texels
                elif len(self.texels.shape) == 3:
                    buffer = numpy.zeros( (height_pow2,width_pow2,self.texels.shape[2]), dtype=self.texels.dtype )
                    buffer[0:height,0:width,:] = self.texels
                else:
                    raise RuntimeError("Unexpected shape for self.texels")

            elif isinstance(self.texels, Image.Image): # PIL Image
                if rescale_original_to_fill_texture_object:
                    # reset coverage values
                    self.buf_lf = 0.0
                    self.buf_rf = 1.0
                    self.buf_bf = 0.0
                    self.buf_tf = 1.0

                    self._buf_l = 0
                    self._buf_r = width_pow2
                    self._buf_t = 0
                    self._buf_b = height_pow2

                    buffer = self.texels.resize((width_pow2,height_pow2),shrink_filter)

                    self.size = (width_pow2, height_pow2)
                else:
                    buffer = Image.new(self.texels.mode,(width_pow2, height_pow2))
                    buffer.paste( self.texels, (0,height_pow2-height,width,height_pow2))
            elif isinstance(self.texels, pygame.surface.Surface): # pygame surface
                buffer = pygame.surface.Surface( (width_pow2, height_pow2),
                                                 self.texels.get_flags(),
                                                 self.texels.get_bitsize() )
                buffer.blit( self.texels, (0,height_pow2-height) )
            else:
                raise RuntimeError("texel data not recognized - changed?")
        else:
            buffer = self.texels

        # Put data in texture object
        if not build_mipmaps:
            texture_object.put_new_image( buffer, internal_format=internal_format, mipmap_level=0 )
        else:
            if 0:
                # Build mipmaps with GLU (faster, but currently broken)
                texture_object.put_new_image_build_mipmaps( buffer, internal_format=internal_format )
            else:
                # Build mipmaps in PIL
                texture_object.put_new_image( buffer, internal_format=internal_format, mipmap_level=0 )
                if not isinstance(self.texels, Image.Image): # PIL Image
                    raise NotImplementedError(
                        "Building of mipmaps not implemented for this texel "+\
                        "data type. (Use PIL Images or set parameter "+\
                        "mipmaps_enabled = False.)")
                this_width, this_height = self.size
                biggest_dim = max(this_width,this_height)
                mipmap_level = 1
                while biggest_dim > 1:
                    this_width = this_width/2.0
                    this_height = this_height/2.0

                    width_pix = int(math.ceil(this_width))
                    height_pix = int(math.ceil(this_height))
                    shrunk = self.texels.resize((width_pix,height_pix),shrink_filter)

                    width_pow2  = next_power_of_2(width_pix)
                    height_pow2  = next_power_of_2(height_pix)

                    im = Image.new(shrunk.mode,(width_pow2,height_pow2))
                    im.paste(shrunk,(0,height_pow2-height_pix,width_pix,height_pow2))

                    texture_object.put_new_image( im,
                                                  mipmap_level=mipmap_level,
                                                  internal_format = internal_format,
                                                  check_opengl_errors = False, # no point -- we've already seen biggest texture work, we're just making mipmap
                                                  )

                    mipmap_level += 1
                    biggest_dim = max(this_width,this_height)

        # Keep reference to texture_object
        self.texture_object = texture_object

    def get_texture_object(self):
        return self.texture_object

class TextureFromFile( Texture ):
    """DEPRECATED."""
    def __init__(self, filename ):
        logger = logging.getLogger('VisionEgg.Textures')
        logger.warning("class TextureFromFile deprecated, use class "
                       "Texture instead.")
        Texture.__init__(self, filename)

class TextureObject(object):
    """Texture data in OpenGL. Potentially resident in video texture memory.

    This class encapsulates the state variables in OpenGL texture objects.  Do not
    change attribute values directly.  Use the methods provided instead."""

    __slots__ = (
        'min_filter',
        'mag_filter',
        'wrap_mode_r', # if dimensions > 2
        'wrap_mode_s',
        'wrap_mode_t', # if dimensions > 1
        'border_color',
        'target',
        'dimensions',
        'gl_id',
        '__gl_module__',
        )

    _cube_map_side_names = ['positive_x', 'negative_x',
                            'positive_y', 'negative_y',
                            'positive_z', 'negative_z']

    def __init__(self,
                 dimensions = 2):
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
        self.__gl_module__ = gl # keep so we there's no error in __del__

    def __del__(self):
        self.__gl_module__.glDeleteTextures(self.gl_id)

    def is_resident(self):
        return gl.glAreTexturesResident( self.gl_id )

    def set_priority(self, priority):
        gl.glPrioritizeTextures( [self.gl_id], [priority] )

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
                      texel_data,
                      mipmap_level = 0,
                      border = 0,
                      check_opengl_errors = True,
                      internal_format = gl.GL_RGB,
                      data_format = None, # automatic guess unless set explicitly
                      data_type = None, # automatic guess unless set explicitly
                      cube_side = None,
                      ):

        """Put numpy array or PIL Image into OpenGL as texture data.

        The texel_data parameter contains the texture data.  If it is
        a numpy array, it must be 1D, 2D, or 3D data in grayscale or
        color (RGB or RGBA).  Remember that OpenGL begins its textures
        from the lower left corner, so texel_data[0,:] = 1.0 would set
        the bottom line of the texture to white, while texel_data[:,0]
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
        description. For numpy arrays: If texel_data.shape is equal
        to the dimensions of the texture object, texel_data is assumed
        to contain luminance (grayscale) information and data_format
        is set to GL_LUMINANCE.  If texel_data.shape is equal to one
        plus the dimensions of the texture object, texel_data is
        assumed to contain color information.  If texel_data.shape[-1]
        is 3, this is assumed to be RGB data and data_format is set to
        GL_RGB.  If, texel_data.shape[-1] is 4, this is assumed to be
        RGBA data and data_format is set to GL_RGBA. For PIL images:
        the "mode" attribute is queried.

        If the data_type parameter is None (the default), it is set to
        GL_UNSIGNED_BYTE. For numpy arrays: texel_data is (re)cast
        to UInt8 and, if it is a floating point type, values are
        assumed to be in the range 0.0-1.0 and are scaled to the range
        0-255.  If the data_type parameter is not None, the texel_data
        is not rescaled or recast.  Currently only GL_UNSIGNED_BYTE is
        supported. For PIL images: texel_data is used as unsigned
        bytes.  This is the usual format for common computer graphics
        files."""

        texel_data = convert_to_numpy_if_array(texel_data)
        if isinstance(texel_data,numpy.ndarray):
            if self.dimensions != 'cube':
                assert(cube_side == None)
                data_dimensions = len(texel_data.shape)
                assert((data_dimensions == self.dimensions) or (data_dimensions == self.dimensions+1))
            else:
                assert(cube_side in TextureObject._cube_map_side_names)
        elif isinstance(texel_data,Image.Image):
            assert( self.dimensions == 2 )
        elif isinstance(texel_data,pygame.surface.Surface):
            assert( self.dimensions == 2 )
        else:
            raise TypeError("Expecting numpy array, PIL image, or pygame surface")

        # make myself the active texture
        gl.glBindTexture(self.target, self.gl_id)

        # Determine the data_format, data_type and rescale the data if needed
        if data_format is None: # guess the format of the data
            if isinstance(texel_data,numpy.ndarray):
                if len(texel_data.shape) == self.dimensions:
                    data_format = gl.GL_LUMINANCE
                elif len(texel_data.shape) == (self.dimensions+1):
                    if texel_data.shape[-1] == 3:
                        data_format = gl.GL_RGB
                    elif texel_data.shape[-1] == 4:
                        data_format = gl.GL_RGBA
                    else:
                        raise RuntimeError("Couldn't determine a format for your texel_data.")
                else:
                    raise RuntimeError("Couldn't determine a format for your texel_data.")
            elif isinstance(texel_data,Image.Image):
                if texel_data.mode == 'L':
                    data_format = gl.GL_LUMINANCE
                elif texel_data.mode == 'RGB':
                    data_format = gl.GL_RGB
                elif texel_data.mode in ('RGBA','RGBX'):
                    data_format = gl.GL_RGBA
                elif texel_data.mode == 'P':
                    raise NotImplementedError("Paletted images are not supported.")
                else:
                    raise RuntimeError("Couldn't determine format for your texel_data. (PIL mode = '%s')"%texel_data.mode)
            elif isinstance(texel_data,pygame.surface.Surface):
                if texel_data.get_alpha():
                    data_format = gl.GL_RGBA
                else:
                    data_format = gl.GL_RGB

        if data_type is None: # guess the data type
            data_type = gl.GL_UNSIGNED_BYTE
            if isinstance(texel_data,numpy.ndarray):
                if texel_data.dtype == numpy.float:
                    texel_data = texel_data*255.0

        if data_type == gl.GL_UNSIGNED_BYTE:
            if isinstance(texel_data,numpy.ndarray):
                texel_data = texel_data.astype(numpy.uint8) # (re)cast if necessary
        else:
            raise NotImplementedError("Only data_type GL_UNSIGNED_BYTE currently supported")

        # determine size and make sure its power of 2
        if self.dimensions == 1:
            # must be numpy array
            width = texel_data.shape[0]
            if not is_power_of_2(width): raise ValueError("texel_data does not have all dimensions == n^2")
        else:
            if isinstance(texel_data,numpy.ndarray):
                width = texel_data.shape[1]
                height = texel_data.shape[0]
            elif isinstance(texel_data,Image.Image):
                width, height = texel_data.size
            elif isinstance(texel_data,pygame.surface.Surface):
                width, height = texel_data.get_size()
            if not is_power_of_2(width): raise ValueError("texel_data does not have all dimensions == n^2")
            if not is_power_of_2(height): raise ValueError("texel_data does not have all dimensions == n^2")
            if self.dimensions == 3:
                # must be numpy array
                depth = texel_data.shape[2]
                if not is_power_of_2(depth): raise ValueError("texel_data does not have all dimensions == n^2")

        if self.dimensions in [2,'cube']:
            if isinstance(texel_data,numpy.ndarray):
                raw_data = texel_data.tostring()
            elif isinstance(texel_data,Image.Image):
                raw_data = texel_data.tostring('raw',texel_data.mode,0,-1)
            elif isinstance(texel_data,pygame.surface.Surface):
                if texel_data.get_alpha():
                    raw_data = pygame.image.tostring(texel_data,'RGBA',1)
                else:
                    raw_data = pygame.image.tostring(texel_data,'RGB',1)

        # check for OpenGL errors
        if check_opengl_errors:
            max_dim = gl.glGetIntegerv( gl.GL_MAX_TEXTURE_SIZE )
            if width > max_dim:
                raise TextureTooLargeError("texel_data is too wide for your video system.")
            if self.dimensions == 1:
                gl.glTexImage1Dub(gl.GL_PROXY_TEXTURE_1D,
                                mipmap_level,
                                internal_format,
                                border,
                                data_format,
                                texel_data)
                if gl.glGetTexLevelParameteriv(gl.GL_PROXY_TEXTURE_1D,mipmap_level,gl.GL_TEXTURE_WIDTH) == 0:
                    raise TextureTooLargeError("texel_data is too wide for your video system.")
            elif self.dimensions in [2,'cube']:
                if height > max_dim:
                    raise TextureTooLargeError("texel_data is too tall for your video system.")
                if self.dimensions == 2:
                    target = gl.GL_PROXY_TEXTURE_2D
                else:
                    target = gl.GL_PROXY_CUBE_MAP
                gl.glTexImage2D(target,
                                mipmap_level,
                                internal_format,
                                width,
                                height,
                                border,
                                data_format,
                                data_type,
                                raw_data)
                if gl.glGetTexLevelParameteriv(target, # Need PyOpenGL >= 2.0
                                               mipmap_level,
                                               gl.GL_TEXTURE_WIDTH) == 0:
                    raise TextureTooLargeError("texel_data is too wide for your video system.")
                if gl.glGetTexLevelParameteriv(target,mipmap_level,gl.GL_TEXTURE_HEIGHT) == 0:
                    raise TextureTooLargeError("texel_data is too tall for your video system.")
            elif self.dimensions == 3:
                if max(height,depth) > max_dim:
                    raise TextureTooLargeError("texel_data is too large for your video system.")
                gl.glTexImage3Dub(gl.GL_PROXY_TEXTURE_3D,
                                  mipmap_level,
                                  internal_format,
                                  border,
                                  data_format,
                                  texel_data)
                if gl.glGetTexLevelParameteriv(gl.GL_PROXY_TEXTURE_3D,mipmap_level,gl.GL_TEXTURE_WIDTH) == 0:
                    raise TextureTooLargeError("texel_data is too wide for your video system.")
                if gl.glGetTexLevelParameteriv(gl.GL_PROXY_TEXTURE_3D,mipmap_level,gl.GL_TEXTURE_HEIGHT) == 0:
                    raise TextureTooLargeError("texel_data is too tall for your video system.")
                if gl.glGetTexLevelParameteriv(gl.GL_PROXY_TEXTURE_3D,mipmap_level,gl.GL_TEXTURE_DEPTH) == 0:
                    raise TextureTooLargeError("texel_data is too deep for your video system.")
            else:
                raise RuntimeError("Unknown number of dimensions.")

        # No OpenGL error, put the texture in!
        if self.dimensions == 1:
            gl.glTexImage1Dub(gl.GL_TEXTURE_1D,
                              mipmap_level,
                              internal_format,
                              border,
                              data_format,
                              texel_data)
        elif self.dimensions in [2,'cube']:
            if self.dimensions == 2:
                target = gl.GL_TEXTURE_2D
            else:
                target_name = 'GL_CUBE_MAP_'+cube_side.upper()
                target = getattr(gl,target_name)
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
                              texel_data)
        else:
            raise RuntimeError("Unknown number of dimensions.")

    def put_new_image_build_mipmaps(self,
                                    texel_data,
                                    internal_format = gl.GL_RGB,
                                    data_format = None, # automatic guess unless set explicitly
                                    data_type = None,   # automatic guess unless set explicitly
                                    cube_side = None,
                                    ):

        """Similar to put_new_image(), but builds mipmaps."""

        if self.dimensions != 2:
            raise ValueError("can only handle 2D texel data for automatic mipmap building")
        texel_data = convert_to_numpy_if_array(texel_data)
        if isinstance(texel_data,numpy.ndarray):
            assert(cube_side == None)
            data_dimensions = len(texel_data.shape)
            assert((data_dimensions == self.dimensions) or (data_dimensions == self.dimensions+1))
        elif isinstance(texel_data,Image.Image):
            assert( self.dimensions == 2 )
        elif isinstance(texel_data,pygame.surface.Surface):
            assert( self.dimensions == 2 )
        else:
            raise TypeError("Expecting numpy array, PIL image, or pygame surface")

        # make myself the active texture
        gl.glBindTexture(self.target, self.gl_id)

        # Determine the data_format, data_type and rescale the data if needed
        if data_format is None: # guess the format of the data
            if isinstance(texel_data,numpy.ndarray):
                if len(texel_data.shape) == self.dimensions:
                    data_format = gl.GL_LUMINANCE
                elif len(texel_data.shape) == (self.dimensions+1):
                    if texel_data.shape[-1] == 3:
                        data_format = gl.GL_RGB
                    elif texel_data.shape[-1] == 4:
                        data_format = gl.GL_RGBA
                    else:
                        raise RuntimeError("Couldn't determine a format for your texel_data.")
                else:
                    raise RuntimeError("Couldn't determine a format for your texel_data.")
            elif isinstance(texel_data,Image.Image):
                if texel_data.mode == 'L':
                    data_format = gl.GL_LUMINANCE
                elif texel_data.mode == 'RGB':
                    data_format = gl.GL_RGB
                elif texel_data.mode in ['RGBA','RGBX']:
                    data_format = gl.GL_RGBA
                elif texel_data.mode == 'P':
                    raise NotImplementedError("Paletted images are not supported.")
                else:
                    raise RuntimeError("Couldn't determine format for your texel_data. (PIL mode = '%s')"%texel_data.mode)
            elif isinstance(texel_data,pygame.surface.Surface):
                if texel_data.get_alpha():
                    data_format = gl.GL_RGBA
                else:
                    data_format = gl.GL_RGB

        if data_type is None: # guess the data type
            data_type = gl.GL_UNSIGNED_BYTE
            if isinstance(texel_data,numpy.ndarray):
                if texel_data.dtype == numpy.float:
                    texel_data = texel_data*255.0

        if data_type == gl.GL_UNSIGNED_BYTE:
            if isinstance(texel_data,numpy.ndarray):
                texel_data = texel_data.astype(numpy.uint8) # (re)cast if necessary
        else:
            raise NotImplementedError("Only data_type GL_UNSIGNED_BYTE currently supported")

        if isinstance(texel_data,numpy.ndarray):
            width = texel_data.shape[1]
            height = texel_data.shape[0]
        elif isinstance(texel_data,Image.Image):
            width, height = texel_data.size
        elif isinstance(texel_data,pygame.surface.Surface):
            width, height = texel_data.get_size()
        if not is_power_of_2(width): raise ValueError("texel_data does not have all dimensions == n^2")
        if not is_power_of_2(height): raise ValueError("texel_data does not have all dimensions == n^2")

        if isinstance(texel_data,numpy.ndarray):
            raw_data = texel_data.tostring()
        elif isinstance(texel_data,Image.Image):
            raw_data = texel_data.tostring('raw',texel_data.mode,0,-1)
        elif isinstance(texel_data,pygame.surface.Surface):
            if texel_data.get_alpha():
                raw_data = pygame.image.tostring(texel_data,'RGBA',1)
            else:
                raw_data = pygame.image.tostring(texel_data,'RGB',1)

        args = (self.target,
                              internal_format,
                              width, # XXX should be width_pow2?
                              height,# XXX should be height_pow2?
                              data_format,
                              data_type)
                              #raw_data)
        print 'args',args

        glu.gluBuild2DMipmaps(self.target,
                              internal_format,
                              width, # XXX should be width_pow2?
                              height,# XXX should be height_pow2?
                              data_format,
                              data_type,
                              raw_data)

    def put_sub_image(self,
                      texel_data,
                      mipmap_level = 0,
                      offset_tuple = None,
                      data_format = None, # automatic guess unless set explicitly
                      data_type = None, # automatic guess unless set explicitly
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

        texel_data = convert_to_numpy_if_array(texel_data)
        if isinstance(texel_data,numpy.ndarray):
            if self.dimensions != 'cube':
                assert(cube_side == None)
                data_dimensions = len(texel_data.shape)
                assert((data_dimensions == self.dimensions) or (data_dimensions == self.dimensions+1))
            else:
                assert(cube_side in TextureObject._cube_map_side_names)
        elif isinstance(texel_data,Image.Image):
            assert( self.dimensions == 2 )
        elif isinstance(texel_data,pygame.surface.Surface):
            assert( self.dimensions == 2 )
        else:
            raise TypeError("Expecting numpy array, PIL image, or pygame surface")

        # make myself the active texture
        gl.glBindTexture(self.target, self.gl_id)

        # Determine the data_format, data_type and rescale the data if needed
        data = texel_data

        if data_format is None: # guess the format of the data
            if isinstance(texel_data,numpy.ndarray):
                if len(data.shape) == self.dimensions:
                    data_format = gl.GL_LUMINANCE
                elif len(data.shape) == (self.dimensions+1):
                    if data.shape[-1] == 3:
                        data_format = gl.GL_RGB
                    elif data.shape[-1] == 4:
                        data_format = gl.GL_RGBA
                    else:
                        raise RuntimeError("Couldn't determine a format for your texel_data.")
                else:
                    raise RuntimeError("Couldn't determine a format for your texel_data.")
            elif isinstance(texel_data,Image.Image):
                if data.mode == 'L':
                    data_format = gl.GL_LUMINANCE
                elif data.mode == 'RGB':
                    data_format = gl.GL_RGB
                elif data.mode in ['RGBA','RGBX']:
                    data_format = gl.GL_RGBA
                elif data.mode == 'P':
                    raise NotImplementedError("Paletted images are not supported.")
                else:
                    raise RuntimeError("Couldn't determine format for your texel_data. (PIL mode = '%s')"%data.mode)
            elif isinstance(texel_data,pygame.surface.Surface):
                if data.get_alpha():
                    data_format = gl.GL_RGBA
                else:
                    data_format = gl.GL_RGB

        if data_type is None: # guess the data type
            data_type = gl.GL_UNSIGNED_BYTE
            if isinstance(data,numpy.ndarray):
                if data.dtype == numpy.float:
                    data = data*255.0

        if data_type == gl.GL_UNSIGNED_BYTE:
            if isinstance(data,numpy.ndarray):
                data = data.astype(numpy.uint8) # (re)cast if necessary
        else:
            raise NotImplementedError("Only data_type GL_UNSIGNED_BYTE currently supported")

        if self.dimensions == 1:
            if offset_tuple is None:
                x_offset = 0
            else:
                x_offset = offset_tuple[0]
            width = data.shape[0]
            raw_data = data.astype(numpy.uint8).tostring()
            gl.glTexSubImage1D(gl.GL_TEXTURE_1D,
                               mipmap_level,
                               x_offset,
                               width,
                               data_format,
                               data_type,
                               raw_data)
        elif self.dimensions in [2,'cube']:
            if self.dimensions == 2:
                target = gl.GL_TEXTURE_2D
            else:
                target_name = 'GL_CUBE_MAP_'+cube_side.upper()
                target = getattr(gl,target_name)
            if offset_tuple is None:
                x_offset = y_offset = 0
            else:
                x_offset, y_offset = offset_tuple
            if isinstance(data,numpy.ndarray):
                width = data.shape[1]
                height = data.shape[0]
                raw_data = data.astype(numpy.uint8).tostring()
            elif isinstance(texel_data,Image.Image):
                width = data.size[0]
                height = data.size[1]
                raw_data = data.tostring('raw',data.mode,0,-1)
            elif isinstance(texel_data,pygame.surface.Surface):
                width, height = texel_data.get_size()
                if data.get_alpha():
                    raw_data = pygame.image.tostring(texel_data,'RGBA',1)
                else:
                    raw_data = pygame.image.tostring(texel_data,'RGB',1)
            gl.glTexSubImage2D(target,
                               mipmap_level,
                               x_offset,
                               y_offset,
                               width,
                               height,
                               data_format,
                               data_type,
                               raw_data)
        elif self.dimensions == 3:
            raise RuntimeError("Cannot put_sub_image on 3D texture_object.")
        else:
            raise RuntimeError("Unknown number of dimensions.")

    def put_new_framebuffer(self,
                            buffer='back',
                            mipmap_level = 0,
                            border = 0,
                            framebuffer_lowerleft = None,
                            size = None,
                            internal_format = gl.GL_RGB,
                            cube_side = None,
                            ):

        """Replace texture object with the framebuffer contents.

        The framebuffer_lowerleft parameter determines the lower left
        corner of the framebuffer region from which to copy texel data
        in pixel units.  For example, (0,0) would be no offset and
        thus the new data would be placed from the lower left of the
        framebuffer.

        For an explanation of most parameters, see the
        put_new_image() method."""

        if self.dimensions != 2:
            raise RuntimeError("put_new_framebuffer only supported for 2D textures.")

        if buffer == 'front':
            gl.glReadBuffer( gl.GL_FRONT )
        elif buffer == 'back':
            gl.glReadBuffer( gl.GL_BACK )
        else:
            raise ValueError('No support for "%s" framebuffer'%buffer)

        # make myself the active texture
        gl.glBindTexture(self.target, self.gl_id)

        if framebuffer_lowerleft is None:
            framebuffer_lowerleft = (0,0)
        x,y = framebuffer_lowerleft

        if size is None:
            raise ValueError("Must specify size for put_new_framebuffer(): cannot guess")

        # determine size and make sure its power of 2
        width, height = size
        if not is_power_of_2(width): raise ValueError("texel_data does not have all dimensions == n^2")
        if not is_power_of_2(height): raise ValueError("texel_data does not have all dimensions == n^2")

        target = gl.GL_TEXTURE_2D
        gl.glCopyTexImage2D(target,
                            mipmap_level,
                            internal_format,
                            x,
                            y,
                            width,
                            height,
                            border)

####################################################################
#
#        Stimulus - TextureStimulus
#
####################################################################

class TextureStimulusBaseClass(VisionEgg.Core.Stimulus):
    """Parameters common to all stimuli that use textures.

    Don't instantiate this class directly.

    Parameters
    ==========
    texture            -- source of texture data (Instance of <class 'VisionEgg.Textures.Texture'>)
                          Default: (determined at runtime)
    texture_mag_filter -- OpenGL filter enum (Integer)
                          Default: GL_LINEAR (9729)
    texture_min_filter -- OpenGL filter enum (Integer)
                          Default: (GL enum determined at runtime)
    texture_wrap_s     -- OpenGL texture wrap enum (Integer)
                          Default: (GL enum determined at runtime)
    texture_wrap_t     -- OpenGL texture wrap enum (Integer)
                          Default: (GL enum determined at runtime)

    Constant Parameters
    ===================
    internal_format   -- format with which OpenGL uses texture data (OpenGL data type enum) (Integer)
                         Default: GL_RGB (6407)
    mipmaps_enabled   -- Are mipmaps enabled? (Boolean)
                         Default: True
    shrink_texture_ok -- Allow automatic shrinking of texture if too big? (Boolean)
                         Default: False
    """

    parameters_and_defaults = {
        'texture':(None,
                   ve_types.Instance(Texture),
                   "source of texture data"),
        'texture_mag_filter':(gl.GL_LINEAR,
                              ve_types.Integer,
                              "OpenGL filter enum",
                              VisionEgg.ParameterDefinition.OPENGL_ENUM),
        'texture_min_filter':(None, # defaults to gl.GL_LINEAR_MIPMAP_LINEAR (unless mipmaps_enabled False, then gl.GL_LINEAR)
                              ve_types.Integer,
                              "OpenGL filter enum",
                              VisionEgg.ParameterDefinition.OPENGL_ENUM),
        'texture_wrap_s':(None, # set to gl.GL_CLAMP_TO_EDGE below
                          ve_types.Integer,
                          "OpenGL texture wrap enum",
                          VisionEgg.ParameterDefinition.OPENGL_ENUM),
        'texture_wrap_t':(None, # set to gl.GL_CLAMP_TO_EDGE below
                          ve_types.Integer,
                          "OpenGL texture wrap enum",
                          VisionEgg.ParameterDefinition.OPENGL_ENUM),
        }

    constant_parameters_and_defaults = {
        'internal_format':(gl.GL_RGB,#None,
                           ve_types.Integer,
                           "format with which OpenGL uses texture data (OpenGL data type enum)",
                           VisionEgg.ParameterDefinition.OPENGL_ENUM),
        'mipmaps_enabled':(True,
                           ve_types.Boolean,
                           "Are mipmaps enabled?"),
        'shrink_texture_ok':(False,
                             ve_types.Boolean,
                             "Allow automatic shrinking of texture if too big?"),
        }

    __slots__ = (
        'texture_object',
        '_using_texture',
        )

    _mipmap_modes = [gl.GL_LINEAR_MIPMAP_LINEAR,gl.GL_LINEAR_MIPMAP_NEAREST,
                     gl.GL_NEAREST_MIPMAP_LINEAR,gl.GL_NEAREST_MIPMAP_NEAREST]

    def __init__(self,**kw):
        VisionEgg.Core.Stimulus.__init__(self,**kw)

        if self.parameters.texture is None:
            # generate default texture
            self.parameters.texture = Texture()

        if self.parameters.texture_min_filter is None:
            # generate default texture minimization filter
            if self.constant_parameters.mipmaps_enabled:
                self.parameters.texture_min_filter = gl.GL_LINEAR_MIPMAP_LINEAR
            else:
                self.parameters.texture_min_filter = gl.GL_LINEAR

        if not self.constant_parameters.mipmaps_enabled:
            if self.parameters.texture_min_filter in TextureStimulusBaseClass._mipmap_modes:
                raise ValueError("texture_min_filter cannot be a mipmap type if mipmaps not enabled.")
        # We have to set these parameters here because we may have
        # re-assigned gl.GL_CLAMP_TO_EDGE.  This allows us to use
        # symbol gl.GL_CLAMP_TO_EDGE even if our version of OpenGL
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
                            internal_format = self.constant_parameters.internal_format,
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
                                    internal_format = self.constant_parameters.internal_format,
                                    build_mipmaps = self.constant_parameters.mipmaps_enabled )
                except TextureTooLargeError:
                    p.texture.make_half_size()
                    resized = 1
                else:
                    loaded_ok = 1
            if resized:
                logger = logging.getLogger('VisionEgg.Textures')
                logger.warning("Resized texture in %s to %d x %d"%(
                    str(self),p.texture.size[0],p.texture.size[1]))

class Mask2D(VisionEgg.ClassWithParameters):
    """A mask for windowing a portion of a texture.

    Thanks to the author, Jon Peirce, of the AlphaStim class from the
    PsychoPy package from which the idea to do this came.

    Constant Parameters
    ===================
    function         -- 'gaussian' or 'circle' (String)
                        Default: gaussian
    num_samples      -- size of mask texture data (units: number of texels) (Sequence2 of Real)
                        Default: (256, 256)
    radius_parameter -- radius for circle, sigma for gaussian (Real)
                        Default: 25.0
    """

    # All of these parameters are constant -- if you need a new mask, create a new instance
    constant_parameters_and_defaults = {
        'function':('gaussian', # can be 'gaussian' or 'circle'
                    ve_types.String,
                    "'gaussian' or 'circle'"),
        'radius_parameter':(25.0, # radius for circle, sigma for gaussian, same units as num_samples
                            ve_types.Real,
                            "radius for circle, sigma for gaussian"),
        'num_samples':((256,256), # size of mask data in texels
                       ve_types.Sequence2(ve_types.Real),
                       "size of mask texture data (units: number of texels)"),
        }
    def __init__(self,**kw):
        VisionEgg.ClassWithParameters.__init__(self,**kw)

        cp = self.constant_parameters # shorthand
        width,height = cp.num_samples
        if width != next_power_of_2(width):
            raise RuntimeError("Mask must have width num_samples power of 2")
        if height != next_power_of_2(height):
            raise RuntimeError("Mask must have height num_samples power of 2")

        gl.glActiveTextureARB(gl.GL_TEXTURE1_ARB) # Need PyOpenGL >= 2.0
        self.texture_object = TextureObject(dimensions=2)

        if cp.function == "gaussian":
            xx = numpyNumeric.outerproduct(numpyNumeric.ones((1,cp.num_samples[1])),
                                      numpyNumeric.arange(0,cp.num_samples[0],1.0)-cp.num_samples[0]/2)
            yy = numpyNumeric.outerproduct(numpyNumeric.arange(0,cp.num_samples[1],1.0)-cp.num_samples[1]/2,
                                      numpyNumeric.ones((1,cp.num_samples[0])))
            dist_from_center = numpyNumeric.sqrt(xx**2 + yy**2)
            sigma = cp.radius_parameter
            data = numpyNumeric.exp( -dist_from_center**2.0 / (2.0*sigma**2.0) )
        elif cp.function == "circle":
            data = numpyNumeric.zeros(cp.num_samples,numpyNumeric.Float)
            # perform anti-aliasing in circle computation by computing
            # at several slightly different locations and averaging
            oversamples = 4
            x_offsets = numpyNumeric.arange(0.0,1.0,1.0/oversamples)
            x_offsets = x_offsets - MLab.mean(x_offsets)
            y_offsets = x_offsets
            for x_offset in x_offsets:
                for y_offset in y_offsets:
                    xx = numpyNumeric.outerproduct(numpyNumeric.ones((1,cp.num_samples[1])),
                                              numpyNumeric.arange(0,cp.num_samples[0],1.0)-cp.num_samples[0]/2+0.5)+x_offset
                    yy = numpyNumeric.outerproduct(numpyNumeric.arange(0,cp.num_samples[1],1.0)-cp.num_samples[1]/2+0.5,
                                              numpyNumeric.ones((1,cp.num_samples[0])))+y_offset
                    dist_from_center = numpyNumeric.sqrt(xx**2 + yy**2)
                    data += dist_from_center <= cp.radius_parameter
            data = data / float( len(x_offsets)*len(y_offsets) )
        else:
            raise RuntimeError("Don't know about window function %s"%self.constant_parameters.function)

        self.texture_object.put_new_image(data,
                                          data_format=gl.GL_ALPHA,
                                          internal_format=gl.GL_ALPHA)
        self.texture_object.set_min_filter(gl.GL_LINEAR) # turn off mipmaps for mask
        self.texture_object.set_wrap_mode_s(gl.GL_CLAMP_TO_EDGE)
        self.texture_object.set_wrap_mode_t(gl.GL_CLAMP_TO_EDGE)
        gl.glTexEnvi(gl.GL_TEXTURE_ENV, gl.GL_TEXTURE_ENV_MODE, gl.GL_MODULATE)

        # reset active texture unit to 0
        gl.glActiveTextureARB(gl.GL_TEXTURE0_ARB)

    def draw_masked_quad_3d(self,lt,rt,bt,tt,v1,v2,v3,v4):
        # The *t parameters are the texture coordinates.

        # By the time this method is called, GL_TEXTURE0_ARB should be
        # loaded as the texture object to be masked.

        gl.glActiveTextureARB(gl.GL_TEXTURE1_ARB) # bind 2nd texture unit to mask texture
        gl.glBindTexture(gl.GL_TEXTURE_2D, self.texture_object.gl_id)
        gl.glEnable(gl.GL_TEXTURE_2D)

        # The normal TEXTURE2D object is the 1st (TEXTURE0) texture unit
        gl.glBegin(gl.GL_QUADS)

        gl.glMultiTexCoord2fARB(gl.GL_TEXTURE0_ARB,lt,bt)
        gl.glMultiTexCoord2fARB(gl.GL_TEXTURE1_ARB,0.0,0.0)
        gl.glVertex3f(*v1)

        gl.glMultiTexCoord2fARB(gl.GL_TEXTURE0_ARB,rt,bt)
        gl.glMultiTexCoord2fARB(gl.GL_TEXTURE1_ARB,1.0,0.0)
        gl.glVertex3f(*v2)

        gl.glMultiTexCoord2fARB(gl.GL_TEXTURE0_ARB,rt,tt)
        gl.glMultiTexCoord2fARB(gl.GL_TEXTURE1_ARB,1.0,1.0)
        gl.glVertex3f(*v3)

        gl.glMultiTexCoord2fARB(gl.GL_TEXTURE0_ARB,lt,tt)
        gl.glMultiTexCoord2fARB(gl.GL_TEXTURE1_ARB,0.0,1.0)
        gl.glVertex3f(*v4)

        gl.glEnd() # GL_QUADS
        gl.glDisable(gl.GL_TEXTURE_2D) # turn off texturing in this texture unit
        gl.glActiveTextureARB(gl.GL_TEXTURE0_ARB) # return to 1st texture unit

    def draw_masked_quad(self,lt,rt,bt,tt,le,re,be,te,depth):
        # The *t parameters are the texture coordinates. The *e
        # parameters are the eye coordinates for the vertices of the
        # quad.
        v1 = (le,be,depth)
        v2 = (re,be,depth)
        v3 = (re,te,depth)
        v4 = (le,te,depth)
        self.draw_masked_quad_3d(lt,rt,bt,tt,v1,v2,v3,v4)

class TextureStimulus(TextureStimulusBaseClass):
    """A textured rectangle.

    This is mainly for 2D use (z coordinate fixed to 0.0 and w
    coordinated fixed to 1.0 if not given).


    Parameters
    ==========
    anchor             -- specifies how position parameter is interpreted (String)
                          Default: lowerleft
    angle              -- units: degrees, 0=right, 90=up (Real)
                          Default: 0.0
    color              -- texture environment color. alpha ignored (if given) for max_alpha parameter (AnyOf(Sequence3 of Real or Sequence4 of Real))
                          Default: (1.0, 1.0, 1.0)
    depth_test         -- perform depth test? (Boolean)
                          Default: False
    mask               -- optional masking function (Instance of <class 'VisionEgg.Textures.Mask2D'>)
                          Default: (determined at runtime)
    max_alpha          -- controls opacity. 1.0=copletely opaque, 0.0=completely transparent (Real)
                          Default: 1.0
    on                 -- draw stimulus? (Boolean)
                          Default: True
    position           -- units: eye coordinates (AnyOf(Sequence2 of Real or Sequence3 of Real or Sequence4 of Real))
                          Default: (0.0, 0.0)
    size               -- defaults to texture data size (units: eye coordinates) (Sequence2 of Real)
                          Default: (determined at runtime)
    texture            -- source of texture data (Instance of <class 'VisionEgg.Textures.Texture'>)
                          Inherited from TextureStimulusBaseClass
                          Default: (determined at runtime)
    texture_mag_filter -- OpenGL filter enum (Integer)
                          Inherited from TextureStimulusBaseClass
                          Default: GL_LINEAR (9729)
    texture_min_filter -- OpenGL filter enum (Integer)
                          Inherited from TextureStimulusBaseClass
                          Default: (GL enum determined at runtime)
    texture_wrap_s     -- OpenGL texture wrap enum (Integer)
                          Inherited from TextureStimulusBaseClass
                          Default: (GL enum determined at runtime)
    texture_wrap_t     -- OpenGL texture wrap enum (Integer)
                          Inherited from TextureStimulusBaseClass
                          Default: (GL enum determined at runtime)

    Constant Parameters
    ===================
    internal_format   -- format with which OpenGL uses texture data (OpenGL data type enum) (Integer)
                         Default: GL_RGB (6407)
    mipmaps_enabled   -- Are mipmaps enabled? (Boolean)
                         Default: True
    shrink_texture_ok -- Allow automatic shrinking of texture if too big? (Boolean)
                         Default: False
    """

    parameters_and_defaults = {
        'on':(True,
              ve_types.Boolean,
              "draw stimulus?"),
        'mask':(None, # texture mask
                ve_types.Instance(Mask2D),
                "optional masking function"),
        'position':((0.0,0.0), # in eye coordinates
                    ve_types.AnyOf(ve_types.Sequence2(ve_types.Real),
                                   ve_types.Sequence3(ve_types.Real),
                                   ve_types.Sequence4(ve_types.Real)),
                    "units: eye coordinates"),
        'anchor':('lowerleft',
                  ve_types.String,
                  "specifies how position parameter is interpreted"),
        'lowerleft':(None,  # DEPRECATED -- don't use
                     ve_types.Sequence2(ve_types.Real),
                     "",
                     VisionEgg.ParameterDefinition.DEPRECATED),
        'angle':(0.0, # in degrees
                 ve_types.Real,
                 "units: degrees, 0=right, 90=up"),
        'size':(None,
                ve_types.Sequence2(ve_types.Real),
                "defaults to texture data size (units: eye coordinates)"),
        'max_alpha':(1.0, # controls "opacity": 1.0 = completely opaque, 0.0 = completely transparent
                     ve_types.Real,
                     "controls opacity. 1.0=copletely opaque, 0.0=completely transparent"),
        'color':((1.0,1.0,1.0), # texture environment color. alpha is ignored (if given) -- use max_alpha parameter
                 ve_types.AnyOf(ve_types.Sequence3(ve_types.Real),
                                ve_types.Sequence4(ve_types.Real)),
                 "texture environment color. alpha ignored (if given) for max_alpha parameter"),
        'depth_test':(False,
                      ve_types.Boolean,
                      "perform depth test?"),
        }

    def draw(self):
        p = self.parameters
        if p.texture != self._using_texture: # self._using_texture is from TextureStimulusBaseClass
            self._reload_texture()
        if p.lowerleft != None:
            if not hasattr(VisionEgg.config,"_GAVE_LOWERLEFT_DEPRECATION"):
                logger = logging.getLogger('VisionEgg.Textures')
                logger.warning("Specifying texture by 'lowerleft' "
                               "deprecated parameter deprecated.  Use "
                               "'position' parameter instead.  (Allows "
                               "use of 'anchor' parameter to set to "
                               "other values.)")
                VisionEgg.config._GAVE_LOWERLEFT_DEPRECATION = 1
            p.anchor = 'lowerleft'
            p.position = p.lowerleft[0], p.lowerleft[1] # copy values (don't copy ref to tuple)
        if p.on:
            tex = p.texture

            if p.size is None:
                # Note: 'size' attribute is not supposed to be part of the API,
                # so this is naughty.
                size = tex.size
            else:
                size = p.size

            # calculate lowerleft corner
            lowerleft = VisionEgg._get_lowerleft(p.position,p.anchor,size)

            # Clear the modelview matrix
            gl.glMatrixMode(gl.GL_MODELVIEW)
            gl.glPushMatrix()
            try:
                if p.depth_test:
                    gl.glEnable(gl.GL_DEPTH_TEST)
                else:
                    gl.glDisable(gl.GL_DEPTH_TEST)
                gl.glEnable( gl.GL_TEXTURE_2D )

                # allow max_alpha value to control blending
                gl.glEnable( gl.GL_BLEND )
                gl.glBlendFunc( gl.GL_SRC_ALPHA, gl.GL_ONE_MINUS_SRC_ALPHA )

                if not self.constant_parameters.mipmaps_enabled:
                    if p.texture_min_filter in TextureStimulusBaseClass._mipmap_modes:
                        raise RuntimeError("Specified a mipmap mode in texture_min_filter, but mipmaps not enabled.")
                self.texture_object.set_min_filter( p.texture_min_filter )
                self.texture_object.set_mag_filter( p.texture_mag_filter )
                self.texture_object.set_wrap_mode_s( p.texture_wrap_s )
                self.texture_object.set_wrap_mode_t( p.texture_wrap_t )
                gl.glTexEnvi(gl.GL_TEXTURE_ENV, gl.GL_TEXTURE_ENV_MODE, gl.GL_MODULATE)

                translate_vector = p.position
                if len(translate_vector) == 2:
                    translate_vector = translate_vector[0], translate_vector[1], 0
                gl.glTranslate(*translate_vector)
                gl.glRotate(p.angle,0,0,1)

                gl.glColor4f(p.color[0],p.color[1],p.color[2],p.max_alpha)

                # draw only if all values are finite
                if numpy.alltrue( numpy.isfinite( numpy.concatenate((lowerleft,p.position)) ) ):
                    l = lowerleft[0] - p.position[0]
                    r = l + size[0]
                    b = lowerleft[1] - p.position[1]
                    t = b + size[1]

                    tex.update()

                    if p.mask:
                        p.mask.draw_masked_quad(tex.buf_lf,tex.buf_rf,tex.buf_bf,tex.buf_tf, # l,r,b,t for texture coordinates
                                                l,r,b,t,0.0) # l,r,b,t in eye coordinates
                    else:
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
            finally:
                gl.glPopMatrix()

class TextureStimulus3D(TextureStimulusBaseClass):
    """A textured rectangle placed arbitrarily in 3 space.

    Parameters
    ==========
    depth_test         -- perform depth test? (Boolean)
                          Default: True
    lowerleft          -- vertex position (units: eye coordinates) (AnyOf(Sequence3 of Real or Sequence4 of Real))
                          Default: (0.0, 0.0, -1.0)
    lowerright         -- vertex position (units: eye coordinates) (AnyOf(Sequence3 of Real or Sequence4 of Real))
                          Default: (1.0, 0.0, -1.0)
    on                 -- (Boolean)
                          Default: True
    texture            -- source of texture data (Instance of <class 'VisionEgg.Textures.Texture'>)
                          Inherited from TextureStimulusBaseClass
                          Default: (determined at runtime)
    texture_mag_filter -- OpenGL filter enum (Integer)
                          Inherited from TextureStimulusBaseClass
                          Default: GL_LINEAR (9729)
    texture_min_filter -- OpenGL filter enum (Integer)
                          Inherited from TextureStimulusBaseClass
                          Default: (GL enum determined at runtime)
    texture_wrap_s     -- OpenGL texture wrap enum (Integer)
                          Inherited from TextureStimulusBaseClass
                          Default: (GL enum determined at runtime)
    texture_wrap_t     -- OpenGL texture wrap enum (Integer)
                          Inherited from TextureStimulusBaseClass
                          Default: (GL enum determined at runtime)
    upperleft          -- vertex position (units: eye coordinates) (AnyOf(Sequence3 of Real or Sequence4 of Real))
                          Default: (0.0, 1.0, -1.0)
    upperright         -- vertex position (units: eye coordinates) (AnyOf(Sequence3 of Real or Sequence4 of Real))
                          Default: (1.0, 1.0, -1.0)

    Constant Parameters
    ===================
    internal_format   -- format with which OpenGL uses texture data (OpenGL data type enum) (Integer)
                         Default: GL_RGB (6407)
    mipmaps_enabled   -- Are mipmaps enabled? (Boolean)
                         Default: True
    shrink_texture_ok -- Allow automatic shrinking of texture if too big? (Boolean)
                         Default: False
    """

    parameters_and_defaults = {'on':(True,
                                     ve_types.Boolean),
                               'lowerleft':((0.0,0.0,-1.0), # in eye coordinates
                                            ve_types.AnyOf(ve_types.Sequence3(ve_types.Real),
                                                           ve_types.Sequence4(ve_types.Real)),
                                            "vertex position (units: eye coordinates)"),
                               'lowerright':((1.0,0.0,-1.0), # in eye coordinates
                                             ve_types.AnyOf(ve_types.Sequence3(ve_types.Real),
                                                            ve_types.Sequence4(ve_types.Real)),
                                            "vertex position (units: eye coordinates)"),
                               'upperleft':((0.0,1.0,-1.0), # in eye coordinates
                                            ve_types.AnyOf(ve_types.Sequence3(ve_types.Real),
                                                           ve_types.Sequence4(ve_types.Real)),
                                            "vertex position (units: eye coordinates)"),
                               'upperright':((1.0,1.0,-1.0), # in eye coordinates
                                             ve_types.AnyOf(ve_types.Sequence3(ve_types.Real),
                                                            ve_types.Sequence4(ve_types.Real)),
                                            "vertex position (units: eye coordinates)"),
                               'depth_test':(True,
                                             ve_types.Boolean,
                                             "perform depth test?"),
                               }

    def draw(self):
        p = self.parameters
        if p.texture != self._using_texture: # self._using_texture is from TextureStimulusBaseClass
            self._reload_texture()
        if p.on:
            if p.depth_test:
                gl.glEnable(gl.GL_DEPTH_TEST)
            else:
                gl.glDisable(gl.GL_DEPTH_TEST)

            gl.glEnable(gl.GL_TEXTURE_2D)
            gl.glBindTexture(gl.GL_TEXTURE_2D,self.texture_object.gl_id)

            if not self.constant_parameters.mipmaps_enabled:
                if p.texture_min_filter in TextureStimulusBaseClass._mipmap_modes:
                    raise RuntimeError("Specified a mipmap mode in texture_min_filter, but mipmaps not enabled.")
            self.texture_object.set_min_filter( p.texture_min_filter )
            self.texture_object.set_mag_filter( p.texture_mag_filter )
            self.texture_object.set_wrap_mode_s( p.texture_wrap_s )
            self.texture_object.set_wrap_mode_t( p.texture_wrap_t )

            # allow max_alpha value to control blending
            gl.glEnable( gl.GL_BLEND )
            gl.glBlendFunc( gl.GL_SRC_ALPHA, gl.GL_ONE_MINUS_SRC_ALPHA )
            gl.glTexEnvi(gl.GL_TEXTURE_ENV, gl.GL_TEXTURE_ENV_MODE, gl.GL_MODULATE)

            tex = self.parameters.texture
            tex.update()

            gl.glBegin(gl.GL_QUADS)
            gl.glTexCoord2f(tex.buf_lf,tex.buf_bf)
            gl.glVertex(*p.lowerleft)

            gl.glTexCoord2f(tex.buf_rf,tex.buf_bf)
            gl.glVertex(*p.lowerright)

            gl.glTexCoord2f(tex.buf_rf,tex.buf_tf)
            gl.glVertex(*p.upperright)

            gl.glTexCoord2f(tex.buf_lf,tex.buf_tf)
            gl.glVertex(*p.upperleft)
            gl.glEnd() # GL_QUADS

####################################################################
#
#        Stimulus - Spinning Drum
#
####################################################################

class SpinningDrum(TextureStimulusBaseClass):
    """Panoramic image texture mapped onto flat rectangle or 3D cylinder.


    Parameters
    ==========
    anchor                -- only used when flat: same as anchor parameter of TextureStimulus (String)
                             Default: center
    angular_position      -- may be best to clamp in range [0.0,360.0] (Real)
                             Default: 0.0
    contrast              -- (Real)
                             Default: 1.0
    drum_center_azimuth   -- changes orientation of drum in space (Real)
                             Default: 0.0
    drum_center_elevation -- changes orientation of drum in space (Real)
                             Default: 0.0
    flat                  -- toggles flat vs. cylinder (Boolean)
                             Default: False
    flat_size             -- defaults to texture data size (units: eye coordinates) (Sequence2 of Real)
                             Default: (determined at runtime)
    flip_image            -- toggles normal vs. horizonally flipped image (Boolean)
                             Default: False
    height                -- height of cyliner, automatically set by texel aspect ratio if < 0. (Real)
                             Default: -1
    num_sides             -- (UnsignedInteger)
                             Default: 50
    on                    -- (Boolean)
                             Default: True
    orientation           -- 0=right, 90=up (Real)
                             Default: 0.0
    position              -- 3D: position of drum center, 2D (flat): same as position parameter for TextureStimulus (AnyOf(Sequence2 of Real or Sequence3 of Real))
                             Default: (0.0, 0.0, 0.0)
    radius                -- radius if cylinder (not used if flat) (Real)
                             Default: 1.0
    texture               -- source of texture data (Instance of <class 'VisionEgg.Textures.Texture'>)
                             Inherited from TextureStimulusBaseClass
                             Default: (determined at runtime)
    texture_mag_filter    -- OpenGL filter enum (Integer)
                             Inherited from TextureStimulusBaseClass
                             Default: GL_LINEAR (9729)
    texture_min_filter    -- OpenGL filter enum (Integer)
                             Inherited from TextureStimulusBaseClass
                             Default: (GL enum determined at runtime)
    texture_wrap_s        -- OpenGL texture wrap enum (Integer)
                             Inherited from TextureStimulusBaseClass
                             Default: (GL enum determined at runtime)
    texture_wrap_t        -- OpenGL texture wrap enum (Integer)
                             Inherited from TextureStimulusBaseClass
                             Default: (GL enum determined at runtime)

    Constant Parameters
    ===================
    internal_format   -- format with which OpenGL uses texture data (OpenGL data type enum) (Integer)
                         Default: GL_RGB (6407)
    mipmaps_enabled   -- Are mipmaps enabled? (Boolean)
                         Default: True
    shrink_texture_ok -- Allow automatic shrinking of texture if too big? (Boolean)
                         Default: False
    """

    parameters_and_defaults = {
        'on':(True,
              ve_types.Boolean),
        'height':(-1,
                  ve_types.Real,
                  'height of cyliner, automatically set by texel aspect ratio if < 0.',
                  ),
        'num_sides':(50,
                     ve_types.UnsignedInteger),
        'angular_position':(0.0, # may be best to clamp [0.0,360.0]
                            ve_types.Real,
                            'may be best to clamp in range [0.0,360.0]'),
        'contrast':(1.0,
                    ve_types.Real),
        'flat':(False,
                ve_types.Boolean,
                'toggles flat vs. cylinder'),
        'flat_size':(None,
                     ve_types.Sequence2(ve_types.Real),
                     "defaults to texture data size (units: eye coordinates)"),
        'flip_image':(False,
                      ve_types.Boolean,
                      'toggles normal vs. horizonally flipped image'),
        'radius':(1.0,
                  ve_types.Real,
                  'radius if cylinder (not used if flat)'),
        'position':( (0.0,0.0,0.0),
                     ve_types.AnyOf(ve_types.Sequence2(ve_types.Real),
                                    ve_types.Sequence3(ve_types.Real)),
                     '3D: position of drum center, 2D (flat): same as position parameter for TextureStimulus'),
        'anchor':( 'center',
                   ve_types.String,
                   'only used when flat: same as anchor parameter of TextureStimulus',
                   ),
        'drum_center_azimuth':(0.0,
                               ve_types.Real,
                               'changes orientation of drum in space',
                               ),
        'drum_center_elevation':(0.0,
                                 ve_types.Real,
                                 'changes orientation of drum in space'),
        'orientation':(0.0,
                       ve_types.Real,
                       '0=right, 90=up'),
        }

    __slots__ = (
        'cached_display_list_normal',
        'cached_display_list_mirror',
        'cached_display_list_num_sides',
        'cached_display_list_radius',
        'cached_display_list_height',
        'texture_stimulus',
        )

    def __init__(self,**kw):
        TextureStimulusBaseClass.__init__(self,**kw)
        self.cached_display_list_normal = gl.glGenLists(1) # Allocate a new display list
        self.cached_display_list_mirror = gl.glGenLists(1) # Allocate a new display list
        self.rebuild_display_list()

    def draw(self):
    	"""Redraw the stimulus on every frame.
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
            # of the texture (with the exception of texels around the
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
            gl.glPushMatrix()
            try:
                gl.glColor4f(0.5,0.5,0.5,p.contrast) # Set the polygons' fragment color (implements contrast)

                if not self.constant_parameters.mipmaps_enabled:
                    if p.texture_min_filter in TextureStimulusBaseClass._mipmap_modes:
                        raise RuntimeError("Specified a mipmap mode in texture_min_filter, but mipmaps not enabled.")
                self.texture_object.set_min_filter( p.texture_min_filter )
                self.texture_object.set_mag_filter( p.texture_mag_filter )
                self.texture_object.set_wrap_mode_s( p.texture_wrap_s )
                self.texture_object.set_wrap_mode_t( p.texture_wrap_t )

                if p.flat: # draw as flat texture on a rectange
                    lowerleft = VisionEgg._get_lowerleft(p.position,p.anchor,p.texture.size)

                    translate_vector = p.position
                    if len(translate_vector) == 2:
                        translate_vector = translate_vector[0], translate_vector[1], 0
                    gl.glTranslate(*translate_vector)
                    gl.glRotatef(p.orientation,0,0,1)

                    if p.flip_image:
                        raise NotImplementedError("flip_image not yet supported for flat spinning drums.")
                    w,h = p.texture.size

                    # calculate texture coordinates based on current angle
                    tex_phase = p.angular_position/360.0 + 0.5 # offset to match non-flat
                    tex_phase = tex_phase % 1.0 # make 0 <= tex_phase < 1.0

                    TINY = 1.0e-10
                    tex = p.texture
                    tex.update()

                    if p.flat_size is None:
                        size = tex.size
                    else:
                        size = p.flat_size

                    l = lowerleft[0] - p.position[0]
                    r = l + size[0]
                    b = lowerleft[1] - p.position[1]
                    t = b + size[1]

                    #tex_phase = 0.0
                    if tex_phase < TINY: # it's effectively zero

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

                    else:
                        # Convert tex_phase into texture buffer fraction
                        buf_break_f = ( (tex.buf_rf - tex.buf_lf) * (1.0-tex_phase) ) + tex.buf_lf

                        # Convert tex_phase into object coords value
                        quad_x_break = (r-l) * tex_phase + l
    ##                    quad_x_break = w * tex_phase

                        gl.glBegin(gl.GL_QUADS)

                        # First quad

                        gl.glTexCoord2f(buf_break_f,tex.buf_bf)
                        gl.glVertex2f(l,b)

                        gl.glTexCoord2f(tex.buf_rf,tex.buf_bf)
                        gl.glVertex2f(quad_x_break,b)

                        gl.glTexCoord2f(tex.buf_rf,tex.buf_tf)
                        gl.glVertex2f(quad_x_break,t)

                        gl.glTexCoord2f(buf_break_f,tex.buf_tf)
                        gl.glVertex2f(l,t)

                        # Second quad

                        gl.glTexCoord2f(tex.buf_lf,tex.buf_bf)
                        gl.glVertex2f(quad_x_break,b)

                        gl.glTexCoord2f(buf_break_f,tex.buf_bf)
                        gl.glVertex2f(r,b)

                        gl.glTexCoord2f(buf_break_f,tex.buf_tf)
                        gl.glVertex2f(r,t)

                        gl.glTexCoord2f(tex.buf_lf,tex.buf_tf)
                        gl.glVertex2f(quad_x_break,t)
                        gl.glEnd() # GL_QUADS

                else: # draw as cylinder
                    gl.glTranslatef(p.position[0],p.position[1],p.position[2])

                    # center the drum on new coordinates
                    gl.glRotatef(p.drum_center_azimuth,0,-1,0)
                    gl.glRotatef(p.drum_center_elevation,1,0,0)

                    # do the orientation
                    gl.glRotatef(p.orientation,0,0,1)

                    # turn the coordinate system so we don't have to deal with
                    # figuring out where to draw the texture relative to drum
                    gl.glRotatef(p.angular_position,0,-1,0)

                    if ((p.num_sides != self.cached_display_list_num_sides) or
                        (p.radius != self.cached_display_list_radius) or
                        (p.height != self.cached_display_list_height)):
                        self.rebuild_display_list()

                    if not p.flip_image:
                        gl.glCallList(self.cached_display_list_normal)
                    else:
                        gl.glCallList(self.cached_display_list_mirror)
            finally:
                gl.glMatrixMode(gl.GL_MODELVIEW)
                gl.glPopMatrix()

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
        if self.parameters.height < 0:
            h = circum/float(tex.size[0])*float(tex.size[1])/2.0
        else:
            h = self.parameters.height

        num_sides = self.parameters.num_sides
        self.cached_display_list_num_sides = num_sides
        self.cached_display_list_radius = r
        self.cached_display_list_height = self.parameters.height

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

class FixationCross(VisionEgg.Core.Stimulus):
    """Cross useful for fixation point.

    Parameters
    ==========
    on       -- (Boolean)
                Default: True
    position -- (Sequence2 of Real)
                Default: (320, 240)
    size     -- (Sequence2 of Real)
                Default: (64, 64)

    Constant Parameters
    ===================
    texture_size -- (Sequence2 of Real)
                    Default: (64, 64)
    """

    parameters_and_defaults = {
        'on':(True,
              ve_types.Boolean),
        'position':((320,240),
                    ve_types.Sequence2(ve_types.Real)),
        'size':((64,64),
                ve_types.Sequence2(ve_types.Real)),
        }
    constant_parameters_and_defaults = {
        'texture_size':((64,64),
                        ve_types.Sequence2(ve_types.Real)),
        }

    __slots__ = (
        'texture_stimulus',
        )

    def __init__(self,**kw):
        VisionEgg.Core.Stimulus.__init__(self,**kw)
        s = self.constant_parameters.texture_size
        mid_x = s[0]/2.0
        mid_y = s[1]/2.0
        texels = Image.new("RGBX",s,(0,0,0,0))
        texels_draw = ImageDraw.Draw(texels)
        texels_draw.rectangle( (mid_x-1, 0, mid_x+1, s[1]), fill=(0,0,0,255) )
        texels_draw.rectangle( (0, mid_y-1, s[0], mid_y+1), fill=(0,0,0,255) )
        texels_draw.line( (mid_x, 0, mid_x, s[1]), fill=(255,255,255,255) )
        texels_draw.line( (0, mid_y, s[0], mid_y), fill=(255,255,255,255) )
        self.texture_stimulus = TextureStimulus( texture = Texture(texels),
                                                 position = self.parameters.position,
                                                 anchor = 'center',
                                                 size = self.parameters.size,
                                                 internal_format = gl.GL_RGBA,
                                                 mipmaps_enabled = False,
                                                 texture_min_filter = gl.GL_NEAREST,
                                                 texture_mag_filter = gl.GL_NEAREST,
                                                 )
    def draw(self):
        contained = self.texture_stimulus.parameters #shorthand
        my = self.parameters #shorthand
        contained.position = my.position
        contained.size = my.size
        contained.on = my.on
        self.texture_stimulus.draw()

class TextureTooLargeError( RuntimeError ):
    pass
