import os, types, new
import VisionEgg
import VisionEgg.Core
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
        VisionEgg._lib3ds.c_init(self,name)
        os.chdir(orig_dir)

    def draw(self):
        # call the C function that does the work
        VisionEgg._lib3ds.draw(self._lib3ds_file)
