#include "Python.h"

/*
 * Copyright (c) 2001, 2002 Andrew Straw.  Distributed under the terms of
 * the GNU Lesser General Public License (LGPL).
 *
 * $Revision$
 * $Date$
 * Author: Andrew Straw <astraw@users.sourceforge.net>
 *
 */
 
#include <stdio.h> // for ioperm
#include <asm/io.h> // for outb

#define TRY(E)     if(! (E)) return NULL

static char base_address_ok__doc__[] = 
"VisionEgg._raw_lpt_linux.base_address_ok(base_address) -> bool";

static PyObject *base_address_ok(PyObject * self, PyObject * args)
{
  long int base_address;

  TRY(PyArg_ParseTuple(args,"l",&base_address));
  if (ioperm(base_address, 8, 1) >= 0) {
    // It's OK.
    return PyInt_FromLong((long)1);
  }
  else {
    return PyInt_FromLong((long)0);
  }
}

static char inp__doc__[] = 
"VisionEgg._raw_lpt_linux.inp(base_address) -> value";

static PyObject *inp(PyObject * self, PyObject * args)
{
  long int base_address;

  TRY(PyArg_ParseTuple(args,"l",&base_address));
  return PyInt_FromLong((long)inb(base_address+1));
}

static char out__doc__[] = 
"VisionEgg._raw_lpt_linux.out(base_address, value) -> None";

static PyObject *out(PyObject * self, PyObject * args)
{
  long int base_address;
  short int value;

  TRY(PyArg_ParseTuple(args,"lh",&base_address,&value));
  outb(value,base_address);

  Py_INCREF(Py_None);
  return Py_None;
}

static PyMethodDef
_raw_lpt_linux_methods[] = {
  { "base_address_ok", base_address_ok, METH_VARARGS, base_address_ok__doc__},
  { "inp", inp, METH_VARARGS, inp__doc__},
  { "out", out, METH_VARARGS, out__doc__},
  { NULL, NULL} /* sentinel */
};

DL_EXPORT(void)
init_raw_lpt_linux(void)
{
  PyObject *module;
  module = Py_InitModule("_raw_lpt_linux", _raw_lpt_linux_methods);
  return;
}
