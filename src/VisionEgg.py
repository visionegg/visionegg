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
#        Stimulus - Static teapot (Base class)
#
####################################################################

class Stimulus:
    """Base class that provides timing routines and core functionality for any stimulus."""
    def __init__(self,durationSec=1.0,fovx=45.0):
        self.durationSec = durationSec
        self.fovx = fovx        # horizontal field of view in degrees
        self.spotOn = 0
        self.drawTimes = [] # List of times the frame was drawn
        self.drawTimes2 = [] # List of times the frame was drawn
        self.drawTimes3 = [] # List of times the frame was drawn
        self.initGL()

    def setDuration(self,durationSec):
        self.durationSec = durationSec

    def setSpotOn(self,spotOn):
        self.spotOn = spotOn

    def registerDaq(self,daq):
        self.daq = daq

    def glut_idle(self): # only called if running in GLUT
        #global glut_window
        glFinish()
        curTimeAbs = getTime()
        curTime = curTimeAbs-self.startTimeAbs
        self.yrot = math.fmod(curTime*360.0/10.0,360.0)
        self.drawGLScene()
        if curTime > self.durationSec:
            graphicsClose() # XXX Wrong! I just want to stop glutMainLoop!
            #glutDestroyWindow(glut_window) # Doesn't stop glutMainLoop

    def glut_go(self):
        self.yrot = 0.0
        self.startTimeAbs = getTime()
        glutDisplayFunc(self.drawGLScene)
        glutIdleFunc(self.glut_idle)
        glutMainLoop()

    def go(self):
        self.startTimeAbs = getTime()
        curTimeAbs = getTime()
        curTime = curTimeAbs-self.startTimeAbs
        while(curTime <= self.durationSec):
            self.yrot = math.fmod(curTime*360.0/10.0,360.0)
            self.drawGLScene()
            curTimeAbs = getTime()
            curTime = curTimeAbs-self.startTimeAbs

    def drawGLScene(self):
    	"""Redraw the scene on every frame.
    
        Could put in C to run faster if needed.
        """
        global use_sdl
        glClear(GL_COLOR_BUFFER_BIT)
        glLoadIdentity()
        glTranslatef(0.0, 0.0, -6.0)
        glRotatef(self.yrot,0.0,1.0,0.0)
        glutSolidTeapot(1.0)
        if use_sdl:
            SDL_GL_SwapBuffers()
        else:
            glutSwapBuffers()

    def initGL(self):
        global screen_width,screen_height
        
        # Initialize OpenGL viewport
        glViewport(0,0,screen_width,screen_height)
        
        # Now setup projection
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()

        fovy = self.fovx / screen_width * screen_height
        gluPerspective(fovy,float(screen_width)/float(screen_height),0.1,100.0)
        glMatrixMode(GL_MODELVIEW)

        glClearColor(0.5, 0.5, 0.5, 0.0)

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
        
    def go_wrapper(self):
        global use_sdl
        if use_sdl:
            self.go()
        else:
            self.glut_go()

    def do_nothing(self):
        preciseSleep( 1000 )

    def stimulus_done(self):
        if use_sdl:
            pass
        else:
            glutIdleFunc(self.do_nothing)
            glutDisplayFunc(self.do_nothing)
        self.clearGL()
        self.frameStats()

    def clearGL(self):
        global screen_width,screen_height
        global use_sdl
        
        # Initialize OpenGL viewport
        glViewport(0,0,screen_width,screen_height)
        
        # Now setup projection
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()

        fovy = self.fovx / screen_width * screen_height
        gluPerspective(fovy,float(screen_width)/float(screen_height),0.1,100.0)
        glMatrixMode(GL_MODELVIEW)

        glClearColor(0.5, 0.5, 0.5, 0.0)
        glClear(GL_COLOR_BUFFER_BIT)
        if use_sdl:
            SDL_GL_SwapBuffers()
        else:
            glutSwapBuffers()
        
####################################################################
#
#        Stimulus - Spinning Drum
#
####################################################################

class SpinningDrum(Stimulus):
    def __init__(self,durationSec,texture,posDegFunc,contrastFunc,numSides=30,radius=3.0,fovx=45.0):
        self.tex = texture
        self.posFunc = posDegFunc
        self.cFunc = contrastFunc
        self.numSides = numSides
        self.radius = radius # in OpenGL (arbitrary) units
        circum = 2.0*math.pi*self.radius
        self.height = circum*float(self.tex.orig.size[1])/float(self.tex.orig.size[0])
        self.texId = texture.load()
        Stimulus.__init__(self,durationSec,fovx)

    def drawGLScene(self):
    	"""Redraw the scene on every frame.
    
        Could put in C to run faster if needed.
        """
        global use_sdl

        glClear(GL_COLOR_BUFFER_BIT)
        glLoadIdentity()

        glRotatef(self.yrot,0.0,1.0,0.0)
        glColor(0.5,0.5,0.5,self.contrast) # Fragment color
        glBindTexture(GL_TEXTURE_2D, self.texId)
        glCallList(self.displayListId)

        if self.spotOn: # draw fixation target
            glPushMatrix()
            glLoadIdentity()
            #glRotatef(90.0,0.0,1.0,0.0)
            glColor(1.0,1.0,1.0,1.0)
            glDisable(GL_TEXTURE_2D)
            glBegin(GL_QUADS)
            size = 0.0005
            glVertex3f(-size,-size,-0.1);
            glVertex3f( size,-size,-0.1);
            glVertex3f( size, size,-0.1);
            glVertex3f(-size, size,-0.1);
            glEnd() # GL_QUADS
            glEnable(GL_TEXTURE_2D)
            glPopMatrix()

        self.drawTimes.append(getTime())
        if use_sdl:
            SDL_GL_SwapBuffers()
        else:
            glutSwapBuffers()
        toggleDOut()
        glFinish() # Apparently this is not a given with double buffering
        self.drawTimes2.append(getTime())

    def initGL(self):
        global screen_width,screen_height
        
        # Initialize OpenGL viewport
        glViewport(0,0,screen_width,screen_height)
        
        # Now setup projection
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()

        fovy = self.fovx / screen_width * screen_height
        gluPerspective(fovy,float(screen_width)/float(screen_height),0.1,100.0)
        glMatrixMode(GL_MODELVIEW)

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

####################################################################
#
#        Graphics initialization
#
####################################################################            
            
def graphicsInit(width=640,height=480,fullscreen=1,realtime_priority=1,vsync=1,try_sdl=1):
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
