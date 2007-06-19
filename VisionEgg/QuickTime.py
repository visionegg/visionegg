# The Vision Egg: QuickTime
#
# Copyright (C) 2001-2003, 2006 Andrew Straw.
# Author: Andrew Straw <astraw@users.sourceforge.net>
# URL: <http://www.visionegg.org/>
#
# Distributed under the terms of the GNU Lesser General Public License
# (LGPL). See LICENSE.TXT that came with this file.

"""
QuickTime movies in the Vision Egg.

"""

import VisionEgg
import VisionEgg.gl_qt # C implementation of GL/QT interface
import VisionEgg.qtmovie as qtmovie
import VisionEgg.Textures

import numpy.oldnumeric as Numeric
import os

import VisionEgg.GL as gl # get all OpenGL stuff in one namespace

__version__ = VisionEgg.release_name
__author__ = 'Andrew Straw <astraw@users.sourceforge.net>'

#######################################################

new_movie_from_filename = qtmovie.new_movie_from_filename
    
class MovieTexture(VisionEgg.Textures.Texture):

    __slots__ = (
        'movie',
        'size',
        'scale',
        'gl_qt_renderer',
        )
    
    def __init__(self,
                 movie=None,
                 texture_size=None, # be default will be big enough for full movie, otherwise 2-tuple
                 ):
        if not isinstance(movie,qtmovie.Movie):
            if isinstance(movie,str) or isinstance(movie,unicode):
                movie = new_movie_from_filename(filename=movie)
        self.movie = movie
        bounds = self.movie.GetMovieBox()
        height = bounds.bottom-bounds.top
        width = bounds.right-bounds.left
        self.movie.SetMovieBox(qtmovie.Rect(top=0,left=0,bottom=height,right=width))
        self.size = (width,height)
        self.scale = 1.0

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
        
        buffer = Numeric.zeros( (tex_shape,tex_shape), Numeric.UInt8 )
        texture_object.put_new_image( buffer,
                                      internal_format=gl.GL_RGB,
                                      mipmap_level=0 )
        self.texture_object = texture_object

        self.gl_qt_renderer = VisionEgg.gl_qt.gl_qt_renderer_create(self.movie,tex_shape,self.scale)

    def update(self):
        # only call this when my texture unit is active
        VisionEgg.gl_qt.gl_qt_renderer_update(self.gl_qt_renderer)

    def __del__(self):
        VisionEgg.gl_qt.gl_qt_renderer_delete(self.gl_qt_renderer)
