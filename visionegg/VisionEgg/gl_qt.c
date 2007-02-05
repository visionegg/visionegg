/*
 * Copyright (c) 2003, 2006 Andrew Straw.  Distributed under the terms
 * of the GNU Lesser General Public License (LGPL).
 *
 * Author: Andrew Straw <astraw@users.sourceforge.net>
 *
 */

#include "Python.h"

#if defined(MS_WINDOWS)
#  include <windows.h>
#endif

#include <stdlib.h>
#include <stdio.h>

#if defined(__APPLE__)
#  include <OpenGL/gl.h>
#  include <QuickTime/Movies.h>
#  include <Carbon/Carbon.h>
#else
#  include <GL/gl.h>
#  include <Movies.h>
#endif

#include "gl_qt.h"

int gl_qt_error = 0;
const char * gl_qt_error_str= NULL;
static char mac_err_str[256];

const char * MAC_OSERR_TO_STR ( int OSErr ) {
  // XXX could make this lookup the error using mac Estr resources
  snprintf(mac_err_str,256,"Mac OS error %d",OSErr);
  return mac_err_str;
}
int gl_qt_err_occurred( void ) {
  return gl_qt_error;
}
const char * gl_qt_err_message( void ) {
  return gl_qt_error_str;
}
void gl_qt_set_error(const char * errmsg) {
  gl_qt_error = 1;
  gl_qt_error_str = errmsg;
}

gl_qt_renderer* gl_qt_renderer_create( Movie theMovie, short tex_shape, float tex_scale ) {
  gl_qt_renderer * render_info = NULL;

  short gMovieWidth, gMovieHeight;
  int wOffScreenDepth;

  long sizeTexture;

  // Movie
  Rect gMovieRect = {0, 0, 0, 0};
  Rect rectNewMovie;
  MatrixRecord 	movieMatrix;

  /// XXX todo: should check tex_shape is power of 2
  render_info = malloc(sizeof(gl_qt_renderer));
  if (render_info == NULL) {
    gl_qt_set_error("memory allocation failure (render_info)");
    return NULL;
  }

  render_info->gl_texel_data = NULL;
  render_info->qt_pixel_data = NULL;
  render_info->offscreen_gworld = NULL;

  render_info->my_movie = theMovie;

  GetMovieBox(render_info->my_movie, &gMovieRect);

  gMovieRect.bottom = gMovieRect.bottom-gMovieRect.top;
  gMovieRect.top = 0;
  gMovieRect.right = gMovieRect.right-gMovieRect.left;
  gMovieRect.left = 0;

  SetMovieBox(render_info->my_movie, &gMovieRect);

  gMovieWidth = (short) (gMovieRect.right - gMovieRect.left);
  gMovieHeight = (short) (gMovieRect.bottom - gMovieRect.top);

  render_info->tex_shape=tex_shape; // on both sides (square)
  wOffScreenDepth=32; // if packed pixel implemented, this could be reduced
  
  // allocate RGB 888 texture buffer
  sizeTexture = 3 * tex_shape * tex_shape; // size of texture in bytes

  render_info->gl_texel_data = (GLubyte *)malloc(sizeTexture);
  if (render_info->gl_texel_data == NULL) {
    gl_qt_set_error("memory allocation failure (render_info->gl_texel_data)");
    goto fail;
  }

  if (tex_scale == 0.0) { // auto-scale
    if (gMovieWidth > gMovieHeight) {
      tex_scale = (float)tex_shape / (float) gMovieWidth;
    }
    else {
      tex_scale = (float)tex_shape / (float) gMovieHeight;
    }
  }

  render_info->tex_width = (short) ((float)gMovieWidth * tex_scale);	
  render_info->tex_height = (short) ((float)gMovieHeight * tex_scale);

  if ((render_info->tex_width > tex_shape) || (render_info->tex_height > tex_shape)) {
    gl_qt_set_error("movie too big for assigned texture shape");
    goto fail;
  }

  SetIdentityMatrix (&movieMatrix);
  ScaleMatrix(&movieMatrix, 
	      X2Fix(tex_scale),  // XXX where is X2Fix defined?
	      X2Fix(tex_scale), 
	      X2Fix(0.0), 
	      X2Fix(0.0));
  SetMovieMatrix(render_info->my_movie, &movieMatrix);

  rectNewMovie.top = 0;
  rectNewMovie.left = 0;
  rectNewMovie.bottom = render_info->tex_height;
  rectNewMovie.right = render_info->tex_width;
  
  render_info->row_stride = render_info->tex_width * wOffScreenDepth / 8;
  render_info->qt_pixel_data = (unsigned char *) malloc(render_info->row_stride * render_info->tex_height);
  if (render_info->qt_pixel_data == NULL) {
    gl_qt_set_error("memory allocation failure (render_info->qt_pixel_data)");
    goto fail;
  }
  memset(render_info->qt_pixel_data, 0, render_info->row_stride * render_info->tex_height);

  QTNewGWorldFromPtr (&(render_info->offscreen_gworld), k32ARGBPixelFormat, 
		      &rectNewMovie, NULL, NULL, 0, 
		      render_info->qt_pixel_data, render_info->row_stride);
  if (render_info->offscreen_gworld == NULL) {
    gl_qt_set_error("error allocating offscreen GWorld");
    goto fail;
  }

  SetMovieGWorld(render_info->my_movie, (CGrafPtr)render_info->offscreen_gworld, NULL);
  render_info->offscreen_pixmap = GetGWorldPixMap(render_info->offscreen_gworld);
  if (!render_info->offscreen_pixmap) {
    gl_qt_set_error("Could not GetGWorldPixMap");
    goto fail;
  }

  if (!LockPixels(render_info->offscreen_pixmap)) {
    gl_qt_set_error("Could not LockPixels");
    goto fail;
  }

  render_info->qt_pixel_data = (unsigned char *) GetPixBaseAddr(render_info->offscreen_pixmap);
  //render_info->row_stride = (unsigned long) GetPixRowBytes(render_info->offscreen_pixmap);

  return render_info;

 fail:
  if (render_info->gl_texel_data != NULL) {
    free(render_info->gl_texel_data);
  }
  if (render_info->qt_pixel_data != NULL) {
    free(render_info->qt_pixel_data);
  }
 
  if (render_info->offscreen_gworld != NULL) {
    DisposeGWorld(render_info->offscreen_gworld);
  }

  if (render_info != NULL) {
    free(render_info);
  }
  return NULL;
}

void gl_qt_renderer_delete( gl_qt_renderer * render_info ) {
  int free_warning = 0;

  if (render_info->offscreen_gworld != NULL) DisposeGWorld(render_info->offscreen_gworld);
  else free_warning = 1;

  if (render_info->gl_texel_data != NULL) free(render_info->gl_texel_data);
  else free_warning = 1;

  if (render_info->qt_pixel_data != NULL) free(render_info->qt_pixel_data);
  else free_warning = 1;

  if (render_info != NULL) free(render_info);
  else free_warning = 1;
  
  if (free_warning) {
    gl_qt_set_error("gl_qt_renderer_delete() called, but something was already deleted!");
  }
}

void gl_qt_renderer_update(gl_qt_renderer * render_info) {

  // Despite the swizzeling, this is faster (on my PowerBook G4 ATI
  // Rage 128 OS X 10.2.6, anyway) than sending the data as GL_ABGR
  // direct to OpenGL.

  // Also, this way we can flip the image 'right side up' (according
  // to OpenGL) for free.

  // Step 1 - 'swizzle' data (convert ABGR to RGB)
  register int i,j;
  register unsigned char * pos;
  register unsigned char * pTextile;
  register int row;

  GLenum error;
  const char *this_msg;

  row = render_info->tex_height;
  for (j = 0; j < render_info->tex_height; j++)
    {
      row--;
      pTextile = render_info->gl_texel_data + row*render_info->tex_width*3;
      //      pTextile = render_info->gl_texel_data + row*render_info->tex_shape*3;
      for (i = 0; i < render_info->tex_width; i++)
	{
	  pos = (unsigned char *)(render_info->qt_pixel_data + (j * render_info->row_stride) + (i * 4));
	  *(pTextile++) = *(pos + 1);
	  *(pTextile++) = *(pos + 2);
	  *(pTextile++) = *(pos + 3);
	}
    }
  // Step 2 - send to OpenGL active 2D texture object
  glTexSubImage2D(GL_TEXTURE_2D, 
		  0, 
		  0, 
		  0, 
		  render_info->tex_width, 
		  render_info->tex_height, 
		  GL_RGB, 
		  GL_UNSIGNED_BYTE, 
		  render_info->gl_texel_data);
  error = glGetError();
  if (GL_NO_ERROR != error) {
    //this_msg = gluErrorString(error);
    this_msg = "unknown error";
    gl_qt_set_error(this_msg);
  }
}
