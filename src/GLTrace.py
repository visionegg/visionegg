"""Trace calls to OpenGL

With this module, you can trace all calls made to OpenGL through PyOpenGL.
To do this, substitute

import OpenGL.GL as gl

with

import VisionEgg.GLTrace as gl

in your code.

Also, trace another module's use of OpenGL by changing its reference
to OpenGL.GL to a reference to VisionEgg.GLTrace.
"""

# Copyright (c) 2003 Andrew Straw.  Distributed under the terms of the
# GNU Lesser General Public License (LGPL).

####################################################################
#
#        Import all the necessary packages
#
####################################################################

import OpenGL.GL as gl

import string        
__cvs__ = string.split('$Revision$')[1]
__date__ = string.join(string.split('$Date$')[1:3], ' ')
__author__ = 'Andrew Straw <astraw@users.sourceforge.net>'

gl_constants = {}

# functions which we don't want to translate arguments to gl constant
raw_args_by_function = {
    'glColor':[0,1,2,3],
    'glColorf':[0,1,2,3],
    'glDepthRange':[0,1],
    'glGenTextures':[0],
    'glGetTexLevelParameteriv':[1],
    'glOrtho':[0,1,2,3,4,5],
    'glReadPixels':[0,1,2,3],
    'glRotate':[0,1,2,3],
    'glTexImage1D':[1,3,4],
    'glTexImage2D':[1,3,4,5],
    'glTexSubImage1D':[1,2,3],
    'glTranslate':[0,1,2],
    'glVertex2f':[0,1],
    'glViewport':[0,1,2,3],
    }

bitmasks_by_function = {
    'glClear':[0],
    }

bitmask_names_by_value = {
    gl.GL_COLOR_BUFFER_BIT : 'GL_COLOR_BUFFER_BIT',
    gl.GL_DEPTH_BUFFER_BIT : 'GL_DEPTH_BUFFER_BIT',
    }

def arg_to_str( arg ):
    if type(arg) == int:
        if arg in gl_constants.keys():
            return gl_constants[arg]
    elif type(arg) == str and len(arg) > 30:
            return "'<string>'"
    return repr(arg)

class Wrapper:
    def __init__(self, function_name):
        self.function_name = function_name
        self.orig_func = getattr(gl,self.function_name)
    def run(self,*args,**kw):
        if kw: kw_str = " AND KEYWORDS"
        else: kw_str = ""
        if 1:
##        if self.function_name in raw_args_by_function:
            arg_str = []
            for i in range(len(args)):
                if self.function_name in raw_args_by_function and i in raw_args_by_function[self.function_name]:
                    arg_str.append(str(args[i])) # don't convert to name of OpenGL constant
                elif self.function_name in bitmasks_by_function and i in bitmasks_by_function[self.function_name]:
                    bitmask_strs = []
                    value = args[i]
                    for bit_value in bitmask_names_by_value:
                        if value & bit_value:
                            value = value & ~bit_value
                            bitmask_strs.append( bitmask_names_by_value[bit_value] )
                    if value != 0:
                        bitmask_strs.append( arg_to_str(args[i]) )
                    arg_str.append( '|'.join(bitmask_strs) )
                else:
                    arg_str.append(arg_to_str(args[i])) # convert to name of OpenGL constant
            arg_str = string.join( arg_str, "," )
##        else:
##            arg_str = string.join( map( arg_to_str, args ), "," )
        try:
            result = self.orig_func(*args,**kw)
        except:
            print "%s(%s)%s"%(self.function_name,arg_str,kw_str)
            raise

        if result is not None:
            result_str = "%s = "%(arg_to_str(result),)
        else:
            result_str = ''
        print "%s%s(%s)%s"%(result_str,self.function_name,arg_str,kw_str)
        return result

def attach():
    for attr_name in dir(gl):
        if callable( getattr(gl,attr_name) ):
            wrapper = Wrapper(attr_name)
            #cmd = "%s = wrapper.run"%attr_name
            #exec cmd
            globals()[attr_name] = wrapper.run
        else:
            #cmd = "%s = getattr(gl,'%s')"%(attr_name,attr_name)
            #print cmd
            attr = getattr(gl,attr_name)
            globals()[attr_name] = attr
            if not attr_name.startswith('__') and not attr_name.startswith('__'):
                if type(getattr(gl,attr_name)) == int:
                    gl_constants[getattr(gl,attr_name)] = attr_name
##                    if getattr(gl,attr) > 256: # assume first n aren't constants (n is arbitrary choice)
##                        gl_constants[getattr(gl,attr)] = attr

attach() # attach when imported
