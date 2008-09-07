#!/usr/bin/env python
"""Setup script for the Vision Egg distribution.
"""
# Copyright (C) 2001-2003 Andrew Straw
# Copyright (C) 2004-2008 California Institute of Technology
# Distributed under the terms of the GNU Lesser General Public License
# (LGPL).

name             = "visionegg"
version          = "1.1.1" # Also change __version__ in
                           # VisionEgg/__init__.py and doc/visionegg.tex.
author           = "Andrew Straw"
author_email     = "astraw@users.sourceforge.net"
home_page        = "http://www.visionegg.org/"
license          = "LGPL" # Lesser GNU Public License
description      = "2D/3D visual stimulus generation"

long_description = \
"""The Vision Egg is a programming library (with demo applications)
that uses standard, inexpensive computer graphics cards to produce
visual stimuli for vision research experiments.

For more information, visit the website at www.visionegg.org

Any feedback, questions, or comments, should go to the mailing list at
visionegg@freelists.org

The Vision Egg is Copyright (c) by its authors and is distributed
under the GNU Lesser General Public License (LGPL).  This software
comes with absolutely no warranties, either expressed or implied.

"""

classifiers = [
    'Development Status :: 5 - Production/Stable',
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
    'Programming Language :: C',
    'Topic :: Multimedia :: Graphics',
    'Topic :: Multimedia :: Graphics :: 3D Rendering',
    'Topic :: Multimedia :: Graphics :: Presentation',
    'Topic :: Multimedia :: Video :: Display',
    'Topic :: Scientific/Engineering',
    'Topic :: Scientific/Engineering :: Human Machine Interfaces',
    'Topic :: Scientific/Engineering :: Medical Science Apps.',
    'Topic :: Scientific/Engineering :: Visualization',
    'Topic :: Software Development :: Libraries',
    ]

from setuptools import setup, Extension
from setuptools.command.build_ext import build_ext

from distutils.errors import CCompilerError
import distutils.command.sdist
from distutils import dir_util
import sys, os.path, glob, traceback
import numpy

packages         = [ 'VisionEgg',
                     'VisionEgg.PyroApps',
                     ]
ext_package      = 'VisionEgg'
ext_modules      = []  # filled in later

# Fill out ext_modules
skip_c_compilation = 0
if not skip_c_compilation:
    if sys.platform == 'darwin':
        gl_extra_link_args = ['-framework','OpenGL']
    else:
        gl_extra_link_args = []

    if sys.platform == 'win32':
        gl_libraries = ['opengl32']#,'glu32']
    elif sys.platform.startswith('linux'):
        gl_libraries = ['GL']
    else:
        gl_libraries = []

    if sys.platform == 'win32':
        qt_include_dirs = [r'C:\Program Files\QuickTime SDK\CIncludes']
        qt_library_dirs = [r'C:\Program Files\QuickTime SDK\Libraries']
        qt_libraries = ['qtmlClient']
        if 1:
            # from http://lab.msdn.microsoft.com/express/visualc/usingpsdk/default.aspx
            winlibs = "kernel32.lib user32.lib gdi32.lib winspool.lib comdlg32.lib advapi32.lib shell32.lib ole32.lib oleaut32.lib uuid.lib"
            winliblist = [fname[:-4] for fname in winlibs.split()]
            qt_libraries = qt_libraries+winliblist
        qt_extra_link_args = []
    elif sys.platform == 'darwin':
        qt_include_dirs = []
        qt_library_dirs = []
        qt_libraries = []
        qt_extra_link_args = ['-framework','QuickTime',
                              '-framework','Carbon',
                              ]
    else:
        qt_include_dirs = []
        qt_library_dirs = []
        qt_libraries = []
        qt_extra_link_args = []

    if sys.platform == 'darwin':
        darwin_maxpriority_sources = ['VisionEgg/darwin_maxpriority.pyx']
        ext_modules.append(Extension(name='darwin_maxpriority',
                                     sources=darwin_maxpriority_sources))
        # VBL synchronization stuff
        ext_modules.append(Extension(name='_darwin_sync_swap',
                                     sources=['VisionEgg/_darwin_sync_swap.m'],
                                     extra_link_args=['-framework','OpenGL']))
        # getfresh
        ext_modules.append(Extension(name='_darwin_getrefresh',
                                     sources=['VisionEgg/darwin_getrefresh.m',
                                              'VisionEgg/darwin_getrefresh_wrap.c'],
                                     extra_link_args=['-framework','Cocoa']))



    elif sys.platform == 'win32':
        ext_modules.append(Extension(name='_win32_maxpriority',
                                     sources=[os.path.join('VisionEgg','win32_maxpriority.c'),
                                              os.path.join('VisionEgg','win32_maxpriority_wrap.c')]))
        ext_modules.append(Extension(name='_win32_getrefresh',
                                     sources=[os.path.join('VisionEgg','win32_getrefresh.c'),
                                              os.path.join('VisionEgg','win32_getrefresh_wrap.c')],
                                     libraries=['User32'],
                                     ))
        vretrace_source = 'win32_vretrace.pyx'
        ext_modules.append(Extension(name='win32_vretrace',
                                     sources=[os.path.join('VisionEgg',vretrace_source),
                                              os.path.join('VisionEgg','win32_load_driver.c')],
                                     libraries=['User32'],
                                     ))

    elif sys.platform.startswith('linux') or sys.platform.startswith('irix'):
        ext_modules.append(Extension(name='_posix_maxpriority',
                                     sources=['VisionEgg/posix_maxpriority.c',
                                              'VisionEgg/posix_maxpriority_wrap.c']))
        if sys.platform.startswith('linux'):
            ext_modules.append(Extension(name='_raw_lpt_linux',sources=['VisionEgg/_raw_lpt_linux.c']))
        else: # sys.platform.startswith('irix')
            ext_modules.append(Extension(name='_raw_plp_irix',sources=['VisionEgg/_raw_plp_irix.c']))

    if sys.platform == 'darwin' or sys.platform== 'win32':
        # QuickTime support
        ext_modules.append(Extension(name='_gl_qt',
                                     sources=['VisionEgg/gl_qt.c',
                                              'VisionEgg/gl_qt_wrap.c',
                                              'VisionEgg/movieconvert.c',
                                              ],
                                     include_dirs=qt_include_dirs,
                                     library_dirs=qt_library_dirs,
                                     libraries=qt_libraries+gl_libraries,
                                     extra_link_args=(qt_extra_link_args+
                                                      gl_extra_link_args),
                                     ))

    # _vegl
    ext_modules.append(Extension(name='_vegl',
                                 sources=['VisionEgg/_vegl.pyx',],
                                 libraries=gl_libraries,
                                 extra_link_args=gl_extra_link_args
                                 ))

    # C extensions for drawing GL stuff
    include_prefix = os.path.join( sys.prefix, 'include', 'python%s'%sys.version[:3] )
    numpy_include_dir = numpy.get_include()
    ext_modules.append(Extension(name='_draw_in_c',
                                 sources=['VisionEgg/_draw_in_c.c'],
                                 include_dirs=[numpy_include_dir],
                                 libraries=gl_libraries,
                                 extra_link_args=gl_extra_link_args
                                 ))

if 0:
    data_files = []
    data_base_dir = 'VisionEgg' # This becomes VISIONEGG_SYSTEM_DIR
    data_dir = os.path.join(data_base_dir,'data')
    test_dir = os.path.join(data_base_dir,'test')
    data_files.append( (data_dir,[os.path.join('data','water.mov')]) )
    data_files.append( (data_dir,[os.path.join('data','panorama.jpg')]) )
    data_files.append( (data_dir,[os.path.join('data','spiral.png')]) )
    data_files.append( (data_dir,[os.path.join('data','az_el.png')]) )
    data_files.append( (data_dir,[os.path.join('data','visionegg.bmp')]) )
    data_files.append( (data_dir,[os.path.join('data','visionegg.tif')]) )
    for filename in os.listdir('test'):
        if filename.endswith('.py'):
            data_files.append( (test_dir,[os.path.join('test',filename)]) )
    data_files.append( (data_base_dir,['check-config.py','VisionEgg.cfg','README.txt','LICENSE.txt']) )
else:
    opj = os.path.join
    package_data = {'VisionEgg':[opj('data','water.mov'),
                                 opj('data','panorama.jpg'),
                                 opj('data','spiral.png'),
                                 opj('data','az_el.png'),
                                 opj('data','visionegg.bmp'),
                                 opj('data','visionegg.tif'),
                                 'VisionEgg.cfg',
                                 ]}

global extension_build_failed
extension_build_failed = 0

class sdist_demo( distutils.command.sdist.sdist ):
    description = 'build demos and documentation'

    def get_file_list (self):
        distutils.command.sdist.sdist.get_file_list(self)
        new_files = []
        for orig_file in self.filelist.files:
            if orig_file.startswith('demo') or orig_file.startswith('doc') or orig_file.startswith('test'):
                new_files.append(orig_file)
            elif orig_file in ['check-config.py',
                               #'VisionEgg.cfg', # location changed.. XXX FIXME
                               'CHANGELOG.txt',
                               'README-DEMOS.txt',
                               'LICENSE.txt',
                               ]:
                new_files.append(orig_file)
        self.filelist.files = new_files

    def make_distribution (self):
        # call sdist make_distribution after changing our name
        base_fullname = self.distribution.get_fullname()
        fullname = base_fullname + "-demo"
        def get_fullname():
            return fullname
        self.distribution.get_fullname = get_fullname # override this method
        distutils.command.sdist.sdist.make_distribution(self) # call super

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
    # make sure older versions of distutils work
    extras_kws = {}
    if (hasattr(distutils.core, 'setup_keywords') and
        'classifiers' in distutils.core.setup_keywords):
        extras_kws['classifiers'] = classifiers

    # Call setup - normal distutils behavior
    setup(
        name=name,
        version=version,
        description=description,
        author=author,
        author_email=author_email,
        url=home_page,
        license=license,
        packages=packages,
        ext_package=ext_package,
        ext_modules=ext_modules,
        package_data=package_data,
        long_description=long_description,
        cmdclass={'build_ext':ve_build_ext,
                  'sdist_demo':sdist_demo,
                  },
        **extras_kws
        )

    if extension_build_failed:
        print ('*'*70+'\n')*3

        print """WARNING: Building of some extensions failed.  Please
        see the messages above for details.\n"""

        print ('*'*70+'\n')*3

if __name__ == "__main__":
    main()
