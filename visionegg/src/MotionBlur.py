# This is the python source code for the MotionBlur module of the Vision Egg package.
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

import math, cPickle

from VisionEgg import *
from imageConvolution import *

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

####################################################################
#
#        Everything needed to create a motion blurred drum
#
####################################################################

class ParamHolder: # dummy class to hold copy of params, basically plays role of C struct
        def __init__(self):
            pass

class BlurTextureFamily:
    def __init__(self,unblurred_filename,nominal_fps=180.0,maxSpeed=5000.0,numCachedTextures=10,cacheFunction='linear',blurKernel='boxcar'):
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
            use_cache = 0

        if use_cache:
            print "Found cache file '%s', loading images."%cache_filename
        else:
            print "Valid cache file '%s' not found, blurring images."%cache_filename

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

    def __init__(self,durationSec,unblurred_filename,posDegFunc,contrastFunc,numSides=30,radius=3.0,fovx=45.0,blur='gaussian',numCachedTextures=10,nominal_fps=180.0):
        self.texs = BlurTextureFamily(unblurred_filename,numCachedTextures=numCachedTextures)
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
