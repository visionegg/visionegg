"""QuickTime movies in the Vision Egg"""

# Copyright (c) 2003 Andrew Straw.  Distributed under the terms of the
# GNU Lesser General Public License (LGPL).

import VisionEgg
import VisionEgg.gl_qt # C implementation of GL/QT interface
import VisionEgg.Textures

import Numeric
import os

gl = VisionEgg.Core.gl # get (potentially modified) OpenGL module from Core

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

#######################################################

is_quicktime_started = False # global variable

class Movie:
    """Wrapped QuickTime movie.

    This should be roughly equivalent to the Java class
    quicktime.std.movies.Movie

    Do not count on this class remaining in Python -- it may get
    migrated to C.
    
    """
    # most of this is probably already in MacPython.  But does that
    # work on Windows???
    def __init__(self, filename=None):
        global is_quicktime_started
        if not is_quicktime_started:
            VisionEgg.gl_qt.initialize_quicktime()
            is_quicktime_started = True
        if not os.path.isfile(filename):
            raise ValueError('filename is not a valid file')
        self.movie = VisionEgg.gl_qt.load_movie(filename)
    def task(self,maxMilliSecToUse=0):
        """Service movies, updating output as necessary

        Arguments:

        maxMilliSecToUse -- Maximum number of milliseconds that
            MoviesTask can work before returning. If this parameter
            is 0, MoviesTask services every active movie exactly once.
        
        """
        VisionEgg.gl_qt.MoviesTask(self.movie,maxMilliSecToUse)
    def is_done(self):
        return VisionEgg.gl_qt.IsMovieDone( self.movie )
    def go_to_beginning(self):
        VisionEgg.gl_qt.GoToBeginningOfMovie( self.movie )
    def start(self):
        VisionEgg.gl_qt.StartMovie(self.movie)
    def stop(self):
        VisionEgg.gl_qt.StopMovie(self.movie)
    def get_box(self):
        return VisionEgg.gl_qt.GetMovieBox(self.movie)

class MovieTexture(VisionEgg.Textures.Texture):
    def __init__(self,
                 movie=None,
                 texture_size=None, # be default will be big enough for full movie, otherwise 2-tuple
                 ):
        if not isinstance(movie,Movie):
            if type(movie) == str:
                movie = Movie(filename=movie)
        self.movie = movie
        left, bottom, right, top = self.movie.get_box()
        width = abs(right-left)
        height = abs(top-bottom)
        self.size = (width,height)
        self.scale = 1.0
        self.started = False

    def make_half_size(self):
        self.size = self.size[0]/2, self.size[1]/2
        self.scale = self.scale/2

    def unload(self):
        raise NotImplementedError('')

    def get_texels_as_image(self):
        raise NotImplementedError('')
    
    def load(self, texture_object,
             build_mipmaps=False,
             rescale_original_to_fill_texture_object = False,
             internal_format=gl.GL_RGB,
             ):
        if build_mipmaps:
            raise ValueError('cannot build mipmaps for QuickTime movies')
        if rescale_original_to_fill_texture_object:
            raise NotImplementedError('')
        width,height = self.size
        tex_shape = VisionEgg.Textures.next_power_of_2(max(width,height))
        
        # fractional coverage
        self.buf_lf = 0.0
        self.buf_rf = float(width)/tex_shape
        self.buf_bf = 0.0
        self.buf_tf = float(height)/tex_shape

        # absolute (texel units) coverage
        self._buf_l = 0
        self._buf_r = width
        self._buf_b = 0
        self._buf_t = height
        
        buffer = Numeric.zeros( (tex_shape,tex_shape), Numeric.UnsignedInt8 )
        texture_object.put_new_image( buffer,
                                      internal_format=gl.GL_RGB,
                                      mipmap_level=0 )
        self.texture_object = texture_object

        self.gl_qt_renderer = VisionEgg.gl_qt.gl_qt_renderer_create(self.movie.movie,tex_shape,self.scale)

    def update(self):
        # only call this when my texture unit is active
        VisionEgg.gl_qt.gl_qt_renderer_update(self.gl_qt_renderer)

    def __del__(self):
        VisionEgg.gl_qt.gl_qt_renderer_delete(self.gl_qt_renderer)
