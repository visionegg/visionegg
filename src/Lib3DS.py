"""Load .3DS files

This module allows Vision Egg programs to use 3D models in the .3DS
file format.  We thank the lib3ds project at
http://lib3ds.sourceforge.net/ for providing the library used.

Several aspects of .3ds files are not yet implemented.  The most
important of these is that only the first texture map is used from the
material properties of an object.  Lighting is not used, so the
specular, ambient and diffuse material properties will have no effect.

It is a known limitation that this module does not currently work on
Mac OS X.

Classes:

Model3DS -- A 3D model from a .3ds file
"""

# Copyright (c) 2002 Andrew Straw.  Distributed under the terms of the
# GNU Lesser General Public License (LGPL).

import os, types, string
import VisionEgg
import VisionEgg.Core
import VisionEgg.Textures
import VisionEgg._lib3ds # helper functions in C
import OpenGL.GL
import Numeric
gl = OpenGL.GL

__version__ = VisionEgg.release_name
__cvs__ = string.split('$Revision$')[1]
__date__ = string.join(string.split('$Date$')[1:3], ' ')
__author__ = 'Andrew Straw <astraw@users.sourceforge.net>'

class Model3DS(VisionEgg.Core.Stimulus):
    """Model3DS -- A 3D model from a .3ds file"""
    parameters_and_defaults = {'scale':(Numeric.array((1.0, 1.0, 1.0),'f'),Numeric.ArrayType),
                               'position':(Numeric.array((0.0, 0.0, 0.0),'f'),Numeric.ArrayType),
                               'orient_angle':(0.0,types.FloatType),
                               'orient_axis':(Numeric.array((0.0, 1.0, 0.0),'f'),Numeric.ArrayType)}
    constant_parameters_and_defaults = {'filename':(None,types.StringType),
                                        'texture_mag_filter':(gl.GL_LINEAR,types.IntType),
                                        'texture_min_filter':(gl.GL_LINEAR_MIPMAP_LINEAR,types.IntType),
                                        'texture_wrap_s':(gl.GL_CLAMP_TO_EDGE,types.IntType),
                                        'texture_wrap_t':(gl.GL_CLAMP_TO_EDGE,types.IntType),
                                        'mipmaps_enabled':(1,types.IntType),
                                        }
    def __init__(self,**kw):
        # Initialize base class
        apply(VisionEgg.Core.Stimulus.__init__,(self,),kw)

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
        # now load the textures to OpenGL
        for filename in tex_dict.keys():
            try:
                texture = VisionEgg.Textures.TextureFromFile(filename)
            except IOError, x: # Might be file not found due to case error
                texture = VisionEgg.Textures.TextureFromFile(string.lower(filename))
            gl_texId = texture.load(build_mipmaps=1,rescale_original_to_fill_texture_object=1)
            tex_dict[filename] = gl_texId # save just the GL texture ID

            # set the texture defaults
            gl.glBindTexture(gl.GL_TEXTURE_2D,gl_texId) # this is probably already done, but it doesn't hurt
            
            gl.glTexParameteri(gl.GL_TEXTURE_2D,gl.GL_TEXTURE_MAG_FILTER,cp.texture_mag_filter)
            if not self.constant_parameters.mipmaps_enabled:
                if cp.texture_min_filter in VisionEgg.Textures.TextureStimulusBaseClass._mipmap_modes:
                    raise RuntimeError("Specified a mipmap mode in texture_min_filter, but mipmaps not enabled.")
            gl.glTexParameteri(gl.GL_TEXTURE_2D,gl.GL_TEXTURE_MIN_FILTER,cp.texture_min_filter)
            gl.glTexParameteri(gl.GL_TEXTURE_2D,gl.GL_TEXTURE_WRAP_S,cp.texture_wrap_s)
            gl.glTexParameteri(gl.GL_TEXTURE_2D,gl.GL_TEXTURE_WRAP_T,cp.texture_wrap_t)              
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

