"""Load config values from environment, config file, or defaults.

Applications should not import this module directly.  Instead, "import
VisionEgg" will result in an attribute "VisionEgg.config", which has
the configuration options as attributes.

This module searches for configuration options from the following
places: environment variables, configuration file, generic defaults.
Environment variables take precedence over the configuration file,
which takes precedence over the generic defaults.

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

# Warning: This code is a bit of a hack

# This is the python source code for the config module of the Vision Egg package.
#
# Copyright (c) 2002 Andrew Straw.  Distributed under the terms of the
# GNU Lesser General Public License (LGPL).

import VisionEgg
import re, os, errno, sys                  # standard python packages
import ConfigParser
import string

__version__ = VisionEgg.release_name
__cvs__ = string.split('$Revision$')[1]
__date__ = string.join(string.split('$Date$')[1:3], ' ')
__author__ = 'Andrew Straw <astraw@users.sourceforge.net>'

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
    'VISIONEGG_HIDE_MOUSE':           1,
    'VISIONEGG_FRAMELESS_WINDOW':     0,
    'VISIONEGG_PREFERRED_BPP':        32,
    'VISIONEGG_MONITOR_REFRESH_HZ':   60.0,
    'VISIONEGG_SYNC_SWAP':            1,
    'VISIONEGG_RECORD_TIMES':         1,
    'VISIONEGG_MAXPRIORITY':          0,
    'VISIONEGG_REQUEST_RED_BITS':     8,
    'VISIONEGG_REQUEST_GREEN_BITS':   8,
    'VISIONEGG_REQUEST_BLUE_BITS':    8,
    'VISIONEGG_REQUEST_ALPHA_BITS':   0,
    'VISIONEGG_TKINTER_OK':           1,
    'VISIONEGG_MESSAGE_LEVEL':        1,
    'VISIONEGG_GUI_ON_ERROR':         1,
    'VISIONEGG_LOG_FILE':             'VisionEgg.log', # "" (blank string) means sys.stderr
    'VISIONEGG_LOG_TO_STDERR':        1,
    'SYNCLYNC_PRESENT':               0,
    }

extra_darwin_defaults = {
    'VISIONEGG_DARWIN_MAXPRIORITY_CONVENTIONAL_NOT_REALTIME'  : 1,
    'VISIONEGG_DARWIN_CONVENTIONAL_PRIORITY'                  : -20, # -20 is best priority
    'VISIONEGG_DARWIN_REALTIME_PERIOD_DENOM'                  : 120,
    'VISIONEGG_DARWIN_REALTIME_COMPUTATION_DENOM'             : 2400,
    'VISIONEGG_DARWIN_REALTIME_CONSTRAINT_DENOM'              : 1200,
    'VISIONEGG_DARWIN_REALTIME_PREEMPTIBLE'                   : 0,
    'VISIONEGG_DARWIN_PTHREAD_PRIORITY'                      : 'max',
}

class Config:
    def __init__(self):
        
        cfg = ConfigParser.ConfigParser()
        
        if sys.executable == sys.argv[0]: # Windows binary
            self.VISIONEGG_SYSTEM_DIR = os.curdir
            self.VISIONEGG_USER_DIR = os.curdir
        else:
            self.VISIONEGG_SYSTEM_DIR = os.path.join(sys.prefix,"VisionEgg")
            user_dir = os.path.expanduser("~")
            self.VISIONEGG_USER_DIR = os.path.join(user_dir,"VisionEgg")

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

        if configFile:
            try:
                cfg.read(configFile)
            except ConfigParser.MissingSectionHeaderError:
#                sys.stderr.write("Error opening old VisionEgg.cfg format file at %s\n"%(os.path.abspath(configFile),))
#                sys.stderr.flush()
                raise
        else:
            # pretend we have a config file
            cfg.add_section('General')
            for key in defaults.keys():
                cfg.set('General',key,str(defaults[key]))
            if sys.platform == 'darwin':
                cfg.add_section('darwin')
                for key in extra_darwin_defaults.keys():
                    cfg.set('darwin',key,str(defaults[key]))

        # Do the general stuff first
        # Set the default values
        for name in defaults.keys():
            setattr(self,name,defaults[name])

        # Get the values from the configFile
        try:
            general_options = cfg.options('General')
        except ConfigParser.NoSectionError,x:
#            sys.stderr.write("Error opening VisionEgg.cfg at %s (is it old format?)\n"%(os.path.abspath(configFile),))
#            sys.stderr.flush()
            raise
        for option in general_options:
            name = string.upper(option)
            if name == "SYNCMASTER_PRESENT": # old name for SyncLync
                continue
            if name not in defaults.keys():
                raise KeyError("Error while reading %s: The variable \"%s\" is not a Vision Egg variable."%(os.path.abspath(configFile),option))
            value = cfg.get('General',option)
            if name in os.environ.keys():
                value = os.environ[name]
            if type(defaults[name]) == type(42): # int
                setattr(self,name,int(value))
            elif type(defaults[name]) == type(42.0): # float
                setattr(self,name,float(value))
            else:
                setattr(self,name,value)

        # Do platform specific stuff
        # Set the default values
        platform_name = sys.platform
        extra_name = "extra_%s_defaults"%(platform_name,)
        if extra_name in globals().keys():
            extra_defaults = globals()[extra_name]
            for name in extra_defaults.keys():
                setattr(self,name,extra_defaults[name])

            # Get the values from the configFile
            try:
                platform_options = cfg.options(platform_name)
            except ConfigParser.NoSectionError,x:
#                sys.stderr.write("Error opening old VisionEgg.cfg format file at %s\n"%(os.path.abspath(configFile),))
#                sys.stderr.flush()
                raise
            for option in platform_options:
                name = string.upper(option)
                if name not in extra_defaults.keys():
                    raise KeyError("No Vision Egg configuration variable \"%s\""%option)
                value = cfg.get(platform_name,option)
                if name in os.environ.keys():
                    value = os.environ[name]
                if type(extra_defaults[name]) == type(42): # int
                    setattr(self,name,int(value))
                elif type(extra_defaults[name]) == type(42.0): # float
                    setattr(self,name,float(value))
                else:
                    setattr(self,name,value)
            
        if(configFile):
            self.VISIONEGG_CONFIG_FILE = os.path.abspath(configFile)
        else:
            self.VISIONEGG_CONFIG_FILE = None

def save_settings():
    """Save the current values to the config file, overwriting what is there."""

    dont_save = ['VISIONEGG_CONFIG_FILE',
                 'VISIONEGG_SYSTEM_DIR',
                 'VISIONEGG_USER_DIR',
                 ]
    
    if not VisionEgg.config.VISIONEGG_CONFIG_FILE:
        raise RuntimeError("No config file in use.")
#    re_section_finder = re.compile(r"^\s?\[(\w+)\]\s?$")
    re_setting_finder = re.compile(r"^\s?((?:VISIONEGG_[A-Z_]*)|(?:SYNCLYNC_[A-Z_]*))\s?=\s?(\S*)\s?$",re.IGNORECASE)

##    used_stderr = 0
##    def stderr_header():
##        sys.stderr.write("VisionEgg.Configuration.save_settings() messages:\n")

#    print VisionEgg.config.VISIONEGG_CONFIG_FILE
    orig_file = open(VisionEgg.config.VISIONEGG_CONFIG_FILE,"r")
    orig_lines = orig_file.readlines()

    line_ending = orig_lines[0][-2:]
    if line_ending[0] not in ['\r','\n','\l']:
        line_ending = line_ending[1]

    out_file_lines = []
    
    saved_config_vars = []
#    current_section = None

    for line in orig_lines:
#        match = re_section_finder.match(out_line)
#        if match:
#            current_section = match.group(1)
##        if string.lower(current_section) == sys.platform or string.lower(current_section) = 'general':
##            pass

        out_line = line # The output is the same as the input unless there's a match
        match = re_setting_finder.match(line)
        if match:
            name = string.upper(match.group(1))
            if name in VisionEgg.config.__dict__.keys():
                if name not in dont_save:
                    # Change the output line
                    out_line = ("%s = %s"%(name,getattr(VisionEgg.config,name,))) + line_ending
                    saved_config_vars.append(name)
##            else:
##                if not used_stderr:
##                    stderr_header()
##                    used_sterr = 1
#                sys.stderr.write("  warning: %s found in config file, but don't know anything about this variable.\n"%(name,))
        out_file_lines.append(out_line)

##    for test_name in VisionEgg.config.__dict__.keys():
##        if test_name not in saved_config_vars:
##            if test_name not in dont_save:
##                if not used_stderr:
##                    stderr_header()
##                    used_stderr = 1
#                sys.stderr.write("  info: Not writing variable %s because it is not in original configuration file.\n"%(test_name,))

    # Close and reopen orig_file in write mode
    orig_file.close()
    orig_file = open(VisionEgg.config.VISIONEGG_CONFIG_FILE,"w")
    for line in out_file_lines:
        orig_file.write(line)

