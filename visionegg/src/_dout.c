#include "Python.h"

/*
 * This is the C source code for a probably evil and definitely not
 * portable bit of code to set a digital out bit on the parallel port
 * of an x86 computer.  It's only been tried under linux.  This is
 * part of the Vision Egg library.
 *
 *
 * Copyright (c) 2001, 2002 Andrew Straw.  Distributed under the terms of
 * the GNU General Public License (GPL).
 *
 * $Revision$
 * $Date$
 * Author = Andrew Straw <astraw@users.sourceforge.net>
 *
 */
 
#include <stdio.h> // for ioperm
#include <asm/io.h> // for outb
#define LPT 0x378

#define TRY(E)     if(! (E)) return NULL

static int lpt_works; // define a couple of global variables
static int lpt_state;

static char _dout_toggle_dout__doc__[] = 
"Toggle DOUT.\n\nLinux x86 specific implementation: Toggles the lowest output\nbit of LPT0 (0x378).";

static PyObject *_dout_toggle_dout(PyObject * self, PyObject * args)
{
  //TRY(PyArg_ParseTuple(args,""));
  if (lpt_works) {
    lpt_state = !lpt_state; // toggle the output bit
    outb(lpt_state,LPT); // send it to LPT
  }
  Py_INCREF(Py_None);
  return Py_None;
}

static char _dout_set_dout__doc__[] = 
"Set DOUT.\n\nLinux x86 specific implementation: Sets the lowest output bit\nof LPT0 (0x378).";

static PyObject *_dout_set_dout(PyObject * self, PyObject * args)
{
  int i;

  TRY(PyArg_ParseTuple(args,"i", &i));
  if (lpt_works) {
    lpt_state = i; // set the output bit
    outb(lpt_state,LPT); // send it to LPT
  }
  Py_INCREF(Py_None);
  return Py_None;
}

static PyMethodDef
_dout_methods[] = {
  { "toggle_dout", _dout_toggle_dout, 1, _dout_toggle_dout__doc__},
  { "set_dout", _dout_set_dout, 1, _dout_set_dout__doc__},
  { NULL, NULL} /* sentinel */
};

DL_EXPORT(void)
init_dout(void)
{
  PyObject *module;
  module = Py_InitModule("_dout", _dout_methods);
  lpt_state = 0;
  if (ioperm(LPT, 8, 1) >= 0) {
    lpt_works = 1;
  }
  else {
    fprintf(stderr,"VisionEgg._dout: No permission to LPT. DOUT functions disabled. (Are you superuser?)\n");
    //PyErr_SetString(PyExc_RuntimeError,"_dout: No permission to LPT. (Are you superuser?)");
    lpt_works = 0;
  }
  if (PyErr_Occurred())
    PyErr_SetString(PyExc_ImportError,"_dout: init failed");
  return;
}
