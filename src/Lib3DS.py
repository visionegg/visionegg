import os, types, new
import VisionEgg
import VisionEgg.Core
import VisionEgg.Textures
import VisionEgg._lib3ds # helper functions in C
import OpenGL.GL
gl = OpenGL.GL

class Model3DS(VisionEgg.Core.Stimulus):
    constant_parameters_and_defaults = {'filename':(None,types.StringType)}
    def __init__(self,**kw):
        # Initialize base class
        apply(VisionEgg.Core.Stimulus.__init__,(self,),kw)

        max_dim = gl.glGetIntegerv( gl.GL_MAX_TEXTURE_SIZE )
        if max_dim is None:
            raise RuntimeError("A screen must be open before you create an instance of Model3DS.");
        
        # Do C initialization stuff
        if self.constant_parameters.filename is None:
            raise RuntimeError("Must specify filename for Object3DS class.")
        orig_dir = os.curdir
        directory,name = os.path.split(self.constant_parameters.filename)
        os.chdir(directory)
        tex_dict = VisionEgg._lib3ds.c_init(self,name)
        # now load the textures to OpenGL
        for filename in tex_dict.keys():
            #filename,gl_texId = tex_dict[texture_name]
            print "loading",filename
            texture = VisionEgg.Textures.TextureFromFile(filename)
            gl_texId = texture.load(build_mipmaps=1,rescale_original_to_fill_texture_object=1)
            tex_dict[filename] = gl_texId # save just the GL texture ID
        os.chdir(orig_dir)
        self.tex_dict = tex_dict
        print self.tex_dict

    def draw(self):
        # call the C function that does the work
        VisionEgg._lib3ds.draw(self._lib3ds_file,self.tex_dict)

    def dump_materials(self):
        # call the C function that does the work
        VisionEgg._lib3ds.dump_materials(self._lib3ds_file)

    def dump_nodes(self):
        # call the C function that does the work
        VisionEgg._lib3ds.dump_nodes(self._lib3ds_file)

    def dump_meshes(self):
        # call the C function that does the work
        VisionEgg._lib3ds.dump_meshes(self._lib3ds_file)

