# The Vision Egg: Lib3DS
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
Use .3DS files.

This module allows Vision Egg programs to use 3D models in the .3DS
file format.  We thank the lib3ds project at
http://lib3ds.sourceforge.net/ for providing the library used.

Several aspects of .3ds files are not yet implemented.  The most
important of these is that only the first texture map is used from the
material properties of an object.  Lighting is not used, so the
specular, ambient and diffuse material properties will have no effect.

"""

try:
    import logging
except ImportError:
    import VisionEgg.py_logging as logging

import os
import VisionEgg
import VisionEgg.Core
import VisionEgg.ParameterTypes as ve_types
import VisionEgg.Textures
import VisionEgg._lib3ds # helper functions in C
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
    
class Model3DS(VisionEgg.Core.Stimulus):
    """Model3DS -- A 3D model from a .3ds file

    Parameters
    ==========
    orient_angle -- (Real)
                    Default: 0.0
    orient_axis  -- (Sequence3 of Real)
                    Default: (0.0, 1.0, 0.0)
    position     -- (Sequence3 of Real)
                    Default: (0.0, 0.0, 0.0)
    scale        -- (Sequence3 of Real)
                    Default: (1.0, 1.0, 1.0)
    on           -- (Boolean)
                    Default: True

    Constant Parameters
    ===================
    filename           -- (String)
                          Default: (determined at runtime)
    mipmaps_enabled    -- (Boolean)
                          Default: True
    shrink_texture_ok  -- (Boolean)
                          Default: False
    texture_mag_filter -- (Integer)
                          Default: 9729
    texture_min_filter -- (Integer)
                          Default: 9987
    texture_wrap_s     -- (Integer)
                          Default: (determined at runtime)
    texture_wrap_t     -- (Integer)
                          Default: (determined at runtime)
    """
    parameters_and_defaults = {'scale':((1.0, 1.0, 1.0),
                                        ve_types.Sequence3(ve_types.Real)),
                               'position':((0.0, 0.0, 0.0),
                                           ve_types.Sequence3(ve_types.Real)),
                               'orient_angle':(0.0,
                                               ve_types.Real),
                               'orient_axis':((0.0, 1.0, 0.0),
                                              ve_types.Sequence3(ve_types.Real)),
                               'on':(True, ve_types.Boolean),
                               }
    constant_parameters_and_defaults = {'filename':(None,
                                                    ve_types.String),
                                        'texture_mag_filter':(gl.GL_LINEAR,
                                                              ve_types.Integer),
                                        'texture_min_filter':(gl.GL_LINEAR_MIPMAP_LINEAR,
                                                              ve_types.Integer),
                                        'texture_wrap_s':(None, # set to gl.GL_CLAMP_TO_EDGE below
                                                          ve_types.Integer), 
                                        'texture_wrap_t':(None, # set to gl.GL_CLAMP_TO_EDGE below
                                                          ve_types.Integer),
                                        'mipmaps_enabled':(True,
                                                           ve_types.Boolean),
                                        'shrink_texture_ok':(False,
                                                             ve_types.Boolean), # boolean
                                        }
    def __init__(self,**kw):
        # Initialize base class
        VisionEgg.Core.Stimulus.__init__(self,**kw)
        
        # We have to set these parameters here because we may have
        # re-assigned gl.GL_CLAMP_TO_EDGE.  This allows us to use
        # symbol gl.GL_CLAMP_TO_EDGE even if our version of OpenGL
        # doesn't support it.
        if self.constant_parameters.texture_wrap_s is None:
            self.constant_parameters.texture_wrap_s = gl.GL_CLAMP_TO_EDGE
        if self.constant_parameters.texture_wrap_t is None:
            self.constant_parameters.texture_wrap_t = gl.GL_CLAMP_TO_EDGE
            
        max_dim = gl.glGetIntegerv( gl.GL_MAX_TEXTURE_SIZE )
        if max_dim is None:
            raise RuntimeError("A screen must be open before you create an instance of Model3DS.");

        cp = self.constant_parameters # shorthand
        # Do C initialization stuff
        if cp.filename is None:
            raise RuntimeError("Must specify filename for Object3DS class.")
        orig_dir = os.path.abspath(os.curdir)
        directory,name = os.path.split(cp.filename)
        if directory:
            os.chdir(directory)
        tex_dict = VisionEgg._lib3ds.c_init(self,name)
        self.textures = [] # keep a list of textures we're using so they don't go out of scope and get deleted
        # now load the textures to OpenGL
        for filename in tex_dict.keys():
            try:
                texture = VisionEgg.Textures.Texture(filename)
            except IOError, x: # Might be file not found due to case error
                texture = VisionEgg.Textures.Texture(filename.lower())
            if not cp.shrink_texture_ok:
                texture.load(VisionEgg.Textures.TextureObject(dimensions=2),
                             build_mipmaps=cp.mipmaps_enabled,
                             rescale_original_to_fill_texture_object=1)
            else:
                max_dim = gl.glGetIntegerv( gl.GL_MAX_TEXTURE_SIZE )
                resized = 0
                while max(texture.size) > max_dim:
                    texture.make_half_size()
                    resized = 1
                loaded_ok = 0
                while not loaded_ok:
                    try:
                        # send texture to OpenGL
                        texture.load( VisionEgg.Textures.TextureObject(dimensions=2),
                                      build_mipmaps=cp.mipmaps_enabled,
                                      rescale_original_to_fill_texture_object=1)
                    except VisionEgg.Textures.TextureTooLargeError:
                        texture.make_half_size()
                        resized = 1
                    else:
                        loaded_ok = 1
                if resized:
                    logger = logging.getLogger('VisionEgg.Lib3DS')
                    logger.warning("Resized texture in %s to %d x %d"%(
                        str(self),texture.size[0],texture.size[1]))
            tex_dict[filename] = texture.texture_object.gl_id # keep the GL texture object id

            # set the texture defaults
            if not cp.mipmaps_enabled:
                if cp.texture_min_filter in TextureStimulusBaseClass._mipmap_modes:
                    raise RuntimeError("Specified a mipmap mode in texture_min_filter, but mipmaps not enabled.")
            texture.texture_object.set_min_filter( cp.texture_min_filter )
            texture.texture_object.set_mag_filter( cp.texture_mag_filter )
            texture.texture_object.set_wrap_mode_s( cp.texture_wrap_s )
            texture.texture_object.set_wrap_mode_t( cp.texture_wrap_t )
            self.textures.append(texture)
                                                                                    
        gl.glTexEnvi(gl.GL_TEXTURE_ENV, gl.GL_TEXTURE_ENV_MODE, gl.GL_REPLACE)

        os.chdir(orig_dir)
        self.tex_dict = tex_dict

        # draw it once to set up display list
        p = self.parameters
        VisionEgg._lib3ds.draw(self._lib3ds_file,
                               self.tex_dict,
                               p.scale[0],
                               p.scale[1],
                               p.scale[2],
                               p.position[0],
                               p.position[1],
                               p.position[2],
                               p.orient_angle,
                               p.orient_axis[0],
                               p.orient_axis[1],
                               p.orient_axis[2])

    def draw(self):
        # call the C function that does the work
        p = self.parameters
        if not p.on:
            return
        VisionEgg._lib3ds.draw(self._lib3ds_file,
                               self.tex_dict,
                               p.scale[0],
                               p.scale[1],
                               p.scale[2],
                               p.position[0],
                               p.position[1],
                               p.position[2],
                               p.orient_angle,
                               p.orient_axis[0],
                               p.orient_axis[1],
                               p.orient_axis[2])

    def dump_materials(self):
        # call the C function that does the work
        VisionEgg._lib3ds.dump_materials(self._lib3ds_file)

    def dump_nodes(self):
        # call the C function that does the work
        VisionEgg._lib3ds.dump_nodes(self._lib3ds_file)

    def dump_meshes(self):
        # call the C function that does the work
        VisionEgg._lib3ds.dump_meshes(self._lib3ds_file)
