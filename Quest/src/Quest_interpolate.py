#!/usr/bin/env python

# The guts of this file were extracted from scipy by Andrew D. Straw
# in 2004 for distribution with the Quest.py module.

# Copyright (c) 2001, 2002 Enthought, Inc.
# Copyright (c) 2004 Andrew D. Straw
#
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
#   a. Redistributions of source code must retain the above copyright notice,
#      this list of conditions and the following disclaimer.
#   b. Redistributions in binary form must reproduce the above copyright
#      notice, this list of conditions and the following disclaimer in the
#      documentation and/or other materials provided with the distribution.
#   c. Neither the name of the Enthought nor the names of its contributors
#      may be used to endorse or promote products derived from this software
#      without specific prior written permission.
#
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED. IN NO EVENT SHALL THE REGENTS OR CONTRIBUTORS BE LIABLE FOR
# ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
# DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
# SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
# CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT
# LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY
# OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH
# DAMAGE.

__all__ = ['interp1d']

from numarray import array, shape, swapaxes, asarray, less, greater, \
     sometrue, logical_or, searchsorted, clip, Int, take, ones, \
     putmask
from numarray.ieeespecial import nan

def atleast_1d(*arys):
    """ Force a sequence of arrays to each be at least 1D.

         Description:
            Force an array to be at least 1D.  If an array is 0D, the 
            array is converted to a single row of values.  Otherwise,
            the array is unaltered.
         Arguments:
            *arys -- arrays to be converted to 1 or more dimensional array.
         Returns:
            input array converted to at least 1D array.
    """
    res = []
    for ary in arys:
        ary = asarray(ary)
        if len(ary.shape) == 0:
            result = array([ary[0]])
        else:
            result = ary
        res.append(result)
    if len(res) == 1:
        return res[0]
    else:
        return res

class interp1d:
    interp_axis = -1 # used to set which is default interpolation
                     # axis.  DO NOT CHANGE OR CODE WILL BREAK.
                     
    def __init__(self,x,y,kind='linear',axis = -1,
                 copy = 1,bounds_error=1, fill_value=None):
        """Initialize a 1d linear interpolation class

        Description:
          x and y are arrays of values used to approximate some function f:
            y = f(x)
          This class returns a function whose call method uses linear
          interpolation to find the value of new points.

        Inputs:
            x -- a 1d array of monotonically increasing real values.
                 x cannot include duplicate values. (otherwise f is
                 overspecified)
            y -- an nd array of real values.  y's length along the
                 interpolation axis must be equal to the length
                 of x.
            kind -- specify the kind of interpolation: 'nearest', 'linear',
                    'cubic', or 'spline'
            axis -- specifies the axis of y along which to 
                    interpolate. Interpolation defaults to the last
                    axis of y.  (default: -1)
            copy -- If 1, the class makes internal copies of x and y.
                    If 0, references to x and y are used. The default 
                    is to copy. (default: 1)
            bounds_error -- If 1, an error is thrown any time interpolation
                            is attempted on a value outside of the range
                            of x (where extrapolation is necessary).
                            If 0, out of bounds values are assigned the
                            NaN (#INF) value.  By default, an error is
                            raised, although this is prone to change.
                            (default: 1)
        """      
        self.axis = axis
        self.copy = copy
        self.bounds_error = bounds_error
        if fill_value is None:
            self.fill_value = nan
        else:
            self.fill_value = fill_value

        if kind != 'linear':
            raise NotImplementedError, "Only linear supported for now. Use fitpack routines for other types."
        
        # Check that both x and y are at least 1 dimensional.    
        if len(shape(x)) == 0 or len(shape(y)) == 0:
            raise ValueError, "x and y arrays must have at least one dimension."  
        # make a "view" of the y array that is rotated to the
        # interpolation axis.  
        oriented_x = x
        oriented_y = swapaxes(y,self.interp_axis,axis)            
        interp_axis = self.interp_axis        
        len_x,len_y = shape(oriented_x)[interp_axis], shape(oriented_y)[interp_axis]
        if len_x != len_y:
            raise ValueError, "x and y arrays must be equal in length along "\
                              "interpolation axis."
        if len_x < 2 or len_y < 2:
            raise ValueError, "x and y arrays must have more than 1 entry"            
        self.x = array(oriented_x,copy=self.copy)
        self.y = array(oriented_y,copy=self.copy)       
        
    def __call__(self,x_new):
        """Find linearly interpolated y_new = <name>(x_new).

        Inputs:        
          x_new -- New independent variables.

        Outputs:
          y_new -- Linearly interpolated values corresponding to x_new.
        """
        # 1. Handle values in x_new that are outside of x.  Throw error,
        #    or return a list of mask array indicating the outofbounds values.
        #    The behavior is set by the bounds_error variable.
        x_new = atleast_1d(x_new)
        out_of_bounds = self._check_bounds(x_new)
        # 2. Find where in the orignal data, the values to interpolate
        #    would be inserted.  
        #    Note: If x_new[n] = x[m], then m is returned by searchsorted.
        x_new_indices = searchsorted(self.x,x_new)
        # 3. Clip x_new_indices so that they are within the range of 
        #    self.x indices and at least 1.  Removes mis-interpolation
        #    of x_new[n] = x[0] 
        x_new_indices = clip(x_new_indices,1,len(self.x)-1).astype(Int)
        # 4. Calculate the slope of regions that each x_new value falls in.
        lo = x_new_indices - 1; hi = x_new_indices        
        
        # !! take() should default to the last axis (IMHO) and remove
        # !! the extra argument.
        x_lo = take(self.x,lo,axis=self.interp_axis)
        x_hi = take(self.x,hi,axis=self.interp_axis);
        y_lo = take(self.y,lo,axis=self.interp_axis)
        y_hi = take(self.y,hi,axis=self.interp_axis);
        slope = (y_hi-y_lo)/(x_hi-x_lo)
        # 5. Calculate the actual value for each entry in x_new.
        y_new = slope*(x_new-x_lo) + y_lo 
        # 6. Fill any values that were out of bounds with NaN
        # !! Need to think about how to do this efficiently for 
        # !! mutli-dimensional Cases.
        yshape = y_new.shape
        y_new = y_new.flat
        new_shape = list(yshape)
        new_shape[self.interp_axis] = 1
        sec_shape = [1]*len(new_shape)
        sec_shape[self.interp_axis] = len(out_of_bounds)
        out_of_bounds.shape = sec_shape
        new_out = ones(new_shape)*out_of_bounds
        putmask(y_new, new_out.flat, self.fill_value)
        y_new.shape = yshape      
        # Rotate the values of y_new back so that they coorespond to the
        # correct x_new values.
        result = swapaxes(y_new,self.interp_axis,self.axis)
        try:
            len(x_new)
            return result
        except TypeError:
            return result[0]
        return result
    
    def _check_bounds(self,x_new):
        # If self.bounds_error = 1, we raise an error if any x_new values
        # fall outside the range of x.  Otherwise, we return an array indicating
        # which values are outside the boundary region.  
        # !! Needs some work for multi-dimensional x !!
        below_bounds = less(x_new,self.x[0])
        above_bounds = greater(x_new,self.x[-1])
        #  Note: sometrue has been redefined to handle length 0 arrays
        # !! Could provide more information about which values are out of bounds
        if self.bounds_error and sometrue(below_bounds):
            raise ValueError, " A value in x_new is below the"\
                              " interpolation range."
        if self.bounds_error and sometrue(above_bounds):
            raise ValueError, " A value in x_new is above the"\
                              " interpolation range."
        # !! Should we emit a warning if some values are out of bounds.
        # !! matlab does not.
        out_of_bounds = logical_or(below_bounds,above_bounds)
        return out_of_bounds
       
    def model_error(self,x_new,y_new):
        # How well do x_new,yy points fit the model?
        # Return an array of error values.
        pass

def test():
    i=interp1d(array([1.0,2,3]),array([4.0,5,6]))
    result = i(array([1.5,2.5]))
    print result
    result = i(array([1.5]))
    print result

if __name__ == '__main__':
    test()
