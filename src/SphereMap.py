"""Stimuli drawn as texture maps on inside of sphere"""

# Copyright (c) 2002 Andrew Straw.  Distributed under the terms
# of the GNU Lesser General Public License (LGPL).

import math, types, string

import VisionEgg.Core
import VisionEgg.Textures
import VisionEgg.Gratings

import OpenGL.GL as gl                          #   main package

import Numeric  				# Numeric Python package
import Image

__version__ = VisionEgg.release_name
__cvs__ = string.split('$Revision$')[1]
__date__ = string.join(string.split('$Date$')[1:3], ' ')
__author__ = 'Andrew Straw <astraw@users.sourceforge.net>'

class SphereMap(VisionEgg.Textures.TextureStimulusBaseClass):
    """Mercator mapping of rectangular texture onto sphere."""
    parameters_and_defaults = {'contrast':(1.0,types.FloatType),
                               'on':(1,types.IntType),
                               'center_azimuth':(0.0,types.FloatType), # 0=right, 90=right
                               'center_elevation':(0.0,types.FloatType), # 0=right, 90=down
                               # Changing these parameters will cause re-computation of display list (may cause frame skip)
                               'radius':(1.0,types.FloatType),
                               'slices':(30,types.IntType),
                               'stacks':(30,types.IntType)}

    def __init__(self,texture=None,shrink_texture_ok=0,**kw):
        apply(VisionEgg.Textures.TextureStimulusBaseClass.__init__,(self,),kw)

        # Create an OpenGL texture object this instance "owns"
        self.texture_object = VisionEgg.Textures.TextureObject(dimensions=2)

        # Get texture data that goes into texture object
        if not isinstance(texture,VisionEgg.Textures.Texture):
            texture = VisionEgg.Textures.Texture(texture)
        self.texture = texture

        if not shrink_texture_ok:
            # send texture to OpenGL
            self.texture.load( self.texture_object,
                               build_mipmaps = self.constant_parameters.mipmaps_enabled )
        else:
            max_dim = gl.glGetIntegerv( gl.GL_MAX_TEXTURE_SIZE )
            resized = 0
            while max(self.texture.size) > max_dim:
                self.texture.make_half_size()
                resized = 1
            loaded_ok = 0
            while not loaded_ok:
                try:
                    # send texture to OpenGL
                    self.texture.load( self.texture_object,
                                       build_mipmaps = self.constant_parameters.mipmaps_enabled )
                    loaded_ok = 1
                except VisionEgg.Textures.TextureTooLargeError,x:
                    self.texture.make_half_size()
                    resized = 1
                    if resized:
                        VisionEgg.Core.message.add(
                            "Resized texture in %s to %d x %d"%(
                            str(self),self.texture.size[0],self.texture.size[1]),VisionEgg.Core.Message.WARNING)
                                                            
        self.cached_display_list = gl.glGenLists(1) # Allocate a new display list
        self.__rebuild_display_list()
        
    def __rebuild_display_list(self):
        gl.glMatrixMode(gl.GL_MODELVIEW)
        gl.glLoadIdentity()

        s_gain = self.texture.buf_rf - self.texture.buf_lf
        t_gain = self.texture.buf_bf - self.texture.buf_tf

        s_offs = self.texture.buf_lf
        t_offs = self.texture.buf_tf
        
        p = self.parameters

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
            gl.glLoadIdentity()

            gl.glColor(0.5,0.5,0.5,p.contrast) # Set the polygons' fragment color (implements contrast)

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

class SphereGrating(VisionEgg.Gratings.LuminanceGratingCommon):
    """Map 2D sinusoidal grating onto sphere."""
    parameters_and_defaults = {'on':(1,types.IntType),
                               'contrast':(1.0,types.FloatType),
                               'spatial_freq_cpd':(1.0/36.0,types.FloatType), # cycles/degree
                               'temporal_freq_hz':(5.0,types.FloatType), # hz
                               't0_time_sec_absolute':(None,types.FloatType),
                               'phase_at_t0':(0.0,types.FloatType), # degrees
                               'orientation':(0.0,types.FloatType), # 0=right, 90=down
                               'grating_center_azimuth':(0.0,types.FloatType), # 0=right, 90=down
                               'grating_center_elevation':(0.0,types.FloatType), # 0=right, 90=down
                               # changing this parameters causes re-drawing of the texture object and may cause frame skipping
                               'num_samples':(1024,types.IntType), # number of spatial samples, should be a power of 2
                               # Changing these parameters will cause re-computation of display list (may cause frame skip)
                               'radius':(1.0,types.FloatType),
                               'slices':(30,types.IntType),
                               'stacks':(30,types.IntType)}
    
    def __init__(self,**kw):
        apply(VisionEgg.Gratings.LuminanceGratingCommon.__init__,(self,),kw)

        if self.parameters.t0_time_sec_absolute is None:
            self.parameters.t0_time_sec_absolute = VisionEgg.timing_func()

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
        inc = 360.0/float(p.num_samples)
        phase = (VisionEgg.timing_func() - p.t0_time_sec_absolute)*p.temporal_freq_hz*360.0 + p.phase_at_t0
        floating_point_sin = Numeric.sin(2.0*math.pi*p.spatial_freq_cpd*Numeric.arange(l,r,inc,'d')-(phase/180.0*math.pi))*0.5*p.contrast+0.5
        floating_point_sin = Numeric.clip(floating_point_sin,0.0,1.0) # allow square wave generation if contrast > 1
        texel_data = (floating_point_sin*self.max_int_val).astype(self.numeric_type).tostring()

        # Because the MAX_TEXTURE_SIZE method is insensitive to the current
        # state of the video system, another check must be done using
        # "proxy textures".
        gl.glTexImage1D(gl.GL_PROXY_TEXTURE_1D,            # target
                     0,                              # level
                     self.gl_internal_format,                   # video RAM internal format: RGB
                     p.num_samples,    # width
                     0,                              # border
                     self.format,                   # format of image data
                     self.gl_type,               # type of image data
                     texel_data)                     # texel data
        if gl.glGetTexLevelParameteriv(gl.GL_PROXY_TEXTURE_1D,0,gl.GL_TEXTURE_WIDTH) == 0:
            raise NumSamplesTooLargeError("Grating num_samples is too wide for your video system!")
        
        # If we got here, it worked and we can load the texture for real.
        gl.glTexImage1D(gl.GL_TEXTURE_1D,            # target
                     0,                              # level
                     self.gl_internal_format,                   # video RAM internal format: RGB
                     p.num_samples,    # width
                     0,                              # border
                     self.format,                   # format of image data
                     self.gl_type,               # type of image data
                     texel_data)                     # texel data
        # Set some texture object defaults
        gl.glTexParameteri(gl.GL_TEXTURE_1D,gl.GL_TEXTURE_WRAP_S,gl.GL_REPEAT)
        gl.glTexParameteri(gl.GL_TEXTURE_1D,gl.GL_TEXTURE_WRAP_T,gl.GL_REPEAT)
        gl.glTexParameteri(gl.GL_TEXTURE_1D,gl.GL_TEXTURE_MAG_FILTER,gl.GL_LINEAR)
        gl.glTexParameteri(gl.GL_TEXTURE_1D,gl.GL_TEXTURE_MIN_FILTER,gl.GL_LINEAR)
        self._cached_num_samples = p.num_samples

    def __rebuild_display_list(self):
        gl.glMatrixMode(gl.GL_MODELVIEW)
        gl.glLoadIdentity()

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

            l = 0.0
            r = 360.0
            inc = 360.0/float(p.num_samples)
            phase = (VisionEgg.timing_func() - p.t0_time_sec_absolute)*p.temporal_freq_hz*360.0 + p.phase_at_t0
            floating_point_sin = Numeric.sin(2.0*math.pi*p.spatial_freq_cpd*Numeric.arange(l,r,inc,'d')-(phase/180.0*math.pi))*0.5*p.contrast+0.5
            floating_point_sin = Numeric.clip(floating_point_sin,0.0,1.0) # allow square wave generation if contrast > 1
            texel_data = (floating_point_sin*self.max_int_val).astype(self.numeric_type).tostring()
        
            gl.glTexSubImage1D(gl.GL_TEXTURE_1D, # target
                            0, # level
                            0, # x offset
                            p.num_samples, # width
                            self.format, # data format
                            self.gl_type, # data type
                            texel_data)
            
            gl.glTexEnvi(gl.GL_TEXTURE_ENV, gl.GL_TEXTURE_ENV_MODE, gl.GL_REPLACE)

            # clear modelview matrix
            gl.glMatrixMode(gl.GL_MODELVIEW)
            gl.glLoadIdentity()

            # center the grating
            gl.glRotatef(p.grating_center_azimuth,0.0,-1.0,0.0)
            gl.glRotatef(p.grating_center_elevation,1.0,0.0,0.0)

            # do the orientation
            gl.glRotatef(p.orientation,0.0,0.0,-1.0)

            gl.glCallList(self.cached_display_list_id)

            gl.glDisable( gl.GL_TEXTURE_1D )

class SphereWindow(VisionEgg.Gratings.LuminanceGratingCommon):

    parameters_and_defaults = {'on':(1,types.IntType),
                               'window_center_elevation':(0.0,types.FloatType),
                               'window_center_azimuth':(0.0,types.FloatType),
                               'opaque_color':((0.5,0.5,0.5,0.0),types.TupleType),
                               # changing these parameters causes re-drawing of the texture object and may cause frame skipping
                               'window_shape':('gaussian',types.StringType),
                               'window_shape_radius_parameter':(36.0,types.FloatType), # radius (degrees) for circle, sigma (degrees) for gaussian
                               'num_s_samples':(512, types.IntType), # number of horizontal spatial samples, should be a power of 2
                               'num_t_samples':(512, types.IntType), # number of vertical spatial samples, should be a power of 2
                               # Changing these parameters will cause re-computation of display list (may cause frame skip)
                               'radius':(1.0,types.FloatType),
                               'slices':(30,types.IntType),
                               'stacks':(30,types.IntType),
                               }
    
    def __init__(self, **kw):
        apply( VisionEgg.Gratings.LuminanceGratingCommon.__init__, (self,), kw )
        
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

        if p.window_shape == 'circle':
            # XXX slow, aliased way of calculating circle
            cartesian_radius = 0.5*math.sin(p.window_shape_radius_parameter/180.0*math.pi)
            cartesian_radius2 = cartesian_radius**2
            floating_point_window = Numeric.zeros((p.num_s_samples,p.num_t_samples),'f')
            for s in range(p.num_s_samples):
                s_frac = float(s)/p.num_s_samples
                s_dist2 = (s_frac-0.5)**2
                for t in range(p.num_t_samples):
                    t_frac = float(t)/p.num_t_samples
                    t_dist2 = (t_frac-0.5)**2

                    if s_dist2 + t_dist2 <= cartesian_radius2:
                        floating_point_window[s,t] = 1.0
                    else:
                        floating_point_window[s,t] = 0.0
        elif p.window_shape == 'gaussian':
            MIN_EXP = -745.0
            MAX_EXP =  709.0
            
            s = Numeric.arange(0.0,p.num_s_samples,1.0,'f')/p.num_s_samples
            t = Numeric.arange(0.0,p.num_t_samples,1.0,'f')/p.num_t_samples
            sigma_normalized = p.window_shape_radius_parameter / 90.0 * 0.5
            
            check_s = -((s-0.5)**2/sigma_normalized**2)
            try:
                # some platforms raise OverflowError when doing this on small numbers
                val_s = Numeric.exp( check_s )
            except OverflowError:
                check_s = Numeric.clip(check_s,MIN_EXP,MAX_EXP)
                val_s = Numeric.exp( check_s )

            check_t = -((t-0.5)**2/sigma_normalized**2)
            try:
                val_t = Numeric.exp( check_t )
            except OverflowError:
                check_t = Numeric.clip(check_t,MIN_EXP,MAX_EXP)
                val_t = Numeric.exp( check_t )
            floating_point_window = Numeric.outerproduct(val_s,val_t)
        else:
            raise RuntimeError('Unknown window_shape "%s"'%(p.window_shape,))

        texel_data = (floating_point_window * self.max_int_val).astype(self.numeric_type).tostring()
   
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
        if (gl.glGetTexLevelParameteriv(gl.GL_PROXY_TEXTURE_2D,0,gl.GL_TEXTURE_WIDTH) == 0) or (gl.glGetTexLevelParameteriv(gl.GL_PROXY_TEXTURE_2D,0,gl.GL_TEXTURE_HEIGHT) == 0):
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
        self._cached_num_s_samples = p.num_s_samples
        self._cached_num_t_samples = p.num_t_samples

    def __rebuild_display_lists(self):
        gl.glMatrixMode(gl.GL_MODELVIEW)
        gl.glLoadIdentity()

        p = self.parameters

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

                gl.glTexCoord2f(x_start_upper*g+o,y_upper*g+o)
                gl.glVertex3f(x_start_upper, y_upper, z_start_upper)

                gl.glTexCoord2f(x_stop_upper*g+o,y_upper*g+o)
                gl.glVertex3f(x_stop_upper, y_upper, z_stop_upper)

                gl.glTexCoord2f(x_stop_lower*g+o,y_lower*g+o)
                gl.glVertex3f(x_stop_lower, y_lower, z_stop_lower)

                gl.glTexCoord2f(x_start_lower*g+o,y_lower*g+o)
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
        
    def draw(self):
    	"""Redraw the scene on every frame.
        """
        p = self.parameters
        
        if self._cached_radius != p.radius or self._cached_slices != p.slices or self._cached_stacks != p.stacks:
            self.__rebuild_display_lists()
            
        if self._cached_window_shape != p.window_shape or self._cached_shape_radius_parameter != p.window_shape_radius_parameter:
            self.__rebuild_texture_object()
            
        if self._cached_num_s_samples != p.num_s_samples or self._cached_num_t_samples != p.num_t_samples:
            self.__rebuild_texture_object()
            
        if p.on:
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
            apply( gl.glColor, p.opaque_color )
            gl.glTexEnvi(gl.GL_TEXTURE_ENV, gl.GL_TEXTURE_ENV_MODE, gl.GL_REPLACE)

            # clear modelview matrix
            gl.glMatrixMode(gl.GL_MODELVIEW)
            gl.glLoadIdentity()

            # do the orientation
            gl.glRotatef(p.window_center_azimuth,0.0,-1.0,0.0)
            gl.glRotatef(p.window_center_elevation,1.0,0.0,0.0)

            gl.glCallList(self.windowed_display_list_id)
            gl.glEnable( gl.GL_TEXTURE_2D )
            gl.glCallList(self.opaque_display_list_id)
