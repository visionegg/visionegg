"""Load config values from environment, config file, or defaults.

Applications should not import this module directly.  Instead, "import
VisionEgg" will result in an attribute "VisionEgg.config", which has
the configuration options as attributes.

This module searches for configuration options in the following order:
environment variables, configuration file, generic defaults.

This module also determines the location of a couple directories.
VISIONEGG_SYSTEM_DIR directory, which is by default "VisionEgg" in the
base python directory (found in Python variable sys.prefix).  If it is
not in VISIONEGG_SYSTEM_DIR, then VISIONEGG_USER_DIR is checked, which
is by default "VisionEgg" in the directory specified by the
environment variable HOME, if it exists, and os.curdir otherwise.

You can create a configuration file that contains defaults for your
system.  This should be a text file with key/value pairs.  Blank lines
and anything after the pound symbol ("#") will be treated as a
comment.  Each key/value pairs should be on its own line and in the
format "KEY=VALUE".  By default the file "VisionEgg.cfg" from the
VISIONEGG_SYSTEM_DIR or VISIONEGG_USER_DIR as specified above.
However, You can specify a different filename and directory by setting
the environment variable VISIONEGG_CONFIG_FILE.  """

# This is the python source code for the config module of the Vision Egg package.
#
# Based on Pyro/configuration.py, copyright (c) Irmen de Jong.
#
# Copyright (c) 2002 Andrew Straw.  Distributed under the terms of the
# GNU Lesser General Public License (LGPL).

####################################################################
#
#        Default configuration variables
#
####################################################################

defaults= {
    'VISIONEGG_GUI_INIT':             0,
    'VISIONEGG_SCREEN_W':             640,
    'VISIONEGG_SCREEN_H':             480,
    'VISIONEGG_FULLSCREEN':           0,
    'VISIONEGG_PREFERRED_BPP':        32,
    'VISIONEGG_MONITOR_REFRESH_HZ':   60.0,
    'VISIONEGG_MAXPRIORITY':          0,
    'VISIONEGG_REQUEST_RED_BITS':     8,
    'VISIONEGG_REQUEST_GREEN_BITS':   8,
    'VISIONEGG_REQUEST_BLUE_BITS':    8,
    'VISIONEGG_REQUEST_ALPHA_BITS':   8,
    }

####################################################################
#
#        Import all the necessary packages
#
####################################################################

import VisionEgg
import re, os, errno, sys                  # standard python packages
import string

__version__ = VisionEgg.release_name
__cvs__ = string.split('$Revision$')[1]
__date__ = string.join(string.split('$Date$')[1:3], ' ')
__author__ = 'Andrew Straw <astraw@users.sourceforge.net>'
__credits__ = 'Thanks to Irmen de Jong. I took most of this code from his Pyro project.'

class Config:
    def __init__(self):
        reader = ConfigReader(defaults)

        self.VISIONEGG_SYSTEM_DIR = os.path.join(sys.prefix,"VisionEgg")
        self.VISIONEGG_USER_DIR = os.path.expanduser("~/VisionEgg")

        # See if there's an environment variable for the config file
        if 'VISIONEGG_CONFIG_FILE' in os.environ.keys():
            configFile = os.environ['VISIONEGG_CONFIG_FILE']
        else:
            # Is there one in VISIONEGG_SYSTEM_DIR?
            configFile = os.path.join(self.VISIONEGG_SYSTEM_DIR,"VisionEgg.cfg")
            if not os.path.isfile(configFile):
                configFile = os.path.join(self.VISIONEGG_USER_DIR,"VisionEgg.cfg")
                if not os.path.isfile(configFile):
                    configFile = None # No file, use defaults specified in environment variables then here
            
        reader.parse(configFile)

        self.__dict__.update(reader.items)

        if(configFile):
            self.VISIONEGG_CONFIG_FILE = os.path.abspath(configFile)
        else:
            self.VISIONEGG_CONFIG_FILE = ''

class ConfigReader:
    def __init__(self, defaults):
        self.matcher=re.compile(r'\s*([^#]\w*)\s*=\s*(\S*)\s*$')
        self.items=defaults.copy()
        
    def parse(self, file):
        done_config_file = 0
        if file:
            done_config_file = 1

            file=open(file).readlines()
            for l in file:
                match=self.matcher.match(l)
                if match:
                    if defaults.has_key(match.group(1)):
                        if match.group(2):
                            self.items[match.group(1)] = match.group(2)
                    else:
                        raise KeyError('Unknown config in configfile: '+match.group(1))

        # Parse the environment variables (they override the config file)
        self.items.update(self.processEnv(defaults.keys()))

        # Now fix up all other items:
        for i in self.items.keys():
            # fix the type if it's an integer
            if type(defaults[i]) == type(42):
                self.items[i] = int(self.items[i])

    def processEnv(self, keys):
        env={}
        for key in keys:
            try: env[key] = os.environ[key]
            except KeyError: pass
        return env
