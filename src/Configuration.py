"""Load config values from environment, config file, or defaults.

Applications should not import this module directly.  Instead, "import
VisionEgg" will result in an attribute "VisionEgg.config", which has
the configuration options as attributes.

This module searches for configuration options in the following order:
environment variables, configuration file, generic defaults.

This module also determines the location of the Vision Egg
directories.  The VISIONEGG_SYSTEM_DIR directory is by default a
directory named "VisionEgg" in the base python directory (found in
Python variable sys.prefix).  VISIONEGG_USER_DIR is by default
"VisionEgg" in the directory specified by the environment variable
HOME, if it exists, and os.curdir otherwise.

You can create a configuration file that contains defaults for your
system.  This should be a text file with key/value pairs.  Blank lines
and anything after the pound symbol ("#") will be treated as a
comment.  Each key/value pairs should be on its own line and in the
format "KEY=VALUE".  By default the file "VisionEgg.cfg" from the
VISIONEGG_USER_DIR or VISIONEGG_SYSTEM_DIR as specified above.
However, You can specify a different filename and directory by setting
the environment variable VISIONEGG_CONFIG_FILE.  """

# This is the python source code for the config module of the Vision Egg package.
#
# Copyright (c) 2002 Andrew Straw.  Distributed under the terms of the
# GNU Lesser General Public License (LGPL).

####################################################################
#
#        Default configuration variables
#
####################################################################

defaults= {
    'VISIONEGG_GUI_INIT':             1,
    'VISIONEGG_SCREEN_W':             640,
    'VISIONEGG_SCREEN_H':             480,
    'VISIONEGG_FULLSCREEN':           0,
    'VISIONEGG_PREFERRED_BPP':        32,
    'VISIONEGG_MONITOR_REFRESH_HZ':   60.0,
    'VISIONEGG_SYNC_SWAP':            1,
    'VISIONEGG_RECORD_TIMES':         0,
    'VISIONEGG_MAXPRIORITY':          0,
    'VISIONEGG_REQUEST_RED_BITS':     8,
    'VISIONEGG_REQUEST_GREEN_BITS':   8,
    'VISIONEGG_REQUEST_BLUE_BITS':    8,
    'VISIONEGG_REQUEST_ALPHA_BITS':   8,
    'VISIONEGG_TKINTER_OK':           1,
    'VISIONEGG_MESSAGE_LEVEL':        1,
    'VISIONEGG_GUI_ON_ERROR':         1,
    'VISIONEGG_LOG_FILE':             'VisionEgg.log', # "" means sys.stderr
    }

####################################################################
#
#        Import all the necessary packages
#
####################################################################

import VisionEgg
import re, os, errno, sys                  # standard python packages
import ConfigParser
import string

__version__ = VisionEgg.release_name
__cvs__ = string.split('$Revision$')[1]
__date__ = string.join(string.split('$Date$')[1:3], ' ')
__author__ = 'Andrew Straw <astraw@users.sourceforge.net>'

class Config:
    def __init__(self):
        
        cfg = ConfigParser.ConfigParser()
        
        if sys.executable == sys.argv[0]: # Windows binary
            self.VISIONEGG_SYSTEM_DIR = os.curdir
            self.VISIONEGG_USER_DIR = os.curdir
        else:
            self.VISIONEGG_SYSTEM_DIR = os.path.join(sys.prefix,"VisionEgg")
            self.VISIONEGG_USER_DIR = os.path.expanduser("~/VisionEgg")

        # See if there's an environment variable for the config file
        if 'VISIONEGG_CONFIG_FILE' in os.environ.keys():
            configFile = os.environ['VISIONEGG_CONFIG_FILE']
        else:
            # Is there one in VISIONEGG_USER_DIR?
            configFile = os.path.join(self.VISIONEGG_USER_DIR,"VisionEgg.cfg")
            if not os.path.isfile(configFile):
                configFile = os.path.join(self.VISIONEGG_SYSTEM_DIR,"VisionEgg.cfg")
                if not os.path.isfile(configFile):
                    configFile = None # No file, use defaults specified in environment variables then here
            

        cfg.read(configFile)

        # Set the default values
        for name in defaults.keys():
            setattr(self,name,defaults[name])

        # Get the values from the configFile
        for option in cfg.options('VisionEgg'):
            name = string.upper(option)
            if name not in defaults.keys():
                raise KeyError("No Vision Egg configuration variable \"%s\""%option)
            if type(defaults[name]) == type(42): # int
                setattr(self,name,int(cfg.get('VisionEgg',option)))
            elif type(defaults[name]) == type(42.0): # float
                setattr(self,name,float(cfg.get('VisionEgg',option)))
            else:
                setattr(self,name,cfg.get('VisionEgg',option))
        
        if(configFile):
            self.VISIONEGG_CONFIG_FILE = os.path.abspath(configFile)
        else:
            self.VISIONEGG_CONFIG_FILE = None
