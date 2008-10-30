# The Vision Egg: SphereMap
#
# Copyright (C) 2001-2004 Andrew Straw.
# Copyright (C) 2005-2008 California Institute of Technology
#
# Author: Andrew Straw <astraw@users.sourceforge.net>
# URL: <http://www.visionegg.org/>
#
# Distributed under the terms of the GNU Lesser General Public License
# (LGPL). See LICENSE.TXT that came with this file.

"""
Stimuli on spheres, including texture maps.

"""

import math, types

import logging

import VisionEgg.Core
import VisionEgg.Textures
import VisionEgg.Text
import VisionEgg.Gratings
import VisionEgg.ThreeDeeMath
import VisionEgg.ParameterTypes as ve_types

import numpy
import numpy.oldnumeric as Numeric
import Image

import VisionEgg.GL as gl # get all OpenGL stuff in one namespace

__version__ = VisionEgg.release_name

class AzElGrid(VisionEgg.Core.Stimulus):
    """Spherical grid of iso-azimuth and iso-elevation lines.

    Parameters
    ==========
    anti_aliasing    -- (Boolean)
                        Default: True
    center_azimuth   -- (Real)
                        Default: 0.0
    center_elevation -- (Real)
                        Default: 0.0
    major_line_color -- (AnyOf(Sequence3 of Real or Sequence4 of Real))
                        Default: (0.0, 0.0, 0.0)
    major_line_width -- (Real)
                        Default: 2.0
    minor_line_color -- (AnyOf(Sequence3 of Real or Sequence4 of Real))
                        Default: (0.0, 0.0, 1.0)
    minor_line_width -- (Real)
                        Default: 1.0
    my_viewport      -- (Instance of <class 'VisionEgg.Core.Viewport'>)
                        Default: (determined at runtime)
    on               -- (Boolean)
                        Default: True
    text_offset      -- (Sequence2 of Real)
                        Default: (3, -2)

    Constant Parameters
    ===================
    az_major_spacing       -- (Real)
                              Default: 30.0
    az_minor_spacing       -- (Real)
                              Default: 10.0
    el_major_spacing       -- (Real)
                              Default: 30.0
    el_minor_spacing       -- (Real)
                              Default: 10.0
    font_size              -- (UnsignedInteger)
                              Default: 24
    num_samples_per_circle -- (UnsignedInteger)
                              Default: 100
    radius                 -- (Real)
                              Default: 1.0
    text_anchor            -- (String)
                              Default: lowerleft
    text_color             -- (AnyOf(Sequence3 of Real or Sequence4 of Real))
                              Default: (0.0, 0.0, 0.0)
    use_text               -- (Boolean)
                              Default: True
    """

    parameters_and_defaults = {
        'on':(True,
              ve_types.Boolean),
        'center_azimuth':(0.0, # 0=right, 90=right
                          ve_types.Real),
        'center_elevation':(0.0, # 0=right, 90=up
                            ve_types.Real),
        'minor_line_width':(1.0,
                            ve_types.Real),
        'major_line_width':(2.0,
                            ve_types.Real),
        'minor_line_color':((0.0,0.0,1.0),
                            ve_types.AnyOf(ve_types.Sequence3(ve_types.Real),
                                           ve_types.Sequence4(ve_types.Real))),
        'major_line_color':((0.0,0.0,0.0),
                            ve_types.AnyOf(ve_types.Sequence3(ve_types.Real),
                                           ve_types.Sequence4(ve_types.Real))),
        'my_viewport':(None, # viewport I'm in
                       ve_types.Instance(VisionEgg.Core.Viewport)),
        'text_offset':((3,-2), # offset (x,y) to nudge text labels
                       ve_types.Sequence2(ve_types.Real)),
        'anti_aliasing' : ( True,
                            ve_types.Boolean ),
        }

    constant_parameters_and_defaults = {
        'use_text':(True,
                    ve_types.Boolean),
        'radius':(1.0,
                  ve_types.Real),
        'az_minor_spacing':(10.0,
                            ve_types.Real),
        'az_major_spacing':(30.0,
                            ve_types.Real),
        'el_minor_spacing':(10.0,
                            ve_types.Real),
        'el_major_spacing':(30.0,
                            ve_types.Real),
        'num_samples_per_circle':(100,
                                  ve_types.UnsignedInteger),
        'font_size':(24,
                     ve_types.UnsignedInteger),
        'text_color':((0.0,0.0,0.0),
                      ve_types.AnyOf(ve_types.Sequence3(ve_types.Real),
                                     ve_types.Sequence4(ve_types.Real))),
        'text_anchor':('lowerleft',
                       ve_types.String),
        }

    __slots__ = (
        'cached_minor_lines_display_list',
        'cached_major_lines_display_list',
        'text_viewport',
        'text_viewport_orig',
        '_gave_alpha_warning',
        'labels',
        'labels_xyz',
        )

    def __init__(self,**kw):
        VisionEgg.Core.Stimulus.__init__(self,**kw)
        self.cached_minor_lines_display_list = gl.glGenLists(1) # Allocate a new display list
        self.cached_major_lines_display_list = gl.glGenLists(1) # Allocate a new display list
        self.__rebuild_display_lists()
        self.text_viewport = None # not set yet
        self._gave_alpha_warning = False

    def __rebuild_display_lists(self):
        def get_xyz(theta,phi,radius):
            # theta normally between 0 and pi (north pole to south pole)
            # phi between -pi and pi
            y = radius * math.cos( theta )
            w = radius * math.sin( theta )
            x = w * math.cos( phi )
            z = w * math.sin( phi )
            return x,y,z
        def draw_half_great_circle(az):
            for i in range(cp.num_samples_per_circle/2):
                # let theta exceed 1 pi to draw 2nd half of circle
                theta_start = i/float(cp.num_samples_per_circle)*2*math.pi
                theta_stop = (i+1)/float(cp.num_samples_per_circle)*2*math.pi
                phi_start = phi_stop = (az-90.0)/180.0*math.pi
                x_start,y_start,z_start = get_xyz(theta_start,phi_start,cp.radius)
                x_stop,y_stop,z_stop = get_xyz(theta_stop,phi_stop,cp.radius)
                gl.glVertex3f(x_start, y_start, z_start)
                gl.glVertex3f(x_stop, y_stop, z_stop)
        def draw_iso_elevation_circle(el):
            # el from -90 = pi to el 90 = 0
            theta_start = theta_stop = -(el-90) / 180.0 * math.pi
            for i in range(cp.num_samples_per_circle):
                phi_start = i/float(cp.num_samples_per_circle)*2*math.pi
                phi_stop = (i+1)/float(cp.num_samples_per_circle)*2*math.pi
                x_start,y_start,z_start = get_xyz(theta_start,phi_start,cp.radius)
                x_stop,y_stop,z_stop = get_xyz(theta_stop,phi_stop,cp.radius)
                gl.glVertex3f(x_start, y_start, z_start)
                gl.glVertex3f(x_stop, y_stop, z_stop)

        cp = self.constant_parameters
        # Weird range construction to be sure to include zero.
        azs_major = numpy.concatenate((
            numpy.arange(0.0,180.0,cp.az_major_spacing),
            -numpy.arange(0.0,180.0,cp.az_major_spacing)[1:]))
        azs_minor = numpy.concatenate((
            numpy.arange(0.0,180.0,cp.az_minor_spacing),
            -numpy.arange(0.0,180.0,cp.az_minor_spacing)[1:]))
        els_major = numpy.concatenate((
            numpy.arange(0.0,90.0,cp.el_major_spacing),
            -numpy.arange(0.0,90.0,cp.el_major_spacing)[1:]))
        els_minor = numpy.concatenate((
            numpy.arange(0.0,90.0,cp.el_minor_spacing),
            -numpy.arange(0.0,90.0,cp.el_minor_spacing)[1:]))

        gl.glNewList(self.cached_minor_lines_display_list,gl.GL_COMPILE)
        gl.glBegin(gl.GL_LINES)
        # az minor
        for az in azs_minor:
            if az in azs_major:
                continue # draw only once as major
            draw_half_great_circle(az)
        for el in els_minor:
            if el in els_major:
                continue # draw only once as major
            draw_iso_elevation_circle(el)
        gl.glEnd()
        gl.glEndList()

        gl.glNewList(self.cached_major_lines_display_list,gl.GL_COMPILE)
        gl.glBegin(gl.GL_LINES)
        for az in azs_major:
            draw_half_great_circle(az)
        for el in els_major:
            draw_iso_elevation_circle(el)
        gl.glEnd()
        gl.glEndList()

        if cp.use_text:
            self.labels = []
            self.labels_xyz = []
            els_major = list(els_major)+[90.0] # make sure we have north pole
            for el in els_major:
                for az in azs_major:
                    theta = -(el-90) / 180.0 * math.pi
                    phi = (az-90.0)/180.0*math.pi
                    x,y,z = get_xyz(theta,phi,cp.radius)
                    self.labels_xyz.append((x,y,z))
                    self.labels.append(
                        VisionEgg.Text.Text( text = '%.0f, %.0f'%(az,el),
                                             font_size = cp.font_size,
                                             color = cp.text_color,
                                             anchor = cp.text_anchor,
                                             )
                        )
                    if (el == -90) or (el == 90):
                        self.labels[-1].parameters.text = 'x, %.0f'%(el,)
                        break # only one label at the poles

            self.labels_xyz = Numeric.array(self.labels_xyz)

    def draw(self):
        p = self.parameters
        cp = self.constant_parameters
        if p.on:
            # Set OpenGL state variables
            gl.glDisable( gl.GL_DEPTH_TEST )
            gl.glDisable( gl.GL_TEXTURE_2D )  # Make sure textures are not drawn
            gl.glMatrixMode(gl.GL_MODELVIEW)
            gl.glPushMatrix()
            gl.glRotatef(p.center_azimuth,0.0,-1.0,0.0)
            gl.glRotatef(p.center_elevation,1.0,0.0,0.0)

            if p.anti_aliasing:
                if len(p.minor_line_color) == 4 and not self._gave_alpha_warning:
                    if p.minor_line_color[3] != 1.0:
                        logger = logging.getLogger('VisionEgg.SphereMap')
                        logger.warning("The parameter anti_aliasing is "
                                       "set to true in the AzElGrid "
                                       "stimulus class, but the color "
                                       "parameter specifies an alpha "
                                       "value other than 1.0.  To "
                                       "acheive the best anti-aliasing, "
                                       "ensure that the alpha value for "
                                       "the color parameter is 1.0.")
                        self._gave_alpha_warning = 1
                if len(p.major_line_color) == 4 and not self._gave_alpha_warning:
                    if p.major_line_color[3] != 1.0:
                        logger = logging.getLogger('VisionEgg.SphereMap')
                        logger.warning("The parameter anti_aliasing is "
                                       "set to true in the AzElGrid "
                                       "stimulus class, but the color "
                                       "parameter specifies an alpha "
                                       "value other than 1.0.  To "
                                       "acheive the best anti-aliasing, "
                                       "ensure that the alpha value for "
                                       "the color parameter is 1.0.")
                        self._gave_alpha_warning = 1
                gl.glEnable( gl.GL_LINE_SMOOTH )
                # allow max_alpha value to control blending
                gl.glEnable( gl.GL_BLEND )
                gl.glBlendFunc( gl.GL_SRC_ALPHA, gl.GL_ONE_MINUS_SRC_ALPHA )
            else:
                gl.glDisable( gl.GL_BLEND )

            if len(p.minor_line_color)==3:
                gl.glColor3f(*p.minor_line_color)
            elif len(p.minor_line_color)==4:
                gl.glColor4f(*p.minor_line_color)
            gl.glLineWidth(p.minor_line_width)
            gl.glCallList(self.cached_minor_lines_display_list)

            if len(p.major_line_color)==3:
                gl.glColor3f(*p.major_line_color)
            elif len(p.major_line_color)==4:
                gl.glColor4f(*p.major_line_color)
            gl.glLineWidth(p.major_line_width)
            gl.glCallList(self.cached_major_lines_display_list)

            if p.anti_aliasing:
                gl.glDisable( gl.GL_LINE_SMOOTH ) # turn off

            if cp.use_text:
                my_view = p.my_viewport
                if (my_view is None) or (not my_view._is_drawing):
                    raise ValueError('use_text is True, but my_viewport not (properly) assigned')

                if self.text_viewport is None or self.text_viewport_orig != my_view:
                    # make viewport for text (uses default orthographic projection)
                    vp = my_view.parameters
                    self.text_viewport = VisionEgg.Core.Viewport(screen=vp.screen,
                                                                 position=vp.position,
                                                                 size=vp.size,
                                                                 anchor=vp.anchor,
                                                                 )
                    lowerleft = VisionEgg._get_lowerleft(vp.position,vp.anchor,vp.size)
                    self.text_viewport.parameters.projection.stateless_translate(-lowerleft[0],-lowerleft[1],0)
                    self.text_viewport_orig = p.my_viewport # in case my_viewport changes, change text_viewport

                # draw text labels
                my_proj = my_view.parameters.projection

                xyz = self.labels_xyz

                t = VisionEgg.ThreeDeeMath.TransformMatrix()
                t.rotate( p.center_azimuth,0.0,-1.0,0.0  ) # acheive same transforms as the lines
                t.rotate( p.center_elevation,1.0,0.0,0.0 )

                xyz = t.transform_vertices(self.labels_xyz)

                clip = my_proj.eye_2_clip(xyz)
                try:
                    # this is much faster when no OverflowError...
                    window_coords = my_view.clip_2_window(clip)
                    all_at_once = True
                except OverflowError:
                    all_at_once = False
                draw_labels = []
                for i in range(len(self.labels)):
                    if clip[i,3] < 0: continue # this vertex is not on screen
                    label = self.labels[i]
                    if all_at_once:
                        this_pos = window_coords[i,:2]
                    else:
                        try:
                            window_coords = my_view.clip_2_window(clip[i,:])
                        except OverflowError:
                            continue # not much we can do with this vertex, either
                        this_pos = window_coords[:2]
                    label.parameters.position = (this_pos[0] + p.text_offset[0],
                                                 this_pos[1] + p.text_offset[1])
                    draw_labels.append(label)
                self.text_viewport.parameters.stimuli = draw_labels
                self.text_viewport.draw()
                my_view.make_current() # restore viewport
            gl.glPopMatrix()

class SphereMap(VisionEgg.Textures.TextureStimulusBaseClass):
    """Mercator mapping of rectangular texture onto sphere.

    Parameters
    ==========
    center_azimuth     -- (Real)
                          Default: 0.0
    center_elevation   -- (Real)
                          Default: 0.0
    contrast           -- (Real)
                          Default: 1.0
    on                 -- (Boolean)
                          Default: True
    radius             -- (Real)
                          Default: 1.0
    slices             -- (UnsignedInteger)
                          Default: 30
    stacks             -- (UnsignedInteger)
                          Default: 30
    texture            -- source of texture data (Instance of <class 'VisionEgg.Textures.Texture'>)
                          Inherited from VisionEgg.Textures.TextureStimulusBaseClass
                          Default: (determined at runtime)
    texture_mag_filter -- OpenGL filter enum (Integer)
                          Inherited from VisionEgg.Textures.TextureStimulusBaseClass
                          Default: GL_LINEAR (9729)
    texture_min_filter -- OpenGL filter enum (Integer)
                          Inherited from VisionEgg.Textures.TextureStimulusBaseClass
                          Default: (GL enum determined at runtime)
    texture_wrap_s     -- OpenGL texture wrap enum (Integer)
                          Inherited from VisionEgg.Textures.TextureStimulusBaseClass
                          Default: (GL enum determined at runtime)
    texture_wrap_t     -- OpenGL texture wrap enum (Integer)
                          Inherited from VisionEgg.Textures.TextureStimulusBaseClass
                          Default: (GL enum determined at runtime)

    Constant Parameters
    ===================
    internal_format   -- format with which OpenGL uses texture data (OpenGL data type enum) (Integer)
                         Default: GL_RGB (6407)
    mipmaps_enabled   -- Are mipmaps enabled? (Boolean)
                         Default: True
    shrink_texture_ok -- Allow automatic shrinking of texture if too big? (Boolean)
                         Default: False
    """

    parameters_and_defaults = {
        'on':(True,
              ve_types.Boolean),
        'contrast':(1.0,
                    ve_types.Real),
        'center_azimuth':(0.0, # 0=right, 90=right
                          ve_types.Real),
        'center_elevation':(0.0, # 0=right, 90=up
                            ve_types.Real),

        # Changing these parameters will cause re-computation of display list (may cause frame skip)
        'radius':(1.0,
                  ve_types.Real),
        'slices':(30,
                  ve_types.UnsignedInteger),
        'stacks':(30,
                  ve_types.UnsignedInteger)}

    __slots__ = (
        'cached_display_list',
        '_cached_radius',
        '_cached_slices',
        '_cached_stacks',
        )

    def __init__(self,**kw):
        VisionEgg.Textures.TextureStimulusBaseClass.__init__(self,**kw)
        self.cached_display_list = gl.glGenLists(1) # Allocate a new display list
        self.__rebuild_display_list()

    def __rebuild_display_list(self):
        p = self.parameters

        s_gain = p.texture.buf_rf - p.texture.buf_lf
        t_gain = p.texture.buf_bf - p.texture.buf_tf

        s_offs = p.texture.buf_lf
        t_offs = p.texture.buf_tf

        gl.glNewList(self.cached_display_list,gl.GL_COMPILE)
        gl.glBegin(gl.GL_QUADS)

        for stack in range(p.stacks):
            stack_upper_frac = float(stack+1)/p.stacks
            stack_lower_frac = float(stack)/p.stacks
            theta_upper = stack_upper_frac * math.pi
            theta_lower = stack_lower_frac * math.pi
            y_upper = p.radius * math.cos( theta_upper )
            w_upper = p.radius * math.sin( theta_upper )
            y_lower = p.radius * math.cos( theta_lower )
            w_lower = p.radius * math.sin( theta_lower )
            for slice in range(p.slices):
                slice_start_frac = float(slice)/p.slices
                slice_stop_frac = float(slice+1)/p.slices
                phi_start = slice_start_frac * 2 * math.pi
                phi_stop = slice_stop_frac * 2 * math.pi
                x_start_upper = w_upper * math.cos(phi_start)
                x_start_lower = w_lower * math.cos(phi_start)
                x_stop_upper = w_upper * math.cos(phi_stop)
                x_stop_lower = w_lower * math.cos(phi_stop)
                z_start_upper = w_upper * math.sin(phi_start)
                z_start_lower = w_lower * math.sin(phi_start)
                z_stop_upper = w_upper * math.sin(phi_stop)
                z_stop_lower = w_lower * math.sin(phi_stop)

                tex_l = slice_start_frac*s_gain+s_offs
                tex_r = slice_stop_frac*s_gain+s_offs
                tex_b = stack_lower_frac*t_gain+t_offs
                tex_t = stack_upper_frac*t_gain+t_offs

                gl.glTexCoord2f(tex_l,tex_t)
                gl.glVertex3f(x_start_upper, y_upper, z_start_upper)

                gl.glTexCoord2f(tex_r,tex_t)
                gl.glVertex3f(x_stop_upper, y_upper, z_stop_upper)

                gl.glTexCoord2f(tex_r,tex_b)
                gl.glVertex3f(x_stop_lower, y_lower, z_stop_lower)

                gl.glTexCoord2f(tex_l,tex_b)
                gl.glVertex3f(x_start_lower, y_lower, z_start_lower)

        gl.glEnd()
        gl.glEndList()
        self._cached_radius = p.radius
        self._cached_slices = p.slices
        self._cached_stacks = p.stacks

    def draw(self):
    	"""Redraw the scene on every frame.
        """
        p = self.parameters

        if self._cached_radius != p.radius or self._cached_slices != p.slices or self._cached_stacks != p.stacks:
            self.__rebuild_display_list()

        if p.on:
            # Set OpenGL state variables
            gl.glEnable( gl.GL_DEPTH_TEST )
            gl.glEnable( gl.GL_TEXTURE_2D )  # Make sure textures are drawn
            gl.glEnable( gl.GL_BLEND ) # Contrast control implemented through blending

            # All of the contrast control stuff is somewhat arcane and
            # not very clear from reading the code, so here is how it
            # works in English. (Not that it makes it any more clear!)
            #
            # In the final "textured fragment" (before being blended
            # to the framebuffer), the color values are equal to those
            # of the texture (with the exception of pixels around the
            # edges which have their amplitudes reduced due to
            # anti-aliasing and are intermediate between the color of
            # the texture and mid-gray), and the alpha value is set to
            # the contrast.  Blending occurs, and by choosing the
            # appropriate values for glBlendFunc, adds the product of
            # fragment alpha (contrast) and fragment color to the
            # product of one minus fragment alpha (contrast) and what
            # was already in the framebuffer.

            gl.glBlendFunc( gl.GL_SRC_ALPHA, gl.GL_ONE_MINUS_SRC_ALPHA )

            gl.glTexEnvi(gl.GL_TEXTURE_ENV, gl.GL_TEXTURE_ENV_MODE, gl.GL_DECAL)

            # clear modelview matrix
            gl.glMatrixMode(gl.GL_MODELVIEW)
            gl.glPushMatrix()
            gl.glColor4f(0.5,0.5,0.5,p.contrast) # Set the polygons' fragment color (implements contrast)

            if not self.constant_parameters.mipmaps_enabled:
                if p.texture_min_filter in VisionEgg.Textures.TextureStimulusBaseClass._mipmap_modes:
                    raise RuntimeError("Specified a mipmap mode in texture_min_filter, but mipmaps not enabled.")
            self.texture_object.set_min_filter( p.texture_min_filter )
            self.texture_object.set_mag_filter( p.texture_mag_filter )
            self.texture_object.set_wrap_mode_s( p.texture_wrap_s )
            self.texture_object.set_wrap_mode_t( p.texture_wrap_t )

            # center the texture map
            gl.glRotatef(p.center_azimuth,0.0,-1.0,0.0)
            gl.glRotatef(p.center_elevation,1.0,0.0,0.0)

            gl.glCallList(self.cached_display_list)
            gl.glPopMatrix()

class SphereGrating(VisionEgg.Gratings.LuminanceGratingCommon):
    """Map 2D sinusoidal grating onto sphere.

    Parameters
    ==========
    bit_depth                       -- precision with which grating is calculated and sent to OpenGL (UnsignedInteger)
                                       Inherited from VisionEgg.Gratings.LuminanceGratingCommon
                                       Default: 8
    check_texture_size              -- (Boolean)
                                       Default: True
    contrast                        -- (Real)
                                       Default: 1.0
    grating_center_azimuth          -- (Real)
                                       Default: 0.0
    grating_center_elevation        -- (Real)
                                       Default: 0.0
    ignore_time                     -- (Boolean)
                                       Default: False
    lowpass_cutoff_cycles_per_texel -- helps prevent spatial aliasing (Real)
                                       Default: 0.5
    min_filter                      -- OpenGL filter enum (Integer)
                                       Default: GL_LINEAR (9729)
    num_samples                     -- (UnsignedInteger)
                                       Default: 1024
    on                              -- (Boolean)
                                       Default: True
    orientation                     -- (Real)
                                       Default: 0.0
    phase_at_t0                     -- (Real)
                                       Default: 0.0
    radius                          -- (Real)
                                       Default: 1.0
    slices                          -- (UnsignedInteger)
                                       Default: 30
    spatial_freq_cpd                -- (Real)
                                       Default: 0.0277777777778
    stacks                          -- (UnsignedInteger)
                                       Default: 30
    t0_time_sec_absolute            -- (Real)
                                       Default: (determined at runtime)
    temporal_freq_hz                -- (Real)
                                       Default: 5.0
    """

    parameters_and_defaults = {
        'on':(True,
              ve_types.Boolean),
        'contrast':(1.0,
                    ve_types.Real),
        'spatial_freq_cpd':(1.0/36.0, # cycles/degree
                            ve_types.Real),
        'temporal_freq_hz':(5.0, # hz
                            ve_types.Real),
        't0_time_sec_absolute':(None,
                                ve_types.Real),
        'ignore_time':(False, # ignore temporal frequency variable - allow control purely with phase_at_t0
                       ve_types.Boolean),
        'phase_at_t0':(0.0,  # degrees
                       ve_types.Real),
        'orientation':(0.0,  # 0=right, 90=up
                       ve_types.Real),
        'grating_center_azimuth':(0.0, # 0=right, 90=down
                                  ve_types.Real),
        'grating_center_elevation':(0.0, # 0=right, 90=down
                                    ve_types.Real),
        'check_texture_size':(True, # slows down drawing but catches errors
                              ve_types.Boolean),
        'lowpass_cutoff_cycles_per_texel':(0.5,
                                           ve_types.Real,
                                           'helps prevent spatial aliasing'),
        'min_filter':(gl.GL_LINEAR,
                      ve_types.Integer,
                      "OpenGL filter enum",
                      VisionEgg.ParameterDefinition.OPENGL_ENUM),
        # changing this parameters causes re-drawing of the texture object and may cause frame skipping
        'num_samples':(1024,  # number of spatial samples, should be a power of 2
                       ve_types.UnsignedInteger),
        # Changing these parameters will cause re-computation of display list (may cause frame skip)
        'radius':(1.0,
                  ve_types.Real),
        'slices':(30,
                  ve_types.UnsignedInteger),
        'stacks':(30,
                  ve_types.UnsignedInteger),
        }

    __slots__ = (
        'texture_object_id',
        'cached_display_list_id',
        '_cached_num_samples',
        '_cached_radius',
        '_cached_slices',
        '_cached_stacks',
        )

    def __init__(self,**kw):
        VisionEgg.Gratings.LuminanceGratingCommon.__init__(self,**kw)

        if self.parameters.t0_time_sec_absolute is None:
            self.parameters.t0_time_sec_absolute = VisionEgg.time_func()

        self.texture_object_id = gl.glGenTextures(1) # Allocate a new texture object
        self.__rebuild_texture_object()

        self.cached_display_list_id = gl.glGenLists(1) # Allocate a new display list
        self.__rebuild_display_list()

    def __rebuild_texture_object(self):
        gl.glBindTexture(gl.GL_TEXTURE_1D,self.texture_object_id)
        p = self.parameters # shorthand

        # Do error-checking on texture to make sure it will load
        max_dim = gl.glGetIntegerv(gl.GL_MAX_TEXTURE_SIZE)
        if p.num_samples > max_dim:
            raise VisionEgg.Gratings.NumSamplesTooLargeError("Grating num_samples too large for video system.\nOpenGL reports maximum size of %d"%(max_dim,))

        self.calculate_bit_depth_dependencies()

        l = 0.0
        r = 360.0

        mipmap_level = 0
        this_mipmap_level_num_samples = p.num_samples
        while this_mipmap_level_num_samples >= 1:
            inc = 360.0/float(this_mipmap_level_num_samples) # degrees per pixel
            cycles_per_texel = p.spatial_freq_cpd * inc
            if cycles_per_texel < p.lowpass_cutoff_cycles_per_texel: # sharp cutoff lowpass filter
                # below cutoff frequency - draw sine wave
                if p.ignore_time:
                    phase = p.phase_at_t0
                else:
                    t_var = VisionEgg.time_func() - p.t0_time_sec_absolute
                    phase = t_var*p.temporal_freq_hz*360.0 + p.phase_at_t0
                floating_point_sin = Numeric.sin(2.0*math.pi*p.spatial_freq_cpd*Numeric.arange(l,r,inc,'d')-(phase/180.0*math.pi))*0.5*p.contrast+0.5
                floating_point_sin = Numeric.clip(floating_point_sin,0.0,1.0) # allow square wave generation if contrast > 1
                texel_data = (floating_point_sin*self.max_int_val).astype(self.numpy_dtype).tostring()
            else:
                # above cutoff frequency - blank
                texel_data = (self.max_int_val*0.5)*Numeric.ones((this_mipmap_level_num_samples,),self.numpy_dtype)

            if p.check_texture_size:
                # Because the MAX_TEXTURE_SIZE method is insensitive to the current
                # state of the video system, another check must be done using
                # "proxy textures".
                gl.glTexImage1D(gl.GL_PROXY_TEXTURE_1D,  # target
                                mipmap_level,            # level
                                self.gl_internal_format, # video RAM internal format: RGB
                                this_mipmap_level_num_samples,        # width
                                0,                       # border
                                self.format,             # format of image data
                                self.gl_type,            # type of image data
                                texel_data)              # texel data
                if gl.glGetTexLevelParameteriv(gl.GL_PROXY_TEXTURE_1D,0,gl.GL_TEXTURE_WIDTH) == 0:
                    raise NumSamplesTooLargeError("Grating num_samples is too wide for your video system!")

            # If we got here, it worked and we can load the texture for real.
            gl.glTexImage1D(gl.GL_TEXTURE_1D,        # target
                            mipmap_level,            # level
                            self.gl_internal_format, # video RAM internal format: RGB
                            this_mipmap_level_num_samples,        # width
                            0,                       # border
                            self.format,             # format of image data
                            self.gl_type,            # type of image data
                            texel_data)              # texel data

            # prepare for next mipmap level
            this_mipmap_level_num_samples = this_mipmap_level_num_samples/2 # integer division
            mipmap_level += 1

        # Set some texture object defaults
        gl.glTexParameteri(gl.GL_TEXTURE_1D,gl.GL_TEXTURE_WRAP_S,gl.GL_REPEAT)
        gl.glTexParameteri(gl.GL_TEXTURE_1D,gl.GL_TEXTURE_WRAP_T,gl.GL_REPEAT)
        gl.glTexParameteri(gl.GL_TEXTURE_1D,gl.GL_TEXTURE_MAG_FILTER,gl.GL_LINEAR)
        gl.glTexParameteri(gl.GL_TEXTURE_1D,gl.GL_TEXTURE_MIN_FILTER,p.min_filter)
        self._cached_num_samples = p.num_samples

    def __rebuild_display_list(self):
        gl.glNewList(self.cached_display_list_id,gl.GL_COMPILE)

        p = self.parameters
        gl.glBegin(gl.GL_QUADS)

        for stack in range(p.stacks):
            stack_upper_frac = float(stack+1)/p.stacks
            stack_lower_frac = float(stack)/p.stacks
            theta_upper = stack_upper_frac * math.pi
            theta_lower = stack_lower_frac * math.pi
            y_upper = p.radius * math.cos( theta_upper )
            w_upper = p.radius * math.sin( theta_upper )
            y_lower = p.radius * math.cos( theta_lower )
            w_lower = p.radius * math.sin( theta_lower )
            for slice in range(p.slices):
                slice_start_frac = float(slice)/p.slices
                slice_stop_frac = float(slice+1)/p.slices
                phi_start = slice_start_frac * 2 * math.pi
                phi_stop = slice_stop_frac * 2 * math.pi
                x_start_upper = w_upper * math.cos(phi_start)
                x_start_lower = w_lower * math.cos(phi_start)
                x_stop_upper = w_upper * math.cos(phi_stop)
                x_stop_lower = w_lower * math.cos(phi_stop)
                z_start_upper = w_upper * math.sin(phi_start)
                z_start_lower = w_lower * math.sin(phi_start)
                z_stop_upper = w_upper * math.sin(phi_stop)
                z_stop_lower = w_lower * math.sin(phi_stop)

                tex_l = slice_start_frac
                tex_r = slice_stop_frac
                tex_b = 0.0#stack_lower_frac
                tex_t = 1.0#stack_upper_frac

                gl.glTexCoord2f(tex_l,tex_t)
                gl.glVertex3f(x_start_upper, y_upper, z_start_upper)

                gl.glTexCoord2f(tex_r,tex_t)
                gl.glVertex3f(x_stop_upper, y_upper, z_stop_upper)

                gl.glTexCoord2f(tex_r,tex_b)
                gl.glVertex3f(x_stop_lower, y_lower, z_stop_lower)

                gl.glTexCoord2f(tex_l,tex_b)
                gl.glVertex3f(x_start_lower, y_lower, z_start_lower)

        gl.glEnd()
        gl.glEndList()
        self._cached_radius = p.radius
        self._cached_slices = p.slices
        self._cached_stacks = p.stacks

    def draw(self):
    	"""Redraw the scene on every frame.
        """
        p = self.parameters

        if self._cached_radius != p.radius or self._cached_slices != p.slices or self._cached_stacks != p.stacks:
            self.__rebuild_display_list()

        if self._cached_num_samples != p.num_samples:
            self.__rebuild_texture_object()

        if p.on:
            if p.bit_depth != self.cached_bit_depth:
                self.calculate_bit_depth_dependencies()
            # Set OpenGL state variables
            gl.glEnable( gl.GL_DEPTH_TEST )
            gl.glEnable( gl.GL_TEXTURE_1D )  # Make sure textures are drawn
            gl.glDisable( gl.GL_TEXTURE_2D )
            gl.glDisable( gl.GL_BLEND )

            gl.glBindTexture(gl.GL_TEXTURE_1D,self.texture_object_id)
            gl.glTexParameteri(gl.GL_TEXTURE_1D,gl.GL_TEXTURE_MIN_FILTER,p.min_filter)

            l = 0.0
            r = 360.0

            mipmap_level = 0
            this_mipmap_level_num_samples = p.num_samples
            while this_mipmap_level_num_samples >= 1:
                inc = 360.0/float(this_mipmap_level_num_samples)# degrees per pixel
                cycles_per_texel = p.spatial_freq_cpd * inc
                if cycles_per_texel < p.lowpass_cutoff_cycles_per_texel: # sharp cutoff lowpass filter
                    if p.ignore_time:
                        phase = p.phase_at_t0
                    else:
                        t_var = VisionEgg.time_func() - p.t0_time_sec_absolute
                        phase = t_var*p.temporal_freq_hz*360.0 + p.phase_at_t0
                    floating_point_sin = Numeric.sin(2.0*math.pi*p.spatial_freq_cpd*Numeric.arange(l,r,inc,'d')-(phase/180.0*math.pi))*0.5*p.contrast+0.5
                    floating_point_sin = Numeric.clip(floating_point_sin,0.0,1.0) # allow square wave generation if contrast > 1
                    texel_data = (floating_point_sin*self.max_int_val).astype(self.numpy_dtype).tostring()
                else:
                    blank = 0.5*Numeric.ones((this_mipmap_level_num_samples,),'d')
                    texel_data = (blank*self.max_int_val).astype(self.numpy_dtype).tostring()

                gl.glTexSubImage1D(gl.GL_TEXTURE_1D,           # target
                                mipmap_level,                  # level
                                0,                             # x offset
                                this_mipmap_level_num_samples, # width
                                self.format,                   # data format
                                self.gl_type,                  # data type
                                texel_data)

                # prepare for next mipmap level
                this_mipmap_level_num_samples = this_mipmap_level_num_samples/2 # integer division
                mipmap_level += 1

            gl.glTexEnvi(gl.GL_TEXTURE_ENV, gl.GL_TEXTURE_ENV_MODE, gl.GL_REPLACE)

            # clear modelview matrix
            gl.glMatrixMode(gl.GL_MODELVIEW)
            gl.glPushMatrix()
            # center the grating
            gl.glRotatef(p.grating_center_azimuth,0.0,-1.0,0.0)
            gl.glRotatef(p.grating_center_elevation,1.0,0.0,0.0)

            # do the orientation
            gl.glRotatef(p.orientation,0.0,0.0,1.0)

            gl.glCallList(self.cached_display_list_id)

            gl.glDisable( gl.GL_TEXTURE_1D )
            gl.glPopMatrix()

class SphereWindow(VisionEgg.Gratings.LuminanceGratingCommon):
    """This draws an opaque sphere with a single window in it.

    This is useful when you need to have a viewport on a 3D scene.

    Parameters
    ==========
    bit_depth                     -- precision with which grating is calculated and sent to OpenGL (UnsignedInteger)
                                     Inherited from VisionEgg.Gratings.LuminanceGratingCommon
                                     Default: 8
    num_s_samples                 -- (UnsignedInteger)
                                     Default: 512
    num_t_samples                 -- (UnsignedInteger)
                                     Default: 512
    on                            -- (Boolean)
                                     Default: True
    opaque_color                  -- (Sequence4 of Real)
                                     Default: (0.5, 0.5, 0.5, 0.0)
    radius                        -- (Real)
                                     Default: 1.0
    slices                        -- (UnsignedInteger)
                                     Default: 30
    stacks                        -- (UnsignedInteger)
                                     Default: 30
    window_center_azimuth         -- (Real)
                                     Default: 0.0
    window_center_elevation       -- (Real)
                                     Default: 0.0
    window_shape                  -- can be 'circle', 'gaussian', or 'lat-long rectangle' (String)
                                     Default: gaussian
    window_shape_parameter2       -- (currently only used for) height of lat-long rectangle (in degrees) (Real)
                                     Default: 30.0
    window_shape_radius_parameter -- radius of circle, sigma of gaussian, width of lat-long rectangle (in degrees) (Real)
                                     Default: 36.0
    """

    parameters_and_defaults = {
        'on':(True,
              ve_types.Boolean),
        'window_center_elevation':(0.0,
                                   ve_types.Real),
        'window_center_azimuth':(0.0,
                                 ve_types.Real),
        'opaque_color':((0.5,0.5,0.5,0.0),
                        ve_types.Sequence4(ve_types.Real)),
        # changing these parameters causes re-drawing of the texture object and may cause frame skipping
        'window_shape':('gaussian', # can be 'circle' or 'gaussian'
                        ve_types.String,
                        "can be 'circle', 'gaussian', or 'lat-long rectangle'",
                        ),
        'window_shape_radius_parameter':(36.0,
                                         ve_types.Real,
                                         'radius of circle, sigma of gaussian, width of lat-long rectangle (in degrees)',
                                         ),
        'window_shape_parameter2':(30.0,
                                   ve_types.Real,
                                   '(currently only used for) height of lat-long rectangle (in degrees)',
                                   ),
        'num_s_samples':(512,  # number of horizontal spatial samples, should be a power of 2
                         ve_types.UnsignedInteger),
        'num_t_samples':(512,  # number of vertical spatial samples, should be a power of 2
                         ve_types.UnsignedInteger),
        # Changing these parameters will cause re-computation of display list (may cause frame skip)
        'radius':(1.0, # XXX could modify code below to use scaling, thus avoiding need for recomputation
                  ve_types.Real),
        'slices':(30,
                  ve_types.UnsignedInteger),
        'stacks':(30,
                  ve_types.UnsignedInteger),
        }

    __slots__ = (
        'texture_object_id',
        'windowed_display_list_id',
        'opaque_display_list_id',
        '_cached_window_shape',
        '_cached_shape_radius_parameter',
        '_cached_shape_parameter2',
        '_cached_num_s_samples',
        '_cached_num_t_samples',
        '_cached_radius',
        '_cached_slices',
        '_cached_stacks',
        '_texture_s_is_azimuth',
        )

    def __init__(self, **kw):
        VisionEgg.Gratings.LuminanceGratingCommon.__init__(self, **kw )

        p = self.parameters

        # set self._texture_s_is_azimuth in advance
        if p.window_shape == 'lat-long rectangle':
            self._texture_s_is_azimuth = True
        else:
            self._texture_s_is_azimuth = False

        self.texture_object_id = gl.glGenTextures(1)
        self.__rebuild_texture_object()

        self.windowed_display_list_id = gl.glGenLists(1) # Allocate a new display list
        self.opaque_display_list_id = gl.glGenLists(1) # Allocate a new display list
        self.__rebuild_display_lists()

    def __rebuild_texture_object(self):
        gl.glBindTexture(gl.GL_TEXTURE_2D,self.texture_object_id)
        p = self.parameters

        # Do error-checking on texture to make sure it will load
        max_dim = gl.glGetIntegerv(gl.GL_MAX_TEXTURE_SIZE)
        if p.num_s_samples > max_dim:
            raise VisionEgg.Gratings.NumSamplesTooLargeError("SphereWindow num_s_samples too large for video system.\nOpenGL reports maximum size of %d"%(max_dim,))
        if p.num_t_samples > max_dim:
            raise VisionEgg.Gratings.NumSamplesTooLargeError("SphereWindow num_t_samples too large for video system.\nOpenGL reports maximum size of %d"%(max_dim,))

        self.calculate_bit_depth_dependencies()
        self.gl_internal_format = gl.GL_ALPHA # change from luminance to alpha
        self.format = gl.GL_ALPHA

        # texture coordinates are Mercator: (determined when building display list)
        #   s: x within sphere
        #   t: z within sphere

        if p.window_shape == 'circle':
            if self._texture_s_is_azimuth:
                self.__rebuild_display_lists()

            # XXX this is aliased
            s_axis = (Numeric.arange(p.num_s_samples)/float(p.num_s_samples)-0.5)**2
            t_axis = (Numeric.arange(p.num_t_samples)/float(p.num_t_samples)-0.5)**2
            mask = s_axis[Numeric.NewAxis,:] + t_axis[:,Numeric.NewAxis]
            angle_deg = min(180,p.window_shape_radius_parameter) # clip angle
            cartesian_radius = 0.5*math.sin(p.window_shape_radius_parameter/180.0*math.pi)
            floating_point_window = Numeric.less(mask,cartesian_radius**2)
        elif p.window_shape == 'gaussian':
            if self._texture_s_is_azimuth:
                self.__rebuild_display_lists()

            MIN_EXP = -745.0
            MAX_EXP =  709.0

            s = Numeric.arange(0.0,p.num_s_samples,1.0,'f')/p.num_s_samples
            t = Numeric.arange(0.0,p.num_t_samples,1.0,'f')/p.num_t_samples
            sigma_normalized = p.window_shape_radius_parameter / 90.0 * 0.5

            check_s = -((s-0.5)**2/(2.0*sigma_normalized**2))
            try:
                # some platforms raise OverflowError when doing this on small numbers
                val_s = Numeric.exp( check_s )
            except OverflowError:
                check_s = Numeric.clip(check_s,MIN_EXP,MAX_EXP)
                val_s = Numeric.exp( check_s )

            check_t = -((t-0.5)**2/(2.0*sigma_normalized**2))
            try:
                val_t = Numeric.exp( check_t )
            except OverflowError:
                check_t = Numeric.clip(check_t,MIN_EXP,MAX_EXP)
                val_t = Numeric.exp( check_t )
            floating_point_window = Numeric.outerproduct(val_t,val_s)
        elif  p.window_shape == 'lat-long rectangle':
            if not self._texture_s_is_azimuth:
                self.__rebuild_display_lists()

            # s coordinate represents -90 to +90 degrees (azimuth).
            s_axis = (Numeric.arange(p.num_s_samples)/float(p.num_s_samples)-0.5)*180
            s_axis = Numeric.less( abs(s_axis), p.window_shape_radius_parameter*0.5 )

            # t coordinate represents height.
            # Convert angle to height.
            angle_deg = min(90,p.window_shape_parameter2*0.5) # clip angle
            desired_height = math.sin(angle_deg/180.0*math.pi)*0.5
            t_axis = Numeric.arange(p.num_t_samples)/float(p.num_t_samples)-0.5
            t_axis = Numeric.less(abs(t_axis),desired_height)
            floating_point_window = Numeric.outerproduct(t_axis,s_axis)
        else:
            raise RuntimeError('Unknown window_shape "%s"'%(p.window_shape,))
        texel_data = (floating_point_window * self.max_int_val).astype(self.numpy_dtype).tostring()

        # Because the MAX_TEXTURE_SIZE method is insensitive to the current
        # state of the video system, another check must be done using
        # "proxy textures".
        gl.glTexImage2D(gl.GL_PROXY_TEXTURE_2D,      # target
                     0,                              # mipmap_level
                     self.gl_internal_format,        # video RAM internal format
                     p.num_s_samples,  # width
                     p.num_t_samples,  # height
                     0,                              # border
                     self.format,                    # format of image data
                     self.gl_type,                   # type of image data
                     texel_data)                     # texel data
        if (gl.glGetTexLevelParameteriv(gl.GL_PROXY_TEXTURE_2D, # Need PyOpenGL >= 2.0
                                        0,
                                        gl.GL_TEXTURE_WIDTH) == 0) or (
            gl.glGetTexLevelParameteriv(gl.GL_PROXY_TEXTURE_2D,
                                        0,
                                        gl.GL_TEXTURE_HEIGHT) == 0):
            raise VisionEgg.Gratings.NumSamplesTooLargeError("SphereWindow num_s_samples or num_t_samples is too large for your video system!")

        gl.glTexImage2D(gl.GL_TEXTURE_2D,      # target
                        0,                              # mipmap_level
                        self.gl_internal_format,        # video RAM internal format
                        p.num_s_samples,  # width
                        p.num_t_samples,  # height
                        0,                              # border
                        self.format,                    # format of image data
                        self.gl_type,                   # type of image data
                        texel_data)                     # texel data

        # Set some texture object defaults
        gl.glTexParameteri(gl.GL_TEXTURE_2D,gl.GL_TEXTURE_WRAP_S,gl.GL_CLAMP_TO_EDGE)
        gl.glTexParameteri(gl.GL_TEXTURE_2D,gl.GL_TEXTURE_WRAP_T,gl.GL_CLAMP_TO_EDGE)
        gl.glTexParameteri(gl.GL_TEXTURE_2D,gl.GL_TEXTURE_MAG_FILTER,gl.GL_LINEAR)
        gl.glTexParameteri(gl.GL_TEXTURE_2D,gl.GL_TEXTURE_MIN_FILTER,gl.GL_LINEAR)

        self._cached_window_shape = p.window_shape
        self._cached_shape_radius_parameter = p.window_shape_radius_parameter
        self._cached_shape_parameter2 = p.window_shape_parameter2
        self._cached_num_s_samples = p.num_s_samples
        self._cached_num_t_samples = p.num_t_samples

    def __rebuild_display_lists(self):
        gl.glMatrixMode(gl.GL_MODELVIEW)
        gl.glPushMatrix()

        p = self.parameters

        if p.window_shape == 'lat-long rectangle':
            self._texture_s_is_azimuth = True
        else:
            self._texture_s_is_azimuth = False

        gl.glNewList(self.windowed_display_list_id,gl.GL_COMPILE)

        gl.glBegin(gl.GL_QUADS)

        for stack in range(p.stacks):
            stack_upper_frac = float(stack+1)/p.stacks
            stack_lower_frac = float(stack)/p.stacks
            theta_upper = stack_upper_frac * math.pi
            theta_lower = stack_lower_frac * math.pi
            y_upper = p.radius * math.cos( theta_upper )
            w_upper = p.radius * math.sin( theta_upper )
            y_lower = p.radius * math.cos( theta_lower )
            w_lower = p.radius * math.sin( theta_lower )
            for slice in range(p.slices/2,p.slices): # only do half of sphere (other half has no window)
                slice_start_frac = float(slice)/p.slices
                slice_stop_frac = float(slice+1)/p.slices
                phi_start = slice_start_frac * 2 * math.pi
                phi_stop = slice_stop_frac * 2 * math.pi
                x_start_upper = w_upper * math.cos(phi_start)
                x_start_lower = w_lower * math.cos(phi_start)
                x_stop_upper = w_upper * math.cos(phi_stop)
                x_stop_lower = w_lower * math.cos(phi_stop)
                z_start_upper = w_upper * math.sin(phi_start)
                z_start_lower = w_lower * math.sin(phi_start)
                z_stop_upper = w_upper * math.sin(phi_stop)
                z_stop_lower = w_lower * math.sin(phi_stop)

                o = 0.5
                g = 0.5 / p.radius

                if self._texture_s_is_azimuth:
                    tex_s_start = slice_start_frac*2-1
                    tex_s_stop = slice_stop_frac*2-1
                else:
                    tex_s_start = x_start_upper*g+o
                    tex_s_stop = x_stop_upper*g+o

                gl.glTexCoord2f(tex_s_start,y_upper*g+o)
                gl.glVertex3f(x_start_upper, y_upper, z_start_upper)

                gl.glTexCoord2f(tex_s_stop,y_upper*g+o)
                gl.glVertex3f(x_stop_upper, y_upper, z_stop_upper)

                gl.glTexCoord2f(tex_s_stop,y_lower*g+o)
                gl.glVertex3f(x_stop_lower, y_lower, z_stop_lower)

                gl.glTexCoord2f(tex_s_start,y_lower*g+o)
                gl.glVertex3f(x_start_lower, y_lower, z_start_lower)

        gl.glEnd()
        gl.glEndList()

        gl.glNewList(self.opaque_display_list_id,gl.GL_COMPILE)

        gl.glBegin(gl.GL_QUADS)

        for stack in range(p.stacks):
            stack_upper_frac = float(stack+1)/p.stacks
            stack_lower_frac = float(stack)/p.stacks
            theta_upper = stack_upper_frac * math.pi
            theta_lower = stack_lower_frac * math.pi
            y_upper = p.radius * math.cos( theta_upper )
            w_upper = p.radius * math.sin( theta_upper )
            y_lower = p.radius * math.cos( theta_lower )
            w_lower = p.radius * math.sin( theta_lower )
            for slice in range(p.slices/2): # half of sphere with no window
                slice_start_frac = float(slice)/p.slices
                slice_stop_frac = float(slice+1)/p.slices
                phi_start = slice_start_frac * 2 * math.pi
                phi_stop = slice_stop_frac * 2 * math.pi
                x_start_upper = w_upper * math.cos(phi_start)
                x_start_lower = w_lower * math.cos(phi_start)
                x_stop_upper = w_upper * math.cos(phi_stop)
                x_stop_lower = w_lower * math.cos(phi_stop)
                z_start_upper = w_upper * math.sin(phi_start)
                z_start_lower = w_lower * math.sin(phi_start)
                z_stop_upper = w_upper * math.sin(phi_stop)
                z_stop_lower = w_lower * math.sin(phi_stop)

                gl.glVertex3f(x_start_upper, y_upper, z_start_upper)

                gl.glVertex3f(x_stop_upper, y_upper, z_stop_upper)

                gl.glVertex3f(x_stop_lower, y_lower, z_stop_lower)

                gl.glVertex3f(x_start_lower, y_lower, z_start_lower)

        gl.glEnd()
        gl.glEndList()
        self._cached_radius = p.radius
        self._cached_slices = p.slices
        self._cached_stacks = p.stacks
        gl.glPopMatrix()

    def draw(self):
    	"""Redraw the scene on every frame.
        """
        p = self.parameters

        if self._cached_radius != p.radius or self._cached_slices != p.slices or self._cached_stacks != p.stacks:
            self.__rebuild_display_lists()

        if self._cached_window_shape != p.window_shape or self._cached_shape_radius_parameter != p.window_shape_radius_parameter:
            self.__rebuild_texture_object()

        if p.window_shape == 'lat-long rectangle' and self._cached_shape_parameter2 != p.window_shape_parameter2:
            self.__rebuild_texture_object()

        if self._cached_num_s_samples != p.num_s_samples or self._cached_num_t_samples != p.num_t_samples:
            self.__rebuild_texture_object()

        if p.on:
            #gl.glPolygonMode( gl.GL_FRONT_AND_BACK, gl.GL_LINE )
            if p.bit_depth != self.cached_bit_depth:
                self.calculate_bit_depth_dependencies()
                self.gl_internal_format = gl.GL_ALPHA # change from luminance to alpha
                self.format = gl.GL_ALPHA
            # Set OpenGL state variables
            gl.glEnable( gl.GL_DEPTH_TEST )
            gl.glEnable( gl.GL_TEXTURE_2D )
            gl.glEnable( gl.GL_BLEND )

            gl.glBlendFunc( gl.GL_ONE_MINUS_SRC_ALPHA, gl.GL_SRC_ALPHA ) # alpha 1.0 = transparent

            gl.glBindTexture(gl.GL_TEXTURE_2D,self.texture_object_id)
            gl.glColor4f( *p.opaque_color )
            gl.glTexEnvi(gl.GL_TEXTURE_ENV, gl.GL_TEXTURE_ENV_MODE, gl.GL_REPLACE)

            # clear modelview matrix
            gl.glMatrixMode(gl.GL_MODELVIEW)
            gl.glPushMatrix()

            # do the window position
            gl.glRotatef(p.window_center_azimuth,0.0,-1.0,0.0)
            gl.glRotatef(p.window_center_elevation,1.0,0.0,0.0)

            gl.glCallList(self.windowed_display_list_id)
            gl.glCallList(self.opaque_display_list_id)
            gl.glPopMatrix()

