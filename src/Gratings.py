"""gratings module of the Vision Egg package"""

# Copyright (c) 2002 Andrew Straw.  Distributed under the terms of the
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

if "GL_CLAMP_TO_EDGE" not in dir(): # should have gotten from importing OpenGL.GL
    import VisionEgg.Textures 
    GL_CLAMP_TO_EDGE = VisionEgg.Textures.GL_CLAMP_TO_EDGE # use whatever hack is there...

import Numeric
from Numeric import * 				# Numeric Python package
from MLab import *                              # Matlab function imitation from Numeric Python

from math import *

####################################################################
#
#        Stimulus - Sinusoidal Grating
#
####################################################################

class SinGrating2D(VisionEgg.Core.Stimulus):
    parameters_and_defaults = {'on':1,
                               'contrast':1.0,
                               'lowerleft':(0.0,0.0),
                               'size':(640.0,480.0),
                               'wavelength':128.0, # in eye coord units
                               'phase':0.0, # degrees
                               'orientation':0.0, # 0=right, 90=down
                               'num_samples':256 # number of spatial samples, should be a power of 2
                               }
    def __init__(self,projection = None,**kw):
        apply(VisionEgg.Core.Stimulus.__init__,(self,),kw)

        self.texture_object = glGenTextures(1)
        glBindTexture(GL_TEXTURE_1D,self.texture_object)
        
        # Do error-checking on texture to make sure it will load
        max_dim = glGetIntegerv(GL_MAX_TEXTURE_SIZE)
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
        glTexImage1D(GL_PROXY_TEXTURE_1D,            # target
                     0,                              # level
                     GL_LUMINANCE,                   # video RAM internal format: RGB
                     self.parameters.num_samples,    # width
                     0,                              # border
                     GL_LUMINANCE,                   # format of image data
                     GL_UNSIGNED_BYTE,               # type of image data
                     texel_data)                     # texel data
        if glGetTexLevelParameteriv(GL_PROXY_TEXTURE_1D,0,GL_TEXTURE_WIDTH) == 0:
            raise VisionEgg.Core.EggError("Grating num_samples is too wide for your video system!")
        
        # If we got here, it worked and we can load the texture for real.
        glTexImage1D(GL_TEXTURE_1D,            # target
                     0,                              # level
                     GL_LUMINANCE,                   # video RAM internal format: RGB
                     self.parameters.num_samples,    # width
                     0,                              # border
                     GL_LUMINANCE,                   # format of image data
                     GL_UNSIGNED_BYTE,               # type of image data
                     texel_data)                     # texel data
        # Set some texture object defaults
        glTexParameteri(GL_TEXTURE_1D,GL_TEXTURE_WRAP_S,GL_REPEAT)
#        glTexParameteri(GL_TEXTURE_1D,GL_TEXTURE_WRAP_S,GL_CLAMP_TO_EDGE)
        glTexParameteri(GL_TEXTURE_1D,GL_TEXTURE_WRAP_T,GL_REPEAT)
        glTexParameteri(GL_TEXTURE_1D,GL_TEXTURE_MAG_FILTER,GL_LINEAR)
        glTexParameteri(GL_TEXTURE_1D,GL_TEXTURE_MIN_FILTER,GL_LINEAR)

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
            glMatrixMode(GL_MODELVIEW)
            glLoadIdentity()

            glDisable(GL_DEPTH_TEST)
            glDisable(GL_BLEND)
            glDisable(GL_TEXTURE_2D)
            glEnable(GL_TEXTURE_1D)
            glBindTexture(GL_TEXTURE_1D,self.texture_object)

            l = self.parameters.lowerleft[0]
            r = l + self.parameters.size[0]
            inc = self.parameters.size[0]/float(self.parameters.num_samples)
            floating_point_sin = Numeric.sin(2.0*math.pi/self.parameters.wavelength*Numeric.arange(l,r,inc,'d')+(self.parameters.phase/180.0*math.pi))*0.5*self.parameters.contrast+0.5
            texel_data = (floating_point_sin*255.0).astype('b').tostring()
        
            glTexSubImage1D(GL_TEXTURE_1D, # target
                            0, # level
                            0, # x offset
                            self.parameters.num_samples, # width
                            GL_LUMINANCE, # data format
                            GL_UNSIGNED_BYTE, # data type
                            texel_data)
            
            glTexEnvi(GL_TEXTURE_ENV, GL_TEXTURE_ENV_MODE, GL_REPLACE)

            l = self.parameters.lowerleft[0]
            r = l + self.parameters.size[0]
            b = self.parameters.lowerleft[1]
            t = b + self.parameters.size[1]

            # Get a matrix used to rotate the texture coordinates
            glMatrixMode(GL_TEXTURE)
            glPushMatrix()
            glLoadIdentity()
            glRotate(self.parameters.orientation,0.0,0.0,-1.0)
            glTranslate(-0.5,-0.5,0.0) # Rotate about the center of the texture
            
            glBegin(GL_QUADS)
            glTexCoord2f(0.0,0.0)
            glVertex2f(l,b)

            glTexCoord2f(1.0,0.0)
            glVertex2f(r,b)

            glTexCoord2f(1.0,1.0)
            glVertex2f(r,t)

            glTexCoord2f(0.0,1.0)
            glVertex2f(l,t)
            glEnd() # GL_QUADS
            
            glPopMatrix() # restore the texture matrix
            
            glDisable(GL_TEXTURE_1D)

class SinGrating3D(VisionEgg.Core.Stimulus):
    parameters_and_defaults = {'on':1,
                               'contrast':1.0,
                               'radius':1.0,
                               'height':10000.0,
                               'wavelength':36.0, # in degrees
                               'phase':0.0, # degrees
                               'orientation':0.0, # 0=right, 90=down
                               'num_samples':1024, # number of spatial samples, should be a power of 2
                               'num_sides':50 # number of sides of cylinder
                               }
    def __init__(self,projection = None,**kw):
        apply(VisionEgg.Core.Stimulus.__init__,(self,),kw)

        self.texture_object = glGenTextures(1)
        glBindTexture(GL_TEXTURE_1D,self.texture_object)
        
        # Do error-checking on texture to make sure it will load
        max_dim = glGetIntegerv(GL_MAX_TEXTURE_SIZE)
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
        glTexImage1D(GL_PROXY_TEXTURE_1D,            # target
                     0,                              # level
                     GL_LUMINANCE,                   # video RAM internal format: RGB
                     self.parameters.num_samples,    # width
                     0,                              # border
                     GL_LUMINANCE,                   # format of image data
                     GL_UNSIGNED_BYTE,               # type of image data
                     texel_data)                     # texel data
        if glGetTexLevelParameteriv(GL_PROXY_TEXTURE_1D,0,GL_TEXTURE_WIDTH) == 0:
            raise VisionEgg.Core.EggError("Grating num_samples is too wide for your video system!")
        
        # If we got here, it worked and we can load the texture for real.
        glTexImage1D(GL_TEXTURE_1D,            # target
                     0,                              # level
                     GL_LUMINANCE,                   # video RAM internal format: RGB
                     self.parameters.num_samples,    # width
                     0,                              # border
                     GL_LUMINANCE,                   # format of image data
                     GL_UNSIGNED_BYTE,               # type of image data
                     texel_data)                     # texel data
        # Set some texture object defaults
        glTexParameteri(GL_TEXTURE_1D,GL_TEXTURE_WRAP_S,GL_REPEAT)
#        glTexParameteri(GL_TEXTURE_1D,GL_TEXTURE_WRAP_S,GL_CLAMP_TO_EDGE)
        glTexParameteri(GL_TEXTURE_1D,GL_TEXTURE_WRAP_T,GL_REPEAT)
        glTexParameteri(GL_TEXTURE_1D,GL_TEXTURE_MAG_FILTER,GL_LINEAR)
        glTexParameteri(GL_TEXTURE_1D,GL_TEXTURE_MIN_FILTER,GL_LINEAR)    

        self.cached_display_list = glGenLists(1) # Allocate a new display list
        self.rebuild_display_list()

    def draw(self):
    	"""Redraw the scene on every frame.
        """
        if self.parameters.on:
            # Set OpenGL state variables
            glDisable( GL_DEPTH_TEST )
            glEnable( GL_TEXTURE_1D )  # Make sure textures are drawn
            glDisable( GL_TEXTURE_2D )
            glDisable( GL_BLEND )

            glBindTexture(GL_TEXTURE_1D,self.texture_object)

            l = 0.0
            r = 360.0
            inc = 360.0/float(self.parameters.num_samples)
            floating_point_sin = Numeric.sin(2.0*math.pi/self.parameters.wavelength*Numeric.arange(l,r,inc,'d')-(self.parameters.phase/180.0*math.pi))*0.5*self.parameters.contrast+0.5
            texel_data = (floating_point_sin*255.0).astype('b').tostring()
        
            glTexSubImage1D(GL_TEXTURE_1D, # target
                            0, # level
                            0, # x offset
                            self.parameters.num_samples, # width
                            GL_LUMINANCE, # data format
                            GL_UNSIGNED_BYTE, # data type
                            texel_data)
            
            glTexEnvi(GL_TEXTURE_ENV, GL_TEXTURE_ENV_MODE, GL_REPLACE)

            # clear modelview matrix
            glMatrixMode(GL_MODELVIEW)
            glLoadIdentity()

            # do the orientation
            glRotatef(self.parameters.orientation,0.0,0.0,1.0)

            if self.parameters.num_sides != self.cached_display_list_num_sides:
                self.rebuild_display_list()
            glCallList(self.cached_display_list)

            glDisable( GL_TEXTURE_1D )

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
        glNewList(self.cached_display_list,GL_COMPILE)
        glBegin(GL_QUADS)
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
            glTexCoord2f(frac1, 0.0)
            glVertex4f( x1, -h, z1, 1.0 )
            
            #Bottom right of quad
            glTexCoord2f(frac2, 0.0)
            glVertex4f( x2, -h, z2, 1.0 )
            #Top right of quad
            glTexCoord2f(frac2, 1.0); 
            glVertex4f( x2,  h, z2, 1.0 )
            #Top left of quad
            glTexCoord2f(frac1, 1.0)
            glVertex4f( x1,  h, z1, 1.0 )
        glEnd()
        glEndList()
