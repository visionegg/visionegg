"""Assorted stimuli"""

# Copyright (c) 2001-2003 Andrew Straw.  Distributed under the terms of the
# GNU Lesser General Public License (LGPL).

all = ['Rectangle3D', 'Target2D', ]

####################################################################
#
#        Import all the necessary packages
#
####################################################################

import VisionEgg.Core
import VisionEgg.ParameterTypes as ve_types

import Numeric

import VisionEgg.GL as gl # get all OpenGL stuff in one namespace

import string

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

class Target2D(VisionEgg.Core.Stimulus):
    
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
                                      ve_types.Sequence4(ve_types.Real))),
        'anchor' : ('center',
                    ve_types.String),
        'size':((64.0,16.0), # in eye coordinates
                ve_types.Sequence2(ve_types.Real)),
        'center' : (None,  # DEPRECATED -- don't use
                    ve_types.Sequence2(ve_types.Real)),  
        }
    
    __slots__ = VisionEgg.Core.Stimulus.__slots__ + (
        '_gave_alpha_warning',
        )
    
    def __init__(self,**kw):
        VisionEgg.Core.Stimulus.__init__(self,**kw)
        self._gave_alpha_warning = 0

    def draw(self):
        p = self.parameters # shorthand
        if p.center is not None:
            if not hasattr(VisionEgg.config,"_GAVE_CENTER_DEPRECATION"):
                VisionEgg.Core.message.add("Specifying Target2D by 'center' parameter deprecated.  Use 'position' parameter instead.  (Allows use of 'anchor' parameter to set to other values.)",
                                           level=VisionEgg.Core.Message.DEPRECATION)
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
            gl.glDisable(gl.GL_BLEND)

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
                        VisionEgg.Core.message.add(
                            """The parameter anti_aliasing is set to
                            true in the Target2D stimulus class, but
                            the color parameter specifies an alpha
                            value other than 1.0.  To acheive
                            anti-aliasing, ensure that the alpha value
                            for the color parameter is 1.0.""",
                            level=VisionEgg.Core.Message.WARNING)
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
    
    parameters_and_defaults = {
        'on':(True,
              ve_types.Boolean),
        'color':((1.0,1.0,1.0,1.0),
                 ve_types.AnyOf(ve_types.Sequence3(ve_types.Real),
                                ve_types.Sequence4(ve_types.Real))),
        'vertex1':(( -10.0, 0.0, -10.0),
                   ve_types.AnyOf(ve_types.Sequence3(ve_types.Real),
                                  ve_types.Sequence4(ve_types.Real))),
        'vertex2':(( -10.0, 0.0,  10.0),
                   ve_types.AnyOf(ve_types.Sequence3(ve_types.Real),
                                  ve_types.Sequence4(ve_types.Real))),
        'vertex3':((  10.0, 0.0,  10.0),
                   ve_types.AnyOf(ve_types.Sequence3(ve_types.Real),
                                  ve_types.Sequence4(ve_types.Real))),
        'vertex4':((  10.0, 0.0, -10.0),
                   ve_types.AnyOf(ve_types.Sequence3(ve_types.Real),
                                  ve_types.Sequence4(ve_types.Real))),
        }
    
    __slots__ = VisionEgg.Core.Stimulus.__slots__
    
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
