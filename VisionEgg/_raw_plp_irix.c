#include "Python.h"

/*
 * This code is a skeleton with no functionality. I don't have
 * the time to get the parallel port working under IRIX, but
 * it looks like it's possible.  I've included the relevant
 * header files below.
 * 
 * Copyright (c) 2001, 2002 Andrew Straw.  Distributed under the terms of
 * the GNU Lesser General Public License (LGPL).
 *
 * $Revision$
 * $Date$
 * Author: Andrew Straw <astraw@users.sourceforge.net>
 *
 */

#include <sys/plp.h>
#include <sys/ioctl.h>

#define TRY(E)     if(! (E)) return NULL

#define ERRSTR "Parallel port possible but not implemented on IRIX."

static char base_address_ok__doc__[] = 
"VisionEgg._raw_plp_irix.base_address_ok(base_address) -> bool";

static PyObject *base_address_ok(PyObject * self, PyObject * args)
{
  long int base_address;

  TRY(PyArg_ParseTuple(args,"l",&base_address));
  PyErr_SetString(PyExc_NotImplementedError,ERRSTR);
  return NULL;
}

static char inp__doc__[] = 
"VisionEgg._raw_plp_irix.inp(base_address) -> value";

static PyObject *inp(PyObject * self, PyObject * args)
{
  long int base_address;

  TRY(PyArg_ParseTuple(args,"l",&base_address));
  PyErr_SetString(PyExc_NotImplementedError,ERRSTR);
  return NULL;
}

static char out__doc__[] = 
"VisionEgg._raw_plp_irix.out(base_address, value) -> None";

static PyObject *out(PyObject * self, PyObject * args)
{
  long int base_address;
  short int value;

  TRY(PyArg_ParseTuple(args,"lh",&base_address,&value));
  PyErr_SetString(PyExc_NotImplementedError,ERRSTR);
  return NULL;
}

static PyMethodDef
_raw_plp_irix_methods[] = {
  { "base_address_ok", base_address_ok, METH_VARARGS, base_address_ok__doc__},
  { "inp", inp, METH_VARARGS, inp__doc__},
  { "out", out, METH_VARARGS, out__doc__},
  { NULL, NULL} /* sentinel */
};

DL_EXPORT(void)
init_raw_plp_irix(void)
{
  Py_InitModule("_raw_plp_irix", _raw_plp_irix_methods);
  return;
}
