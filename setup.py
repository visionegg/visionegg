#!/usr/bin/env python
"""Setup script for the Vision Egg distribution.
"""
# Copyright (c) 2001 Andrew Straw.  Distributed under the terms of the
# GNU General Public License (GPL).

from distutils.core import setup, Extension
import os, sys

find_SDL_command = 'sdl-config --version'
print "Attempting to find SDL by executing '%s'." % find_SDL_command
No_SDL_On_Path = os.system( find_SDL_command )

if No_SDL_On_Path:
    build_sdl = 0
else:
    build_sdl = 1

if len(sys.argv) > 1:
    if sys.argv[1] == 'sdist':
        build_sdl = 1 # Always include in a source distribution

if build_sdl:
    print "Attempting to build with SDL. If you get compilation errors"
    print "such as 'SDL/SDL.h: No such file or directory', edit setup.py"
    print "and set build_sdl = 0."
else:
    print "WARNING: Building without SDL.  Some graphics functionality"
    print "may be lost."

# Base packages and extension modules
pkgs = [ 'VisionEgg' ]
ext_mods=[ Extension(name='_visionegg',sources=['src/_visionegg.c']) ]

# More packages if build_sdl is enabled
if build_sdl:
      pkgs.append( 'VisionEgg.SDL' )
      ext_mods.append( Extension(name='SDL._sdl',
                                 sources=['src/SDL/_sdl.c'],
                                 library_dirs=['/usr/X11R6/lib'],
                                 libraries=['SDL','GL','GLU']) )

# Normal distutils stuff
setup(name="visionegg",
      version = "0.6.0",
      description = "Vision Egg",
      url = 'http://visionegg.sourceforge.net',
      author = "Andrew Straw",
      author_email = "astraw@users.sourceforge.net",
      licence = "GPL",
      package_dir={'VisionEgg' : 'src'},
      packages=pkgs,
      ext_package='VisionEgg',
      ext_modules=ext_mods
)








