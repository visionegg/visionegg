"""Load VisionEgg configuration values.

This module searches for configuration options in the following order:
environment variables, configuration file, generic defaults.  This
configuration file is by default ./VisionEgg.conf, but can be
specified with the environment variable VISIONEGG_CONFIG_FILE.

You can create a file with defaults for your system.  This should
be a text file with key/value pairs.  Blank lines and anything after
the pound symbol ("#") will be treated as a comment.  Each key/value
pairs should be on its own line and in the format "KEY=VALUE".  By
default the file "VisionEgg.conf" from the current directory is used,
but you can change this by setting the environment variable
VISIONEGG_CONFIG_FILE.

Applications should not import this module directly, because it is
automatically imported when any module of the VisionEgg is imported.
Values are accessible as members of VisionEgg.config.  For example,
VisionEgg.config.VISIONEGG_FULLSCREEN.
"""

# This is the python source code for the config module of the Vision Egg package.
#
# Based on Pyro/configuration.py, copyright (c) Irmen de Jong.
#
# Copyright (c) 2002 Andrew Straw.  Distributed under the terms of the
# GNU General Public License (GPL).  

####################################################################
#
#        Default configuration variables
#
####################################################################

# Special characters are '%c' (current directory, absolute) and
# $STORAGE which is replaced by the VISIONEGG_STORAGE path.

defaults= {
    'VISIONEGG_STORAGE':              '%u/VisionEggStorage', # %u means os.environ['HOME']
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

import string
__version__ = string.split('$Revision$')[1]
__date__ = string.join(string.split('$Date$')[1:3], ' ')
__author__ = 'Andrew Straw <astraw@users.sourceforge.net>'

import re, os, errno                     # standard python packages

class Config:
    def __init__(self):
        reader = ConfigReader(defaults)

        # See if there's an environment variable for the config file
        try:
            configFile = os.environ['VISIONEGG_CONFIG_FILE']
        except KeyError:
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
            if x.errno not in allowErrnos:
                print 'HMMMM errno=',repr(x.errno),type(x.errno)
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
            try:
                value = re.sub('%u',os.environ['HOME'],value)
            except KeyError: # no environment variable 'HOME' -- use os.curdir
                value = re.sub('%u',os.curdir,value)
            value = re.sub('^\$STORAGE\/',self.items['VISIONEGG_STORAGE'],value)
        return value
