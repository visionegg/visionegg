# In addition to running this script, there are additional things that
# must be done to build the binary demos:

# For the demos to find the font file, we modify
# site-packages/VisionEgg/Text.py to include r'.\freesansbold.ttf' as
# the default font. (in Text.__init__
# self.font = pygame.font.Font(r'.\freesansbold.ttf',cp.font_size)

# In VisionEgg.cfg, set VISIONEGG_LOG_TO_STDERR = 0.

import sys
import setup # our setup.py file
import distutils.core
import py2exe

numarray_includes=['numarray.libnumarray',
                   'numarray.memory',
                   'numarray._bytes',
                   'numarray._chararray',
                   'numarray._conv',
                   'numarray._converter',
                   'numarray._ndarray',
                   'numarray._numarray',
                   'numarray._operator',
                   'numarray._sort',
                   'numarray._ufunc',
                   'numarray._ufuncBool',
                   'numarray._ufuncComplex32',
                   'numarray._ufuncComplex64',
                   'numarray._ufuncFloat32',
                   'numarray._ufuncFloat64',
                   'numarray._ufuncInt16',
                   'numarray._ufuncInt32',
                   'numarray._ufuncInt64',
                   'numarray._ufuncInt8',
                   'numarray._ufuncUInt16',
                   'numarray._ufuncUInt32',
                   'numarray._ufuncUInt64',
                   'numarray._ufuncUInt8',
                   ]
tk_excludes=[
    'Tkconstants',
    'Tkinter',
    'tcl',
    ]

import sys, os, glob

windowed_scripts = glob.glob(r'demo\*.py')

data_files = []
for d in setup.data_files:
    todir = d[0]
    source = d[1]
    todir = os.path.normpath(todir.replace( 'VisionEgg','.'))
    source = [s for s in source if not s.endswith('.py')] # don't include .py files
    data_files.append( (todir,source) )

# include pygame font
data_files.append( ('.',[os.path.join(sys.prefix,
                                      'lib','site-packages','pygame','freesansbold.ttf'),
                         ]))
print data_files
console_scripts = ['check-config.py']
#1/0
distutils.core.setup(
    windows=windowed_scripts,
    console=console_scripts,
    data_files=data_files,
    options={"py2exe":{"optimize":2,
                       "includes":numarray_includes,
                       #"excludes":tk_excludes,
                       "dll_excludes": ["glut32.dll"],
                       },},
    )
