#include "Python.h"

/*
 * This is the C source code for various bits of the Vision Egg library.
 *
 * Copyright (c) 2001 Andrew Straw.  Distributed under the terms of the
 * GNU General Public License (GPL).
 *
 * $Revision$
 * $Date$
 * Author = Andrew Straw <astraw@users.sourceforge.net>
 *
 */
 
/* For _visionegg_getTime */
#include <sys/time.h>
#include <time.h>

/* For _visionegg_precise_sleep */
#include <unistd.h>

/* For _visionegg_setRealtime */
#ifndef __APPLE_CC__
#include <sys/mman.h>
#include <sched.h>
#include <errno.h>
#endif

#ifdef XXX_LPT_DOUT // This turns on a very non-portable i386 linux hack
#include <stdio.h> // for ioperm
#include <asm/io.h> // for outb
#define LPT 0x378
#endif

#define TRY(E)     if(! (E)) return NULL

static PyObject *_visionegg_getTime(PyObject * self, PyObject * args)
{
  double result;

#define USE_GETTIMEOFDAY
#ifdef USE_GETTIMEOFDAY
  static struct timeval tv;
  double sec;
  double usec;
  gettimeofday(&tv,NULL);
  sec = tv.tv_sec;
  usec = tv.tv_usec;
  result = sec + (usec*1.0e-6);
#endif
#ifdef USE_GETTIMEOFDAY2
  /* This seems broken. */
  //  static struct timeval mytv;
  //  gettimeofday(&mytv,NULL);
  //  return(mytv.tv_sec+mytv.tv_usec/1000000.0);
  static struct timespec myts;
  gettimeofday(&myts,NULL);
  result = (double)myts.tv_sec + (double)((double)myts.tv_nsec/(double)1.0e9);
#endif
#ifdef USE_RDTSC
  /* Never really tried to get this working.  It's not very portable! */
  // This bit is shamelessly stolen and modified from
  // latency-graph.c, (c) Benno Senoner, http://www.linuxdj.com/latency-graph
  extern double cpu_hz; // set magically from /proc/cpuinfo?
  unsigned long long int rdtsc;

  __asm__ volatile (".byte 0x0f, 0x31" : "=A" (rdtsc));

  result = rdtsc / cpu_hz;
#endif
  return Py_BuildValue("d",result);
}

static PyObject *_visionegg_preciseSleep(PyObject * self, PyObject * args)
{
  double arg1;
  unsigned long usec;

  TRY(PyArg_ParseTuple(args,"d", &arg1));
  usec = (unsigned long)(arg1*1.0e6); // Convert seconds to microseconds
  usleep(usec);
  Py_INCREF(Py_None);
  return Py_None;
}

static PyObject *_visionegg_setRealtime(PyObject * self, PyObject * args)
{
#ifndef __APPLE_CC__ // Mac OS X doesn't support setscheduler() commands
  int policy;
  struct sched_param params;

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

#endif /* closes ifndef __APPLE_CC__ */

  Py_INCREF(Py_None);
  return Py_None;  /* It worked OK. */
}

#ifdef XXX_LPT_DOUT
static int lpt_works; // define a couple of global variables
static int lpt_state;
#endif

static PyObject *_visionegg_toggleDOut(PyObject * self, PyObject * args)
{
#ifdef XXX_LPT_DOUT
  if (lpt_works) {
    lpt_state = !lpt_state; // toggle the output bit
    outb(lpt_state,LPT); // send it to LPT
  }
#endif
  Py_INCREF(Py_None);
  return Py_None;
}

static PyObject *_visionegg_set_dout(PyObject * self, PyObject * args)
{
  int i;

#ifdef XXX_LPT_DOUT
  TRY(PyArg_ParseTuple(args,"i", &i));
  if (lpt_works) {
    lpt_state = i; // set the output bit
    outb(lpt_state,LPT); // send it to LPT
  }
#endif
  Py_INCREF(Py_None);
  return Py_None;
}

static PyMethodDef
_visionegg_methods[] = {
  { "getTime", _visionegg_getTime, 1},
  { "preciseSleep", _visionegg_preciseSleep, 1},
  { "setRealtime", _visionegg_setRealtime, 1},
  { "toggleDOut", _visionegg_toggleDOut, 1},
  { "set_dout", _visionegg_set_dout, 1},
  { NULL, NULL} /* sentinel */
};

DL_EXPORT(void)
init_visionegg(void)
{
  PyObject *module;
  module = Py_InitModule("_visionegg", _visionegg_methods);
#ifdef XXX_LPT_DOUT
  lpt_state = 0;
  if (ioperm(LPT, 8, 1) >= 0) {
    lpt_works = 1;
  }
  else {
    fprintf(stderr,"_visionegg: No permission to LPT. (Are you superuser?)\n");
    //PyErr_SetString(PyExc_RuntimeError,"_visionegg: No permission to LPT. (Are you superuser?)");
    lpt_works = 0;
  }
#endif
  if (PyErr_Occurred())
    PyErr_SetString(PyExc_ImportError,"_visionegg: init failed");
  return;
}
