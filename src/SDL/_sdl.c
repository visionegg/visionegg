#include "Python.h"
#include <SDL/SDL.h>

/*
 * This is the C source code for the Vision Egg's binding of the SDL library.
 *
 * Copyright (c) 2001 Andrew Straw.  Distributed under the terms of the
 * GNU General Public License (GPL).
 *
 * $Revision$
 * $Date$
 * Author = Andrew Straw <astraw@users.sourceforge.net>
 *
 */

#define TRY(E)     if(! (E)) return NULL
#define SDL_TRY(E) if( (E)) { PyErr_SetString(_sdl_Error,SDL_GetError()); return NULL; }
#define SDL_TRY_NULLBAD(E) if( (E)==NULL) { PyErr_SetString(_sdl_Error,SDL_GetError()); return NULL; }

// globals
static PyObject *_sdl_Error;

static PyObject *_sdl_GL_GetAttribute(PyObject * self, PyObject * args)
{
  int arg1;
  int result;
  SDL_GLattr a;

  TRY(PyArg_ParseTuple(args,"i", &arg1));
  switch(arg1) {
    case 0x01: a = SDL_GL_RED_SIZE; break;
    case 0x02: a = SDL_GL_GREEN_SIZE; break;
    case 0x03: a = SDL_GL_BLUE_SIZE; break;
    case 0x04: a = SDL_GL_ALPHA_SIZE; break;
    case 0x05: a = SDL_GL_BUFFER_SIZE; break;
    case 0x06: a = SDL_GL_DOUBLEBUFFER; break;
    case 0x07: a = SDL_GL_DEPTH_SIZE; break;
    case 0x08: a = SDL_GL_STENCIL_SIZE; break;
    case 0x09: a = SDL_GL_ACCUM_RED_SIZE; break;
    case 0x0A: a = SDL_GL_ACCUM_GREEN_SIZE; break;
    case 0x0B: a = SDL_GL_ACCUM_BLUE_SIZE; break;
    case 0x0C: a = SDL_GL_ACCUM_ALPHA_SIZE; break;
  default: PyErr_SetString(_sdl_Error,"Invalid flag passed to SDL_GL_SetAttribute."); return NULL;
  }
  SDL_TRY(SDL_GL_GetAttribute(a,&result));
  return Py_BuildValue("i",result);  
}

static PyObject *_sdl_ListModes(PyObject * self, PyObject * args)
{
  PyObject* arg1;
  int arg2;

  SDL_Rect** modes;
  int i;
  PyObject* result;

  if (!SDL_WasInit(SDL_INIT_VIDEO)) {
    PyErr_SetString(_sdl_Error,"Video subsystem not initialized.");
    return NULL;
  }

  TRY(PyArg_ParseTuple(args,"Oi",&arg1, &arg2));
  if (arg1 != Py_None) {
    PyErr_SetString(_sdl_Error,"Sorry, can't handle pixel formats yet.");
    return NULL;
  }
  modes=SDL_ListModes(NULL,arg2);

  if (modes == (SDL_Rect**)0) { // No modes available
    PyErr_SetString(_sdl_Error,"No modes available.");
    return NULL;
  }
  if (modes == (SDL_Rect**)-1) { // Resolutions not restricted
    Py_INCREF(Py_None);
    return Py_None;
  }
  else {
    result = PyList_New(0);
    for (i=0;modes[i];++i) {
      if (PyList_Append(result,Py_BuildValue("(i,i)",modes[i]->w,modes[i]->h)))
	return NULL;
    }
  }
  return result;
}

static PyObject *_sdl_GL_SetAttribute(PyObject * self, PyObject * args)
{
  int arg1, arg2;
  SDL_GLattr a;

  TRY(PyArg_ParseTuple(args,"ii", &arg1, &arg2));
  switch(arg1) {
    case 0x01: a = SDL_GL_RED_SIZE; break;
    case 0x02: a = SDL_GL_GREEN_SIZE; break;
    case 0x03: a = SDL_GL_BLUE_SIZE; break;
    case 0x04: a = SDL_GL_ALPHA_SIZE; break;
    case 0x05: a = SDL_GL_BUFFER_SIZE; break;
    case 0x06: a = SDL_GL_DOUBLEBUFFER; break;
    case 0x07: a = SDL_GL_DEPTH_SIZE; break;
    case 0x08: a = SDL_GL_STENCIL_SIZE; break;
    case 0x09: a = SDL_GL_ACCUM_RED_SIZE; break;
    case 0x0A: a = SDL_GL_ACCUM_GREEN_SIZE; break;
    case 0x0B: a = SDL_GL_ACCUM_BLUE_SIZE; break;
    case 0x0C: a = SDL_GL_ACCUM_ALPHA_SIZE; break;
  default: PyErr_SetString(_sdl_Error,"Invalid flag passed to SDL_GL_SetAttribute."); return NULL;
  }
  SDL_TRY(SDL_GL_SetAttribute(a,arg2));
  Py_INCREF(Py_None);
  return Py_None;  
}

static PyObject *_sdl_GL_SwapBuffers(PyObject * self, PyObject * args)
{
  SDL_GL_SwapBuffers();
  Py_INCREF(Py_None);
  return Py_None;
}

static PyObject *_sdl_Init(PyObject * self, PyObject * args)
{
  int arg1;
  TRY(PyArg_ParseTuple(args,"i", &arg1));
  SDL_TRY(SDL_Init(arg1));
  Py_INCREF(Py_None);
  return Py_None;
}

static PyObject *_sdl_Quit(PyObject * self, PyObject * args)
{
  SDL_Quit();
  Py_INCREF(Py_None);
  return Py_None;
}

static PyObject *_sdl_SetVideoMode(PyObject * self, PyObject * args)
{
  int arg1, arg2, arg3, arg4;
  SDL_Surface *surf;

  TRY(PyArg_ParseTuple(args,"iiii", &arg1, &arg2, &arg3, &arg4));
  surf = SDL_SetVideoMode(arg1,arg2,arg3,arg4);
  SDL_TRY_NULLBAD(surf);
  return PyCObject_FromVoidPtr((void*)surf,NULL);
}

static PyObject *_sdl_ShowCursor(PyObject * self, PyObject * args)
{
  int arg1, result;
  TRY(PyArg_ParseTuple(args,"i", &arg1));
  result = SDL_ShowCursor(arg1);
  
  return Py_BuildValue("i", result);
}

static PyObject *_sdl_WM_SetCaption(PyObject * self, PyObject * args)
{
  char * arg1, * arg2;

  arg1 = NULL;
  arg2 = NULL;
  TRY(PyArg_ParseTuple(args,"|zz",&arg1,&arg2));
  SDL_WM_SetCaption(arg1,arg2);
  Py_INCREF(Py_None);
  return Py_None;
}


static PyMethodDef
_sdl_methods[] = {
  { "SDL_GL_GetAttribute", _sdl_GL_GetAttribute, 1},
  { "SDL_GL_SetAttribute", _sdl_GL_SetAttribute, 1},
  { "SDL_GL_SwapBuffers", _sdl_GL_SwapBuffers, 1},
  { "SDL_Init", _sdl_Init, 1},
  { "SDL_ListModes", _sdl_ListModes, 1},
  { "SDL_Quit", _sdl_Quit, 1},
  { "SDL_SetVideoMode",_sdl_SetVideoMode, 1},
  { "SDL_ShowCursor", _sdl_ShowCursor, 1},
  { "SDL_WM_SetCaption", _sdl_WM_SetCaption, 1},
  { NULL, NULL} /* sentinel */
};

DL_EXPORT(void)
init_sdl(void)
{
  PyObject *module;
  module = Py_InitModule("_sdl", _sdl_methods);
  _sdl_Error = Py_BuildValue("s", "_sdl.error: ");
  //_sdl_Error = PyExc_RuntimeError;
  if (PyErr_Occurred())
    PyErr_SetString(PyExc_ImportError,"_sdl: init failed");
  return;
}
