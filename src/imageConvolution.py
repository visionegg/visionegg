# This is the python source code for the imageConvolution module of the Vision Egg package.
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

import math, sys
import Image, ImageDraw
from Numeric import *
from MLab import *
from FFT import *

####################################################################
#
#        Math functions
#
####################################################################

def complex_abs(array):
    """Return an array with the magnitudes of an array of complex numbers"""
    return sqrt(array*conjugate(array)).real

####################################################################
#
#        Linear filter implementation
#
####################################################################

class Filter:
    """Base class for filters"""
    def __init__(self,unityGain=1):
        self.damn_close_to_zero = 1.0e-10
        self.unityGain = unityGain
        
    def get_data(self,width):
        if (width % 2) == 0: # normal case, even width
            x = arange(width,typecode='f')
            x[width/2:] = (x[width/2:]-width).astype('f') # XXX Posible error: may need to subtract (width+1) rather than just width
        else:
            raise NotImplementedError("Non-even widths not implemented yet.")
        data = self.kernelFunction(x)
        if data[width/2] > self.damn_close_to_zero:
            print data[width/2]
            raise RuntimeError("Filter kernel too wide!")
        if self.unityGain:
            data = data / sum(data)
        return data

    def kernelFunction(self,x):
        return equal(x,0).astype('f')

class GaussianFilter(Filter):
    def __init__(self,sigma,unityGain=1):
        Filter.__init__(self,unityGain)
        if sigma < 0.8:
            print "WARNING: Convolving with a Gaussian of radius", sigma
            print "(Anything less than 0.8 results in sampling error!)"
        self.sigma = float(sigma)

    def kernelFunction(self,x):
        tmp = -(x*x)/(self.sigma*self.sigma)
        try:
            result = exp(tmp)
        except OverflowError: # Numeric gets a math range error sometimes
            result = zeros(tmp.shape).astype('f')
            for i in range(result.shape[0]):
                result[i] = math.exp(tmp[i])
        return result
                
class BoxcarFilter(Filter):
    def __init__(self,radius,unityGain=1):
        Filter.__init__(self,unityGain)
        self.radius = float(radius)

    def kernelFunction(self,x):
        #return less_equal(abx(x),self.radius).astype('f')
        return less_equal(x*x,self.radius*self.radius).astype('f') # quicker than above, same result

####################################################################
#
#        Convolution implementation
#
####################################################################

def convolveImageHoriz(image,filter,edgeMethod='wrap'):
    if edgeMethod != 'wrap':
        raise NotImplementedError("convolveImageHoriz only does wrap-around convolutions.")
    if image.mode != 'RGB' and image.mode != 'L':
        raise NotImplementedError("convolveImageHoriz can only handle 'RGB' and 'L' mode images.")
    
    data = array(image.getdata())
    if len(image.getbands()) == 1: # luminance only
        data.shape = (image.size[1],image.size[0],1)
    else: # RGB
        data.shape = (image.size[1],image.size[0],3)
    height,width = data.shape[:2] 
    data = data.astype('f')
    data = data / 255.0
    
    fft_width = width

    filter_f = fft(filter.get_data(fft_width))
    
    for color_index in range(data.shape[2]):
        for row in range(data.shape[0]):
            row_f = fft(data[row,:,color_index],fft_width)
            conv_f = filter_f * row_f
            data[row,:,color_index] = complex_abs(inverse_fft(conv_f))

    data = data * 255.0
    data = data.astype('b')
    if data.shape[2] == 3:
        mode = rawmode = 'RGB'
        bits = data.tostring()
    else:
        mode = rawmode = 'L'
        bits = data.tostring()

    out = Image.fromstring(mode,(width,height), bits, "raw", rawmode)
    
    return out
    
if __name__ == '__main__':
    # Create a test image
    im = Image.new("RGB",(128,128),(0,0,255))
    #im = Image.new("L",(128,128),0)
    draw = ImageDraw.Draw(im)
    draw.line((0,0) + im.size)
    draw.line((0,im.size[1],im.size[0],0))
    draw.line((im.size[0],im.size[1],im.size[0],0))
    draw.line((im.size[0]-1,im.size[1],im.size[0]-1,0))
    draw.ellipse((5,0)+(10,10))
    del draw

    # Create a filter
    #f = BoxcarFilter(1.0,unityGain=0)

    try:
        sigma = float(sys.argv[1])
    except:
        sigma = 1.5
        print "Usage: imageConvolution.py [sigma]\n(Or use it as a python module!)"
    f = GaussianFilter(sigma)

    # save the original
    im.save("orig.ppm")

    # Now blur the image with the filter!
    blurred = convolveImageHoriz(im,f)

    # save the blurred image
    blurred.save("blurred.ppm")
