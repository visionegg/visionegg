#!/usr/bin/env python
"""Setup script for the Vision Egg distribution.
"""
# Copyright (c) 2001, 2002 Andrew Straw.  Distributed under the terms of the
# GNU General Public License (GPL).

from distutils.core import setup, Extension

# Normal distutils stuff
setup(name="visionegg",
      version = "0.7.0",
      description = "Vision Egg",
      url = 'http://visionegg.sourceforge.net',
      author = "Andrew Straw",
      author_email = "astraw@users.sourceforge.net",
      licence = "GPL",
      package_dir={'VisionEgg' : 'src'},
      packages=[ 'VisionEgg' ],
      ext_package='VisionEgg',
      ext_modules=[ Extension(name='_visionegg',sources=['src/_visionegg.c']) ]
)








