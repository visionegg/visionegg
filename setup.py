#!/usr/bin/env python
"""Setup script for the Vision Egg distribution.
"""
# Copyright (c) 2001-2002 Andrew Straw.  Distributed under the terms of the
# GNU Lesser General Public License (LGPL).

from distutils.core import setup, Extension
import sys
import os.path

extensions = []
is_source_distribution = 0

if len(sys.argv) > 1:
    if sys.argv[1] == 'sdist':
        is_source_distribution = 1

if sys.platform not in ['cygwin','darwin','mac','win32'] or is_source_distribution:
    # The maximum priority stuff should work on most versions of Unix.
    # (It depends on the system call sched_setscheduler.)
    extensions.append(Extension(name='_maxpriority',sources=['src/_maxpriority.c']))

if sys.platform == 'linux2' or is_source_distribution:
    extensions.append(Extension(name='_dout',sources=['src/_dout.c']))

def visit_script_dir(scripts, dirname, filenames):
    for filename in filenames:
        if filename[-3:] == '.py':
            if filename != '__init__.py':
                scripts.append(os.path.join(dirname,filename))

def gather_scripts():
    scripts = []
    os.path.walk('demo',visit_script_dir,scripts)
    os.path.walk('test',visit_script_dir,scripts)
    return scripts

def organize_script_dirs(scripts):
    scripts_by_dir = {}
    for script in scripts:
        dirname = os.path.join('VisionEgg',os.path.split(script)[0])
        if dirname not in scripts_by_dir.keys():
            scripts_by_dir[dirname] = []
        scripts_by_dir[dirname].append(script)
    organized = []
    for dirname in scripts_by_dir.keys():
        organized.append( (dirname, scripts_by_dir[dirname]) )
    return organized

scripts = gather_scripts()
data_files = organize_script_dirs(scripts)

long_description = """
The Vision Egg is a programming library (with demo
applications) that uses standard, inexpensive computer graphics
cards to produce visual stimuli for vision research
experiments."""

# Normal distutils stuff
setup(name="visionegg",
      version = "0.8.3a0",
      description = "Vision Egg",
      url = 'http://www.visionegg.org/',
      author = "Andrew Straw",
      author_email = "astraw@users.sourceforge.net",
      licence = "LGPL",
      package_dir={'VisionEgg' : 'src',
                   #'VisionEgg.test' : 'test',
                   #'VisionEgg.demo' : 'demo',
                   },
      packages=[ 'VisionEgg',
                 #'VisionEgg.test',
                 #'VisionEgg.demo',
                 #'VisionEgg.demo.GUI',
                 #'VisionEgg.demo.Pyro',
                 ],
      ext_package='VisionEgg',
      ext_modules=extensions,
      data_files = data_files,
      long_description = long_description 
)








