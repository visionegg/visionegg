#!/usr/bin/env python
"""Setup script for the Vision Egg distribution.
"""
# Copyright (c) 2001-2002 Andrew Straw.  Distributed under the terms of the
# GNU Lesser General Public License (LGPL).

name             = "visionegg"
version          = "0.9.4a4"
author           = "Andrew Straw"
author_email     = "astraw@users.sourceforge.net"
home_page        = "http://www.visionegg.org/"
license          = "LGPL" # Lesser GNU Public License
description      = "2D/3D visual stimulus generation"
platform         = ['win32','darwin','linux','irix','others']

long_description = \
"""The Vision Egg is a programming library (with demo applications) that
uses standard, inexpensive computer graphics cards to produce visual
stimuli for vision research experiments.

For more information, visit the website at www.visionegg.org

This is release %s. Although it is already suitable for experiments,
this is still beta software.  Any feedback, questions, or comments,
should go to the mailing list at visionegg@freelists.org

The Vision Egg is copyright (c) Andrew D. Straw, 2001-2003 and is
distributed under the GNU Lesser General Public License (LGPL).  This
software comes with absolutely no warranties, either expressed or
implied.
"""%(version,)

classifiers = [
    'Development Status :: 4 - Beta',
    'Environment :: Win32 (MS Windows)',
    'Environment :: X11 Applications',
    'Environment :: MacOS X',
    'Environment :: Other Environment',
    'Intended Audience :: Developers',
    'Intended Audience :: Science/Research',
    'License :: OSI Approved :: GNU Library or Lesser General Public License (LGPL)',
    'Natural Language :: English',
    'Operating System :: Microsoft :: Windows',
    'Operating System :: MacOS :: MacOS X',
    'Operating System :: POSIX :: Linux',
    'Operating System :: POSIX :: IRIX',
    'Programming Language :: Python',
    'Topic :: Multimedia :: Graphics',
    'Topic :: Scientific/Engineering',
    'Topic :: Scientific/Engineering :: Medical Science Apps.',
    ]

package_dir      = {'VisionEgg'          : 'src',
                    'VisionEgg.PyroApps' : os.path.join('src','PyroApps')}
packages         = [ 'VisionEgg',
                     'VisionEgg.PyroApps' ]
ext_package      = 'VisionEgg'
ext_modules      = []  # filled in later

from distutils.core import setup, Extension
from distutils.command.build_ext import build_ext
from distutils.errors import CCompilerError
import sys, os.path, glob, traceback

# Fill out ext_modules
skip_c_compilation = 0
if not skip_c_compilation:
    # priority raising/setting C extensions
    if sys.platform == 'darwin':
        ext_modules.append(Extension(name='_darwin_maxpriority',
                                     sources=['src/darwin_maxpriority.c',
                                              'src/darwin_maxpriority_wrap.c']))
    elif sys.platform == 'win32':
        ext_modules.append(Extension(name='_win32_maxpriority',
                                     sources=[os.path.join('src','win32_maxpriority.c'),
                                              os.path.join('src','win32_maxpriority_wrap.c')]))
    elif sys.platform in ['linux2','irix','posix']:
        ext_modules.append(Extension(name='_posix_maxpriority',
                                     sources=['src/posix_maxpriority.c',
                                              'src/posix_maxpriority_wrap.c']))

    # _lib3ds
    lib3ds_sources = glob.glob(os.path.join('lib3ds','*.c'))
    lib3ds_sources.append(os.path.join('src','_lib3ds.c'))
    if sys.platform == 'darwin':
        extra_link_args = ['-framework','OpenGL']
    else:
        extra_link_args = []
    if sys.platform == 'win32':
        libraries = ['opengl32']
    else:
        libraries = []
    ext_modules.append(Extension(name='_lib3ds',
                                 sources=lib3ds_sources,
                                 include_dirs=['.','lib3ds'],
                                 libraries=libraries,
                                 extra_link_args=extra_link_args
                                 ))
    if sys.platform == "darwin":
        # VBL synchronization stuff
        ext_modules.append(Extension(name='_darwin_sync_swap',
                                     sources=['src/_darwin_sync_swap.m'],
                                     extra_compile_args=['-framework','OpenGL'],
                                     extra_link_args=['-framework','OpenGL']))
        # Cocoa application stuff
        ext_modules.append(Extension(name='_darwin_app_stuff',
                                     sources=['src/darwin_app_stuff.m',
                                              'src/darwin_app_stuff_wrap.c'],
                                     extra_link_args=['-framework','Cocoa']))

    if sys.platform == 'linux2':
        ext_modules.append(Extension(name='_raw_lpt_linux',sources=['src/_raw_lpt_linux.c']))

    if sys.platform[:4] == 'irix':
        ext_modules.append(Extension(name='_raw_plp_irix',sources=['src/_raw_plp_irix.c']))

# Find the demo scripts
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
data_dir = os.path.join('VisionEgg','data')
demo_dir = os.path.join('VisionEgg','demo')
data_files.append( (data_dir,[os.path.join('data','panorama.jpg')]) )
data_files.append( (data_dir,[os.path.join('data','az_el.png')]) )
data_files.append( (data_dir,[os.path.join('data','visionegg.bmp')]) )
data_files.append( (data_dir,[os.path.join('data','visionegg.tif')]) )
data_files.append( (demo_dir,[os.path.join('demo','README.txt')]) )
data_files.append( (os.path.join(demo_dir,'tcp'),[os.path.join('demo','tcp','README.txt')]) )
data_files.append( ('VisionEgg',['check-config.py','VisionEgg.cfg','README.txt','LICENSE.txt']) )

global extension_build_failed
extension_build_failed = 0

class ve_build_ext( build_ext ):
    # This class allows C extension building to fail.
    # No extension is essential to the Vision Egg.
    def build_extension(self, ext):
        try:
            build_ext.build_extension(self, ext)
        except CCompilerError, x:
            print ('*'*70+'\n')*3
            
            print """WARNING: The %s extension module to the Vision
            Egg could not be compiled.  The Vision Egg should run, but
            the features present in that file will not be
            available.

            Above is the ouput showing how the compilation
            failed."""%ext.name

            if sys.platform == 'win32':
                print
                
                print """I see you are using Windows.  The default
                compiler for this platform is the Microsoft Visual
                Studio C compiler.  However, a free alternative
                compiler called mingw can be used instead."""

            print 
            print ('*'*70+'\n')*3
            global extension_build_failed
            if not extension_build_failed:
                extension_build_failed = 1

def main():
    # patch distutils if it can't cope with the "classifiers" keyword
    if sys.version < '2.2.3':
        from distutils.dist import DistributionMetadata
        DistributionMetadata.classifiers = None
        
    # Call setup - normal distutils behavior
    setup(
        name=name,
        version=version,
        description=description,
        author=author,
        author_email=author_email,
        url=home_page,
        license=license,
        package_dir=package_dir,
        packages=packages,
        ext_package=ext_package,
        ext_modules=ext_modules,
        data_files=data_files,
        long_description=long_description,
        cmdclass={'build_ext':ve_build_ext}, # replace Python default build_ext class with ours
        classifiers=classifiers
        )

    if extension_build_failed:
        print ('*'*70+'\n')*3
        
        print """WARNING: Building of some extensions failed.  Please
        see the messages above for details.\n"""

        print ('*'*70+'\n')*3

if __name__ == "__main__":
    main()
