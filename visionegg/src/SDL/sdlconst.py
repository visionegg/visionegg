# A subset of SDL constants
#
# There are only enough here to use the subset of SDL functions
# wrapped by the Vision Egg.  These functions are mainly
# the video subsystem of SDL.
import string
__version__ = string.split('$Revision$')[1]
__date__ = string.join(string.split('$Date$')[1:3], ' ')
__author__ = 'Andrew Straw <astraw@users.sourceforge.net>'

SDL_DISABLE = 0
SDL_ENABLE = 1

# Flags to SDL_Init()
# There are more of these... I should add them!
SDL_INIT_VIDEO = 0x00000020

# Flags in SDL_SetVideoMode and SDL_Surface.
# There are more of these... I should add them!
SDL_SWSURFACE  = 0x00000000	# Surface is in system memory */
SDL_HWSURFACE  = 0x00000001	# Surface is in video memory */
SDL_ASYNCBLIT  = 0x00000004	# Use asynchronous blits if possible */
# Available for SDL_SetVideoMode() 
SDL_ANYFORMAT  = 0x10000000	# Allow any video depth/pixel-format */
SDL_HWPALETTE  = 0x20000000	# Surface has exclusive palette */
SDL_DOUBLEBUF  = 0x40000000	# Set up double-buffered video mode */
SDL_FULLSCREEN = 0x80000000	# Surface is a full screen display */
SDL_OPENGL     = 0x00000002      # Create an OpenGL rendering context */
SDL_OPENGLBLIT = 0x0000000A	# Create an OpenGL rendering context and use it for blitting */
SDL_RESIZABLE  = 0x00000010	# This video mode may be resized */
# Used internally (read-only) 
SDL_HWACCEL    = 0x00000100	# Blit uses hardware acceleration */
SDL_SRCCOLORKEY= 0x00001000	# Blit uses a source color key */
SDL_RLEACCELOK = 0x00002000	# Private flag */
SDL_RLEACCEL   = 0x00004000	# Colorkey blit is RLE accelerated */
SDL_SRCALPHA   = 0x00010000	# Blit uses source alpha blending */
SDL_PREALLOC   = 0x01000000	# Surface uses preallocated memory */

# SDL_GLattr for use by SDL_GL_SetAttribute and SDL_GL_GetAttribute.
SDL_GL_RED_SIZE = 0x01
SDL_GL_GREEN_SIZE = 0x02
SDL_GL_BLUE_SIZE = 0x03
SDL_GL_ALPHA_SIZE = 0x04
SDL_GL_BUFFER_SIZE = 0x05
SDL_GL_DOUBLEBUFFER = 0x06
SDL_GL_DEPTH_SIZE = 0x07
SDL_GL_STENCIL_SIZE = 0x08
SDL_GL_ACCUM_RED_SIZE = 0x09
SDL_GL_ACCUM_GREEN_SIZE = 0x0A
SDL_GL_ACCUM_BLUE_SIZE = 0x0B
SDL_GL_ACCUM_ALPHA_SIZE = 0x0C
