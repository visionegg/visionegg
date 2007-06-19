/*
 * Copyright (c) 2003 Andrew Straw.  Distributed under the terms of
 * the GNU Lesser General Public License (LGPL).
 *
 * $Revision$
 * $Date$
 * Author: Andrew Straw <astraw@users.sourceforge.net>
 *
 */

#include "Python.h"
#include "numpy/oldnumeric.h"

#if defined(MS_WINDOWS)
#  include <windows.h>
#endif

#if defined(__APPLE__)
#  include <OpenGL/gl.h>
#else
#  include <GL/gl.h>
#endif

static char draw_dots__doc__[] = 
"VisionEgg._draw_in_c._draw_dots(x,y,z) -> None";

static PyObject *
draw_dots(PyObject *self, PyObject *args)
{
  PyObject *input1, *input2, *input3;
  PyArrayObject *x=NULL;
  PyArrayObject *y=NULL;
  PyArrayObject *z=NULL;
  int i, n;

  if (!PyArg_ParseTuple(args, "OOO", &input1, &input2, &input3))
    return NULL;
  x = (PyArrayObject *)
    PyArray_ContiguousFromObject(input1, PyArray_DOUBLE, 1, 1);
  if (x == NULL)
    goto fail;
  y = (PyArrayObject *)
    PyArray_ContiguousFromObject(input2, PyArray_DOUBLE, 1, 1);
  if (y == NULL)
    goto fail;
  z = (PyArrayObject *)
    PyArray_ContiguousFromObject(input3, PyArray_DOUBLE, 1, 1);
  if (z == NULL)
    goto fail;

  n = x->dimensions[0];

  if (n != y->dimensions[0]) {
    PyErr_SetString(PyExc_ValueError,"All three arguments must be same length");
    goto fail;
  }

  if (n != z->dimensions[0]) {
    PyErr_SetString(PyExc_ValueError,"All three arguments must be same length");
    goto fail;
  }

  glBegin(GL_POINTS);
  for (i = 0; i < n; i++) {
    glVertex3f( *(double *)(x->data + i*x->strides[0]),
		*(double *)(y->data + i*y->strides[0]),
		*(double *)(z->data + i*z->strides[0]));
  }
  glEnd();

  Py_DECREF(x);
  Py_DECREF(y);
  Py_DECREF(z);

  Py_INCREF(Py_None);
  return Py_None;

 fail:
  Py_XDECREF(x);
  Py_XDECREF(y);
  Py_XDECREF(z);

  return NULL;
}

static PyMethodDef
_draw_in_c_methods[] = {
  { "draw_dots", draw_dots, METH_VARARGS, draw_dots__doc__},
  { NULL, NULL} /* sentinel */
};

DL_EXPORT(void)
init_draw_in_c(void)
{
  Py_InitModule("_draw_in_c", _draw_in_c_methods);
  import_array();
  return;
}
