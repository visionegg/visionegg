#include "Python.h"

/*
 * This is the C source code for setting maximum priority by the Vision Egg
 * library.
 *
 * I believe it requires some POSIX commands or a darwin system. I know
 * it works on linux and Mac OS X 10.1.4 but not Windows.
 *
 * Copyright (c) 2001, 2002 Andrew Straw.  Distributed under the terms of
 * the GNU Lesser General Public License (LGPL).
 *
 * $Revision$
 * $Date$
 * Author = Andrew Straw <astraw@users.sourceforge.net>
 *
 */

#ifndef __APPLE__
#include <sys/mman.h>
#include <sched.h>
#include <errno.h>
#else
/* Everything to support realtime in Apple Mac OS X is based on the following two things:

   1) http://developer.apple.com/techpubs/macosx/Darwin/General/KernelProgramming/scheduler/Using_Mach__pplications.html

   2) The Mac OS X port of the Esound daemon.

*/

#include "darwin_pthread_modified.h" // Had problems with original...
#include <mach/mach.h>
#include <sys/sysctl.h>
#endif /* closes ifndef __APPLE__ */

#define TRY(E)     if(! (E)) return NULL

static char set_realtime__doc__[] = 
"Raise the Vision Egg to maximum priority.

The following optional keyword arguments only have an effect
on the darwin (Mac OS X) platform:

  darwin_period_denom = 120;
  darwin_computation_denom = 2400;
  darwin_constraint_denom = 1200;
  darwin_preemptible = 0;";

static PyObject *set_realtime(PyObject *self, PyObject *args, PyObject *kw)
{
  static char *kwlist[] = {"darwin_period_denom",
			   "darwin_computation_denom",
			   "darwin_constraint_denom",
			   "darwin_preemptible",
			   NULL};

  int darwin_period_denom;
  int darwin_computation_denom;
  int darwin_constraint_denom;
  int darwin_preemptible;
#ifndef __APPLE__
  struct sched_param params;
  int policy;
#else /* ifndef __APPLE__ */
  struct thread_time_constraint_policy ttcpolicy;
  int ret;
  int bus_speed, mib [2] = { CTL_HW, HW_BUS_FREQ };
  size_t len;
#endif /* ifndef __APPLE__ */

  /* Default values for keyword arguments */
  darwin_period_denom = 120;
  darwin_computation_denom = 2400;
  darwin_constraint_denom = 1200;
  darwin_preemptible = 0;

  /* Get keyword arguments */
  TRY(PyArg_ParseTupleAndKeywords(args,kw,"|iiii",kwlist,
				  &darwin_period_denom,
				  &darwin_computation_denom,
				  &darwin_constraint_denom,
				  &darwin_preemptible));

#ifndef __APPLE__

  /* This should work on all POSIX non-Apple platforms. See below for
     Apple Mac OS X implementation. */

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
#endif /* closes ifndef __APPLE__ */

#ifdef __APPLE__
  /* The Apple Mac OS X specific version */

  len = sizeof(bus_speed);
  sysctl( mib, 2, &bus_speed, &len, NULL, 0);

  ttcpolicy.period= bus_speed / darwin_period_denom;
  ttcpolicy.computation=bus_speed / darwin_computation_denom;
  ttcpolicy.constraint=bus_speed / darwin_constraint_denom;
  ttcpolicy.preemptible= darwin_preemptible ;

  ret=thread_policy_set(mach_thread_self(),
			THREAD_TIME_CONSTRAINT_POLICY,
			(int *)&ttcpolicy,
			THREAD_TIME_CONSTRAINT_POLICY_COUNT);

  if (ret != KERN_SUCCESS) {
    PyErr_SetString(PyExc_RuntimeError,"Failed trying to set realtime priority in Mac OS X.");
    return NULL;
  }

#endif /* clases ifdef __APPLE__ */

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
