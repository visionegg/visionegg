"""Load .3DS files

This module allows Vision Egg programs to use 3D models in the .3DS
file format.  We thank the lib3ds project at
http://lib3ds.sourceforge.net/ for providing the library used.

Several aspects of .3ds files are not yet implemented.  The most
important of these is that only the first texture map is used from the
material properties of an object.  Lighting is not used, so the
specular, ambient and diffuse material properties will have no effect.

Classes:

Model3DS -- A 3D model from a .3ds file
"""

# Copyright (c) 2002 Andrew Straw.  Distributed under the terms of the
# GNU Lesser General Public License (LGPL).

import os, types, string
import VisionEgg
import VisionEgg.Core
import VisionEgg.ParameterTypes as ve_types
import VisionEgg.Textures
import VisionEgg._lib3ds # helper functions in C
import Numeric

gl = VisionEgg.Core.gl # get (potentially modified) OpenGL module from Core

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
    
class Model3DS(VisionEgg.Core.Stimulus):
    """Model3DS -- A 3D model from a .3ds file"""
    parameters_and_defaults = {'scale':((1.0, 1.0, 1.0),
                                        ve_types.Sequence3(ve_types.Real)),
                               'position':((0.0, 0.0, 0.0),
                                           ve_types.Sequence3(ve_types.Real)),
                               'orient_angle':(0.0,
                                               ve_types.Real),
                               'orient_axis':((0.0, 1.0, 0.0),
                                              ve_types.Sequence3(ve_types.Real)),
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
                texture = VisionEgg.Textures.Texture(string.lower(filename))
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
                    VisionEgg.Core.message.add(
                        "Resized texture in %s to %d x %d"%(
                        str(self),texture.size[0],texture.size[1]),VisionEgg.Core.Message.WARNING)
                        
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
