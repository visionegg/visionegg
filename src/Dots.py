"""Random dot stimuli"""

# Copyright (c) 2003 Andrew Straw.  Distributed under the terms
# of the GNU Lesser General Public License (LGPL).

all = ['DotArea2D', 'draw_dots',]

####################################################################
#
#        Import all the necessary packages
#
####################################################################

import VisionEgg
import VisionEgg.Core
import VisionEgg.ParameterTypes as ve_types

import Numeric, RandomArray
import math, types, string

import VisionEgg.GL as gl # get all OpenGL stuff in one namespace

##try:
##    import VisionEgg._draw_in_c
##    draw_dots = VisionEgg._draw_in_c.draw_dots # draw in C for speed
##except ImportError, x:
##    VisionEgg.Core.message.add("Could not import VisionEgg._draw_in_c module, dots will be drawn in Python.",
##                               level=VisionEgg.Core.Message.WARNING)
##    def draw_dots(xs,ys,zs):
##        """Python method for drawing dots.  Slower than C version"""
##        if not (len(xs) == len(ys) == len(zs)):
##            raise ValueError("All input arguments must be same length")
##        gl.glBegin(gl.GL_POINTS)
##        for i in xrange(len(xs)):
##            gl.glVertex3f(xs[i],ys[i],zs[i])
##        gl.glEnd()

def draw_dots(xs,ys,zs):
    """Python method for drawing dots.  May be replaced by a faster C version."""
    if not (len(xs) == len(ys) == len(zs)):
        raise ValueError("All input arguments must be same length")
    gl.glBegin(gl.GL_POINTS)
    for i in xrange(len(xs)):
        gl.glVertex3f(xs[i],ys[i],zs[i])
    gl.glEnd()
        
__version__ = VisionEgg.release_name
__cvs__ = string.split('$Revision$')[1]
__date__ = string.join(string.split('$Date$')[1:3], ' ')
__author__ = 'Andrew Straw <astraw@users.sourceforge.net>'

# Use Python's bool constants if available, make aliases if not
try:
    True
except NameError:
    True = 1==1
    False = 1==0

class DotArea2D(VisionEgg.Core.Stimulus):
    """Random dots of constant velocity

    Every dot has the same velocity. Some fraction of the dots all
    move in the one direction, while the rest move in random
    directions. Dots wrap around edges. Each dot has a lifespan.
    """
    
    parameters_and_defaults = {
        'on' : ( True,
                 ve_types.Boolean ),
        'position' : ( ( 320.0, 240.0 ), # in eye coordinates
                       ve_types.Sequence2(ve_types.Real) ),
        'anchor' : ('center',
                    ve_types.String),
        'size' :   ( ( 300.0, 300.0 ), # in eye coordinates
                     ve_types.Sequence2(ve_types.Real) ),
        'signal_fraction' : ( 0.5,
                              ve_types.Real ),
        'signal_direction_deg' : ( 90.0,
                                   ve_types.Real ),
        'velocity_pixels_per_sec' : ( 10.0,
                                      ve_types.Real ),
        'dot_lifespan_sec' : ( 5.0,
                               ve_types.Real ),
        'color' : ((1.0,1.0,1.0),
                   ve_types.AnyOf(ve_types.Sequence3(ve_types.Real),
                                  ve_types.Sequence4(ve_types.Real))),
        'dot_size' : (4.0, # pixels
                      ve_types.Real),
        'anti_aliasing' : ( True,
                            ve_types.Boolean ),
        'depth' : ( None, # set for depth testing
                    ve_types.Real ),
        'center' : (None,  # DEPRECATED -- don't use
                    ve_types.Sequence2(ve_types.Real)),        
        }
    
    constant_parameters_and_defaults = {
        'num_dots' : ( 100,
                       ve_types.UnsignedInteger ),
        }

    __slots__ = VisionEgg.Core.Stimulus.__slots__ + (
        'x_positions',
        'y_positions',
        'random_directions_radians',
        'last_time_sec',
        'start_times_sec',
        '_gave_alpha_warning',
        )
    
    def __init__(self, **kw):
        VisionEgg.Core.Stimulus.__init__(self,**kw)
        # store positions normalized between 0 and 1 so that re-sizing is ok
        num_dots = self.constant_parameters.num_dots # shorthand
        self.x_positions = RandomArray.uniform(0.0,1.0,(num_dots,))
        self.y_positions = RandomArray.uniform(0.0,1.0,(num_dots,))
        self.random_directions_radians = RandomArray.uniform(0.0,2*math.pi,(num_dots,))
        self.last_time_sec = VisionEgg.time_func()
        self.start_times_sec = None # setup variable, assign later
        self._gave_alpha_warning = 0

    def draw(self):
        # XXX This method is not speed-optimized. I just wrote it to
        # get the job done.
        
        p = self.parameters # shorthand
        if p.center is not None:
            if not hasattr(VisionEgg.config,"_GAVE_CENTER_DEPRECATION"):
                VisionEgg.Core.message.add("Specifying DotArea2D by 'center' parameter deprecated.  Use 'position' parameter instead.  (Allows use of 'anchor' parameter to set to other values.)",
                                           level=VisionEgg.Core.Message.DEPRECATION)
                VisionEgg.config._GAVE_CENTER_DEPRECATION = 1
            p.anchor = 'center'
            p.position = p.center[0], p.center[1] # copy values (don't copy ref to tuple)
        if p.on:
            # calculate center
            center = VisionEgg._get_center(p.position,p.anchor,p.size)
            
            if p.anti_aliasing:
                if len(p.color) == 4 and not self._gave_alpha_warning:
                    if p.color[3] != 1.0:
                        VisionEgg.Core.message.add(
                            """The parameter anti_aliasing is set to
                            true in the DotArea2D stimulus class, but
                            the color parameter specifies an alpha
                            value other than 1.0.  To acheive the best
                            anti-aliasing, ensure that the alpha value
                            for the color parameter is 1.0.""",
                            level=VisionEgg.Core.Message.WARNING)
                        self._gave_alpha_warning = 1
                gl.glEnable( gl.GL_POINT_SMOOTH )
                # allow max_alpha value to control blending
                gl.glEnable( gl.GL_BLEND )
                gl.glBlendFunc( gl.GL_SRC_ALPHA, gl.GL_ONE_MINUS_SRC_ALPHA )
            else:
                gl.glDisable( gl.GL_BLEND )
                
            now_sec = VisionEgg.time_func()
            if self.start_times_sec:
                # compute extinct dots and generate new positions
                replace_indices = Numeric.nonzero( Numeric.greater( now_sec - self.start_times_sec, p.dot_lifespan_sec) )
                Numeric.put( self.start_times_sec, replace_indices, now_sec )

                new_x_positions = RandomArray.uniform(0.0,1.0,
                                                      (len(replace_indices),))
                Numeric.put( self.x_positions, replace_indices, new_x_positions )

                new_y_positions = RandomArray.uniform(0.0,1.0,
                                                      (len(replace_indices),))
                Numeric.put( self.y_positions, replace_indices, new_y_positions )

                new_random_directions_radians = RandomArray.uniform(0.0,2*math.pi,
                                                                    (len(replace_indices),))
                Numeric.put( self.random_directions_radians, replace_indices, new_random_directions_radians )
            else:
                # initialize dot extinction values to random (uniform) distribution
                self.start_times_sec = RandomArray.uniform( now_sec - p.dot_lifespan_sec, now_sec,
                                                            (self.constant_parameters.num_dots,))

            signal_num_dots = int(round(p.signal_fraction * self.constant_parameters.num_dots))
            time_delta_sec = now_sec - self.last_time_sec
            self.last_time_sec = now_sec # reset for next loop
            x_increment_normalized =  math.cos(p.signal_direction_deg/180.0*math.pi) * p.velocity_pixels_per_sec / p.size[0] * time_delta_sec
            y_increment_normalized = -math.sin(p.signal_direction_deg/180.0*math.pi) * p.velocity_pixels_per_sec / p.size[1] * time_delta_sec
            self.x_positions[:signal_num_dots] += x_increment_normalized
            self.y_positions[:signal_num_dots] += y_increment_normalized

            num_random_dots = self.constant_parameters.num_dots - signal_num_dots
            random_x_increment_normalized =  Numeric.cos(self.random_directions_radians[signal_num_dots:]) * p.velocity_pixels_per_sec / p.size[0] * time_delta_sec
            random_y_increment_normalized = -Numeric.sin(self.random_directions_radians[signal_num_dots:]) * p.velocity_pixels_per_sec / p.size[1] * time_delta_sec
            self.x_positions[signal_num_dots:] += random_x_increment_normalized
            self.y_positions[signal_num_dots:] += random_y_increment_normalized

            self.x_positions = Numeric.fmod( self.x_positions, 1.0 ) # wrap
            self.y_positions = Numeric.fmod( self.y_positions, 1.0 )

            self.x_positions = Numeric.fmod( self.x_positions+1, 1.0 ) # wrap again for values < 1
            self.y_positions = Numeric.fmod( self.y_positions+1, 1.0 )

            xs = (self.x_positions - 0.5) * p.size[0] + center[0]
            ys = (self.y_positions - 0.5) * p.size[1] + center[1]

            gl.glColorf( p.color ) 
            gl.glPointSize(p.dot_size)

            # Clear the modeview matrix
            gl.glMatrixMode(gl.GL_MODELVIEW)
            gl.glLoadIdentity()
            
            gl.glDisable(gl.GL_TEXTURE_2D)
            
            if p.depth is None:
                depth = 0.0
            else:
                gl.glEnable(gl.GL_DEPTH_TEST)
                depth = p.depth
            zs = (depth,)*len(xs) # make N tuple with repeat value of depth
            draw_dots(xs,ys,zs)
            if p.anti_aliasing:
                gl.glDisable( gl.GL_POINT_SMOOTH ) # turn off
