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
#from OpenGL.GL.ARB.texture_env_combine import * #   this is needed to do contrast
#from OpenGL.GL.ARB.texture_compression import * #   can use this to fit more textures in memory
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
    def __init__(self,unblurred_filename,target_fps=180.0,maxSpeed=2000.0,numCachedTextures=10,cacheFunction='linear',blurKernel='boxcar'):
        self.p = ParamHolder()
        # Compute blur family parameters
        self.p.orig_name = unblurred_filename
        self.orig = Image.open(self.p.orig_name)
        self.p.im_width = self.orig.size[0]
        self.p.target_fps = target_fps
        self.p.sec_per_frame = 1.0/self.p.target_fps
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
                    print "Saved '%s' (blurred for %.1f degrees per second, %.2f pixels per frame)"%(filename,deg_per_sec,pix_per_frame)
                except:
                    new_cache_valid = 0
                    print "Failed to save '%s'"%(filename)
            else: # use cache
                filename = p.filenames[i]
                print "Loading '%s' (blurred for %.1f degrees per second, %.2f pixels per frame)"%(filename,deg_per_sec,pix_per_frame)
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

    def __init__(self,durationSec,unblurred_filename,position_function,contrast_function,numSides=30,radius=3.0,blur='gaussian',numCachedTextures=10,target_fps=180.0,maxSpeed=2000.0,projection=PerspectiveProjection()):
        self.texs = BlurTextureFamily(unblurred_filename,numCachedTextures=numCachedTextures,maxSpeed=maxSpeed,target_fps=target_fps)
        self.blurOn = 1
        self.last_time = 0.0
        self.last_yrot = position_function(self.last_time)
        SpinningDrum.__init__(self,durationSec,TextureFromPILImage(self.texs.orig),position_function,contrast_function,numSides,radius,projection) # XXX should change so it doesn't load base texture again

    def setBlurOn(self,on):
        self.blurOn = on
        
    def getTexId(self,delta_pos,delta_t):
        if self.blurOn: # Find the appropriate texture
            if delta_t < 1.0e-6: # less than 1 microsecond (this should be less than a frame could possibly take to draw)
                vel_dps = 0
                speedIndex = 0
            else:
                vel_dps = delta_pos/delta_t
                # Get the highest cached velocity less than or equal to the current velocity
                speedIndex = nonzero(less_equal(self.texs.texGLSpeedsDps,abs(vel_dps)))[-1]
        else: # In case motion blur is turned off
            speedIndex = 0
        return self.texs.texGLIdList[speedIndex]

    def drawGLScene(self):

        # I know that self.cur_time has been set for me.
        # Calculate my other variables from that.
        
        #self.contrast = self.cFunc(self.curTime) # Let SpinningDrum do this
        self.yrot = self.position_function(self.cur_time)

        delta_yrot = self.yrot - self.last_yrot # change in position (units: degrees)
        delta_t = self.cur_time - self.last_time

        self.texId = self.getTexId(delta_yrot,delta_t) # sets the texture object that SpinningDrum uses
        SpinningDrum.drawGLScene(self) # call my base class to do most of the work
        
        # Set for next cycle
        self.last_time = self.cur_time
        self.last_yrot = self.yrot
