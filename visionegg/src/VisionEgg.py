# This is the python source code for the primary module of the Vision Egg package.
#
#
# Copyright (c) 2001 Andrew Straw.  Distributed under the terms of the
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

import sys, os, math                            # standard python packages
import Image, ImageDraw                         # Python Imaging Library packages
						                        # from PyOpenGL:
from OpenGL.GL import *                         #   main package
from OpenGL.GL.ARB.texture_env_combine import * #   this is needed to do contrast
from OpenGL.GL.ARB.texture_compression import * #   can use this to fit more textures in memory
from OpenGL.GLU import *                        #   utility routines
from OpenGL.GLUT import *						#   only if used if no SDL
from Numeric import * 							# Numeric Python package
from MLab import *                              # Matlab function imitation from Numeric Python

from _visionegg import * # internal C code

global use_sdl
try:
    from SDL import * # This is really VisionEgg.SDL (Why doesn't "from VisionEgg.SDL import *" work?)
    use_sdl = 1
except:
    print "WARNING: python module SDL not found.  Performance and features may be affected."
    use_sdl = 0

####################################################################
#
#        Error handling
#
####################################################################
    
class EggError(Exception):
    """Created whenever an exception happens in the Vision Egg package
    """
    def __init__(self,str):
        Exception.__init__(self,str)

####################################################################
#
#        Data acquisition
#
####################################################################
    
class Daq:
    """Base class that defines interface for any data acquisition implementation
    """
    def __init__(self,device,channelParamList,triggerMethod):
        pass # Not implemented yet

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

    def load(self,minFilter=GL_LINEAR,magFilter=GL_LINEAR):
        """Load texture into video RAM"""
        # Someday put all this in a texture buffer manager.
        # The buffer manager will keep track of which
        # buffers are loaded.  It will associate images
        # with power of 2 buffers.
        
        # Create a buffer whose sides are a power of 2
        width_pow2  = int(pow(2.0,math.ceil(self.__log2(float(self.orig.size[0])))))
        height_pow2 = int(pow(2.0,math.ceil(self.__log2(float(self.orig.size[0])))))
        
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

        texId = self.buf.load(minFilter,magFilter) # return the OpenGL Texture ID (uses "texture objects")
        del self.orig # clear Image from system RAM
        return texId

    def __log2(self,f):
    	"""Private method - logarithm base 2"""
        return math.log(f)/math.log(2)

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
    def load(self,minFilter=GL_LINEAR,magFilter=GL_LINEAR):
        self.gl_id = glGenTextures(1)
        glBindTexture(GL_TEXTURE_2D, self.gl_id)
        glTexParameteri(GL_TEXTURE_2D,GL_TEXTURE_MAG_FILTER,magFilter)
        glTexParameteri(GL_TEXTURE_2D,GL_TEXTURE_MIN_FILTER,minFilter)
        glTexParameteri(GL_TEXTURE_2D,GL_TEXTURE_WRAP_S,GL_CLAMP) # Hopefully make artifacts more visible
        glTexParameteri(GL_TEXTURE_2D,GL_TEXTURE_WRAP_T,GL_CLAMP)
        if self.im.mode == "RGB":
            glTexImage2D(GL_TEXTURE_2D,                  # target
                         0, # level
#                         GL_RGB,                         # video RAM internal format: RGB
                         GL_COMPRESSED_RGB_ARB,          # video RAM internal format: compressed RGB
                         self.im.size[0],                # width
                         self.im.size[1],                # height
                         0,                              # border
                         GL_RGB,                         # format of image data
                         GL_UNSIGNED_BYTE,               # type of image data
                         self.im.tostring("raw","RGB"))  # image data
#        elif self.im.mode == "RGBA":
#            glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA,
#                         self.im.size[0], self.im.size[1],
#                         0,GL_RGBX, GL_UNSIGNED_BYTE,self.im.tostring("raw","RGBA"))#,0,-1))
        else:
            raise EggError("Unknown image mode '%s'"%(self.im.mode,))
        del self.im  # remove the image from system memory
        return self.gl_id
    
####################################################################
#
#        Projection classes - use OrthographicProjection, Perspective Projection
#
####################################################################

class Projection:
    """Abstract base class that defines how to set the OpenGL projection matrix"""
    def __init__(self):
        raise RuntimeError("Must use a subclass of Projection")
    def set_GL_projection_matrix(self):
        raise RuntimeError("Must use a subclass of Projection")

class OrthographicProjection(Projection):
    """An orthographic projection"""
    def __init__(self,left=-1.0,right=1.0,bottom=-1.0,top=1.0,z_clip_near=0.1,z_clip_far=100.0):
        self.left = left
        self.right = right
        self.bottom = bottom
        self.top = top
        self.z_clip_near = z_clip_near
        self.z_clip_far = z_clip_far

    def set_GL_projection_matrix(self):
        """Set the OpenGL projection matrix and then put OpenGL into modelview mode"""
        matrix_mode = glGetIntegerv(GL_MATRIX_MODE) # Save the GL of the matrix state
        glMatrixMode(GL_PROJECTION) # Set OpenGL matrix state to modify the projection matrix
        glLoadIdentity() # Clear the projection matrix
        glOrtho(self.left,self.right,self.bottom,self.top,self.z_clip_near,self.z_clip_far) # Let GL create a matrix and compose it
        if matrix_mode != GL_PROJECTION:
            glMatrixMode(matrix_mode) # Set the matrix mode back

class PerspectiveProjection(Projection):
    """A perspective projection"""
    def __init__(self,fov_x=45.0,z_clip_near = 0.1,z_clip_far=100.0):
        self.fov_x = fov_x
        self.z_clip_near = z_clip_near
        self.z_clip_far = z_clip_far

    def set_GL_projection_matrix(self):
        """Set the OpenGL projection matrix and then put OpenGL into modelview mode"""
        
        global screen_width,screen_height
        
        self.fov_y = self.fov_x / screen_width * screen_height       # Wish that this could be done in __init__, but
        self.aspect_ratio = float(screen_width)/float(screen_height) # screen_width and screen_heigh may not be defined.

        matrix_mode = glGetIntegerv(GL_MATRIX_MODE) # Save the GL of the matrix state
        glMatrixMode(GL_PROJECTION) # Set OpenGL matrix state to modify the projection matrix
        glLoadIdentity() # Clear the projection matrix
        gluPerspective(self.fov_y,self.aspect_ratio,self.z_clip_near,self.z_clip_far) # Let GLU create a matrix and compose it
        if matrix_mode != GL_PROJECTION:
            glMatrixMode(matrix_mode) # Set the matrix mode back

####################################################################
#
#        Stimulus - Base class (Spinning teapot, just to show something)
#
####################################################################

class Stimulus:
    """Base class that provides timing routines and core functionality for any stimulus."""
    def __init__(self,durationSec=5.0,bgcolor=(0.5,0.5,0.5,0.0),projection=OrthographicProjection()):
        self.durationSec = durationSec
        self.projection = projection
        self.spotOn = 0
        self.bgcolor = bgcolor
#        self.drawTimes = [] # List of times the frame was drawn
#        self.drawTimes2 = [] # List of times ?
#        self.drawTimes3 = [] # List of times ?
        self.initGL()

    def setDuration(self,durationSec):
        self.durationSec = durationSec

    def setSpotOn(self,spotOn):
        self.spotOn = spotOn
        if self.spotOn:
            # setup an orthographic projection so the fixation spot is always square
            global screen_width,screen_height

            x = 100.0
            y = x * screen_height / screen_width
            self.spot_projection = OrthographicProjection(left=-0.5*x,right=0.5*x,bottom=-0.5*y,top=0.5*y,z_clip_near=-1.0,z_clip_far=1.0)

    def registerDaq(self,daq):
        self.daq = daq
        
    def drawFixationSpot(self):
        """Draw a fixation spot at the center of the screen"""
        # save current matrix mode
        matrix_mode = glGetIntegerv(GL_MATRIX_MODE)

        # before we clear the modelview matrix, save its state
        if matrix_mode != GL_MODELVIEW:
            glMatrixMode(GL_MODELVIEW)
        glPushMatrix() # save the current modelview to the stack
        glLoadIdentity() # clear the modelview matrix

        # before we clear the projection matrix, save its state
        glMatrixMode(GL_PROJECTION) 
        glPushMatrix()
        glLoadIdentity()
        self.spot_projection.set_GL_projection_matrix()

        glColor(1.0,1.0,1.0,1.0) # Should cache the color value
        glDisable(GL_TEXTURE_2D)
        # This could go in a display list to speed it up
        glBegin(GL_QUADS)
        size = 0.25
        glVertex3f(-size,-size, 0.0);
        glVertex3f( size,-size, 0.0);
        glVertex3f( size, size, 0.0);
        glVertex3f(-size, size, 0.0);
        glEnd() # GL_QUADS
        glEnable(GL_TEXTURE_2D)

        glPopMatrix() # restore projection matrix

        glMatrixMode(GL_MODELVIEW)
        glPopMatrix() # restore modelview matrix

        if matrix_mode != GL_MODELVIEW:
            glMatrixMode(matrix_mode)   # restore matrix state

    def glut_idle(self): # only called if running in GLUT
#        lastTime = self.curTime # even though it's confusing between these two instructions, this must be done now
#        lastyrot = self.yrot

#        self.contrast = self.cFunc(self.curTime)
#        self.yrot = self.posFunc(self.curTime)

#        delta_pos = self.yrot - lastyrot # degrees
#        delta_t = self.curTime - lastTime # seconds

#        self.texId = self.getTexId(delta_pos,delta_t)
        
        self.drawGLScene()
        cur_time_absolute = getTime()
        self.cur_time = cur_time_absolute-self.start_time_absolute
        if self.cur_time > self.durationSec:
            self.stimulus_done()
            #graphicsClose() # XXX Wrong! I just want to stop glutMainLoop!
            #glutDestroyWindow(glut_window) # doesn't quit glutMainLoop

    def glut_go(self): # only called if running in GLUT
        self.start_time_absolute = getTime()
        self.cur_time = 0.0
#        self.yrot = self.posFunc(0.0)
        glutIdleFunc(self.glut_idle)
#        self.glut_idle() # call glut_idle() at least once before calling drawGLScene
        glutDisplayFunc(self.drawGLScene)
        glutMainLoop()
        
    def sdl_go(self):
        """Could put in C to run faster.

        Bare bones timing routines.
        """
        self.start_time_absolute = getTime()
        self.cur_time = 0.0
        #self.yrot = self.posFunc(self.curTime)
        #lastyrot = self.yrot
        #lastTime = self.curTime
        while (self.cur_time <= self.durationSec):
            #self.contrast = self.cFunc(self.curTime)
            #self.yrot = self.posFunc(self.curTime)

            #delta_pos = self.yrot - lastyrot
            #delta_t = self.curTime - lastTime

            #lastTime = self.curTime

            #self.drawTimes3.append(getTime())
            #self.texId = self.getTexId(delta_pos,delta_t)
            
            #lastyrot = self.yrot
            self.drawGLScene()
            cur_time_absolute = getTime()
            self.cur_time = cur_time_absolute-self.start_time_absolute
        self.stimulus_done()

    def drawGLScene(self):
    	"""Redraw the scene on every frame.
    
        Since this is just a base class, do something simple.
        Drawing a teapot seems a good idea, since it looks
        relatively pretty and takes one line of code.
        """
        yrot = self.cur_time*90.0 # spin 90 degrees per second
        glClear(GL_COLOR_BUFFER_BIT)
        glLoadIdentity()
        glTranslatef(0.0, 0.0, -6.0)
        glRotatef(yrot,0.0,1.0,0.0)
        glutSolidTeapot(0.5)
        swap_buffers()

    def initGL(self):
        global screen_width,screen_height
        
        # Initialize OpenGL viewport
        glViewport(0,0,screen_width,screen_height)
        self.projection.set_GL_projection_matrix()
        glClearColor(0.0, 0.0, 0.0, 0.0)

    def histogram(self,a, bins):  # straight from NumDoc.pdf
        n = searchsorted(sort(a),bins)
        n = concatenate([n, [len(a)]])
        return n[1:]-n[:-1]
        
    def print_hist(self,a, bins):
        hist = self.histogram(a,bins)
        lines = 10
        maxhist = float(max(hist))
        h = hist # copy
        hist = hist.astype('f')/maxhist*float(lines) # normalize to 10
        print "Histogram:"
        for line in range(lines):
            val = float(lines)-1.0-float(line)
            print "%6d"%(round(maxhist*val/10.0),),
            q = greater(hist,val)
            for qi in q:
                s = ' '
                if qi:
                    s = '*'
                print "%5s"%(s,),
            print
        print " Time:",
        for bin in bins:
            print "%5d"%(int(bin*1.0e3),),
        print "(msec)"
        print "Total:",
        for hi in h:
            print "%5d"%(hi,),
        print

    def frameStats(self):
        drawTimes = array(self.drawTimes)
        drawTimes2 = array(self.drawTimes2)
        drawTimes3 = array(self.drawTimes3)
        self.drawTimes = [] # clear the list
        self.drawTimes2 = [] # clear the list
        self.drawTimes3 = []
        drawTimes3 = drawTimes - drawTimes3 # texture finding time
        drawTimes2 = drawTimes2 - drawTimes # get the swap buffer time
        drawTimes = drawTimes[1:] - drawTimes[:-1] # get inter-frame interval
        print (len(drawTimes)+1), "frames drawn."
        mean_sec = mean(drawTimes)
        print "mean frame to frame time:", mean_sec*1.0e6, "(usec), fps: ",1.0/mean_sec, " max:",max(drawTimes)*1.0e6
        print "mean swap buffer time:", mean(drawTimes2)*1.0e6, "(usec) max:",max(drawTimes2)*1.0e6
        print "mean texture finding time:", mean(drawTimes3)*1.0e6, "(usec) max:",max(drawTimes3)*1.0e6

        bins = arange(0.0,15.0,1.0) # msec
        bins = bins*1.0e-3 # sec
        print "Frame to frame"
        self.print_hist(drawTimes,bins)

        print "Swap buffers"
        self.print_hist(drawTimes2,bins)
        
        print "Texture finding"
        self.print_hist(drawTimes3,bins)
        
    def go(self):
        global use_sdl
        if use_sdl:
            self.sdl_go()
        else:
            self.glut_go()

#    def do_nothing(self):
#        preciseSleep( 1000 )

    def stimulus_done(self):
        global use_sdl
        
        if use_sdl:
            pass
        else:
            # I'd really like to break out of the glutMainLoop, but I can't
            glutIdleFunc(self.do_nothing)
            glutDisplayFunc(self.do_nothing)
        self.clearGL()
#        self.frameStats()

    def clearGL(self):
        #global screen_width,screen_height
        #global use_sdl
        
        # Initialize OpenGL viewport
        #glViewport(0,0,screen_width,screen_height)
        
        # Now setup projection
        # self.projection.set_GL_projection_matrix()

        glClearColor(self.bgcolor[0],self.bgcolor[1],self.bgcolor[2],self.bgcolor[3])
        glClear(GL_COLOR_BUFFER_BIT)
        swap_buffers()
        #if use_sdl:
        #    SDL_GL_SwapBuffers()
        #else:
        #    glutSwapBuffers()
        
####################################################################
#
#        Stimulus - Spinning Drum
#
####################################################################

class SpinningDrum(Stimulus):
    def __init__(self,durationSec,texture,position_function,contrast_function,numSides=30,radius=3.0,projection=PerspectiveProjection()):
        self.tex = texture
        self.position_function = position_function
        self.contrast_function = contrast_function
        self.numSides = numSides
        self.radius = radius # in OpenGL (arbitrary) units
        circum = 2.0*math.pi*self.radius
        self.height = circum*float(self.tex.orig.size[1])/float(self.tex.orig.size[0])
        self.texId = texture.load()
        bgcolor = (0.5,0.5,0.5,0.0) # this is fixed so that contrast 0 is this color
        Stimulus.__init__(self,durationSec,bgcolor,projection)

    def drawGLScene(self):
    	"""Redraw the scene on every frame.
    
        Could put in C to run faster if needed.
        """
        glClear(GL_COLOR_BUFFER_BIT)
        glLoadIdentity()

        yrot = self.position_function(self.cur_time)
        contrast = self.contrast_function(self.cur_time)
        
        glRotatef(yrot,0.0,1.0,0.0)
        glColor(0.5,0.5,0.5,contrast) # Fragment color
        glBindTexture(GL_TEXTURE_2D, self.texId)
        glCallList(self.displayListId)

        if self.spotOn: # draw fixation target
            self.drawFixationSpot()
            
        #self.drawTimes.append(getTime())
        swap_buffers()

    def initGL(self):
        global screen_width,screen_height
        
        # Initialize OpenGL viewport
        glViewport(0,0,screen_width,screen_height)
        
        # Now setup projection
        self.projection.set_GL_projection_matrix()

        glClearColor(0.5, 0.5, 0.5, 0.0 )
        glClear(GL_COLOR_BUFFER_BIT)

        if 0:
            # turn on anti-aliasing
            glEnable(GL_POLYGON_SMOOTH) # doesn't seem to be supported on nVidia GeForce 2
            glEnable(GL_LINE_SMOOTH)

            # must configure and enable blending to do anti-aliasing
            glBlendFunc(GL_SRC_ALPHA,GL_ONE_MINUS_SRC_ALPHA)
            glEnable(GL_BLEND)
        if 0:  # only draw lines, not faces
            glPolygonMode(GL_FRONT_AND_BACK,GL_LINE)
            
        glEnable(GL_TEXTURE_2D) # draw the textures!
        glBindTexture(GL_TEXTURE_2D, self.tex.buf.gl_id)

        if 'GL_ARB_texture_env_combine' in glGetString(GL_EXTENSIONS).split():
            contrast_control_enabled = 1
        else:
            contrast_control_enabled = 0

        if not contrast_control_enabled:
            glTexEnvi(GL_TEXTURE_ENV, GL_TEXTURE_ENV_MODE, GL_MODULATE) # use if ARB_texture_env_combine extension not avaliable
            print "WARNING: OpenGL extension GL_ARB_texture_env_combine not found.  Contrast control disabled."
        else:
            glTexEnvi(GL_TEXTURE_ENV, GL_TEXTURE_ENV_MODE, GL_COMBINE_ARB) # use ARB extension

            # this is really tricky, esp. since there's not much documentation!
            glTexEnvi(GL_TEXTURE_ENV, GL_COMBINE_RGB_ARB, GL_INTERPOLATE_ARB)

            # GL_INTERPOLATE_ARB means the texture function is = Arg0*(Arg2) + Arg1*(1-Arg2)
            # So we want Arg2 to be contrast, Arg0 to be the texture, and Arg1 to be the "incoming fragment" (the polygon)
            # Now we have to define what Arg<n> is.

            # Setup Arg0
            glTexEnvi(GL_TEXTURE_ENV, GL_SOURCE0_RGB_ARB, GL_TEXTURE)
            glTexEnvi(GL_TEXTURE_ENV, GL_OPERAND0_RGB_ARB, GL_SRC_COLOR)
            # Setup Arg1
            glTexEnvi(GL_TEXTURE_ENV, GL_SOURCE1_RGB_ARB, GL_PRIMARY_COLOR_ARB)
            glTexEnvi(GL_TEXTURE_ENV, GL_OPERAND1_RGB_ARB, GL_SRC_COLOR)
            # Setup Arg2
            glTexEnvi(GL_TEXTURE_ENV, GL_SOURCE2_RGB_ARB, GL_PRIMARY_COLOR_ARB)
            glTexEnvi(GL_TEXTURE_ENV, GL_OPERAND2_RGB_ARB, GL_SRC_ALPHA)

            glTexEnvi(GL_TEXTURE_ENV, GL_COMBINE_ALPHA_ARB, GL_MODULATE) # just multiply texture alpha with fragment alpha

        r = self.radius # shorthand
        h = self.height # shorthand
        numSides = self.numSides # shorthand

        # Build the display list
        #
        # A "display list" is a series of OpenGL commands that is
        # cached in a list for rapid re-drawing of the same object.
        #
        # This draws a display list for an approximation of a cylinder.
        # The cylinder has "numSides" sides. The following code
        # generates a list of vertices and the texture coordinates
        # to be used by those vertices.
        self.displayListId = glGenLists(1) # Allocate a new display list
        deltaTheta = 2.0*math.pi/numSides
        glNewList(self.displayListId,GL_COMPILE)
        glBegin(GL_QUADS)
        for i in range(numSides):
            theta1 = i*deltaTheta
            theta2 = (i+1)*deltaTheta
            frac1 = (self.tex.buf_l + (float(i)/numSides*self.tex.width))/float(self.tex.width)
            frac2 = (self.tex.buf_l + (float(i+1)/numSides*self.tex.width))/float(self.tex.width)
            
            #Bottom left of quad
            glTexCoord2f(frac1, self.tex.buf_bf)
            glVertex3f( r*math.cos(theta1), -h, r*math.sin(theta1) )
            #Bottom right of quad
            glTexCoord2f(frac2, self.tex.buf_bf)
            glVertex3f( r*math.cos(theta2), -h, r*math.sin(theta2) )
            #Top right of quad
            glTexCoord2f(frac2, self.tex.buf_tf); 
            glVertex3f( r*math.cos(theta2),  h, r*math.sin(theta2) )
            #Top left of quad
            glTexCoord2f(frac1, self.tex.buf_tf)
            glVertex3f( r*math.cos(theta1),  h, r*math.sin(theta1) )
        glEnd()
        glEndList()

class MovingTarget(Stimulus):
    def __init__(self,
                 position_function,
                 durationSec=10.0,
                 orientation=0.0,
                 width=5.0,
                 height=5.0,
                 color=(1.0,1.0,1.0,1.0),
                 bgcolor=(0.0,0.0,0.0,0.0),
                 anti_aliasing=0,
                 projection=None):

        if projection == None:
            # Create an orthogonal projection that where square units
            # will create square objects on screen
            global screen_width, screen_height

            projection_width = 200.0
            projection_height = projection_width * screen_height / screen_width
            l = -0.5*projection_width
            r = 0.5*projection_width
            t = 0.5*projection_height
            b = -0.5*projection_height
            projection=OrthographicProjection(left=l,
                                              right=r,
                                              top=t,
                                              bottom=b)
        self.position_function = position_function
        self.width = width
        self.height = height
        self.color = color
        #self.background = background # done in base class
        self.orientation = orientation # degrees, 0 moves rightwards, 90 moves downwards
        self.anti_aliasing = anti_aliasing
        Stimulus.__init__(self,durationSec,bgcolor,projection)
    
    def initGL(self):
        global screen_width,screen_height
        
        # Initialize OpenGL viewport
        glViewport(0,0,screen_width,screen_height)
        
        # Now setup projection
        self.projection.set_GL_projection_matrix()

        # Set the background color and clear the GL window
        glClearColor(self.bgcolor[0], self.bgcolor[1], self.bgcolor[2], self.bgcolor[3])
        glClear(GL_COLOR_BUFFER_BIT)

        # Set the foreground color
        glColor(self.color[0], self.color[1], self.color[2], self.color[3])
        
        # Build the display list
        self.displayListId = glGenLists(1) # Allocate a new display list

        glNewList(self.displayListId,GL_COMPILE)
        glBegin(GL_QUADS)
        #Bottom left of quad
        glVertex2f(-0.5*self.width, -0.5*self.height)
        #Bottom right
        glVertex2f( 0.5*self.width, -0.5*self.height)
        #Top right
        glVertex2f( 0.5*self.width,  0.5*self.height)
        #Top left
        glVertex2f(-0.5*self.width,  0.5*self.height)
        glEnd()
        glEndList()

        if self.anti_aliasing:
            # GL_POLYGON_SMOOTH doesn't seem to work
            # so we'll first draw a filled polygon (aliased)
            # then draw the outline of the polygon (with anti-aliasing)
            # and finally the corners of the polygon (with anti-aliasing)
            
            # Calculate coverage value for each pixel of outline and corners
            # and store as alpha
            glEnable(GL_LINE_SMOOTH)
            glEnable(GL_POINT_SMOOTH)
                    
            # Now specify how to use the alpha value
            glBlendFunc(GL_SRC_ALPHA,GL_ONE_MINUS_SRC_ALPHA)
            glEnable(GL_BLEND)

    def drawGLScene(self):
        glClear(GL_COLOR_BUFFER_BIT) # clear the framebuffer
        glLoadIdentity() # clear the modelview matrix

        position = self.position_function(self.cur_time)
        glTranslatef(position[0],position[1],-1.0) # center the modelview matrix where we want the target
        glRotatef(self.orientation,0.0,0.0,-1.0) # rotate the modelview matrix to our orientation

        glCallList(self.displayListId) # draw the target (precompiled display list)
        
        if self.anti_aliasing:
            # Draw a second polygon in line mode, so the edges are anti-aliased
            glPolygonMode(GL_FRONT_AND_BACK,GL_LINE)
            glCallList(self.displayListId)

            # Draw a third polygon in point mode, so the corners are anti-aliased
            glPolygonMode(GL_FRONT_AND_BACK,GL_POINT)
            glCallList(self.displayListId) # draw the target (precompiled display list)

            # Set the polygon mode back to fill mode
            glPolygonMode(GL_FRONT_AND_BACK,GL_FILL)

        if self.spotOn: # probably never on for a moving target stimulus, but still...
            self.drawFixationSpot()

        swap_buffers()

####################################################################
#
#        Graphics initialization
#
####################################################################            
            
def graphicsInit(width=640,height=480,fullscreen=0,realtime_priority=0,vsync=0,try_sdl=1):
    global use_sdl
    global glut_window
    global screen_width,screen_height

    screen_width = width
    screen_height = height
    
    if vsync: # There is no cross-platform way to do this
        os.environ["__GL_SYNC_TO_VBLANK"] = "1" # This works for nVidia drivers on linux

    if realtime_priority:
        setRealtime()

    if not try_sdl:
        use_sdl = 0

    caption = "Vision Egg"

    if use_sdl:
        print "Using SDL"
        # Initialize SDL, we only need the video section
        SDL_Init(SDL_INIT_VIDEO)
        
        # Setup double buffering in OpenGL
        SDL_GL_SetAttribute( SDL_GL_DOUBLEBUFFER, 1 )

        # Setup OpenGL framebuffer
        SDL_GL_SetAttribute( SDL_GL_RED_SIZE, 8 )
        SDL_GL_SetAttribute( SDL_GL_GREEN_SIZE, 8 )
        SDL_GL_SetAttribute( SDL_GL_BLUE_SIZE, 8 )
        #SDL_GL_SetAttribute( SDL_GL_ALPHA_SIZE, 8 )

        # Set the video mode
        if fullscreen:
            flags = SDL_OPENGL | SDL_FULLSCREEN
        else:
            flags = SDL_OPENGL
        modeList = SDL_ListModes(None,flags)
        if modeList is not None: # we have limited modes
            if (screen_width,screen_height) not in modeList:
                screen_width = modeList[0][0]
                screen_height = modeList[0][1]
                print "WARNING: Using %dx%d video mode instead of requested size."%(width,height)
        SDL_SetVideoMode(screen_width, screen_height, 0, flags )

        if 0:
            print "SDL_GL_GetAttribute( SDL_GL_RED_SIZE ) =", SDL_GL_GetAttribute( SDL_GL_RED_SIZE )
            print "SDL_GL_GetAttribute( SDL_GL_GREEN_SIZE ) =", SDL_GL_GetAttribute( SDL_GL_GREEN_SIZE )
            print "SDL_GL_GetAttribute( SDL_GL_BLUE_SIZE ) =", SDL_GL_GetAttribute( SDL_GL_BLUE_SIZE )
            print "SDL_GL_GetAttribute( SDL_GL_ALPHA_SIZE ) =", SDL_GL_GetAttribute( SDL_GL_ALPHA_SIZE )
            print "SDL_GL_GetAttribute( SDL_GL_DOUBLEBUFFER ) =", SDL_GL_GetAttribute( SDL_GL_DOUBLEBUFFER )
            print "SDL_GL_GetAttribute( SDL_GL_BUFFER_SIZE ) =", SDL_GL_GetAttribute( SDL_GL_BUFFER_SIZE )
            print "SDL_GL_GetAttribute( SDL_GL_DEPTH_SIZE ) =", SDL_GL_GetAttribute( SDL_GL_DEPTH_SIZE )
            print "SDL_GL_GetAttribute( SDL_GL_STENCIL_SIZE ) =", SDL_GL_GetAttribute( SDL_GL_STENCIL_SIZE )
            print "SDL_GL_GetAttribute( SDL_GL_ACCUM_RED_SIZE ) =", SDL_GL_GetAttribute( SDL_GL_ACCUM_RED_SIZE )
            print "SDL_GL_GetAttribute( SDL_GL_ACCUM_GREEN_SIZE ) =", SDL_GL_GetAttribute( SDL_GL_ACCUM_GREEN_SIZE )
            print "SDL_GL_GetAttribute( SDL_GL_ACCUM_BLUE_SIZE ) =", SDL_GL_GetAttribute( SDL_GL_ACCUM_BLUE_SIZE )
            print "SDL_GL_GetAttribute( SDL_GL_ACCUM_ALPHA_SIZE ) =", SDL_GL_GetAttribute( SDL_GL_ACCUM_BLUE_SIZE )
            print "glGetIntegerv(GL_MAX_TEXTURE_SIZE) = ", glGetIntegerv(GL_MAX_TEXTURE_SIZE ) 
            #print "glGetFloatv(GL_COLOR_MATRIX) = ", glGetFloatv(GL_COLOR_MATRIX) # requires imaging subset
            for extension in glGetString(GL_EXTENSIONS).split():
                print extension

        # Set the window caption
        SDL_WM_SetCaption(caption)
        # Hide the cursor 
        SDL_ShowCursor(SDL_DISABLE)

    else: # closes "if use_sdl:"
        print "Using GLUT"
        # need to figure out if fullscreen is possible with GLUT
        glutInit(sys.argv)
        glutInitDisplayMode( GLUT_DOUBLE | GLUT_RGB )
        glutInitWindowSize(screen_width,screen_height)
        glut_window = glutCreateWindow(caption)
        if fullscreen:
            glutFullScreen()

####################################################################
#
#        Graphics close
#
####################################################################            

def graphicsClose():
    global use_sdl
    if use_sdl:
        SDL_ShowCursor(SDL_ENABLE)
        SDL_Quit()
    sys.exit() # Shouldn't do this, but it's the only way I know to quit glutMainLoop

####################################################################
#
#        Swap the buffers
#
####################################################################            

def swap_buffers():
    """Swap OpenGL buffers."""

    # Of all the routines that could be put in C for speed, this may
    # be the biggest bang for the buck.  Then again, it may not.
    global use_sdl

    if use_sdl:
        SDL_GL_SwapBuffers()
    else:
        glutSwapBuffers()
    #toggleDOut()
    #glFinish() # Apparently this is not a given with double buffering
    #self.drawTimes2.append(getTime())

