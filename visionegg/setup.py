#!/usr/bin/env python
"""Setup script for the Vision Egg distribution.
"""
# Copyright (c) 2001-2002 Andrew Straw.  Distributed under the terms of the
# GNU Lesser General Public License (LGPL).

from distutils.core import setup, Extension
import sys
import os.path

extensions = []

if sys.platform not in ['cygwin','darwin','mac','win32']:
    # The maximum priority stuff should work on most versions of Unix.
    # (It depends on the system call sched_setscheduler.)
    extensions.append(Extension(name='_maxpriority',sources=['src/_maxpriority.c']))

if sys.platform == 'linux2':
    extensions.append(Extension(name='_raw_lpt_linux',sources=['src/_raw_lpt_linux.c']))

if sys.platform[:4] == 'irix':
    extensions.append(Extension(name='_raw_plp_irix',sources=['src/_raw_plp_irix.c']))

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
data_files.append( ('VisionEgg/data',['data/panorama.jpg']) )
data_files.append( ('VisionEgg',['check-config.py','VisionEgg.cfg']) )

long_description = """
The Vision Egg is a programming library (with demo
applications) that uses standard, inexpensive computer graphics
cards to produce visual stimuli for vision research
experiments."""

# Normal distutils stuff
setup(name="visionegg",
      version = "0.9.1",
      description = "Vision Egg",
      url = 'http://www.visionegg.org/',
      author = "Andrew Straw",
      author_email = "astraw@users.sourceforge.net",
      license = "LGPL",
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








