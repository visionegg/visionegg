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
#define MAX_BASE_ADDRESSES 4

static long int ok_base_addresses[MAX_BASE_ADDRESSES];
static long int not_ok_base_addresses[MAX_BASE_ADDRESSES];
static unsigned short num_ok_base_addresses;
static unsigned short num_not_ok_base_addresses;

static short c_ok(long int base_address)
{
  unsigned short i;

  for (i=0; i<num_ok_base_addresses; i++) {
    if (base_address == ok_base_addresses[i]) {
      return 1;
    }
  }

  for (i=0; i<num_not_ok_base_addresses; i++) {
    if (base_address == not_ok_base_addresses[i]) {
      return 0;
    }
  }

  return -1; // unchecked
}

static short int c_check(long int base_address, short raise_ex)
{
  short ok;

  ok = c_ok(base_address);
  if (ok==-1) {
    if (ioperm(base_address, 8, 1) >= 0) {
      // it's OK
      ok_base_addresses[num_ok_base_addresses] = base_address;
      if (num_ok_base_addresses < MAX_BASE_ADDRESSES) {
	num_ok_base_addresses++;
      }
      return 1;
    }
    else {
      not_ok_base_addresses[num_not_ok_base_addresses] = base_address;
      if (num_not_ok_base_addresses < MAX_BASE_ADDRESSES) {
	num_not_ok_base_addresses++;
      }
      if (raise_ex) {
	PyErr_SetString(PyExc_IOError,"Cannot open LPT.  (Do you have permission?)");
      }
      return 0;
    } 
  }
  else {
    if (ok==0 && raise_ex) {
      PyErr_SetString(PyExc_IOError,"Cannot open LPT.  (Do you have permission?)");
    }
    return ok;
  }
}

static char base_address_ok__doc__[] = 
"VisionEgg._raw_lpt_linux.base_address_ok(base_address) -> bool";

static PyObject *base_address_ok(PyObject * self, PyObject * args)
{
  long int base_address;
  short ok;

  TRY(PyArg_ParseTuple(args,"l",&base_address));
  ok = c_ok(base_address);
  if (ok==-1) {
    return PyInt_FromLong((long)c_check(base_address,0));
  }
  else {
    return PyInt_FromLong((long)ok);
  }
}

static char inp__doc__[] = 
"VisionEgg._raw_lpt_linux.inp(base_address) -> value";

static PyObject *inp(PyObject * self, PyObject * args)
{
  long int base_address;
  unsigned short i;
  short ok;

  TRY(PyArg_ParseTuple(args,"l",&base_address));
  base_address = base_address - 1; // Convert to LPT base.

  // Fast check on port
  ok = 0;
  for (i=0; i<num_ok_base_addresses; i++) {
    if (base_address == ok_base_addresses[i]) {
      ok = 1;
      break;
    }
  }

  // Port not known to be OK, check it
  if (!ok) {
    if (!c_check(base_address,1)) {
      return NULL;
    }
  }

  return PyInt_FromLong((long)inb(base_address));
}

static char out__doc__[] = 
"VisionEgg._raw_lpt_linux.out(base_address, value) -> None";

static PyObject *out(PyObject * self, PyObject * args)
{
  long int base_address;
  short int value;
  unsigned short i;
  short ok;

  TRY(PyArg_ParseTuple(args,"lh",&base_address,&value));
  
  // Fast check on port
  ok = 0;
  for (i=0; i<num_ok_base_addresses; i++) {
    if (base_address == ok_base_addresses[i]) {
      ok = 1;
      break;
    }
  }

  // Port not known to be OK, check it
  if (!ok) {
    if (!c_check(base_address,1)) {
      return NULL;
    }
  }

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
  Py_InitModule("_raw_lpt_linux", _raw_lpt_linux_methods);
  num_ok_base_addresses = 0;
  num_not_ok_base_addresses = 0;

  c_check(0x0378,0);

  return;
}
