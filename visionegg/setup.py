#!/usr/bin/env python
"""Setup script for the Vision Egg distribution.
"""

from distutils.core import setup, Extension

build_sdl = 1

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
setup(name="VisionEgg",
      version = "0.5.0",
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








