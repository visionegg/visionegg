# This is the python source code for the primary module of the Vision Egg package.
#
#
import string
__version__ = string.split('$Revision$')[1]
__date__ = string.join(string.split('$Date$')[1:3], ' ')
__author__ = 'Andrew Straw <astraw@users.sourceforge.net>'

import os, math, cPickle # standard python packages
import Image, ImageDraw # Python Imaging Library packages
from OpenGL.GL import * # PyOpenGL packages
from OpenGL.GL.ARB.texture_env_combine import * # this is needed to do contrast
from OpenGL.GL.ARB.texture_compression import *
from OpenGL.GLU import *
from OpenGL.GLUT import *
from Numeric import * # Numeric Python packages
from MLab import *
global use_sdl
try:
    from SDL import * # This is really VisionEgg.SDL (Why doesn't "from VisionEgg.SDL import *" work?)
    use_sdl = 1
except:
    print "WARNING: python module SDL not found.  Performance and features may be affected."
    use_sdl = 0
from _visionegg import * # internal C code
from imageConvolution import *

class EggError(Exception):
    def __init__(self,str):
        Exception.__init__(self,str)

class Daq:
    def __init__(self,device,channelParamList,triggerMethod):
        pass

class TextureBuffer:
    """Raw texture buffer to load to OpenGL with glTexImage2D.

    Lengths of sides should be a power of 2."""
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
#            gluBuild2DMipmaps(GL_TEXTURE_2D, GL_RGB,
#                              self.im.size[0], self.im.size[1],GL_RGB,
#                              GL_UNSIGNED_BYTE,self.im.tostring("raw","RGB"))#,0,-1))
            glTexImage2D(GL_TEXTURE_2D, # target
                         0, # level
#                         GL_RGB, # internal format
                         GL_COMPRESSED_RGB_ARB, # internal format
                         self.im.size[0], # width
                         self.im.size[1], # height
                         0, # border
                         GL_RGB, # format
                         GL_UNSIGNED_BYTE, # type
                         self.im.tostring("raw","RGB"))#,0,-1))
#        elif self.im.mode == "RGBA":
#            glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA,
#                         self.im.size[0], self.im.size[1],
#                         0,GL_RGBX, GL_UNSIGNED_BYTE,self.im.tostring("raw","RGBA"))#,0,-1))
        else:
            raise EggError("Unknown image mode '%s'"%(self.im.mode,))
        return self.gl_id

class Texture:
    def __init__(self,size=(128,128)):
        if 'orig' not in dir(self): # The image is not already defined.
            # Create a default texture
            self.orig = Image.new("RGB",size,(0,0,255))
            draw = ImageDraw.Draw(self.orig)
            draw.line((0,0) + self.orig.size, fill=(255,255,255))
            draw.line((0,self.orig.size[1],self.orig.size[0],0), fill=(255,255,255))
            #draw.text((0,0),"Default texture")

    def load(self,minFilter=GL_LINEAR,magFilter=GL_LINEAR):
        # Someday put all this in a texture buffer manager.
        # The buffer manager will keep track of which
        # buffers are loaded.  It will associate images
        # with power of 2 buffers.
        
        # Create a buffer whose sides are a power of 2
        width_pow2  = int(pow(2.0,math.ceil(self.log2(float(self.orig.size[0])))))
        height_pow2 = int(pow(2.0,math.ceil(self.log2(float(self.orig.size[0])))))
        
        self.buf = TextureBuffer( (width_pow2, height_pow2) )
        self.buf.im.paste(self.orig,(0,0,self.orig.size[0],self.orig.size[1]))

        # location of myself in the buffer, in pixels
        self.buf_l = 0
        self.buf_r = self.orig.size[0]
        self.buf_t = 0
        self.buf_b = self.orig.size[1]
        
        # location of myself in the buffer, in fraction
        self.buf_lf = 0.0
        self.buf_rf = float(self.orig.size[0])/float(self.buf.im.size[0])
        self.buf_tf = 0.0
        self.buf_bf = float(self.orig.size[1])/float(self.buf.im.size[1])

        return self.buf.load(minFilter,magFilter) # return the OpenGL ID

    def log2(self,f):
        return math.log(f)/math.log(2)

class TextureFromFile(Texture):
    def __init__(self,filename):
        self.orig = Image.open(filename)
        Texture.__init__(self,self.orig.size)

class TextureFromPILImage(Texture):
    def __init__(self,image):
        self.orig = image
        Texture.__init__(self,self.orig.size)

class Stimulus:
    def __init__(self,durationSec=1.0,fovx=45.0):
        self.durationSec = durationSec
        self.fovx = fovx
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
        
class SpinningDrum(Stimulus):
    def __init__(self,durationSec,texture,posDegFunc,contrastFunc,numSides=30,radius=3.0,fovx=45.0):
        self.tex = texture
        self.posFunc = posDegFunc
        self.cFunc = contrastFunc
        self.numSides = numSides
        self.radius = radius # in OpenGL (arbitrary) units
        circum = 2.0*math.pi*self.radius
        self.height = circum*float(self.tex.orig.size[1])/float(self.tex.orig.size[0])
        #self.height = self.radius*float(self.tex.orig.size[1])/float(self.tex.orig.size[0])
        #print "self.height = ", self.height
        self.texId = texture.load()
        print "SpinningDrum loaded texture"
        Stimulus.__init__(self,durationSec,fovx)

    def glut_idle(self): # only called if running in GLUT
        #global glut_window
        curTimeAbs = getTime()
        curTime = curTimeAbs-self.startTimeAbs
        self.contrast = self.cFunc(curTime)
        self.yrot = self.posFunc(curTime)
        self.drawGLScene()
        if curTime > self.durationSec:
            self.stimulus_done()
            #graphicsClose() # XXX Wrong! I just want to stop glutMainLoop!
            #glutDestroyWindow(glut_window) # doesn't quit glutMainLoop

    def glut_go(self): # only called if running in GLUT
        self.startTimeAbs = getTime()
        glutIdleFunc(self.glut_idle)
        self.glut_idle() # set self.contrast and self.yrot
        glutDisplayFunc(self.drawGLScene)
        glutMainLoop()
        
    def go(self):
        """Could put in C to run faster.

        Bare bones timing routines.
        """
        startTimeAbs = getTime()
        curTimeAbs = startTimeAbs
        self.startTimeAbs = startTimeAbs
        curTime = curTimeAbs-startTimeAbs
        lastTime = curTime
        while (curTime <= self.durationSec):
            self.contrast = self.cFunc(curTime)
            self.yrot = self.posFunc(curTime)
            self.drawGLScene()
            curTimeAbs = getTime()
            curTime = curTimeAbs-startTimeAbs
            lastTime = curTime
        self.stimulus_done()

    def go2(self):
        """Could put in C to run faster.

        Timing routines to supposedly incorporate frame draw latencies, etc.
        """
        fps = 180 # guess
        startTimeAbs = getTime()
        curTimeAbs = getTime()
        curTime = curTimeAbs-startTimeAbs
        while (curTime <= self.durationSec):
            curTimeAbs = getTime()
            curTime = curTimeAbs-startTimeAbs

            nextFrameTime = curTime+2.7e-6 # seconds to next frame if no discrete update
            nextFrameNum = math.ceil(nextFrameTime * fps)
            realNextFrameTime = nextFrameNum / fps
            
            self.contrast = self.cFunc(realNextFrameTime)
            self.yrot = self.posFunc(realNextFrameTime)
            
            self.drawGLScene()
            curTime2Abs = getTime()
            curTime2 = curTime2Abs-startTimeAbs
            #print "drawGLScene took %g usec."%( (curTime2-curTime)*1.0e6,)
        self.stimulus_done()

    def go3(self):
        """Could put in C to run faster.

        Timing routines to supposedly incorporate frame draw latencies, etc.
        """
        fps = 180 # guess
        spf = 1.0/180.0 # seconds per frame
        frameTimes = arange(0.0,float(self.durationSec),spf) # array of frame times
        frameTimes = frameTimes+spf
        col2 = []
        col1 = []
        #sleeps = []
        i=0
        
        startTimeAbs = getTime()
        curTimeAbs = getTime()
        curTime = curTimeAbs-startTimeAbs
        
        while (i < len(frameTimes)):
#        while (curTime <= self.durationSec):
            
            curTimeAbs = getTime()
            curTime = curTimeAbs-startTimeAbs

            col1.append( curTime )

            #curFrameFrac = curTime * fps
            #fracs.append( math.fmod(curFrameFrac,1.0) )
            #nextFrame = math.ceil(curFrameFrac) 
            #nextTime = nextFrame / fps
            nextTime = frameTimes[i]
            i=i+1
            col2.append( nextTime )
            self.contrast = self.cFunc(nextTime)
            self.yrot = self.posFunc(nextTime)
            
            self.drawGLScene()
            curTime2Abs = getTime()
            curTime2 = curTime2Abs-startTimeAbs
            #print "pyDrawScene took %g usec."%( (curTime2-curTime)*1.0e6,)

            # now sleep until the vertical retrace is actually started and
            # we can draw on the back buffer the next frame
            if curTime2 < nextTime:
                #preciseSleep( 100 )
                curTime2Abs = getTime()
                curTime2 = curTime2Abs-startTimeAbs

        self.stimulus_done()
        for i in range(len(col2)):
            print "%f %f"%(col1[i],col2[i])

    def drawGLScene(self):
        """Could put in C to run faster.
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
        # build the display list
        self.displayListId = glGenLists(1)
        deltaTheta = 2.0*math.pi/numSides
        glNewList(self.displayListId,GL_COMPILE)
        glBegin(GL_QUADS)
        for i in range(numSides):
            theta1 = i*deltaTheta
            theta2 = (i+1)*deltaTheta
            frac1 = (self.tex.buf_l + (float(i)/numSides*self.tex.orig.size[0]))/float(self.tex.buf.im.size[0])
            frac2 = (self.tex.buf_l + (float(i+1)/numSides*self.tex.orig.size[0]))/float(self.tex.buf.im.size[0])
            
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
        
class ParamHolder: # dummy class to hold copy of params, basically plays role of C struct
        def __init__(self):
            pass

class BlurTextureFamily:
    def __init__(self,unblurred_filename,nominal_fps=180.0,maxSpeed=5000.0,numCachedTextures=27,cacheFunction='linear',blurKernel='boxcar'):
        self.p = ParamHolder()
        # Compute blur family parameters
        self.p.orig_name = unblurred_filename
        self.orig = Image.open(self.p.orig_name)
        self.p.im_width = self.orig.size[0]
        self.p.nominal_fps = nominal_fps
        self.p.sec_per_frame = 1.0/self.p.nominal_fps
        self.p.maxSpeed = maxSpeed # dps
        self.p.numCachedTextures = numCachedTextures
        self.p.blurKernel = blurKernel
        self.p.cacheFunction = cacheFunction

        # calculate speedList based on parameters
        self.p.speedList = self.computeSpeedList(self.p)

        # nothing is loaded into OpenGL yet
        self.texGLIdList = []
        self.texGLSpeedsDps = zeros((0,)) # empty array

        #now load images into OpenGL
        self.loadToGL(self.p)
        
    def computeSpeedList(self,p):
        if p.cacheFunction == 'linear':
            dpsSpeedList = arange(0.0,p.maxSpeed,p.maxSpeed/p.numCachedTextures) # dps
        elif p.cacheFunction == 'exp': # exponentially increasing speed look up table
            dpsSpeedList = arange(float(p.numCachedTextures))/float(p.numCachedTextures)
            logmax = math.log(p.maxSpeed)
            dpsSpeedList = dpsSpeedList*logmax
            dpsSpeedList = exp(dpsSpeedList)
        elif p.cacheFunction == 'hand_picked1':
            pixSpeedList = array([0.0, 10.0, 20.0])
            dpsSpeedList = pixSpeedList / float(p.im_width)*360.0 / p.sec_per_frame
        elif p.cacheFunction == 'hand_picked2':
            dpsSpeedList = array([0.0, 250.0, 500.0, 1000.0, 1500.0])
        else:
            raise RuntimeError("Unknown cacheFunction '%s'"%(p.cacheFunction,))
        
        pixSpeedList = dpsSpeedList * float(p.im_width)/360.0 * p.sec_per_frame
        speedList = []
        for i in range(dpsSpeedList.shape[0]):
            speedList.append( (dpsSpeedList[i], pixSpeedList[i]) )
            print "%10f degrees per sec\t==\t%10f pixels"%(dpsSpeedList[i],pixSpeedList[i])
        return speedList

    def loadToGL(self,p,cache_filename="blur_params.pickle"):
        # clear OpenGL if needed
        if (len(self.texGLIdList) != 0) or (self.texGLSpeedsDps.shape[0] != 0):
            raise NotImplemetedError("No code yet to clear textures out of OpenGL")
        else:
            self.texGLSpeedsDps = [] # make this a list for now, convert to Numeric array later
        
        # check to see if this family has already been computed and is cached
        use_cache = 1
        try:
            f = open(cache_filename,"rb")
            cached_p = cPickle.load(f)
            for attr in dir(p):
                val = getattr(p,attr)
                try:
                    cached_val = getattr(cached_p,attr)
                    if val != cached_val: # Attributes not the same, don't use cache
                        use_cache = 0
                        break
                except: # Attribute not in cached version, don't use cache
                    use_cache = 0
                    break 
        except (IOError, EOFError):
            print "Valid cache file not found"
            use_cache = 0

        # compute (or load) the blurred images, load into OpenGL
        if use_cache:
            p = cached_p
        else:
            p.filenames = [ p.orig_name ] # initialize list
            new_cache_valid = 1 # will set to 0 if something goes wrong, otherwise save the new cache params

        # Load original image first
        tex = TextureFromPILImage( self.orig )
        self.texGLIdList.append( tex.load() ) # create OpenGL texture object
        self.texGLSpeedsDps.append( 0.0 ) # lower bound of speed this texture is used for

        for i in range(1,len(p.speedList)): # index zero is unblurred image, which we don't need to blur!
            (deg_per_sec, pix_per_frame) = p.speedList[i]
            if not use_cache:
                if p.blurKernel == 'gaussian':
                    filter = GaussianFilter(pix_per_frame/10.0)
                elif p.blurKernel == 'boxcar':
                    filter = BoxcarFilter(pix_per_frame)
                else:
                    raise RuntimeError("Filter type '%s' not implemented"%(p.blurKernel,))
                blurred = convolveImageHoriz(self.orig,filter)
                filename = "blur_cache%02d.ppm"%(i,)
                try:
                    blurred.save(filename)
                    p.filenames.append(filename)
                    print "Saved '%s' (blurred for %f pixels per frame)"%(filename,pix_per_frame)
                except:
                    new_cache_valid = 0
                    print "Failed to save '%s'"%(filename)
            else: # use cache
                filename = p.filenames[i]
                print "Loading '%s' (blurred for %f pixels per frame)"%(filename,pix_per_frame)
                blurred = Image.open(filename)
            tex = TextureFromPILImage( blurred )
            self.texGLIdList.append( tex.load() ) # create OpenGL texture object
            self.texGLSpeedsDps.append( deg_per_sec ) # lower bound of speed this texture is used for
            
        self.texGLSpeedsDps = array(self.texGLSpeedsDps) # convert back to Numeric array type

        # save our cache parameters if we re-made the cache
        if not use_cache: # save our new cache parameters
            if new_cache_valid:
                try:
                    f = open(cache_filename,"wb")
                    cPickle.dump(p,f)
                except IOError:
                    print "Failed to save cache parameters is '%s'"%(cache_filename,)
                    
class BlurredDrum(SpinningDrum):
    def __init__(self,durationSec,unblurred_filename,posDegFunc,contrastFunc,numSides=30,radius=3.0,fovx=45.0,blur='gaussian',nominal_fps=180.0):
        self.texs = BlurTextureFamily(unblurred_filename)
        self.blurOn = 1
        SpinningDrum.__init__(self,durationSec,TextureFromPILImage(self.texs.orig),posDegFunc,contrastFunc,numSides,radius,fovx) # XXX should change so it doesn't load base texture again

    def setBlurOn(self,on):
        self.blurOn = on
        
    def glut_idle(self): # only called if running in GLUT
        #global glut_window
        glFinish()
        curTimeAbs = getTime() # do this first
        lastTime = self.curTime # even though it's confusing between these two instructions, this must be done now
        self.curTime = curTimeAbs-self.startTimeAbs
        lastyrot = self.yrot

        self.contrast = self.cFunc(self.curTime)
        self.yrot = self.posFunc(self.curTime)

        delta_pos = self.yrot - lastyrot # degrees
        delta_t = self.curTime - lastTime # seconds

        self.texId = self.getTexId(delta_pos,delta_t)
        
        self.drawGLScene()
        if self.curTime > self.durationSec:
            self.stimulus_done()
            #graphicsClose() # XXX Wrong! I just want to stop glutMainLoop!
            #glutDestroyWindow(glut_window) # doesn't quit glutMainLoop

    def glut_go(self): # only called if running in GLUT
        self.startTimeAbs = getTime()
        self.curTime = self.startTimeAbs
        self.yrot = self.posFunc(0.0)
        glutIdleFunc(self.glut_idle)
        self.glut_idle() # set self.contrast and self.yrot
        glutDisplayFunc(self.drawGLScene)
        glutMainLoop()
        
    def go(self):
        """Could put in C to run faster.

        Bare bones timing routines.
        """
        startTimeAbs = getTime()
        self.curTime = 0.0
        self.yrot = self.posFunc(self.curTime)
        lastyrot = self.yrot
        lastTime = self.curTime
        while (self.curTime <= self.durationSec):
            self.contrast = self.cFunc(self.curTime)
            self.yrot = self.posFunc(self.curTime)

            delta_pos = self.yrot - lastyrot
            delta_t = self.curTime - lastTime

            lastTime = self.curTime

            self.drawTimes3.append(getTime())
            self.texId = self.getTexId(delta_pos,delta_t)
            
            lastyrot = self.yrot
            self.drawGLScene()
            curTimeAbs = getTime()
            self.curTime = curTimeAbs-startTimeAbs
        self.stimulus_done()

    def getTexId(self,delta_pos,delta_t):
        if delta_t < 1.0e-6: # less than 1 microsecond (this should be less than a frame could possibly take to draw
            vel_dps = 0
            speedIndex = 0
        else:
            vel_dps = delta_pos/delta_t
            # Get the highest cached velocity less than or equal to the current velocity
            speedIndex = nonzero(less_equal(self.texs.texGLSpeedsDps,abs(vel_dps)))[-1]
        if not self.blurOn: # In case motion blur is turned off
            speedIndex = 0
        #print "%f: %f dps - %d"%(self.curTime,vel_dps,self.texs.texGLIdList[speedIndex])
        #resident = glAreTexturesResident(self.texs.texGLIdList)
        #print self.texs.texGLIdList
        #print resident
        return self.texs.texGLIdList[speedIndex]
    
def graphicsInit(width=640,height=480,fullscreen=1,realtime_priority=1,vsync=1,try_sdl=1):
    global use_sdl
    global glut_window
    global screen_width,screen_height

    screen_width = width
    screen_height = height
    # This works for nVidia drivers on linux
    if vsync:
        os.environ["__GL_SYNC_TO_VBLANK"] = "1"

    if realtime_priority:
        setRealtime()

    if not try_sdl:
        use_sdl = 0

    caption = "EGG"

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

def graphicsClose():
    global use_sdl
    if use_sdl:
        SDL_ShowCursor(SDL_ENABLE)
        SDL_Quit()
    sys.exit() # Shouldn't do this, but it's the only way I know to quit glutMainLoop
