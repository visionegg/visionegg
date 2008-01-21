#ifndef _QUICKTIME_C_H_
#define _QUICKTIME_C_H_

#include "vegl.h"

#if defined(__APPLE__)
#  include <QuickTime/Movies.h>
#else
#  include <Movies.h>
#endif

typedef struct {
  Movie my_movie;

  // OpenGL info
  GLubyte * gl_texel_data;
  short tex_shape;
  short tex_height;
  short tex_width;

  // QuickTime offscreen info
  unsigned char * qt_pixel_data;
  unsigned long row_stride;
  GWorldPtr offscreen_gworld;
  PixMapHandle offscreen_pixmap;
} gl_qt_renderer;

/* Error checking */

int gl_qt_err_occurred(void);
const char * gl_qt_err_message(void);

/* Standard functions */

gl_qt_renderer* gl_qt_renderer_create( Movie theMovie, short tex_shape, float tex_scale ); // tex_scale = 0.0 is auto
void gl_qt_renderer_delete( gl_qt_renderer *);
void gl_qt_renderer_update( gl_qt_renderer *);

#endif
