"""Texture (images mapped onto polygons) stimuli."""

# Copyright (c) 2001-2002 Andrew Straw.  Distributed under the terms of the
# GNU Lesser General Public License (LGPL).

####################################################################
#
#        Import all the necessary packages
#
####################################################################

import VisionEgg
import VisionEgg.Core
import Image, ImageDraw                         # Python Imaging Library packages
import math,types
import OpenGL.GL
gl = OpenGL.GL

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

############ Import texture compression stuff and use it, if possible ##############
# This may mess up image statistics! Check the output before using in an experiment!

##try:
##    import OpenGL.GL.ARB.texture_compression #   can use this to fit more textures in texture memory
##    # This following function call doesn't seem to return any
##    # useful info, at least on my PowerBook G4.  So it's commented
##    # out for now.
##    ## if not OpenGL.GL.ARB.texture_compression.glInitTextureCompressionARB(): 
##        ## VisionEgg.config.VISIONEGG_TEXTURE_COMPRESSION = 0
##    for attr in dir(OpenGL.GL.ARB.texture_compression):
##        # Put all OpenGL extension names into "gl" variable
##        setattr(gl,attr,getattr(OpenGL.GL.ARB.texture_compression,attr))
##except:
##    VisionEgg.config.VISIONEGG_TEXTURE_COMPRESSION = 0
# Don't use texture compression.  (XXX Should remove this as a config variable.)
VisionEgg.config.VISIONEGG_TEXTURE_COMPRESSION = 0

def __no_clamp_to_edge_callback():
    # Error callback automatically called if OpenGL version < 1.2
    
    # This function is called if the OpenGL version is < 1.2, in which
    # case GL_CLAMP_TO_EDGE is not defined by default.
    
    try:
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
    """Base class to handle textures, whether loaded to OpenGL or not."""
    def __init__(self,size=(128,128)):
    	"""Base class is a white 'x' on a blue background."""
        # Create a default texture
        self.orig = Image.new("RGB",size,(0,0,255))
        draw = ImageDraw.Draw(self.orig)
        draw.line((0,0) + self.orig.size, fill=(255,255,255))
        draw.line((0,self.orig.size[1],self.orig.size[0],0), fill=(255,255,255))

    def load(self, build_mipmaps=1):
        """Load texture into OpenGL."""
        # Someday put all this in a texture buffer manager.
        # The buffer manager will do a much better job of putting
        # images in texture memory, packing them closely, keeping
        # everything organized, and making the world a better place.
        # For now, though, we're stuck with this!

        # Create a buffer whose sides are a power of 2
        def next_power_of_2(f):
            return max(math.pow(2.0,math.ceil(math.log(f)/math.log(2.0))),1.0)

        width = self.orig.size[0]
        height = self.orig.size[1]

        width_pow2  = int(next_power_of_2(width))
        height_pow2  = int(next_power_of_2(height))

        self.buf = TextureBuffer( size=(width_pow2, height_pow2) )
        self.buf.im.paste(self.orig,(0,0,width,height))

        # Location of myself in the buffer, in pixels
        # This is a semi-private variable: you should probably use the
        # fractional variables (see below), because those will be the
        # same, regardless of mipmap level, while the absolute
        # position in pixels (these variables) will vary.
        self._buf_l = 0
        self._buf_r = width
        self._buf_t = 0
        self._buf_b = height

        # my size
        self.width = width
        self.height = height
        
        # location of myself in the buffer, in fraction
        self.buf_lf = 0.0
        self.buf_rf = float(width)/float(width_pow2)
        self.buf_bf = float(height)/float(height_pow2) # handle OpenGL "flip" by called the bottom of the texture the top
        self.buf_tf = 0.0

        texId = self.buf.load() # return the OpenGL Texture ID (uses "texture objects")

        if build_mipmaps:
            # Could use GLU to do this, but let's do it ourselves for more control
            this_width = width
            this_height = height
            biggest_dim = max(this_width,this_height)
            mipmap_level = 1
            while biggest_dim > 1:
                this_width = this_width/2.0
                this_height = this_height/2.0

                width_pix = int(math.ceil(this_width))
                height_pix = int(math.ceil(this_height))
                shrunk = self.orig.resize((width_pix,height_pix),Image.BICUBIC)
                
                width_pow2  = int(next_power_of_2(this_width))
                height_pow2  = int(next_power_of_2(this_height))

                im = Image.new( mode="RGB",size=(width_pow2,height_pow2), color=(127,127,127))
                im.paste(shrunk,(0,0,width_pix,height_pix))

                self.buf.im = im
                self.buf.load(mipmap_level=mipmap_level)
                
                mipmap_level += 1
                biggest_dim = max(this_width,this_height)
        
        #del self.orig # clear Image from system RAM
        return texId

    def get_pil_image(self):
        """Returns a PIL Image of the texture."""
        return self.orig

    def get_texture_buffer(self):
        return self.buf

class TextureFromFile(Texture):
    """A Texture that is loaded from a graphics file"""
    def __init__(self,file):
        try:
            self.orig = Image.open(file)
        except Exception, x:
            import os
            try:
                VisionEgg.Core.message.add("Could not open \"%s\", raising exception."%(os.path.abspath(file),),
                                           level=VisionEgg.Core.Message.WARNING)
            except:
                pass
            raise x
        if hasattr(file,"seek"):
            file.seek(0) # go back to beginning

class TextureFromPILImage(Texture):
    """A Texture that is loaded from a Python Imaging Library Image."""
    def __init__(self,image):
        if isinstance(image,Image.Image):
            self.orig = image
        else:
            raise ValueError("TextureFromPILImage expecting instance of Image.Image")

class TextureBuffer:
    """Pixel data size n^2 b m^2 that can be loaded as an OpenGL texture."""
    def __init__(self,size=(256,256),mode="RGB",color=(127,127,127)):
        def next_power_of_2(f):
            return math.pow(2.0,math.ceil(math.log(f)/math.log(2.0)))
        if next_power_of_2(size[0]) != size[0] or next_power_of_2(size[1]) != size[1]:
            raise ValueError("TextureBuffer size must be power of 2.")
        self.im = Image.new(mode,size,color)
            
    def load(self,mipmap_level=0):
        """This loads the texture into OpenGL's texture memory."""
        if mipmap_level == 0: # Normal case
            self.gl_id = gl.glGenTextures(1)
            gl.glBindTexture(gl.GL_TEXTURE_2D, self.gl_id)
            gl.glEnable( gl.GL_TEXTURE_2D )
        else: # special case, make you've called mipmap_level 0 beforehand
            gl.glBindTexture(gl.GL_TEXTURE_2D, self.gl_id)
            gl.glEnable( gl.GL_TEXTURE_2D )
        if self.im.mode == "RGB":
            image_data = self.im.tostring("raw","RGB") # -1 flips data so it's right side up in OpenGL

            # Do error-checking on texture to make sure it will load
            max_dim = gl.glGetIntegerv( gl.GL_MAX_TEXTURE_SIZE )
            if self.im.size[0] > max_dim or self.im.size[1] > max_dim:
                self.free() # Delete texture from OpenGL
                raise TextureTooLargeError("Texture dimensions are too large for video system.\nOpenGL reports maximum size of %d x %d"%(max_dim,max_dim))
            
            # Because the MAX_TEXTURE_SIZE method is insensitive to the current
            # state of the video system, another check must be done using
            # "proxy textures".
            if VisionEgg.config.VISIONEGG_TEXTURE_COMPRESSION:
                gl.glTexImage2D(gl.GL_PROXY_TEXTURE_2D,            # target
                                mipmap_level,                                 # level
                                gl.GL_COMPRESSED_RGB_ARB,          # video RAM internal format: compressed RGB
                                self.im.size[0],                   # width
                                self.im.size[1],                   # height
                                0,                                 # border
                                gl.GL_RGB,                         # format of image data
                                gl.GL_UNSIGNED_BYTE,               # type of image data
                                image_data)                        # image data
            else:
                gl.glTexImage2D(gl.GL_PROXY_TEXTURE_2D,            # target
                                mipmap_level,                                 # level
                                gl.GL_RGB,                         # video RAM internal format: RGB
                                self.im.size[0],                   # width
                                self.im.size[1],                   # height
                                0,                                 # border
                                gl.GL_RGB,                         # format of image data
                                gl.GL_UNSIGNED_BYTE,               # type of image data
                                image_data)                        # image data
                
            if gl.glGetTexLevelParameteriv(gl.GL_PROXY_TEXTURE_2D,0,gl.GL_TEXTURE_WIDTH) == 0:
                self.free() # Delete texture from OpenGL
                raise TextureTooLargeError("Texture is too wide for your video system!")
            if gl.glGetTexLevelParameteriv(gl.GL_PROXY_TEXTURE_2D,0,gl.GL_TEXTURE_HEIGHT) == 0:
                self.free() # Delete texture from OpenGL
                raise TextureTooLargeError("Texture is too tall for your video system!")

            if VisionEgg.config.VISIONEGG_TEXTURE_COMPRESSION:
                gl.glTexImage2D(gl.GL_TEXTURE_2D,                  # target
                                mipmap_level,                                 # level
                                gl.GL_COMPRESSED_RGB_ARB,          # video RAM internal format: compressed RGB
                                self.im.size[0],                   # width
                                self.im.size[1],                   # height
                                0,                                 # border
                                gl.GL_RGB,                         # format of image data
                                gl.GL_UNSIGNED_BYTE,               # type of image data
                                image_data)                        # image data
            else:
                gl.glTexImage2D(gl.GL_TEXTURE_2D,                  # target
                                mipmap_level,                                 # level
                                gl.GL_RGB,                         # video RAM internal format: RGB                             self.im.size[0],                # width
                                self.im.size[0],                   # width
                                self.im.size[1],                   # height
                                0,                                 # border
                                gl.GL_RGB,                         # format of image data
                                gl.GL_UNSIGNED_BYTE,               # type of image data
                                image_data)                        # image data
        else:
            raise EggError("Unknown image mode '%s'"%(self.im.mode,))
        del self.im  # remove the image from system memory
        # Set some texture object defaults
        gl.glTexParameteri(gl.GL_TEXTURE_2D,gl.GL_TEXTURE_WRAP_S,gl.GL_CLAMP_TO_EDGE)
        gl.glTexParameteri(gl.GL_TEXTURE_2D,gl.GL_TEXTURE_WRAP_T,gl.GL_CLAMP_TO_EDGE)
        gl.glTexParameteri(gl.GL_TEXTURE_2D,gl.GL_TEXTURE_MAG_FILTER,gl.GL_LINEAR)
        gl.glTexParameteri(gl.GL_TEXTURE_2D,gl.GL_TEXTURE_MIN_FILTER,gl.GL_LINEAR)        
        return self.gl_id

    def put_sub_image(self,pil_image,lower_left, size):
        """This function always segfaults, for some reason!"""
        # Could it be that the width and height must be a power of 2?
        gl.glBindTexture(gl.GL_TEXTURE_2D, self.gl_id)
        print "bound texture"
        data = pil_image.tostring("raw","RGB")# ,0,-1) # the -1 will flip the data
        print "converted data"
        if VisionEgg.config.VISIONEGG_TEXTURE_COMPRESSION:
            print "trying to put compressed image data"
            gl.glCompressedTexSubImage2DARB(gl.GL_TEXTURE_2D, # target
                                         0, # level
                                         lower_left[0], # x offset
                                         lower_left[1], # y offset
                                         gl.GL_RGB,
                                         size[0], # width
                                         size[1], # height
                                         0,
                                         gl.GL_UNSIGNED_INT,
                                         data)
        else:
            print "trying to put non-compressed image data"
            gl.glTexSubImage2D(gl.GL_TEXTURE_2D, # target
                            0, # level
                            lower_left[0], # x offset
                            lower_left[1], # y offset
                            size[0], # width
                            size[1], # height
                            gl.GL_RGB,
                            gl.GL_UNSIGNED_INT,
                            data)

    def free(self):
        gl.glDeleteTextures(self.gl_id)

####################################################################
#
#        Stimulus - TextureStimulus
#
####################################################################

class TextureStimulusBaseClass(VisionEgg.Core.Stimulus):
    """Parameters common to all stimuli that use textures.

    Don't instantiate this class directly."""
    parameters_and_defaults = {'texture_mag_filter':(gl.GL_LINEAR,types.IntType),
                               'texture_min_filter':(gl.GL_LINEAR_MIPMAP_LINEAR,types.IntType),
                               'texture_wrap_s':(gl.GL_CLAMP_TO_EDGE,types.IntType),
                               'texture_wrap_t':(gl.GL_CLAMP_TO_EDGE,types.IntType),
                               }
    
    constant_parameters_and_defaults = {'mipmaps_enabled':(1,types.IntType),
                                        }
    _mipmap_modes = [gl.GL_LINEAR_MIPMAP_LINEAR,gl.GL_LINEAR_MIPMAP_NEAREST,
                     gl.GL_NEAREST_MIPMAP_LINEAR,gl.GL_NEAREST_MIPMAP_NEAREST]

class TextureStimulus(TextureStimulusBaseClass):
    parameters_and_defaults = {'on':(1,types.IntType),
                               'lowerleft':((0.0,0.0),types.TupleType),
                               'size':((640.0,480.0),types.TupleType)}
    def __init__(self,texture=None,shrink_texture_ok=0,**kw):
        apply(TextureStimulusBaseClass.__init__,(self,),kw)

        if texture is not None:
            self.texture = texture
        else:
            self.texture = Texture(size=(256,16))

        if not shrink_texture_ok:
            self.texture_object = self.texture.load(build_mipmaps=self.constant_parameters.mipmaps_enabled)
        else:
            max_dim = gl.glGetIntegerv( gl.GL_MAX_TEXTURE_SIZE )
            resized = 0
            while max(self.texture.orig.size) > max_dim:
                w = self.texture.orig.size[0]/2
                h = self.texture.orig.size[1]/2
                self.texture.orig = self.texture.orig.resize((w,h),Image.BICUBIC)
                resized = 1
            loaded_ok = 0
            while not loaded_ok:
                try:
                    self.texture_object = self.texture.load(build_mipmaps=self.constant_parameters.mipmaps_enabled)
                    loaded_ok = 1
                except TextureTooLargeError,x:
                    w = self.texture.orig.size[0]/2
                    h = self.texture.orig.size[1]/2
                    self.texture.orig = self.texture.orig.resize((w,h),Image.BICUBIC)
                    resized = 1
            if resized:
                VisionEgg.Core.message.add(
                    "Resized texture in %s to %d x %d"%(
                    str(self),w,h),VisionEgg.Core.Message.WARNING)
                self.parameters.size = (w,h)

    def draw(self):
        p = self.parameters
        if p.on:
            # Clear the modeview matrix
            gl.glMatrixMode(gl.GL_MODELVIEW)
            gl.glLoadIdentity()
            
            gl.glDisable(gl.GL_DEPTH_TEST)
            gl.glDisable(gl.GL_BLEND)
            gl.glEnable(gl.GL_TEXTURE_2D)
            gl.glBindTexture(gl.GL_TEXTURE_2D,self.texture_object)
            
            gl.glTexParameteri(gl.GL_TEXTURE_2D,gl.GL_TEXTURE_MAG_FILTER,p.texture_mag_filter)
            if not self.constant_parameters.mipmaps_enabled:
                if p.texture_min_filter in TextureStimulusBaseClass._mipmap_modes:
                    raise RuntimeError("Specified a mipmap mode in texture_min_filter, but mipmaps not enabled.")
            gl.glTexParameteri(gl.GL_TEXTURE_2D,gl.GL_TEXTURE_MIN_FILTER,p.texture_min_filter)
                
            gl.glTexParameteri(gl.GL_TEXTURE_2D,gl.GL_TEXTURE_WRAP_S,p.texture_wrap_s)
            gl.glTexParameteri(gl.GL_TEXTURE_2D,gl.GL_TEXTURE_WRAP_T,p.texture_wrap_t)
            
            gl.glTexEnvi(gl.GL_TEXTURE_ENV, gl.GL_TEXTURE_ENV_MODE, gl.GL_REPLACE)

            l = p.lowerleft[0]
            r = l + p.size[0]
            b = p.lowerleft[1]
            t = b + p.size[1]

            tex = self.texture
            
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
                               'dist_from_o':(1.0,types.FloatType) # z if flat, radius if cylinder
                               }
    
    # To avoid rescaling the texture size, make sure you are using a
    # viewport with an orthographic projection where left=0,
    # right=viewport.parameters.size[0],
    # bottom=0,top=viewport.parameters.size[1].

    def __init__(self,texture=None,shrink_texture_ok=0,**kw):
        apply(TextureStimulusBaseClass.__init__,(self,),kw)
        if texture is not None:
            self.texture = texture
        else:
            self.texture = Texture(size=(256,16))

        if not shrink_texture_ok:
            self.texture_object = self.texture.load(build_mipmaps=self.constant_parameters.mipmaps_enabled)
        else:
            max_dim = gl.glGetIntegerv( gl.GL_MAX_TEXTURE_SIZE )
            resized = 0
            while max(self.texture.orig.size) > max_dim:
                w = self.texture.orig.size[0]/2
                h = self.texture.orig.size[1]/2
                self.texture.orig = self.texture.orig.resize((w,h),Image.BICUBIC)
                resized = 1
            loaded_ok = 0
            while not loaded_ok:
                try:
                    self.texture_object = self.texture.load(build_mipmaps=self.constant_parameters.mipmaps_enabled)
                    loaded_ok = 1
                except TextureTooLargeError,x:
                    w = self.texture.orig.size[0]/2
                    h = self.texture.orig.size[1]/2
                    if min(w,h) <= 0:
                        raise TextureTooLargeError("Strange: even a 0 size texture is too large.")
                    self.texture.orig = self.texture.orig.resize((w,h),Image.BICUBIC)
                    resized = 1
            if resized:
                VisionEgg.Core.message.add(
                    "Resized texture in %s to %d x %d"%(
                    str(self),w,h),VisionEgg.Core.Message.WARNING)
            
        self.cached_display_list = gl.glGenLists(1) # Allocate a new display list
        self.rebuild_display_list()

    def draw(self):
    	"""Redraw the scene on every frame.
        """
        p = self.parameters
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
            gl.glBindTexture(gl.GL_TEXTURE_2D, self.texture_object) # make sure to texture polygon

            # Make sure texture object parameters set the way we want
            gl.glTexParameteri(gl.GL_TEXTURE_2D,gl.GL_TEXTURE_MAG_FILTER,p.texture_mag_filter)
            if not self.constant_parameters.mipmaps_enabled:
                if p.texture_min_filter in TextureStimulusBaseClass._mipmap_modes:
                    raise RuntimeError("Specified a mipmap mode in texture_min_filter, but mipmaps not enabled.")
            gl.glTexParameteri(gl.GL_TEXTURE_2D,gl.GL_TEXTURE_MIN_FILTER,p.texture_min_filter)
                
            gl.glTexParameteri(gl.GL_TEXTURE_2D,gl.GL_TEXTURE_WRAP_S,p.texture_wrap_s)
            gl.glTexParameteri(gl.GL_TEXTURE_2D,gl.GL_TEXTURE_WRAP_T,p.texture_wrap_t)

            if p.flat: # draw as flat texture on a rectange
                w = self.texture.width
                h = self.texture.height

                # calculate texture coordinates based on current angle
                tex_phase = p.angular_position/-360.0 + 0.5 # offset to match non-flat
                tex_phase = tex_phase % 1.0 # make 0 <= tex_phase < 1.0
                
                TINY = 1.0e-10
                if tex_phase < TINY: # it's effectively zero

                    gl.glBegin(gl.GL_QUADS)
                    gl.glTexCoord2f(self.texture.buf_lf,self.texture.buf_bf)
                    gl.glVertex2f(0.0,0.0)

                    gl.glTexCoord2f(self.texture.buf_rf,self.texture.buf_bf)
                    gl.glVertex2f(w,0.0)

                    gl.glTexCoord2f(self.texture.buf_rf,self.texture.buf_tf)
                    gl.glVertex2f(w,h)

                    gl.glTexCoord2f(self.texture.buf_lf,self.texture.buf_tf)
                    gl.glVertex2f(0.0,h)
                    gl.glEnd() # GL_QUADS

                else:
                    # Convert tex_phase into texture buffer fraction
                    buf_break_f = ( (self.texture.buf_rf - self.texture.buf_lf) * (1.0-tex_phase) ) + self.texture.buf_lf

                    # Convert tex_phase into object coords value
                    quad_x_break = w * tex_phase

                    gl.glBegin(gl.GL_QUADS)

                    # First quad

                    gl.glTexCoord2f(buf_break_f,self.texture.buf_bf)
                    gl.glVertex2f(0.0,0.0)

                    gl.glTexCoord2f(self.texture.buf_rf,self.texture.buf_bf)
                    gl.glVertex2f(quad_x_break,0.0)

                    gl.glTexCoord2f(self.texture.buf_rf,self.texture.buf_tf)
                    gl.glVertex2f(quad_x_break,h)

                    gl.glTexCoord2f(buf_break_f,self.texture.buf_tf)
                    gl.glVertex2f(0.0,h)

                    # Second quad

                    gl.glTexCoord2f(self.texture.buf_lf,self.texture.buf_bf)
                    gl.glVertex2f(quad_x_break,0.0)

                    gl.glTexCoord2f(buf_break_f,self.texture.buf_bf)
                    gl.glVertex2f(w,0.0)

                    gl.glTexCoord2f(buf_break_f,self.texture.buf_tf)
                    gl.glVertex2f(w,h)

                    gl.glTexCoord2f(self.texture.buf_lf,self.texture.buf_tf)
                    gl.glVertex2f(quad_x_break,h)
                    gl.glEnd() # GL_QUADS

            else: # draw as cylinder
                # turn the coordinate system so we don't have to deal with
                # figuring out where to draw the texture relative to drum
                gl.glRotatef(p.angular_position,0.0,1.0,0.0)

                if p.num_sides != self.cached_display_list_num_sides:
                    self.rebuild_display_list()
                gl.glCallList(self.cached_display_list)

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
        r = self.parameters.dist_from_o # in OpenGL (arbitrary) units
        circum = 2.0*math.pi*r
        h = circum/float(self.texture.width)*float(self.texture.height)/2.0

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
            frac1 = (self.texture.buf_lf + (float(i)/num_sides*self.texture.width))/float(self.texture.width)
            frac2 = (self.texture.buf_lf + (float(i+1)/num_sides*self.texture.width))/float(self.texture.width)
            # location of sides
            x1 = r*math.cos(theta1)
            z1 = r*math.sin(theta1)
            x2 = r*math.cos(theta2)
            z2 = r*math.sin(theta2)

            #Bottom left of quad
            gl.glTexCoord2f(frac1, self.texture.buf_bf)
            gl.glVertex4f( x1, -h, z1, 1.0 ) # 4th coordinate is "w"--look up "homogeneous coordinates" for more info.
            
            #Bottom right of quad
            gl.glTexCoord2f(frac2, self.texture.buf_bf)
            gl.glVertex4f( x2, -h, z2, 1.0 )
            #Top right of quad
            gl.glTexCoord2f(frac2, self.texture.buf_tf); 
            gl.glVertex4f( x2,  h, z2, 1.0 )
            #Top left of quad
            gl.glTexCoord2f(frac1, self.texture.buf_tf)
            gl.glVertex4f( x1,  h, z1, 1.0 )
        gl.glEnd()
        gl.glEndList()

class TextureTooLargeError(VisionEgg.Core.EggError):
    pass
