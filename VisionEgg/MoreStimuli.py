# The Vision Egg: MoreStimuli
#
# Copyright (C) 2001-2003 Andrew Straw.
#           (C) 2005 by Hertie Institute for Clinical Brain Research,
#            Department of Cognitive Neurology, University of Tuebingen
#           (C) 2005,2008 California Institute of Technology
#           (C) 2006 Peter Jurica and Gijs Plomp
#
# URL: http://www.visionegg.org
#
# Distributed under the terms of the GNU Lesser General Public License
# (LGPL). See LICENSE.TXT that came with this file.

"""
Assorted stimuli.

"""

####################################################################
#
#        Import all the necessary packages
#
####################################################################

import logging

import VisionEgg
import VisionEgg.Core
import VisionEgg.ParameterTypes as ve_types

import numpy.oldnumeric as Numeric

import math

import VisionEgg.GL as gl # get all OpenGL stuff in one namespace

class Target2D(VisionEgg.Core.Stimulus):
    """Rectanglular stimulus.

    Parameters
    ==========
    anchor        -- specifies how position parameter is interpreted (String)
                     Default: center
    anti_aliasing -- (Boolean)
                     Default: True
    center        -- DEPRECATED: don't use (Sequence2 of Real)
                     Default: (determined at runtime)
    color         -- (AnyOf(Sequence3 of Real or Sequence4 of Real))
                     Default: (1.0, 1.0, 1.0)
    on            -- draw stimulus? (Boolean) (Boolean)
                     Default: True
    orientation   -- (Real)
                     Default: 0.0
    position      -- units: eye coordinates (AnyOf(Sequence2 of Real or Sequence3 of Real or Sequence4 of Real))
                     Default: (320.0, 240.0)
    size          -- units: eye coordinates (Sequence2 of Real)
                     Default: (64.0, 16.0)
    """

    parameters_and_defaults = {
        'on':(True,
              ve_types.Boolean,
              "draw stimulus? (Boolean)"),
        'color':((1.0,1.0,1.0),
                 ve_types.AnyOf(ve_types.Sequence3(ve_types.Real),
                                ve_types.Sequence4(ve_types.Real))),
        'anti_aliasing':(True,
                         ve_types.Boolean),
        'orientation':(0.0,
                       ve_types.Real),
        'position' : ( ( 320.0, 240.0 ),
                       ve_types.AnyOf(ve_types.Sequence2(ve_types.Real),
                                      ve_types.Sequence3(ve_types.Real),
                                      ve_types.Sequence4(ve_types.Real)),
                       "units: eye coordinates"),
        'anchor' : ('center',
                    ve_types.String,
                    "specifies how position parameter is interpreted"),
        'size':((64.0,16.0),
                ve_types.Sequence2(ve_types.Real),
                "units: eye coordinates"),
        'center' : (None,
                    ve_types.Sequence2(ve_types.Real),
                    "DEPRECATED: don't use"),
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
            gl.glPushMatrix()
            gl.glTranslate(center[0],center[1],0.0)
            gl.glRotate(p.orientation,0.0,0.0,1.0)

            if len(p.color)==3:
                gl.glColor3f(*p.color)
            elif len(p.color)==4:
                gl.glColor4f(*p.color)
            gl.glDisable(gl.GL_DEPTH_TEST)
            gl.glDisable(gl.GL_TEXTURE_2D)
            gl.glBlendFunc(gl.GL_SRC_ALPHA,gl.GL_ONE_MINUS_SRC_ALPHA)
            gl.glEnable(gl.GL_BLEND)

            w = p.size[0]/2.0
            h = p.size[1]/2.0

            gl.glBegin(gl.GL_QUADS)
            gl.glVertex3f(-w,-h, 0.0)
            gl.glVertex3f( w,-h, 0.0)
            gl.glVertex3f( w, h, 0.0)
            gl.glVertex3f(-w, h, 0.0)
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
            gl.glPopMatrix()

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
            if len(p.color)==3:
                gl.glColor3f(*p.color)
            elif len(p.color)==4:
                gl.glColor4f(*p.color)

            gl.glDisable(gl.GL_TEXTURE_2D)
            gl.glDisable(gl.GL_DEPTH_TEST)
            gl.glDisable(gl.GL_BLEND)

            gl.glBegin(gl.GL_QUADS)
            gl.glVertex(*p.vertex1)
            gl.glVertex(*p.vertex2)
            gl.glVertex(*p.vertex3)
            gl.glVertex(*p.vertex4)
            gl.glEnd() # GL_QUADS

            gl.glDisable(gl.GL_TEXTURE_2D)
            gl.glDisable(gl.GL_BLEND)

            gl.glBegin(gl.GL_QUADS)
            gl.glVertex(*p.vertex1)
            gl.glVertex(*p.vertex2)
            gl.glVertex(*p.vertex3)
            gl.glVertex(*p.vertex4)
            gl.glEnd() # GL_QUADS

class Arrow(VisionEgg.Core.Stimulus):
    """Arrow stimulus.

    Parameters
    ==========
    anchor        -- (String)
                     Default: center
    anti_aliasing -- (Boolean)
                     Default: True
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
        'position' : ( ( 320.0, 240.0 ), # In eye coordinates
                       ve_types.AnyOf(ve_types.Sequence2(ve_types.Real),
                                      ve_types.Sequence3(ve_types.Real),
                                      ve_types.Sequence4(ve_types.Real)),
                       "units: eye coordinates"),
        'anchor' : ('center',
                    ve_types.String),
        'size':((64.0,16.0), # In eye coordinates
                ve_types.Sequence2(ve_types.Real)),
        }

    __slots__ = VisionEgg.Core.Stimulus.__slots__ + (
        '_gave_alpha_warning',
        )

    def __init__(self,**kw):
        VisionEgg.Core.Stimulus.__init__(self,**kw)
        self._gave_alpha_warning = 0

    def draw(self):
        p = self.parameters # Shorthand
        if p.on:
            # Calculate center
            center = VisionEgg._get_center(p.position,p.anchor,p.size)
            gl.glMatrixMode(gl.GL_MODELVIEW)
            gl.glPushMatrix()
            gl.glTranslate(center[0],center[1],0.0)
            gl.glRotate(-p.orientation,0.0,0.0,1.0)

            if len(p.color)==3:
                gl.glColor3f(*p.color)
            elif len(p.color)==4:
                gl.glColor4f(*p.color)
            gl.glDisable(gl.GL_DEPTH_TEST)
            gl.glDisable(gl.GL_TEXTURE_2D)
            gl.glBlendFunc(gl.GL_SRC_ALPHA,gl.GL_ONE_MINUS_SRC_ALPHA)
            gl.glEnable(gl.GL_BLEND)

            w = p.size[0]/2.0
            h = p.size[1]/2.0

            gl.glBegin(gl.GL_QUADS) # Draw Rectangle
            gl.glVertex3f( 0.25*w, h, 0.0)
            gl.glVertex3f(-w, h, 0.0)
            gl.glVertex3f(-w,-h, 0.0)
            gl.glVertex3f( 0.25*w, -h, 0.0)
            gl.glEnd() # GL_QUADS

            gl.glBegin(gl.GL_TRIANGLES) # Draw Triangle
            gl.glVertex3f( 1.00*w, 0.0*h, 0.0) # Top
            gl.glVertex3f( 0.25*w,-3.0*h, 0.0)
            gl.glVertex3f( 0.25*w, 3.0*h, 0.0)
            gl.glEnd() # GL_QUADS

            if p.anti_aliasing:
                if not self._gave_alpha_warning:
                    if len(p.color) > 3 and p.color[3] != 1.0:
                        logger = logging.getLogger('VisionEgg.Arrow')
                        logger.warning("The parameter anti_aliasing is "
                                       "set to true in the Arrow "
                                       "stimulus class, but the color "
                                       "parameter specifies an alpha "
                                       "value other than 1.0.  To "
                                       "acheive anti-aliasing, ensure "
                                       "that the alpha value for the "
                                       "color parameter is 1.0.")
                        self._gave_alpha_warning = 1

                # We've already drawn a filled polygon (aliased), now redraw
                # the outline of the polygon (with anti-aliasing). (Using
                # GL_POLYGON_SMOOTH results in artifactual lines where
                # triangles were joined to create quad, at least on some OpenGL
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

                gl.glVertex3f( 0.25*w, h, 0.0) # Draw Rectangle
                gl.glVertex3f(-w, h, 0.0)
                gl.glVertex3f(-w,-h, 0.0)
                gl.glVertex3f( 0.25*w, -h, 0.0)
                gl.glVertex3f( 1.00*w, 0.0*h, 0.0) # Draw Triangle
                gl.glVertex3f( 0.25*w,-3.0*h, 0.0)
                gl.glVertex3f( 0.25*w, 3.0*h, 0.0)
                gl.glEnd() # GL_QUADS

                # Set the polygon mode back to fill mode
                gl.glPolygonMode(gl.GL_FRONT_AND_BACK,gl.GL_FILL)
                gl.glDisable(gl.GL_LINE_SMOOTH)
            gl.glPopMatrix()

class FilledCircle(VisionEgg.Core.Stimulus):
    """  A circular stimulus, typically used as a fixation point.

    (Note, this implementation almost certainly could be made faster
    using display lists.)

    Parameters
    ==========
    anchor        -- how position parameter is used (String)
                     Default: center
    anti_aliasing -- (Boolean)
                     Default: True
    color         -- color (AnyOf(Sequence3 of Real or Sequence4 of Real))
                     Default: (1.0, 1.0, 1.0)
    num_triangles -- number of triangles used to draw circle (Integer)
                     Default: 51
    on            -- draw? (Boolean)
                     Default: True
    position      -- position in eye coordinates (AnyOf(Sequence2 of Real or Sequence3 of Real or Sequence4 of Real))
                     Default: (320.0, 240.0)
    radius        -- radius in eye coordinates (Real)
                     Default: 2.0
    """

    parameters_and_defaults = VisionEgg.ParameterDefinition({
        'on':(True,
              ve_types.Boolean,
              'draw?'),
        'color':((1.0,1.0,1.0),
                 ve_types.AnyOf(ve_types.Sequence3(ve_types.Real),
                                ve_types.Sequence4(ve_types.Real)),
                 'color'),
        'anti_aliasing':(True,
                         ve_types.Boolean),
        'position' : ( ( 320.0, 240.0 ), # in eye coordinates
                       ve_types.AnyOf(ve_types.Sequence2(ve_types.Real),
                                      ve_types.Sequence3(ve_types.Real),
                                      ve_types.Sequence4(ve_types.Real)),
                       'position in eye coordinates'),
        'anchor' : ('center',
                    ve_types.String,
                    'how position parameter is used'),
        'radius':(2.0,
                  ve_types.Real,
                  'radius in eye coordinates'),
        'num_triangles':(51,
                         ve_types.Integer,
                         'number of triangles used to draw circle'),
        })
    __slots__ = VisionEgg.Core.Stimulus.__slots__ + (
        '_gave_alpha_warning',
        )

    def __init__(self,**kw):
        VisionEgg.Core.Stimulus.__init__(self,**kw)
        self._gave_alpha_warning = 0

    def draw(self):
        p = self.parameters # shorthand
        if p.on:
            # calculate center
            center = VisionEgg._get_center(p.position,p.anchor,(p.radius, p.radius))
            gl.glDisable(gl.GL_DEPTH_TEST)
            gl.glDisable(gl.GL_TEXTURE_2D)
            gl.glDisable(gl.GL_BLEND)

            if len(p.color)==3:
                gl.glColor3f(*p.color)
            elif len(p.color)==4:
                gl.glColor4f(*p.color)

          # Build filled circle from points
#           gl.glBegin(gl.GL_POINTS)
#           radius = int(math.ceil(p.radius))
#           for i in range(-radius, radius):
#               for j in range(-radius, radius):
#                   if(i * i + j * j < radius * radius):
#                       gl.glVertex3f(p.position[0] + i, p.position[1] + j, 0.0)
#           gl.glEnd() # GL_POINTS

            # Build filled circle from triangles (this is typically faster
            # then the commented code above with the points)
            gl.glBegin(gl.GL_TRIANGLE_FAN)
            gl.glVertex3f(p.position[0], p.position[1], 0.0)
            angles = Numeric.arange(p.num_triangles)/float(p.num_triangles)*2.0*math.pi
            verts = Numeric.zeros( (p.num_triangles,2), Numeric.Float )
            verts[:,0] = p.position[0] + p.radius * Numeric.cos(angles)
            verts[:,1] = p.position[1] + p.radius * Numeric.sin(angles)
            for i in range(verts.shape[0]):
                gl.glVertex2fv(verts[i])
            gl.glVertex2fv(verts[0])

            gl.glEnd() # GL_TRIANGLE_FAN
            if p.anti_aliasing:
                if not self._gave_alpha_warning:
                    if len(p.color) > 3 and p.color[3] != 1.0:
                        logger = logging.getLogger('VisionEgg.Arrow')
                        logger.warning("The parameter anti_aliasing is "
                                       "set to true in the Arrow "
                                       "stimulus class, but the color "
                                       "parameter specifies an alpha "
                                       "value other than 1.0.  To "
                                       "acheive anti-aliasing, ensure "
                                       "that the alpha value for the "
                                       "color parameter is 1.0.")
                        self._gave_alpha_warning = 1

                        # We've already drawn a filled polygon (aliased), now redraw
                        # the outline of the polygon (with anti-aliasing). (Using
                        # GL_POLYGON_SMOOTH results in artifactual lines where
                        # triangles were joined to create quad, at least on some OpenGL
                        # implementations.)

                # Calculate coverage value for each pixel of outline
                # and store as alpha
                gl.glEnable(gl.GL_LINE_SMOOTH)
                # Now specify how to use the alpha value
                gl.glBlendFunc(gl.GL_SRC_ALPHA,gl.GL_ONE_MINUS_SRC_ALPHA)
                gl.glEnable(gl.GL_BLEND)

                # Draw a second polygon in line mode, so the edges are anti-aliased
                gl.glPolygonMode(gl.GL_FRONT_AND_BACK,gl.GL_LINE)
                gl.glBegin(gl.GL_TRIANGLE_FAN)
                gl.glVertex3f(p.position[0], p.position[1], 0.0)
                angles = Numeric.arange(p.num_triangles)/float(p.num_triangles)*2.0*math.pi
                verts = Numeric.zeros( (p.num_triangles,2), Numeric.Float )
                verts[:,0] = p.position[0] + p.radius * Numeric.cos(angles)
                verts[:,1] = p.position[1] + p.radius * Numeric.sin(angles)
                for i in range(verts.shape[0]):
                    gl.glVertex2fv(verts[i])
                gl.glVertex2fv(verts[0])
                gl.glEnd() # GL_TRIANGLE_FAN

                # Set the polygon mode back to fill mode
                gl.glPolygonMode(gl.GL_FRONT_AND_BACK,gl.GL_FILL)
                gl.glDisable(gl.GL_LINE_SMOOTH)

