# The Vision Egg: MoreStimuli
#
# Copyright (C) 2001-2003 Andrew Straw.
# Author: Andrew Straw <astraw@users.sourceforge.net>
# URL: <http://www.visionegg.org/>
#
# Distributed under the terms of the GNU Lesser General Public License
# (LGPL). See LICENSE.TXT that came with this file.
#
# $Id$

"""
Assorted stimuli.

"""

####################################################################
#
#        Import all the necessary packages
#
####################################################################

try:
    import logging
except ImportError:
    import VisionEgg.py_logging as logging

import VisionEgg
import VisionEgg.Core
import VisionEgg.ParameterTypes as ve_types

import Numeric

import VisionEgg.GL as gl # get all OpenGL stuff in one namespace

__version__ = VisionEgg.release_name
__cvs__ = '$Revision$'.split()[1]
__date__ = ' '.join('$Date$'.split()[1:3])
__author__ = 'Andrew Straw <astraw@users.sourceforge.net>'

# Use Python's bool constants if available, make aliases if not
try:
    True
except NameError:
    True = 1==1
    False = 1==0

class Target2D(VisionEgg.Core.Stimulus):
    """Rectanglular stimulus.

    Parameters
    ==========
    anchor        -- (String)
                     Default: center
    anti_aliasing -- (Boolean)
                     Default: True
    center        -- (Sequence2 of Real)
                     Default: (determined at instantiation)
    color         -- (AnyOf(Sequence3 of Real or Sequence4 of Real))
                     Default: (1.0, 1.0, 1.0)
    on            -- (Boolean)
                     Default: True
    orientation   -- (Real)
                     Default: 0.0
    position      -- units: eye coordinates (AnyOf(Sequence2 of Real or Sequence3 of Real or Sequence4 of Real))
                     Default: (320.0, 240.0)
    size          -- (Sequence2 of Real)
                     Default: (64.0, 16.0)
    """
    
    parameters_and_defaults = {
        'on':(True,
              ve_types.Boolean),
        'color':((1.0,1.0,1.0),
                 ve_types.AnyOf(ve_types.Sequence3(ve_types.Real),
                                ve_types.Sequence4(ve_types.Real))),
        'anti_aliasing':(True,
                         ve_types.Boolean),
        'orientation':(0.0, # 0.0 degrees = right, 90.0 degrees = up
                       ve_types.Real),
        'position' : ( ( 320.0, 240.0 ), # in eye coordinates
                       ve_types.AnyOf(ve_types.Sequence2(ve_types.Real),
                                      ve_types.Sequence3(ve_types.Real),
                                      ve_types.Sequence4(ve_types.Real)),
                       "units: eye coordinates"),
        'anchor' : ('center',
                    ve_types.String),
        'size':((64.0,16.0), # in eye coordinates
                ve_types.Sequence2(ve_types.Real)),
        'center' : (None,  # DEPRECATED -- don't use
                    ve_types.Sequence2(ve_types.Real)),  
        }
    
    __slots__ = (
        '_gave_alpha_warning',
        )
    
    def __init__(self,**kw):
        VisionEgg.Core.Stimulus.__init__(self,**kw)
        self._gave_alpha_warning = 0

    def draw(self):
        p = self.parameters # shorthand
        if p.center is not None:
            if not hasattr(VisionEgg.config,"_GAVE_CENTER_DEPRECATION"):
                logger = logging.getLogger('VisionEgg.MoreStimuli')
                logger.warning("Specifying Target2D by deprecated "
                               "'center' parameter deprecated.  Use "
                               "'position' parameter instead.  (Allows "
                               "use of 'anchor' parameter to set to "
                               "other values.)")
                VisionEgg.config._GAVE_CENTER_DEPRECATION = 1
            p.anchor = 'center'
            p.position = p.center[0], p.center[1] # copy values (don't copy ref to tuple)
        if p.on:
            # calculate center
            center = VisionEgg._get_center(p.position,p.anchor,p.size)
            gl.glMatrixMode(gl.GL_MODELVIEW)
            gl.glLoadIdentity()
            gl.glTranslate(center[0],center[1],0.0)
            gl.glRotate(p.orientation,0.0,0.0,1.0)

            gl.glColorf(*p.color)
            gl.glDisable(gl.GL_DEPTH_TEST)
            gl.glDisable(gl.GL_TEXTURE_2D)
            gl.glBlendFunc(gl.GL_SRC_ALPHA,gl.GL_ONE_MINUS_SRC_ALPHA)
            gl.glEnable(gl.GL_BLEND)

            w = p.size[0]/2.0
            h = p.size[1]/2.0
            
            gl.glBegin(gl.GL_QUADS)
            gl.glVertex3f(-w,-h, 0.0);
            gl.glVertex3f( w,-h, 0.0);
            gl.glVertex3f( w, h, 0.0);
            gl.glVertex3f(-w, h, 0.0);
            gl.glEnd() # GL_QUADS
            
            if p.anti_aliasing:
                if not self._gave_alpha_warning:
                    if len(p.color) > 3 and p.color[3] != 1.0:
                        logger = logging.getLogger('VisionEgg.MoreStimuli')
                        logger.warning("The parameter anti_aliasing is "
                                       "set to true in the Target2D "
                                       "stimulus class, but the color "
                                       "parameter specifies an alpha "
                                       "value other than 1.0.  To "
                                       "acheive anti-aliasing, ensure "
                                       "that the alpha value for the "
                                       "color parameter is 1.0.")
                        self._gave_alpha_warning = 1

                # We've already drawn a filled polygon (aliased), now
                # redraw the outline of the polygon (with
                # anti-aliasing).  (Using GL_POLYGON_SMOOTH results in
                # artifactual lines where triangles were joined to
                # create quad, at least on some OpenGL
                # implementations.)

                # Calculate coverage value for each pixel of outline
                # and store as alpha
                gl.glEnable(gl.GL_LINE_SMOOTH)
                # Now specify how to use the alpha value
                gl.glBlendFunc(gl.GL_SRC_ALPHA,gl.GL_ONE_MINUS_SRC_ALPHA)
                gl.glEnable(gl.GL_BLEND)

                # Draw a second polygon in line mode, so the edges are anti-aliased
                gl.glPolygonMode(gl.GL_FRONT_AND_BACK,gl.GL_LINE)
                gl.glBegin(gl.GL_QUADS)
                gl.glVertex3f(-w,-h, 0.0);
                gl.glVertex3f( w,-h, 0.0);
                gl.glVertex3f( w, h, 0.0);
                gl.glVertex3f(-w, h, 0.0);
                gl.glEnd() # GL_QUADS

                # Set the polygon mode back to fill mode
                gl.glPolygonMode(gl.GL_FRONT_AND_BACK,gl.GL_FILL)
                gl.glDisable(gl.GL_LINE_SMOOTH)

class Rectangle3D(VisionEgg.Core.Stimulus):
    """Solid color rectangle positioned explicitly by four vertices.

    Parameters
    ==========
    color   -- (AnyOf(Sequence3 of Real or Sequence4 of Real))
               Default: (1.0, 1.0, 1.0, 1.0)
    on      -- (Boolean)
               Default: True
    vertex1 -- units: eye coordinates (AnyOf(Sequence3 of Real or Sequence4 of Real))
               Default: (-10.0, 0.0, -10.0)
    vertex2 -- units: eye coordinates (AnyOf(Sequence3 of Real or Sequence4 of Real))
               Default: (-10.0, 0.0, 10.0)
    vertex3 -- units: eye coordinates (AnyOf(Sequence3 of Real or Sequence4 of Real))
               Default: (10.0, 0.0, 10.0)
    vertex4 -- units: eye coordinates (AnyOf(Sequence3 of Real or Sequence4 of Real))
               Default: (10.0, 0.0, -10.0)
    """
    
    parameters_and_defaults = {
        'on':(True,
              ve_types.Boolean),
        'color':((1.0,1.0,1.0,1.0),
                 ve_types.AnyOf(ve_types.Sequence3(ve_types.Real),
                                ve_types.Sequence4(ve_types.Real))),
        'vertex1':(( -10.0, 0.0, -10.0),
                   ve_types.AnyOf(ve_types.Sequence3(ve_types.Real),
                                  ve_types.Sequence4(ve_types.Real)),
                 "units: eye coordinates"),
        'vertex2':(( -10.0, 0.0,  10.0),
                   ve_types.AnyOf(ve_types.Sequence3(ve_types.Real),
                                  ve_types.Sequence4(ve_types.Real)),
                 "units: eye coordinates"),
        'vertex3':((  10.0, 0.0,  10.0),
                   ve_types.AnyOf(ve_types.Sequence3(ve_types.Real),
                                  ve_types.Sequence4(ve_types.Real)),
                 "units: eye coordinates"),
        'vertex4':((  10.0, 0.0, -10.0),
                   ve_types.AnyOf(ve_types.Sequence3(ve_types.Real),
                                  ve_types.Sequence4(ve_types.Real)),
                 "units: eye coordinates"),
        }
    
    def __init__(self,**kw):
        VisionEgg.Core.Stimulus.__init__(self,**kw)

    def draw(self):
        p = self.parameters # shorthand
        if p.on:
            gl.glMatrixMode(gl.GL_MODELVIEW)
            gl.glLoadIdentity()

            gl.glColorf(*p.color)
                
            gl.glDisable(gl.GL_TEXTURE_2D)
            gl.glDisable(gl.GL_BLEND)

            gl.glBegin(gl.GL_QUADS)
            gl.glVertex(*p.vertex1)
            gl.glVertex(*p.vertex2)
            gl.glVertex(*p.vertex3)
            gl.glVertex(*p.vertex4)
            gl.glEnd() # GL_QUADS
