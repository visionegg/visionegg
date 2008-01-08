# The Vision Egg: GLTrace
#
# Copyright (C) 2001-2004 Andrew Straw
# Copyright (C) 2004,2008 California Institute of Technology
#
# URL: <http://www.visionegg.org/>
#
# Distributed under the terms of the GNU Lesser General Public License
# (LGPL). See LICENSE.TXT that came with this file.

"""
Trace calls to OpenGL

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

gl_constants = {}

# functions which we don't want to translate arguments to gl constant
raw_args_by_function = {
    'glColor':[0,1,2,3],
    'glColorf':[0,1,2,3],
    'glDepthRange':[0,1],
    'glGenTextures':[0],
    'glGetTexLevelParameteriv':[1],
    'glOrtho':[0,1,2,3,4,5],
    'glPixelStorei':[1],
    'glReadPixels':[0,1,2,3],
    'glRotate':[0,1,2,3],
    'glTexCoord2f':[0,1],
    'glTexImage1D':[1,3,4],
    'glTexImage2D':[1,3,4,5],
    'glTexSubImage1D':[1,2,3],
    'glTranslate':[0,1,2],
    'glVertex2f':[0,1],
    'glVertex3f':[0,1,2],
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
    if isinstance(arg, int):
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
            arg_str = ','.join( arg_str )
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

def gl_trace_attach():
    for attr_name in dir(gl):
        if callable( getattr(gl,attr_name) ):
            wrapper = Wrapper(attr_name)
            globals()[attr_name] = wrapper.run
        else:
            attr = getattr(gl,attr_name)
            globals()[attr_name] = attr
            if not attr_name.startswith('__') and not attr_name.startswith('__'):
                if type(getattr(gl,attr_name)) == int:
                    gl_constants[getattr(gl,attr_name)] = attr_name
    if not hasattr(gl,'GL_CLAMP_TO_EDGE'):
        # XXX This hack requires opengl >= 1.2. See Core.py for more info.
        globals()['GL_CLAMP_TO_EDGE'] = 0x812F
    if hasattr(gl,'glActiveTexture'):
        # XXX Another, similar hack.
        globals()['glActiveTextureARB'] = gl.glActiveTexture
        globals()['glMultiTexCoord2fARB'] = gl.glMultiTexCoord2f
        globals()['GL_TEXTURE0_ARB'] = gl.GL_TEXTURE0
        globals()['GL_TEXTURE1_ARB'] = gl.GL_TEXTURE1

gl_trace_attach() # attach when imported
