#include "Python.h"

/*
 * This is the C source code for setting maximum priority by the Vision Egg
 * library.
 *
 * It requires some POSIX (I believe) commands, but anyhow, I know
 * it works on linux and doesn't on Mac OS X 10.1.2 or Windows NT.
 *
 * Copyright (c) 2001, 2002 Andrew Straw.  Distributed under the terms of
 * the GNU Lesser General Public License (LGPL).
 *
 * $Revision$
 * $Date$
 * Author = Andrew Straw <astraw@users.sourceforge.net>
 *
 */
 
/* For _maxpriority_set_realtime */
#include <sys/mman.h>
#include <sched.h>
#include <errno.h>

#define TRY(E)     if(! (E)) return NULL

static char set_realtime__doc__[] = 
"Raise the Vision Egg to maximum priority.";

static PyObject *set_realtime(PyObject * self, PyObject * args)
{
  int policy;
  struct sched_param params;

  TRY(PyArg_ParseTuple(args,""));

  /* First, tell the scheduler that we want maximum priority! */
  //  policy = SCHED_RR;
  policy = SCHED_FIFO;
  params.sched_priority = sched_get_priority_max(policy);

  if (sched_setscheduler(0,policy,&params) == -1) { // pid 0 means this process
    switch(errno) {
    case EPERM:
      PyErr_SetString(PyExc_RuntimeError,"sched_setscheduler returned EPERM (Are you superuser?)");
      return NULL;
      break;
    case ESRCH:
      PyErr_SetString(PyExc_RuntimeError,"sched_setscheduler returned ESRCH");
      return NULL;
      break;
    case EINVAL:
      PyErr_SetString(PyExc_RuntimeError,"sched_setscheduler returned EINVAL");
      return NULL;
      break;
    default:
      PyErr_SetString(PyExc_RuntimeError,"sched_setscheduler returned unknown error");
      return NULL;
      break;
    }
  }
  
#ifdef MCL_CURRENT
#ifdef MCL_FUTURE
  /* Second, prevent the memory from paging. */
  if (mlockall(MCL_CURRENT|MCL_FUTURE) == -1) {
    switch(errno) {
    case EPERM:
      PyErr_SetString(PyExc_RuntimeError,"mlockall returned EPERM (Are you superuser?)");
      return NULL;
      break;
    case ESRCH:
      PyErr_SetString(PyExc_RuntimeError,"mlockall returned ESRCH");
      return NULL;
      break;
    case EINVAL:
      PyErr_SetString(PyExc_RuntimeError,"mlockall returned EINVAL");
      return NULL;
      break;
    default:
      PyErr_SetString(PyExc_RuntimeError,"mlockall returned unknown error");
      return NULL;
      break;
    }
  }
#endif /* closes ifdef MCL_FUTURE */
#endif /* closes ifdef MCL_CURRENT */

  Py_INCREF(Py_None);
  return Py_None;  /* It worked OK. */
}

static PyMethodDef
_maxpriority_methods[] = {
  { "set_realtime", set_realtime, METH_VARARGS, set_realtime__doc__},
  { NULL, NULL} /* sentinel */
};

DL_EXPORT(void)
init_maxpriority(void)
{
  Py_InitModule("_maxpriority", _maxpriority_methods);
  return;
}
