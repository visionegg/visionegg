"""gratings module of the Vision Egg package"""

# Copyright (c) 2002 Andrew Straw.  Distributed under the terms of the
# GNU Lesser General Public License (LGPL).

####################################################################
#
#        Import all the necessary packages
#
####################################################################

import VisionEgg
import VisionEgg.Core
import Numeric
import math, types, string
import OpenGL.GL
gl = OpenGL.GL

__version__ = VisionEgg.release_name
__cvs__ = string.split('$Revision$')[1]
__date__ = string.join(string.split('$Date$')[1:3], ' ')
__author__ = 'Andrew Straw <astraw@users.sourceforge.net>'
__all__ = ['SinGrating2D','SinGrating3D']


####################################################################
#
#        Stimulus - Sinusoidal Grating
#
####################################################################

class SinGrating2D(VisionEgg.Core.Stimulus):
    """Sine wave grating stimulus"""
    parameters_and_defaults = {'on':(1,types.IntType),
                               'contrast':(1.0,types.FloatType),
                               'lowerleft':((0.0,0.0),types.TupleType),
                               'size':((640.0,480.0),types.TupleType),
                               'wavelength':(128.0,types.FloatType), # in eye coord units
                               'phase':(0.0,types.FloatType), # degrees
                               'orientation':(0.0,types.FloatType), # 0=right, 90=down
                               'num_samples':(512, types.IntType) # number of spatial samples, should be a power of 2
                               }
    def __init__(self,projection = None,**kw):
        apply(VisionEgg.Core.Stimulus.__init__,(self,),kw)

        self.texture_object = gl.glGenTextures(1)
        gl.glBindTexture(gl.GL_TEXTURE_1D,self.texture_object)
        
        # Do error-checking on texture to make sure it will load
        max_dim = gl.glGetIntegerv(gl.GL_MAX_TEXTURE_SIZE)
        if self.parameters.num_samples > max_dim:
            raise VisionEgg.Core.EggError("Grating num_samples too large for video system.\nOpenGL reports maximum size of %d"%(max_dim,))

        l = self.parameters.lowerleft[0]
        r = l + self.parameters.size[0]
        inc = self.parameters.size[0]/float(self.parameters.num_samples)
        floating_point_sin = Numeric.sin(2.0*math.pi/self.parameters.wavelength*Numeric.arange(l,r,inc,'d')+(self.parameters.phase/180.0*math.pi))*0.5*self.parameters.contrast+0.5
        texel_data = (floating_point_sin*255.0).astype('b').tostring()

        # Because the MAX_TEXTURE_SIZE method is insensitive to the current
        # state of the video system, another check must be done using
        # "proxy textures".
        gl.glTexImage1D(gl.GL_PROXY_TEXTURE_1D,            # target
                     0,                              # level
                     gl.GL_LUMINANCE,                   # video RAM internal format: RGB
                     self.parameters.num_samples,    # width
                     0,                              # border
                     gl.GL_LUMINANCE,                   # format of image data
                     gl.GL_UNSIGNED_BYTE,               # type of image data
                     texel_data)                     # texel data
        if gl.glGetTexLevelParameteriv(gl.GL_PROXY_TEXTURE_1D,0,gl.GL_TEXTURE_WIDTH) == 0:
            raise VisionEgg.Core.EggError("Grating num_samples is too wide for your video system!")
        
        # If we got here, it worked and we can load the texture for real.
        gl.glTexImage1D(gl.GL_TEXTURE_1D,            # target
                     0,                              # level
                     gl.GL_LUMINANCE,                   # video RAM internal format: RGB
                     self.parameters.num_samples,    # width
                     0,                              # border
                     gl.GL_LUMINANCE,                   # format of image data
                     gl.GL_UNSIGNED_BYTE,               # type of image data
                     texel_data)                     # texel data
        # Set some texture object defaults
        gl.glTexParameteri(gl.GL_TEXTURE_1D,gl.GL_TEXTURE_WRAP_S,gl.GL_REPEAT)
        gl.glTexParameteri(gl.GL_TEXTURE_1D,gl.GL_TEXTURE_WRAP_T,gl.GL_REPEAT)
        gl.glTexParameteri(gl.GL_TEXTURE_1D,gl.GL_TEXTURE_MAG_FILTER,gl.GL_LINEAR)
        gl.glTexParameteri(gl.GL_TEXTURE_1D,gl.GL_TEXTURE_MIN_FILTER,gl.GL_LINEAR)

        if self.parameters.size[0] != self.parameters.size[1]:
            self.give_size_warning()
        else:
            self.gave_size_warning = 0

    def give_size_warning(self):
        print "WARNING: SinGrating does not have equal width and height."
        print "Gratings will have variable size based on orientation."
        self.gave_size_warning = 1

    def draw(self):
        if self.parameters.on:
            if self.parameters.size[0] != self.parameters.size[1]:
                if not self.gave_size_warning:
                    self.give_size_warning()
                    
            # Clear the modeview matrix
            gl.glMatrixMode(gl.GL_MODELVIEW)
            gl.glLoadIdentity()

            gl.glDisable(gl.GL_DEPTH_TEST)
            gl.glDisable(gl.GL_BLEND)
            gl.glDisable(gl.GL_TEXTURE_2D)
            gl.glEnable(gl.GL_TEXTURE_1D)
            gl.glBindTexture(gl.GL_TEXTURE_1D,self.texture_object)

            l = self.parameters.lowerleft[0]
            r = l + self.parameters.size[0]
            inc = self.parameters.size[0]/float(self.parameters.num_samples)
            floating_point_sin = Numeric.sin(2.0*math.pi/self.parameters.wavelength*Numeric.arange(l,r,inc,'d')+(self.parameters.phase/180.0*math.pi))*0.5*self.parameters.contrast+0.5
            texel_data = (floating_point_sin*255.0).astype('b').tostring()
        
            gl.glTexSubImage1D(gl.GL_TEXTURE_1D, # target
                            0, # level
                            0, # x offset
                            self.parameters.num_samples, # width
                            gl.GL_LUMINANCE, # data format
                            gl.GL_UNSIGNED_BYTE, # data type
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
            gl.glRotate(self.parameters.orientation,0.0,0.0,-1.0)
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

class SinGrating3D(VisionEgg.Core.Stimulus):
    """Sine wave grating mapped on the inside of a cylinder."""
    parameters_and_defaults = {'on':(1,types.IntType),
                               'contrast':(1.0,types.FloatType),
                               'radius':(1.0,types.FloatType),
                               'height':(10000.0,types.FloatType),
                               'wavelength':(36.0,types.FloatType), # in degrees
                               'phase':(0.0,types.FloatType), # degrees
                               'orientation':(0.0,types.FloatType), # 0=right, 90=down
                               'num_samples':(1024,types.IntType), # number of spatial samples, should be a power of 2
                               'num_sides':(50,types.IntType) # number of sides of cylinder
                               }
    def __init__(self,projection = None,**kw):
        apply(VisionEgg.Core.Stimulus.__init__,(self,),kw)

        self.texture_object = gl.glGenTextures(1)
        gl.glBindTexture(gl.GL_TEXTURE_1D,self.texture_object)
        
        # Do error-checking on texture to make sure it will load
        max_dim = gl.glGetIntegerv(gl.GL_MAX_TEXTURE_SIZE)
        if self.parameters.num_samples > max_dim:
            raise VisionEgg.Core.EggError("Grating num_samples too large for video system.\nOpenGL reports maximum size of %d"%(max_dim,))

        l = 0.0
        r = 360.0
        inc = 360.0/float(self.parameters.num_samples)
        floating_point_sin = Numeric.sin(2.0*math.pi/self.parameters.wavelength*Numeric.arange(l,r,inc,'d')+(self.parameters.phase/180.0*math.pi))*0.5*self.parameters.contrast+0.5
        texel_data = (floating_point_sin*255.0).astype('b').tostring()

        # Because the MAX_TEXTURE_SIZE method is insensitive to the current
        # state of the video system, another check must be done using
        # "proxy textures".
        gl.glTexImage1D(gl.GL_PROXY_TEXTURE_1D,            # target
                     0,                              # level
                     gl.GL_LUMINANCE,                   # video RAM internal format: RGB
                     self.parameters.num_samples,    # width
                     0,                              # border
                     gl.GL_LUMINANCE,                   # format of image data
                     gl.GL_UNSIGNED_BYTE,               # type of image data
                     texel_data)                     # texel data
        if gl.glGetTexLevelParameteriv(gl.GL_PROXY_TEXTURE_1D,0,gl.GL_TEXTURE_WIDTH) == 0:
            raise VisionEgg.Core.EggError("Grating num_samples is too wide for your video system!")
        
        # If we got here, it worked and we can load the texture for real.
        gl.glTexImage1D(gl.GL_TEXTURE_1D,            # target
                     0,                              # level
                     gl.GL_LUMINANCE,                   # video RAM internal format: RGB
                     self.parameters.num_samples,    # width
                     0,                              # border
                     gl.GL_LUMINANCE,                   # format of image data
                     gl.GL_UNSIGNED_BYTE,               # type of image data
                     texel_data)                     # texel data
        # Set some texture object defaults
        gl.glTexParameteri(gl.GL_TEXTURE_1D,gl.GL_TEXTURE_WRAP_S,gl.GL_REPEAT)
        gl.glTexParameteri(gl.GL_TEXTURE_1D,gl.GL_TEXTURE_WRAP_T,gl.GL_REPEAT)
        gl.glTexParameteri(gl.GL_TEXTURE_1D,gl.GL_TEXTURE_MAG_FILTER,gl.GL_LINEAR)
        gl.glTexParameteri(gl.GL_TEXTURE_1D,gl.GL_TEXTURE_MIN_FILTER,gl.GL_LINEAR)    

        self.cached_display_list = gl.glGenLists(1) # Allocate a new display list
        self.rebuild_display_list()

    def draw(self):
    	"""Redraw the scene on every frame.
        """
        if self.parameters.on:
            # Set OpenGL state variables
            gl.glDisable( gl.GL_DEPTH_TEST )
            gl.glEnable( gl.GL_TEXTURE_1D )  # Make sure textures are drawn
            gl.glDisable( gl.GL_TEXTURE_2D )
            gl.glDisable( gl.GL_BLEND )

            gl.glBindTexture(gl.GL_TEXTURE_1D,self.texture_object)

            l = 0.0
            r = 360.0
            inc = 360.0/float(self.parameters.num_samples)
            floating_point_sin = Numeric.sin(2.0*math.pi/self.parameters.wavelength*Numeric.arange(l,r,inc,'d')-(self.parameters.phase/180.0*math.pi))*0.5*self.parameters.contrast+0.5
            texel_data = (floating_point_sin*255.0).astype('b').tostring()
        
            gl.glTexSubImage1D(gl.GL_TEXTURE_1D, # target
                            0, # level
                            0, # x offset
                            self.parameters.num_samples, # width
                            gl.GL_LUMINANCE, # data format
                            gl.GL_UNSIGNED_BYTE, # data type
                            texel_data)
            
            gl.glTexEnvi(gl.GL_TEXTURE_ENV, gl.GL_TEXTURE_ENV_MODE, gl.GL_REPLACE)

            # clear modelview matrix
            gl.glMatrixMode(gl.GL_MODELVIEW)
            gl.glLoadIdentity()

            # do the orientation
            gl.glRotatef(self.parameters.orientation,0.0,0.0,1.0)

            if self.parameters.num_sides != self.cached_display_list_num_sides:
                self.rebuild_display_list()
            gl.glCallList(self.cached_display_list)

            gl.glDisable( gl.GL_TEXTURE_1D )

    def rebuild_display_list(self):
        # (Re)build the display list
        #
        # This draws a display list for an approximation of a cylinder.
        # The cylinder has "num_sides" sides. The following code
        # generates a list of vertices and the texture coordinates
        # to be used by those vertices.
        r = self.parameters.radius # in OpenGL (arbitrary) units
        circum = 2.0*pi*r
        h = self.parameters.height/2.0

        num_sides = self.parameters.num_sides
        self.cached_display_list_num_sides = num_sides
        
        deltaTheta = 2.0*pi / num_sides
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
