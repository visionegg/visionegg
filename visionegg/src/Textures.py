"""texture module of the Vision Egg package"""

# Copyright (c) 2001, 2002 Andrew Straw.  Distributed under the terms of the
# GNU General Public License (GPL).

####################################################################
#
#        Import all the necessary packages
#
####################################################################

import string
__version__ = string.split('$Revision$')[1]
__date__ = string.join(string.split('$Date$')[1:3], ' ')
__author__ = 'Andrew Straw <astraw@users.sourceforge.net>'

import VisionEgg
import VisionEgg.Core
import Image, ImageDraw                         # Python Imaging Library packages

			                        # from PyOpenGL:
from OpenGL.GL import *                         #   main package

def no_clamp_to_edge():
    """Called if OpenGL version < 1.2
    
    This function is called if the OpenGL version is < 1.2, in which
    case GL_CLAMP_TO_EDGE is not defined by default."""
    
    failed = 1
    try:
        import OpenGL.GL.SGIS.texture_edge_clamp
        if OpenGL.GL.SGIS.texture_edge_clamp.glInitTextureEdgeClampSGIS():
            GL_CLAMP_TO_EDGE = OpenGL.GL.SGIS.texture_edge_clamp.GL_CLAMP_TO_EDGE_SGIS
            failed = 0
    except:
        pass
    if failed:
         print "VISIONEGG WARNING: Your version of OpenGL is less than 1.2,"
         print "and you do not have the GL_SGIS_texture_edge_clamp OpenGL"
         print "extension.  therefore, you do not have GL_CLAMP_TO_EDGE"
         print "available.  It may be impossible to get exact 1:1"
         print "reproduction of your textures.  Using GL_CLAMP instead of"
         print "GL_CLAMP_TO_EDGE."
         GL_CLAMP_TO_EDGE = GL_CLAMP

if "GL_CLAMP_TO_EDGE" not in dir():
    # Hack because this isn't defined in my PyOpenGL modules:
    VisionEgg.Core.add_gl_assumption("GL_VERSION",1.2,no_clamp_to_edge)
    #print "HACK: setting GL_CLAMP_TO_EDGE.  If your textures are messed up, this may be why!"
    GL_CLAMP_TO_EDGE = 0x812F # This value is in Mesa gl.h and nVidia gl.h, so hopefully it's OK

from Numeric import * 				# Numeric Python package
from MLab import *                              # Matlab function imitation from Numeric Python

from math import *

############ Import texture compression stuff and use it, if possible ##############
# This may mess up image statistics! Check the output before using in an experiment!

try:
    from OpenGL.GL.ARB.texture_compression import * #   can use this to fit more textures in texture memory
    # This following function call doesn't seem to return any
    # useful info, at least on my PowerBook G4.  So it's commented
    # out for now.
    ## if not glInitTextureCompressionARB(): 
        ## VisionEgg.config.VISIONEGG_TEXTURE_COMPRESSION = 0
except:
    VisionEgg.config.VISIONEGG_TEXTURE_COMPRESSION = 0

def next_power_of_2(f):
    return pow(2.0,math.ceil(math.log(f)/math.log(2.0)))

####################################################################
#
#        Textures
#
####################################################################

class Texture:
    """Base class to handle textures."""
    def __init__(self,size=(128,128)):
    	"""Creates a white 'x' on a blue background unless self.orig is already defined."""
        if 'orig' not in dir(self): # The image is not already defined.
            # Create a default texture
            self.orig = Image.new("RGB",size,(0,0,255))
            draw = ImageDraw.Draw(self.orig)
            draw.line((0,0) + self.orig.size, fill=(255,255,255))
            draw.line((0,self.orig.size[1],self.orig.size[0],0), fill=(255,255,255))
            #draw.text((0,0),"Default texture")

    def load(self):
        """Load texture into video RAM"""
        # Someday put all this in a texture buffer manager.
        # The buffer manager will keep track of which
        # buffers are loaded.  It will associate images
        # with power of 2 buffers.

        # Create a buffer whose sides are a power of 2
        width_pow2  = int(next_power_of_2(self.orig.size[0]))
        height_pow2  = int(next_power_of_2(self.orig.size[1]))

        self.buf = TextureBuffer( (width_pow2, height_pow2) )
        self.buf.im.paste(self.orig,(0,0,self.orig.size[0],self.orig.size[1]))

        # location of myself in the buffer, in pixels
        self.buf_l = 0
        self.buf_r = self.orig.size[0]
        self.buf_t = 0
        self.buf_b = self.orig.size[1]

        # my size
        self.width = self.buf_r - self.buf_l
        self.height = self.buf_b - self.buf_t
        
        # location of myself in the buffer, in fraction
        self.buf_lf = 0.0
        self.buf_rf = float(self.orig.size[0])/float(self.buf.im.size[0])
        self.buf_tf = 0.0
        self.buf_bf = float(self.orig.size[1])/float(self.buf.im.size[1])

        texId = self.buf.load() # return the OpenGL Texture ID (uses "texture objects")
#        del self.orig # clear Image from system RAM
        return texId

    def get_pil_image(self):
        """Returns a PIL Image of the texture."""
        return self.orig

    def get_texture_buffer(self):
        return self.buf

class TextureFromFile(Texture):
    """A Texture that is loaded from a graphics file"""
    def __init__(self,filename):
        self.orig = Image.open(filename)
        Texture.__init__(self,self.orig.size)

class TextureFromPILImage(Texture):
    """A Texture that is loaded from a Python Imaging Library Image."""
    def __init__(self,image):
        self.orig = image
        Texture.__init__(self,self.orig.size)

class TextureBuffer:
    """Internal VisionEgg class.
    
    Loads an Image (from the Python Imaging Library) into video (texture) RAM.
    Width and height of Image should be power of 2."""
    def __init__(self,sizeTuple,mode="RGB",color=(127,127,127)):
        self.im = Image.new(mode,sizeTuple,color)
    def load(self):
        """This loads the texture into OpenGL's texture memory."""
        # THIS CODE HAS A BUG (OR A FEATURE, DEPENDING ON YOUR POV) ---
        # OpenGL has the y-values of pixels start at 0 at the LOWER
        # part of the screen, whereas almost everything else starts
        # counting from the top of the screen.  The code below was
        # written during a time when I forgot this about OpenGL, and
        # therefore just forces its way around the issue.
        self.gl_id = glGenTextures(1)
        glBindTexture(GL_TEXTURE_2D, self.gl_id)
        glEnable( GL_TEXTURE_2D )
        if self.im.mode == "RGB":
            image_data = self.im.tostring("raw","RGB")

            # Do error-checking on texture to make sure it will load
            max_dim = glGetIntegerv(GL_MAX_TEXTURE_SIZE)
            if self.im.size[0] > max_dim or self.im.size[1] > max_dim:
                raise VisionEgg.Core.EggError("Texture dimensions are too large for video system.\nOpenGL reports maximum size of %d x %d"%(max_dim,max_dim))
            
            # Because the MAX_TEXTURE_SIZE method is insensitive to the current
            # state of the video system, another check must be done using
            # "proxy textures".
            if VisionEgg.config.VISIONEGG_TEXTURE_COMPRESSION:
                glTexImage2D(GL_PROXY_TEXTURE_2D,            # target
                             0,                              # level
                             GL_COMPRESSED_RGB_ARB,          # video RAM internal format: compressed RGB
                             self.im.size[0],                # width
                             self.im.size[1],                # height
                             0,                              # border
                             GL_RGB,                         # format of image data
                             GL_UNSIGNED_BYTE,               # type of image data
                             image_data)                     # image data
            else:
                glTexImage2D(GL_PROXY_TEXTURE_2D,            # target
                             0,                              # level
                             GL_RGB,                         # video RAM internal format: RGB
                             self.im.size[0],                # width
                             self.im.size[1],                # height
                             0,                              # border
                             GL_RGB,                         # format of image data
                             GL_UNSIGNED_BYTE,               # type of image data
                             image_data)                     # image data
                
            if glGetTexLevelParameteriv(GL_PROXY_TEXTURE_2D,0,GL_TEXTURE_WIDTH) == 0:
                raise VisionEgg.Core.EggError("Texture is too wide for your video system!")
            if glGetTexLevelParameteriv(GL_PROXY_TEXTURE_2D,0,GL_TEXTURE_HEIGHT) == 0:
                raise VisionEgg.Core.EggError("Texture is too tall for your video system!")

            if VisionEgg.config.VISIONEGG_TEXTURE_COMPRESSION:
                glTexImage2D(GL_TEXTURE_2D,                  # target
                             0,                              # level
                             GL_COMPRESSED_RGB_ARB,          # video RAM internal format: compressed RGB
                             self.im.size[0],                # width
                             self.im.size[1],                # height
                             0,                              # border
                             GL_RGB,                         # format of image data
                             GL_UNSIGNED_BYTE,               # type of image data
                             image_data)                     # image data
            else:
                glTexImage2D(GL_TEXTURE_2D,                  # target
                             0,                              # level
                             GL_RGB,                         # video RAM internal format: RGB                             self.im.size[0],                # width
                             self.im.size[0],                # width
                             self.im.size[1],                # height
                             0,                              # border
                             GL_RGB,                         # format of image data
                             GL_UNSIGNED_BYTE,               # type of image data
                             image_data)                     # image data
            
        else:
            raise EggError("Unknown image mode '%s'"%(self.im.mode,))
        del self.im  # remove the image from system memory
        # Set some texture object defaults
        glTexParameteri(GL_TEXTURE_2D,GL_TEXTURE_WRAP_S,GL_CLAMP_TO_EDGE)
        glTexParameteri(GL_TEXTURE_2D,GL_TEXTURE_WRAP_T,GL_CLAMP_TO_EDGE)
        glTexParameteri(GL_TEXTURE_2D,GL_TEXTURE_MAG_FILTER,GL_LINEAR)
        glTexParameteri(GL_TEXTURE_2D,GL_TEXTURE_MIN_FILTER,GL_LINEAR)        
        return self.gl_id

    def put_sub_image(self,pil_image,lower_left, size):
        """This function always segfaults, for some reason!"""
        # Could it be that the width and height must be a power of 2?
        glBindTexture(GL_TEXTURE_2D, self.gl_id)
        print "bound texture"
        data = pil_image.tostring("raw","RGB",0,-1)
        print "converted data"
        if VisionEgg.config.VISIONEGG_TEXTURE_COMPRESSION:
            print "trying to put compressed image data"
            glCompressedTexSubImage2DARB(GL_TEXTURE_2D, # target
                                         0, # level
                                         lower_left[0], # x offset
                                         lower_left[1], # y offset
                                         GL_RGB,
                                         size[0], # width
                                         size[1], # height
                                         0,
                                         GL_UNSIGNED_INT,
                                         data)
        else:
            print "trying to put non-compressed image data"
            glTexSubImage2D(GL_TEXTURE_2D, # target
                            0, # level
                            lower_left[0], # x offset
                            lower_left[1], # y offset
                            size[0], # width
                            size[1], # height
                            GL_RGB,
                            GL_UNSIGNED_INT,
                            data)

    def free(self):
        glDeleteTextures(self.gl_id)

####################################################################
#
#        Stimulus - TextureStimulus
#
####################################################################

class TextureStimulusBaseClass(VisionEgg.Core.Stimulus):
    """Parameters common to all stimuli that use textures.

    Don't instantiate this class directly."""
    parameters_and_defaults = {'texture_scale_linear_interp':1,
                               'texture_repeat':0}    # if 0 clamp to edge

class TextureStimulus(TextureStimulusBaseClass):
    parameters_and_defaults = {'on':1,
                               'lowerleft':(0.0,0.0),
                               'size':(640.0,480.0)}
    def __init__(self,texture=Texture(size=(256,16)),**kw):
        apply(TextureStimulusBaseClass.__init__,(self,),kw)
        self.texture = texture
        self.texture_object = self.texture.load()

    def draw(self):
        if self.parameters.on:
            # Clear the modeview matrix
            glMatrixMode(GL_MODELVIEW)
            glLoadIdentity()
            
            glDisable(GL_DEPTH_TEST)
            glDisable(GL_BLEND)
            glEnable(GL_TEXTURE_2D)
            glBindTexture(GL_TEXTURE_2D,self.texture_object)
            
            if self.parameters.texture_scale_linear_interp:
                glTexParameteri(GL_TEXTURE_2D,GL_TEXTURE_MAG_FILTER,GL_LINEAR)
                glTexParameteri(GL_TEXTURE_2D,GL_TEXTURE_MIN_FILTER,GL_LINEAR)
            else:
                glTexParameteri(GL_TEXTURE_2D,GL_TEXTURE_MAG_FILTER,GL_NEAREST)
                glTexParameteri(GL_TEXTURE_2D,GL_TEXTURE_MIN_FILTER,GL_NEAREST)
                
            if self.parameters.texture_repeat:
                glTexParameteri(GL_TEXTURE_2D,GL_TEXTURE_WRAP_S,GL_REPEAT)
                glTexParameteri(GL_TEXTURE_2D,GL_TEXTURE_WRAP_T,GL_REPEAT)
            else:
                glTexParameteri(GL_TEXTURE_2D,GL_TEXTURE_WRAP_S,GL_CLAMP_TO_EDGE)
                glTexParameteri(GL_TEXTURE_2D,GL_TEXTURE_WRAP_T,GL_CLAMP_TO_EDGE)
            
            glTexEnvi(GL_TEXTURE_ENV, GL_TEXTURE_ENV_MODE, GL_REPLACE)

            p = self.parameters
            l = p.lowerleft[0]
            r = l + p.size[0]
            b = p.lowerleft[1]
            t = b + p.size[1]
            
            glBegin(GL_QUADS)
            glTexCoord2f(self.texture.buf_lf,self.texture.buf_bf)
            glVertex2f(l,b)

            glTexCoord2f(self.texture.buf_rf,self.texture.buf_bf)
            glVertex2f(r,b)

            glTexCoord2f(self.texture.buf_rf,self.texture.buf_tf)
            glVertex2f(r,t)

            glTexCoord2f(self.texture.buf_lf,self.texture.buf_tf)
            glVertex2f(l,t)
            glEnd() # GL_QUADS
            
####################################################################
#
#        Stimulus - Spinning Drum
#
####################################################################

class SpinningDrum(TextureStimulusBaseClass):
    parameters_and_defaults = {'num_sides':50,
                               'angular_position':0.0,
                               'contrast':1.0,
                               'on':1,
                               'flat':0, # toggles flat vs. cylinder
                               'dist_from_o':1.0 # z if flat, radius if cylinder
                               }
    
    # To avoid rescaling the texture size, make sure you are using a
    # viewport with an orthographic projection where left=0,
    # right=viewport.parameters.size[0],
    # bottom=0,top=viewport.parameters.size[1].

    def __init__(self,texture=Texture(size=(256,16)),**kw):
        apply(TextureStimulusBaseClass.__init__,(self,),kw)
        self.texture = texture
        self.texture_object = self.texture.load()

        self.cached_display_list = glGenLists(1) # Allocate a new display list
        self.rebuild_display_list()

    def draw(self):
    	"""Redraw the scene on every frame.
        """
        if self.parameters.on:
            # Set OpenGL state variables
            glDisable( GL_DEPTH_TEST )
            glEnable( GL_TEXTURE_2D )  # Make sure textures are drawn
            glEnable( GL_BLEND ) # Contrast control implemented through blending

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

            glBlendFunc( GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA )
            
            glTexEnvi(GL_TEXTURE_ENV, GL_TEXTURE_ENV_MODE, GL_DECAL)
            
            # clear modelview matrix
            glMatrixMode(GL_MODELVIEW)
            glLoadIdentity()

            glColor(0.5,0.5,0.5,self.parameters.contrast) # Set the polygons' fragment color (implements contrast)
            glBindTexture(GL_TEXTURE_2D, self.texture_object) # make sure to texture polygon

            # Make sure texture object parameters set the way we want
            if self.parameters.texture_scale_linear_interp:
                glTexParameteri(GL_TEXTURE_2D,GL_TEXTURE_MAG_FILTER,GL_LINEAR)
                glTexParameteri(GL_TEXTURE_2D,GL_TEXTURE_MIN_FILTER,GL_LINEAR)
            else:
                glTexParameteri(GL_TEXTURE_2D,GL_TEXTURE_MAG_FILTER,GL_NEAREST)
                glTexParameteri(GL_TEXTURE_2D,GL_TEXTURE_MIN_FILTER,GL_NEAREST)

            if self.parameters.texture_repeat:
                glTexParameteri(GL_TEXTURE_2D,GL_TEXTURE_WRAP_S,GL_REPEAT)
                glTexParameteri(GL_TEXTURE_2D,GL_TEXTURE_WRAP_T,GL_REPEAT)
            else:
                glTexParameteri(GL_TEXTURE_2D,GL_TEXTURE_WRAP_S,GL_CLAMP_TO_EDGE)
                glTexParameteri(GL_TEXTURE_2D,GL_TEXTURE_WRAP_T,GL_CLAMP_TO_EDGE)
            

            if self.parameters.flat: # draw as flat texture on a rectange
                w = self.texture.width
                h = self.texture.height

                # calculate texture coordinates based on current angle
                tex_phase = self.parameters.angular_position/360.0
                tex_phase = tex_phase % 1.0 # make 0 <= tex_phase < 1.0
                
                TINY = 1.0e-10
                if tex_phase < TINY: # it's effectively zero

                    glBegin(GL_QUADS)
                    glTexCoord2f(self.texture.buf_lf,self.texture.buf_bf)
                    glVertex2f(0.0,0.0)

                    glTexCoord2f(self.texture.buf_rf,self.texture.buf_bf)
                    glVertex2f(w,0.0)

                    glTexCoord2f(self.texture.buf_rf,self.texture.buf_tf)
                    glVertex2f(w,h)

                    glTexCoord2f(self.texture.buf_lf,self.texture.buf_tf)
                    glVertex2f(0.0,h)
                    glEnd() # GL_QUADS

                else:
                    # Convert tex_phase into texture buffer fraction
                    buf_break_f = ( (self.texture.buf_rf - self.texture.buf_lf) * (1.0-tex_phase) ) + self.texture.buf_lf

                    # Convert tex_phase into object coords value
                    quad_x_break = w * tex_phase

                    glBegin(GL_QUADS)

                    # First quad

                    glTexCoord2f(buf_break_f,self.texture.buf_bf)
                    glVertex2f(0.0,0.0)

                    glTexCoord2f(self.texture.buf_rf,self.texture.buf_bf)
                    glVertex2f(quad_x_break,0.0)

                    glTexCoord2f(self.texture.buf_rf,self.texture.buf_tf)
                    glVertex2f(quad_x_break,h)

                    glTexCoord2f(buf_break_f,self.texture.buf_tf)
                    glVertex2f(0.0,h)

                    # Second quad

                    glTexCoord2f(self.texture.buf_lf,self.texture.buf_bf)
                    glVertex2f(quad_x_break,0.0)

                    glTexCoord2f(buf_break_f,self.texture.buf_bf)
                    glVertex2f(w,0.0)

                    glTexCoord2f(buf_break_f,self.texture.buf_tf)
                    glVertex2f(w,h)

                    glTexCoord2f(self.texture.buf_lf,self.texture.buf_tf)
                    glVertex2f(quad_x_break,h)
                    glEnd() # GL_QUADS

            else: # draw as cylinder
                # turn the coordinate system so we don't have to deal with
                # figuring out where to draw the texture relative to drum
                glRotatef(self.parameters.angular_position,0.0,1.0,0.0)

                if self.parameters.num_sides != self.cached_display_list_num_sides:
                    self.rebuild_display_list()
                glCallList(self.cached_display_list)

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
        circum = 2.0*pi*r
        h = circum/float(self.texture.width)*float(self.texture.height)/2.0

        num_sides = self.parameters.num_sides
        self.cached_display_list_num_sides = num_sides
        
        deltaTheta = 2.0*pi / num_sides
        glNewList(self.cached_display_list,GL_COMPILE)
        glBegin(GL_QUADS)
        for i in range(num_sides):
            # angle of sides
            theta1 = i*deltaTheta
            theta2 = (i+1)*deltaTheta
            # fraction of texture
            frac1 = (self.texture.buf_l + (float(i)/num_sides*self.texture.width))/float(self.texture.width)
            frac2 = (self.texture.buf_l + (float(i+1)/num_sides*self.texture.width))/float(self.texture.width)
            # location of sides
            x1 = r*math.cos(theta1)
            z1 = r*math.sin(theta1)
            x2 = r*math.cos(theta2)
            z2 = r*math.sin(theta2)

            #Bottom left of quad
            glTexCoord2f(frac1, self.texture.buf_bf)
            glVertex4f( x1, -h, z1, 1.0 ) # 4th coordinate is "w"--look up "homogeneous coordinates" for more info.
            
            #Bottom right of quad
            glTexCoord2f(frac2, self.texture.buf_bf)
            glVertex4f( x2, -h, z2, 1.0 )
            #Top right of quad
            glTexCoord2f(frac2, self.texture.buf_tf); 
            glVertex4f( x2,  h, z2, 1.0 )
            #Top left of quad
            glTexCoord2f(frac1, self.texture.buf_tf)
            glVertex4f( x1,  h, z1, 1.0 )
        glEnd()
        glEndList()
