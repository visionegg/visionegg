#include "Python.h"

/*
 * This is the C source code for synchronizing frame buffer buffer
 * swapping with vertical retrace pulse on the darwin platform.
 *
 * Copyright (c) 2002 Andrew Straw.  Distributed under the terms of
 * the GNU Lesser General Public License (LGPL).
 *
 * $Revision$
 * $Date$
 * Author = Andrew Straw <astraw@users.sourceforge.net>
 *
 */

#include <Cocoa/Cocoa.h>
#include <OpenGL/OpenGL.h>
#include <Carbon/Carbon.h>

#define TRY(E)     if(! (E)) return NULL

static char sync_swap__doc__[] = 
"Synchronize framebuffer swapping with vertical retrace sync pulse.";

static PyObject *sync_swap(PyObject * self, PyObject * args)
{
  CGLContextObj context;

  context = CGLGetCurrentContext();

  //CGLSetParameter(context,  kCGLCPSwapInterval, 1);
  //PyErr_SetString(PyExc_NotImplementedError,"_darwin_sync_swap.swap() not yet working. (And exception tracebacks not, either!)");

  Py_INCREF(Py_None);
  return Py_None;  /* It worked OK. */
}

static PyMethodDef
_darwin_sync_swap_methods[] = {
  { "sync_swap", sync_swap, METH_VARARGS, sync_swap__doc__},
  { NULL, NULL} /* sentinel */
};

DL_EXPORT(void)
init_darwin_sync_swap(void)
{
  Py_InitModule("_darwin_sync_swap", _darwin_sync_swap_methods);
  return;
}
