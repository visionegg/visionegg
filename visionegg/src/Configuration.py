"""Load VisionEgg configuration values.

Applications should not import this module directly.  Instead, "import
VisionEgg" will result in an attribute "VisionEgg.config", which has
the configuration options as attributes.

This module searches for configuration options in the following order:
environment variables, configuration file, generic defaults.

The configuration file is by default VisionEgg.conf in the
VISIONEGG_STORAGE directory, which is by default "VisionEgg/storage"
in the base python directory.

You can create a file with defaults for your system.  This should be a
text file with key/value pairs.  Blank lines and anything after the
pound symbol ("#") will be treated as a comment.  Each key/value pairs
should be on its own line and in the format "KEY=VALUE".  By default
the file "VisionEgg.conf" from the VISIONEGG_STORAGE directory is used
if present.  You can specify a different filename and directory by
setting the environment variable VISIONEGG_CONFIG_FILE.
"""

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

# Special values:
#  %u means os.environ['HOME'] if defined, os.curdir otherwise
#  %b means sys.prefix
#  %c means os.curdir

defaults= {
    'VISIONEGG_STORAGE':              '%b/VisionEgg/storage',
    'VISIONEGG_DEFAULT_INIT':         'config', # could also be 'GUI'
    'VISIONEGG_SCREEN_W':             640,
    'VISIONEGG_SCREEN_H':             480,
    'VISIONEGG_FULLSCREEN':           0,
    'VISIONEGG_PREFERRED_BPP':        32,
    'VISIONEGG_SCREEN_BGCOLOR':       (0.5,0.5,0.5,0.0),
    'VISIONEGG_TEXTURE_COMPRESSION':  0,
    'VISIONEGG_MONITOR_REFRESH_HZ':   60,
    'VISIONEGG_MAXPRIORITY':          0
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

        # See if there's an environment variable for the config file
        if 'VISIONEGG_CONFIG_FILE' in os.environ.keys():
            configFile = os.environ['VISIONEGG_CONFIG_FILE']
        else:
            configFile = '' # If not, let the reader see if there's one in VISIONEGG_STORAGE
            
        try:
            reader.parse(configFile)
        except EnvironmentError,x:
            raise Exception("Error reading config file: "+configFile+": "+str(x))
        self.__dict__.update(reader.items)
        if(configFile):
            self.__dict__['VISIONEGG_CONFIG_FILE'] = os.path.abspath(configFile)
        else:
            self.__dict__['VISIONEGG_CONFIG_FILE'] = ''

        # Create the storage directory if it doesn't exist yet
        (drive,path)=os.path.splitdrive(self.VISIONEGG_STORAGE)
        allowErrnos=[errno.EEXIST, errno.EBUSY]
        if drive and (path=='\\' or path==''):
            # On windows, mkdir of drive root throws EACCES...
            allowErrnos.append(errno.EACCES)
        try:
            os.mkdir(self.VISIONEGG_STORAGE)
        except OSError,x:
            if x.errno == 13:#errno.EPERM:
                print "XXX hack!"
                self.VISIONEGG_STORAGE = os.path.join(os.environ['HOME'],"VisionEgg/storage")
                try:
                    os.mkdir(self.VISIONEGG_STORAGE)
                except OSError,x:
                    if x.errno not in allowErrnos:
                        raise 
            if x.errno not in allowErrnos:
                raise 

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

        # First, fix up VISIONEGG_STORAGE because others depend on it.
        self.items['VISIONEGG_STORAGE'] = self.treatSpecial(self.items['VISIONEGG_STORAGE'])

        # Now see if there's a config file in VISIONEGG_STORAGE and use that if we haven't already done a config file
        if not done_config_file:
            file = os.path.join(self.items['VISIONEGG_STORAGE'],'VisionEgg.cfg')
            if os.path.isfile(file):
                file=open(file).readlines()
                for l in file:
                    match=self.matcher.match(l)
                    if match:
                        if defaults.has_key(match.group(1)):
                            if match.group(2):
                                self.items[match.group(1)] = match.group(2)
                        else:
                            raise KeyError('Unknown config in configfile: '+match.group(1))
                
                # Parse the environment variables again (they override the config file)
                self.items.update(self.processEnv(defaults.keys()))
        
        # Now fix up all other items:
        for i in self.items.keys():

            newVal = self.treatSpecial(self.items[i])
            if i in ('VISIONEGG_STORAGE',):
                newVal=os.path.abspath(newVal)
            # fix the variable type if it's an integer
            if type(defaults[i]) == type(42):
                newVal = int(newVal)
            self.items[i]= newVal

    def processEnv(self, keys):
        env={}
        for key in keys:
            try: env[key] = os.environ[key]
            except KeyError: pass
        return env

    def treatSpecial(self, value):
        # treat special escape strings
        if type(value)==type(""):
            value = re.sub('%c',os.curdir,value)
            value = re.sub('%b',sys.prefix,value)
            try:
                value = re.sub('%u',os.environ['HOME'],value)
            except KeyError: # no environment variable 'HOME' -- use os.curdir
                value = re.sub('%u',os.curdir,value)
        return value
